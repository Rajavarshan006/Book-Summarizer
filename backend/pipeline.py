from typing import Dict, Optional
from datetime import datetime
import logging
import nltk

from backend.preprocessing import (
    clean_text,
    preprocess_text
)
from backend.language_detection import detect_language
from backend.sentence_segmentation import segment_sentences
from backend.text_statistics import calculate_text_statistics
from backend.text_chunking import chunk_text, get_chunk_summary_info, IntelligentTextChunker
from backend.chunk_repository import chunk_repository

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')


class PreprocessingPipeline:
    """
    Comprehensive text preprocessing pipeline wrapper.
    Orchestrates all preprocessing steps: cleaning, language detection,
    sentence segmentation, statistics calculation, and text chunking.
    """

    # Named constants for word-to-token conversion
    WORD_TO_TOKEN_RATIO = 1.3
    DEFAULT_MIN_CHUNK_WORDS = 100

    def __init__(self, chunk_size: int = 1200, overlap_size: int = 125, word_to_token_ratio: Optional[float] = None):
        """
        Initialize the preprocessing pipeline.

        Args:
            chunk_size: Target words per chunk (default 1200)
            overlap_size: Overlap words between chunks (default 125)
            word_to_token_ratio: Conversion ratio from words to tokens (default 1.3)
        """
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.word_to_token_ratio = word_to_token_ratio or self.WORD_TO_TOKEN_RATIO
        self.logger = logger
    
    def process(self, text: str, book_id: str = None) -> Dict:
        """
        Execute the complete preprocessing pipeline.

        Args:
            text: Raw text to process
            book_id: Optional book ID to associate chunks with

        Returns:
            Dictionary containing:
            - success: Whether processing succeeded
            - processed_text: Final cleaned text
            - language: Detected language info
            - statistics: Text statistics
            - chunks: List of text chunks
            - chunk_info: Summary of chunking
            - metadata: Processing metadata (timestamps, steps executed)
            - errors: Any errors encountered during processing
        """
        start_time = datetime.now()
        errors = []
        results = {
            "success": False,
            "processed_text": "",
            "language": None,
            "statistics": None,
            "chunks": [],
            "chunk_info": None,
            "metadata": {
                "start_time": start_time.isoformat(),
                "end_time": None,
                "duration_seconds": None,
                "steps_completed": []
            },
            "errors": []
        }
        
        try:
            # Step 1: Validate input
            if not text or not isinstance(text, str):
                raise ValueError("Input text must be a non-empty string")
            
            self.logger.info(f"Starting preprocessing pipeline for {len(text)} characters")
            
            # Step 2: Clean text
            try:
                cleaned_text = clean_text(text)
                results["metadata"]["steps_completed"].append("clean_text")
                self.logger.info("✓ Text cleaning completed")
            except Exception as e:
                error_msg = f"Text cleaning failed: {str(e)}"
                self.logger.error(error_msg)
                errors.append(error_msg)
                return self._finalize_results(results, errors, start_time)
            
            # Step 3: Detect language
            try:
                language = detect_language(cleaned_text)
                results["language"] = language
                results["metadata"]["steps_completed"].append("language_detection")
                self.logger.info(f"✓ Language detected: {language['language_name']}")
            except Exception as e:
                error_msg = f"Language detection failed: {str(e)}"
                self.logger.warning(error_msg)
                errors.append(error_msg)
                # Don't fail pipeline on language detection error
            
            # Step 4: Segment sentences
            try:
                sentences = segment_sentences(cleaned_text)
                results["metadata"]["steps_completed"].append("sentence_segmentation")
                self.logger.info(f"✓ Sentence segmentation completed: {len(sentences)} sentences")
            except Exception as e:
                error_msg = f"Sentence segmentation failed: {str(e)}"
                self.logger.error(error_msg)
                errors.append(error_msg)
                return self._finalize_results(results, errors, start_time)
            
            # Step 5: Calculate statistics
            try:
                statistics = calculate_text_statistics(cleaned_text)
                results["statistics"] = statistics
                results["metadata"]["steps_completed"].append("statistics_calculation")
                self.logger.info(f"✓ Statistics calculated: {statistics['word_count']} words")
            except Exception as e:
                error_msg = f"Statistics calculation failed: {str(e)}"
                self.logger.warning(error_msg)
                errors.append(error_msg)
                # Don't fail pipeline on statistics error
            
            # Step 6: Create text chunks using consistent token-based approach
            try:
                # Convert word-based parameters to token-based parameters once
                converted_max_tokens = round(self.chunk_size * self.word_to_token_ratio)
                converted_overlap_tokens = round(self.overlap_size * self.word_to_token_ratio)
                converted_min_chunk_tokens = round(self.DEFAULT_MIN_CHUNK_WORDS * self.word_to_token_ratio)

                # Use IntelligentTextChunker for consistent token-based chunking
                chunker = IntelligentTextChunker(
                    max_tokens=converted_max_tokens,
                    overlap_tokens=converted_overlap_tokens,
                    min_chunk_tokens=converted_min_chunk_tokens
                )
                chunks = chunker.chunk_text(cleaned_text)
                chunk_info = chunker.get_advanced_chunk_stats(chunks)

                # Convert advanced stats to legacy format for backward compatibility
                legacy_chunk_info = get_chunk_summary_info(chunks)
                results["chunks"] = chunks
                results["chunk_info"] = legacy_chunk_info
                results["metadata"]["steps_completed"].append("text_chunking")

                # If book_id is provided, store chunks in database using the same parameters
                if book_id:
                    created_chunks = chunk_repository.create_chunks_for_book(
                        book_id, cleaned_text,
                        max_tokens=converted_max_tokens,
                        overlap_tokens=converted_overlap_tokens,
                        min_chunk_tokens=converted_min_chunk_tokens
                    )
                    results["stored_chunks"] = len(created_chunks)
                    results["metadata"]["steps_completed"].append("chunk_storage")

                self.logger.info(f"✓ Text chunking completed: {len(chunks)} chunks")
            except Exception as e:
                error_msg = f"Text chunking failed: {str(e)}"
                self.logger.error(error_msg)
                errors.append(error_msg)
                return self._finalize_results(results, errors, start_time)
            
            # Step 7: Set final results
            results["processed_text"] = cleaned_text
            results["success"] = True
            results["errors"] = errors if errors else None
            
            self.logger.info("✓ Preprocessing pipeline completed successfully")
            
        except Exception as e:
            error_msg = f"Pipeline execution failed: {str(e)}"
            self.logger.error(error_msg)
            errors.append(error_msg)
            results["errors"] = errors
        
        return self._finalize_results(results, errors, start_time)
    
    def _finalize_results(self, results: Dict, errors: list, start_time: datetime) -> Dict:
        """Finalize results and add metadata."""
        end_time = datetime.now()
        results["metadata"]["end_time"] = end_time.isoformat()
        results["metadata"]["duration_seconds"] = round(
            (end_time - start_time).total_seconds(), 2
        )
        results["errors"] = errors if errors else None
        return results
    
    def get_summary(self, results: Dict) -> Dict:
        """
        Get a summary of preprocessing results.
        
        Args:
            results: Results from process() method
            
        Returns:
            Summary dictionary with key metrics
        """
        return {
            "success": results["success"],
            "language": results["language"]["language_name"] if results.get("language") else None,
            "word_count": results["statistics"]["word_count"] if results.get("statistics") else 0,
            "sentence_count": results["statistics"]["sentence_count"] if results.get("statistics") else 0,
            "chunk_count": len(results.get("chunks", [])),
            "processing_time": results["metadata"]["duration_seconds"],
            "steps_completed": len(results["metadata"]["steps_completed"]),
            "errors_count": len(results.get("errors") or [])
        }


class IntelligentPreprocessingPipeline:
    """
    Enhanced preprocessing pipeline with intelligent token-based chunking.
    Uses the IntelligentTextChunker for better handling of long documents
    that exceed model token limits.
    """

    def __init__(self, model_name: str = "t5-small", max_tokens: int = 512,
                 overlap_tokens: int = 100, min_chunk_tokens: int = 50):
        """
        Initialize the intelligent preprocessing pipeline.

        Args:
            model_name: Name of the model for token limit lookup
            max_tokens: Maximum tokens per chunk
            overlap_tokens: Number of tokens to overlap between chunks
            min_chunk_tokens: Minimum tokens for a valid chunk
        """
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.min_chunk_tokens = min_chunk_tokens
        self.chunker = IntelligentTextChunker(
            model_name=model_name,
            max_tokens=max_tokens,
            overlap_tokens=overlap_tokens,
            min_chunk_tokens=min_chunk_tokens
        )
        self.logger = logger

    def process(self, text: str, book_id: str = None) -> Dict:
        """
        Execute the intelligent preprocessing pipeline.

        Args:
            text: Raw text to process
            book_id: Optional book ID to associate chunks with

        Returns:
            Dictionary containing:
            - success: Whether processing succeeded
            - processed_text: Final cleaned text
            - language: Detected language info
            - statistics: Text statistics
            - chunks: List of text chunks with advanced metadata
            - chunk_info: Comprehensive chunking statistics
            - metadata: Processing metadata
            - errors: Any errors encountered
        """
        start_time = datetime.now()
        errors = []
        results = {
            "success": False,
            "processed_text": "",
            "language": None,
            "statistics": None,
            "chunks": [],
            "chunk_info": None,
            "metadata": {
                "start_time": start_time.isoformat(),
                "end_time": None,
                "duration_seconds": None,
                "steps_completed": [],
                "chunking_method": "intelligent_token_based"
            },
            "errors": []
        }

        try:
            # Step 1: Validate input
            if not text or not isinstance(text, str):
                raise ValueError("Input text must be a non-empty string")

            self.logger.info(f"Starting intelligent preprocessing pipeline for {len(text)} characters")

            # Step 2: Clean text
            try:
                cleaned_text = clean_text(text)
                results["metadata"]["steps_completed"].append("clean_text")
                self.logger.info("✓ Text cleaning completed")
            except Exception as e:
                error_msg = f"Text cleaning failed: {str(e)}"
                self.logger.error(error_msg)
                errors.append(error_msg)
                return self._finalize_results(results, errors, start_time)

            # Step 3: Detect language
            try:
                language = detect_language(cleaned_text)
                results["language"] = language
                results["metadata"]["steps_completed"].append("language_detection")
                self.logger.info(f"✓ Language detected: {language['language_name']}")
            except Exception as e:
                error_msg = f"Language detection failed: {str(e)}"
                self.logger.warning(error_msg)
                errors.append(error_msg)
                # Don't fail pipeline on language detection error

            # Step 4: Segment sentences
            try:
                sentences = segment_sentences(cleaned_text)
                results["metadata"]["steps_completed"].append("sentence_segmentation")
                self.logger.info(f"✓ Sentence segmentation completed: {len(sentences)} sentences")
            except Exception as e:
                error_msg = f"Sentence segmentation failed: {str(e)}"
                self.logger.error(error_msg)
                errors.append(error_msg)
                return self._finalize_results(results, errors, start_time)

            # Step 5: Calculate statistics
            try:
                statistics = calculate_text_statistics(cleaned_text)
                results["statistics"] = statistics
                results["metadata"]["steps_completed"].append("statistics_calculation")
                self.logger.info(f"✓ Statistics calculated: {statistics['word_count']} words")
            except Exception as e:
                error_msg = f"Statistics calculation failed: {str(e)}"
                self.logger.warning(error_msg)
                errors.append(error_msg)
                # Don't fail pipeline on statistics error

            # Step 6: Create intelligent text chunks
            try:
                chunks = self.chunker.chunk_text(cleaned_text)
                chunk_info = self.chunker.get_advanced_chunk_stats(chunks)
                results["chunks"] = chunks
                results["chunk_info"] = chunk_info
                results["metadata"]["steps_completed"].append("intelligent_text_chunking")

                # If book_id is provided, store chunks in database
                if book_id:
                    created_chunks = chunk_repository.create_chunks_for_book(
                        book_id, cleaned_text,
                        model_name=self.model_name,
                        max_tokens=self.max_tokens,
                        overlap_tokens=self.overlap_tokens,
                        min_chunk_tokens=self.min_chunk_tokens
                    )
                    results["stored_chunks"] = len(created_chunks)
                    results["metadata"]["steps_completed"].append("chunk_storage")

                self.logger.info(f"✓ Intelligent text chunking completed: {len(chunks)} chunks")
                chunking_stats = chunk_info.get('chunking_stats', {})
                quality_metrics = chunk_info.get('quality_metrics', {})
                if chunking_stats:
                    self.logger.info(f"  Token range: {chunking_stats.get('min_tokens', 'N/A')}-{chunking_stats.get('max_tokens', 'N/A')}")
                if quality_metrics:
                    self.logger.info(f"  Overlap effectiveness: {quality_metrics.get('overlap_effectiveness', 0):.2f}")
            except Exception as e:
                error_msg = f"Intelligent text chunking failed: {str(e)}"
                self.logger.error(error_msg)
                errors.append(error_msg)
                return self._finalize_results(results, errors, start_time)

            # Step 7: Set final results
            results["processed_text"] = cleaned_text
            results["success"] = True
            results["errors"] = errors if errors else None

            self.logger.info("✓ Intelligent preprocessing pipeline completed successfully")

        except Exception as e:
            error_msg = f"Pipeline execution failed: {str(e)}"
            self.logger.error(error_msg)
            errors.append(error_msg)
            results["errors"] = errors

        return self._finalize_results(results, errors, start_time)

    def _finalize_results(self, results: Dict, errors: list, start_time: datetime) -> Dict:
        """Finalize results and add metadata."""
        end_time = datetime.now()
        results["metadata"]["end_time"] = end_time.isoformat()
        results["metadata"]["duration_seconds"] = round(
            (end_time - start_time).total_seconds(), 2
        )
        results["errors"] = errors if errors else None
        return results

    def get_summary(self, results: Dict) -> Dict:
        """
        Get a summary of intelligent preprocessing results.

        Args:
            results: Results from process() method

        Returns:
            Summary dictionary with key metrics
        """
        chunk_info = results.get("chunk_info", {})
        chunking_stats = chunk_info.get("chunking_stats", {}) if isinstance(chunk_info, dict) else {}
        quality_metrics = chunk_info.get("quality_metrics", {}) if isinstance(chunk_info, dict) else {}

        return {
            "success": results["success"],
            "language": results["language"]["language_name"] if results.get("language") else None,
            "word_count": results["statistics"]["word_count"] if results.get("statistics") else 0,
            "sentence_count": results["statistics"]["sentence_count"] if results.get("statistics") else 0,
            "chunk_count": len(results.get("chunks", [])),
            "avg_tokens_per_chunk": chunking_stats.get("avg_tokens_per_chunk", 0),
            "overlap_effectiveness": quality_metrics.get("overlap_effectiveness", 0),
            "processing_time": results["metadata"]["duration_seconds"],
            "steps_completed": len(results["metadata"]["steps_completed"]),
            "errors_count": len(results.get("errors") or []),
            "chunking_method": results["metadata"].get("chunking_method", "unknown")
        }

# Convenience function for simple processing
def preprocess(text: str, book_id: str = None, chunk_size: int = 1200, overlap_size: int = 125) -> Dict:
    """
    Simple preprocessing function wrapper.

    Args:
        text: Raw text to preprocess
        book_id: Optional book ID to associate chunks with
        chunk_size: Target words per chunk
        overlap_size: Overlap words between chunks

    Returns:
        Comprehensive preprocessing results
    """
    pipeline = PreprocessingPipeline(chunk_size=chunk_size, overlap_size=overlap_size)
    return pipeline.process(text, book_id)


# Convenience function for intelligent processing
def intelligent_preprocess(text: str, book_id: str = None, model_name: str = "t5-small", max_tokens: int = 512,
                          overlap_tokens: int = 100, min_chunk_tokens: int = 50) -> Dict:
    """
    Intelligent preprocessing with token-based chunking.

    Args:
        text: Raw text to preprocess
        book_id: Optional book ID to associate chunks with
        model_name: Name of the model for token limit lookup
        max_tokens: Maximum tokens per chunk
        overlap_tokens: Number of tokens to overlap between chunks
        min_chunk_tokens: Minimum tokens for a valid chunk

    Returns:
        Comprehensive preprocessing results with intelligent chunking
    """
    pipeline = IntelligentPreprocessingPipeline(
        model_name=model_name,
        max_tokens=max_tokens,
        overlap_tokens=overlap_tokens,
        min_chunk_tokens=min_chunk_tokens
    )
    return pipeline.process(text, book_id)

# Convenience function for quick summary
def quick_summary(text: str) -> Dict:
    """
    Get a quick summary of text statistics without full preprocessing.
    
    Args:
        text: Text to summarize
        
    Returns:
        Quick summary dictionary
    """
    try:
        cleaned = clean_text(text)
        stats = calculate_text_statistics(cleaned)
        language = detect_language(cleaned)
        sentences = segment_sentences(cleaned)
        
        return {
            "success": True,
            "word_count": stats["word_count"],
            "character_count": stats["char_count"],
            "sentence_count": stats["sentence_count"],
            "language": language["language_name"],
            "avg_words_per_sentence": stats["avg_words_per_sentence"],
            "reading_time_minutes": round(stats["word_count"] / 225, 2)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
