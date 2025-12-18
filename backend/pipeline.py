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
from backend.text_chunking import chunk_text, get_chunk_summary_info

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
    
    def __init__(self, chunk_size: int = 1200, overlap_size: int = 125):
        """
        Initialize the preprocessing pipeline.
        
        Args:
            chunk_size: Target words per chunk (default 1200)
            overlap_size: Overlap words between chunks (default 125)
        """
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.logger = logger
    
    def process(self, text: str, return_raw_steps: bool = False) -> Dict:
        """
        Execute the complete preprocessing pipeline.
        
        Args:
            text: Raw text to process
            return_raw_steps: If True, include individual processing steps in output
            
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
            
            # Step 6: Create text chunks
            try:
                chunks = chunk_text(cleaned_text, self.chunk_size, self.overlap_size)
                chunk_info = get_chunk_summary_info(chunks)
                results["chunks"] = chunks
                results["chunk_info"] = chunk_info
                results["metadata"]["steps_completed"].append("text_chunking")
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


# Convenience function for simple processing
def preprocess(text: str, chunk_size: int = 1200, overlap_size: int = 125) -> Dict:
    """
    Simple preprocessing function wrapper.
    
    Args:
        text: Raw text to preprocess
        chunk_size: Target words per chunk
        overlap_size: Overlap words between chunks
        
    Returns:
        Comprehensive preprocessing results
    """
    pipeline = PreprocessingPipeline(chunk_size=chunk_size, overlap_size=overlap_size)
    return pipeline.process(text)


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
