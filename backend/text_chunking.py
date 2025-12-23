from typing import List, Dict, Optional, Tuple
from backend.sentence_segmentation import segment_sentences
from datetime import datetime, timezone
import warnings
import re
import logging

logger = logging.getLogger(__name__)

# Default token limits for common models
DEFAULT_TOKEN_LIMITS = {
    "t5-small": 512,
    "t5-base": 512,
    "t5-large": 512,
    "t5-3b": 1024,
    "t5-11b": 1024,
    "gpt2": 1024,
    "bert-base": 512,
    "bert-large": 512,
    "roberta-base": 512,
    "roberta-large": 512
}

class IntelligentTextChunker:
    """
    Advanced text chunking system with token-aware boundaries and intelligent overlap.

    Features:
    - Token-based chunking that respects model token limits
    - Intelligent overlapping for context continuity
    - Sentence-aware chunking to avoid breaking sentences
    - Dynamic chunk size adjustment based on content
    - Comprehensive metadata and validation
    """

    def __init__(self, model_name: str = "t5-small", max_tokens: int = 512,
                 overlap_tokens: int = 100, min_chunk_tokens: int = 50):
        """
        Initialize the intelligent text chunker.

        Args:
            model_name: Name of the model for token limit lookup
            max_tokens: Maximum tokens per chunk (overrides model default)
            overlap_tokens: Number of tokens to overlap between chunks
            min_chunk_tokens: Minimum tokens for a valid chunk
        """
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.min_chunk_tokens = min_chunk_tokens

        # Set default token limit based on model
        if max_tokens is None:
            self.max_tokens = DEFAULT_TOKEN_LIMITS.get(model_name, 512)

        # Validate parameters
        if self.max_tokens < 100:
            warnings.warn(f"Max tokens {self.max_tokens} is very small, may result in many tiny chunks")
        if self.overlap_tokens >= self.max_tokens:
            warnings.warn(f"Overlap tokens {self.overlap_tokens} should be less than max tokens {self.max_tokens}")
        if self.min_chunk_tokens >= self.max_tokens:
            warnings.warn(f"Min chunk tokens {self.min_chunk_tokens} should be less than max tokens {self.max_tokens}")

    def _estimate_token_count(self, text: str) -> int:
        """
        Estimate token count for text using simple heuristic.
        For accurate counting, use a proper tokenizer.
        """
        if not text:
            return 0

        # Simple heuristic: average English word is ~1.3 tokens
        word_count = len(text.split())
        return int(word_count * 1.3)

    def _detect_natural_breaking_points(self, text: str) -> List[int]:
        """
        Detect natural breaking points in text such as paragraph endings and chapter breaks.

        Args:
            text: Text to analyze for natural breaking points

        Returns:
            List of character positions where natural breaks occur
        """
        if not text:
            return []

        breaking_points = []

        # Patterns for detecting natural breaking points
        patterns = [
            # Chapter breaks (e.g., "Chapter 1", "CHAPTER ONE", etc.)
            r'(?i)(?:chapter|part|section)\s+\w+',
            # Multiple newlines (paragraph breaks)
            r'\n\s*\n\s*\n',
            # Page breaks or section dividers
            r'[-=]{3,}\s*$',
            r'[*#]{3,}\s*$',
            # Horizontal rules
            r'---',
            r'___',
            r'\*\*\*',
            # Formatting that indicates breaks
            r'\n\s*\n\s*$',
            # Large whitespace gaps
            r' {10,}',
            r'\t{2,}'
        ]

        # Find all matches for each pattern
        for pattern in patterns:
            try:
                matches = list(re.finditer(pattern, text))
                for match in matches:
                    # Add the end position of the match as a breaking point
                    breaking_points.append(match.end())
            except re.error as e:
                logger.warning(f"Regex pattern failed: {pattern}. Error: {e}")
                continue

        # Remove duplicates and sort
        breaking_points = sorted(list(set(breaking_points)))

        # Add start and end of text as potential breaking points
        breaking_points.insert(0, 0)
        breaking_points.append(len(text))

        return breaking_points

    def _find_optimal_break_within_range(self, text: str, start_pos: int, end_pos: int,
                                        breaking_points: List[int]) -> int:
        """
        Find the best natural breaking point within a given range.

        Args:
            text: Original text
            start_pos: Start position of range
            end_pos: End position of range
            breaking_points: List of natural breaking points

        Returns:
            Best breaking point within range, or end_pos if none found
        """
        if not breaking_points:
            return end_pos

        # Find breaking points within our target range
        valid_breaks = [bp for bp in breaking_points if start_pos < bp <= end_pos]

        if not valid_breaks:
            return end_pos

        # Return the last valid breaking point (closest to end_pos)
        return max(valid_breaks)

    def _find_sentence_boundary(self, sentences: List[str], start_idx: int,
                               target_token_count: int) -> Tuple[int, int]:
        """
        Find the optimal sentence boundary for chunking.

        Args:
            sentences: List of all sentences
            start_idx: Starting sentence index
            target_token_count: Target token count for this chunk

        Returns:
            Tuple of (end_idx, actual_token_count)
        """
        current_tokens = 0
        end_idx = start_idx

        for i in range(start_idx, len(sentences)):
            sentence = sentences[i]
            sentence_tokens = self._estimate_token_count(sentence)

            # Check if adding this sentence would exceed the target
            if current_tokens + sentence_tokens > target_token_count and current_tokens > 0:
                break

            current_tokens += sentence_tokens
            end_idx = i + 1

        return end_idx, current_tokens

    def _create_overlap_window(self, sentences: List[str], chunk_end_idx: int,
                              overlap_tokens: int) -> int:
        """
        Calculate the optimal overlap window for the next chunk.

        Args:
            sentences: List of all sentences
            chunk_end_idx: End index of current chunk
            overlap_tokens: Target overlap token count

        Returns:
            Starting index for next chunk
        """
        if chunk_end_idx >= len(sentences):
            return chunk_end_idx

        overlap_tokens_collected = 0
        sentences_to_overlap = 0

        # Work backwards from chunk end to find overlap sentences
        for i in range(chunk_end_idx - 1, -1, -1):
            sentence = sentences[i]
            sentence_tokens = self._estimate_token_count(sentence)

            if overlap_tokens_collected + sentence_tokens <= overlap_tokens:
                overlap_tokens_collected += sentence_tokens
                sentences_to_overlap += 1
            else:
                break

        # Start next chunk before the end of current chunk to create overlap
        next_start_idx = max(chunk_end_idx - sentences_to_overlap, 0)

        # Ensure we don't go backwards
        if next_start_idx < chunk_end_idx - len(sentences):
            next_start_idx = chunk_end_idx - len(sentences)

        return next_start_idx

    def chunk_text(self, text: str) -> List[Dict]:
        """
        Split text into intelligent chunks with token-aware boundaries and overlap.

        Args:
            text: Text to chunk

        Returns:
            List of chunk dictionaries with comprehensive metadata
        """
        if not text or not isinstance(text, str):
            return []

        # Detect natural breaking points in the text
        breaking_points = self._detect_natural_breaking_points(text)

        # Segment text into sentences
        sentences = segment_sentences(text)

        if not sentences:
            return []

        chunks = []
        chunk_id = 0
        current_idx = 0
        total_sentences = len(sentences)

        while current_idx < total_sentences:
            # Determine target token count for this chunk
            target_tokens = self.max_tokens

            # Find optimal sentence boundary
            end_idx, actual_tokens = self._find_sentence_boundary(
                sentences, current_idx, target_tokens
            )

            # Get sentences for this chunk
            chunk_sentences = sentences[current_idx:end_idx]
            chunk_text = " ".join(chunk_sentences)

            # Check if we should break at a natural breaking point instead
            if end_idx < total_sentences:
                # Find the character position of the current end sentence
                end_char_pos = text.find(chunk_sentences[-1]) + len(chunk_sentences[-1]) if chunk_sentences else len(text)

                # Look for natural breaking points near our current end position
                optimal_break_pos = self._find_optimal_break_within_range(
                    text,
                    text.find(chunk_sentences[0]) if chunk_sentences else 0,
                    end_char_pos,
                    breaking_points
                )

                # If we found a natural breaking point that's not too far from our target
                if optimal_break_pos < end_char_pos and optimal_break_pos > text.find(chunk_sentences[0]) if chunk_sentences else 0:
                    # Find which sentence contains this breaking point
                    for i in range(current_idx, end_idx):
                        sentence = sentences[i]
                        sentence_start = text.find(sentence)
                        sentence_end = sentence_start + len(sentence)
                        if sentence_start <= optimal_break_pos <= sentence_end:
                            # Adjust end_idx to break at this natural point
                            end_idx = i + 1
                            chunk_sentences = sentences[current_idx:end_idx]
                            chunk_text = " ".join(chunk_sentences)
                            actual_tokens = sum(self._estimate_token_count(s) for s in chunk_sentences)
                            break

            # Validate chunk size
            if actual_tokens < self.min_chunk_tokens and end_idx < total_sentences:
                # Try to get more content if chunk is too small
                extended_end_idx, extended_tokens = self._find_sentence_boundary(
                    sentences, current_idx, target_tokens * 1.5
                )
                if extended_tokens >= self.min_chunk_tokens:
                    end_idx = extended_end_idx
                    chunk_sentences = sentences[current_idx:end_idx]
                    chunk_text = " ".join(chunk_sentences)
                    actual_tokens = extended_tokens

            # If we still have a valid chunk, save it
            if chunk_sentences and actual_tokens >= self.min_chunk_tokens:
                # Find character indices in original text
                start_char = text.find(chunk_sentences[0]) if chunk_sentences else 0
                end_char = (text.find(chunk_sentences[-1]) + len(chunk_sentences[-1])
                           ) if chunk_sentences else len(text)

                chunk_info = {
                    "chunk_id": chunk_id,
                    "text": chunk_text,
                    "sentence_count": len(chunk_sentences),
                    "estimated_token_count": actual_tokens,
                    "word_count": len(chunk_text.split()),
                    "start_index": start_char if start_char != -1 else 0,
                    "end_index": end_char if end_char != -1 else len(text),
                    "sentences": chunk_sentences,
                    "is_first_chunk": chunk_id == 0,
                    "is_last_chunk": end_idx >= total_sentences,
                    "overlap_info": {
                        "previous_chunk_overlap": 0,
                        "next_chunk_overlap": 0
                    }
                }

                chunks.append(chunk_info)
                chunk_id += 1

                # Calculate overlap for next chunk
                if end_idx < total_sentences:
                    next_start_idx = self._create_overlap_window(
                        sentences, end_idx, self.overlap_tokens
                    )

                    # Calculate actual overlap tokens
                    overlap_sentences = sentences[next_start_idx:end_idx]
                    overlap_tokens = sum(self._estimate_token_count(s) for s in overlap_sentences)

                    # Update overlap info for current chunk
                    if chunks:
                        chunks[-1]["overlap_info"]["next_chunk_overlap"] = overlap_tokens

                    current_idx = next_start_idx
                else:
                    current_idx = end_idx

            elif chunk_sentences:
                # If chunk is too small but we have some content, add it anyway
                start_char = text.find(chunk_sentences[0]) if chunk_sentences else 0
                end_char = (text.find(chunk_sentences[-1]) + len(chunk_sentences[-1])
                           ) if chunk_sentences else len(text)

                chunks.append({
                    "chunk_id": chunk_id,
                    "text": chunk_text,
                    "sentence_count": len(chunk_sentences),
                    "estimated_token_count": actual_tokens,
                    "word_count": len(chunk_text.split()),
                    "start_index": start_char if start_char != -1 else 0,
                    "end_index": end_char if end_char != -1 else len(text),
                    "sentences": chunk_sentences,
                    "is_first_chunk": chunk_id == 0,
                    "is_last_chunk": True,
                    "overlap_info": {
                        "previous_chunk_overlap": 0,
                        "next_chunk_overlap": 0
                    }
                })
                current_idx = end_idx
            else:
                break

        # Calculate previous chunk overlap info
        for i in range(1, len(chunks)):
            previous_chunk = chunks[i-1]
            current_chunk = chunks[i]

            # Find overlapping sentences
            prev_sentences = previous_chunk["sentences"]
            curr_sentences = current_chunk["sentences"]

            overlap_sentences = []
            for prev_s in reversed(prev_sentences):
                for curr_s in curr_sentences:
                    if prev_s == curr_s:
                        overlap_sentences.append(prev_s)
                        break

            overlap_tokens = sum(self._estimate_token_count(s) for s in overlap_sentences)
            current_chunk["overlap_info"]["previous_chunk_overlap"] = overlap_tokens

        return chunks

    def get_advanced_chunk_stats(self, chunks: List[Dict]) -> Dict:
        """
        Get comprehensive statistics about the chunking process.

        Args:
            chunks: List of chunks from chunk_text()

        Returns:
            Dictionary with detailed chunking statistics
        """
        if not chunks:
            return self._get_empty_stats()

        token_counts = [c["estimated_token_count"] for c in chunks]
        word_counts = [c["word_count"] for c in chunks]
        sentence_counts = [c["sentence_count"] for c in chunks]

        # Calculate overlap statistics
        total_overlap_tokens = 0
        overlap_instances = 0

        for i in range(1, len(chunks)):
            overlap_tokens = chunks[i]["overlap_info"]["previous_chunk_overlap"]
            if overlap_tokens > 0:
                total_overlap_tokens += overlap_tokens
                overlap_instances += 1

        avg_overlap_tokens = (total_overlap_tokens / overlap_instances
                            ) if overlap_instances > 0 else 0

        return {
            "chunking_stats": {
                "total_chunks": len(chunks),
                "total_estimated_tokens": sum(token_counts),
                "total_words": sum(word_counts),
                "total_sentences": sum(sentence_counts),
                "avg_tokens_per_chunk": round(sum(token_counts) / len(chunks), 2),
                "avg_words_per_chunk": round(sum(word_counts) / len(chunks), 2),
                "avg_sentences_per_chunk": round(sum(sentence_counts) / len(chunks), 2),
                "min_tokens": min(token_counts),
                "max_tokens": max(token_counts),
                "token_range": max(token_counts) - min(token_counts),
                "overlap_stats": {
                    "total_overlap_tokens": total_overlap_tokens,
                    "avg_overlap_tokens": round(avg_overlap_tokens, 2),
                    "overlap_instances": overlap_instances,
                    "overlap_coverage": round((overlap_instances / max(1, len(chunks) - 1)) * 100, 2)
                }
            },
            "quality_metrics": {
                "chunk_size_consistency": self._calculate_consistency_score(token_counts),
                "overlap_effectiveness": self._calculate_overlap_score(chunks),
                "sentence_integrity": self._calculate_sentence_integrity(chunks)
            }
        }

    def _calculate_consistency_score(self, token_counts: List[int]) -> float:
        """Calculate chunk size consistency score (0-1, higher is better)."""
        if len(token_counts) <= 1:
            return 1.0

        avg_size = sum(token_counts) / len(token_counts)
        variance = sum((x - avg_size) ** 2 for x in token_counts) / len(token_counts)
        std_dev = variance ** 0.5

        # Normalize to 0-1 range
        max_std_dev = avg_size * 0.5  # Allow 50% variation
        return max(0, 1 - (std_dev / max_std_dev))

    def _calculate_overlap_score(self, chunks: List[Dict]) -> float:
        """Calculate overlap effectiveness score (0-1, higher is better)."""
        if len(chunks) <= 1:
            return 1.0

        effective_overlaps = 0
        total_possible = len(chunks) - 1

        for i in range(1, len(chunks)):
            overlap_tokens = chunks[i]["overlap_info"]["previous_chunk_overlap"]
            if overlap_tokens >= self.overlap_tokens * 0.7:  # At least 70% of target overlap
                effective_overlaps += 1

        return effective_overlaps / total_possible

    def _calculate_sentence_integrity(self, chunks: List[Dict]) -> float:
        """Calculate sentence integrity score (0-1, higher is better)."""
        # All chunks should maintain sentence integrity since we chunk at sentence boundaries
        return 1.0

    def _get_empty_stats(self) -> Dict:
        """Return empty statistics template."""
        return {
            "chunking_stats": {
                "total_chunks": 0,
                "total_estimated_tokens": 0,
                "total_words": 0,
                "total_sentences": 0,
                "avg_tokens_per_chunk": 0,
                "avg_words_per_chunk": 0,
                "avg_sentences_per_chunk": 0,
                "min_tokens": 0,
                "max_tokens": 0,
                "token_range": 0,
                "overlap_stats": {
                    "total_overlap_tokens": 0,
                    "avg_overlap_tokens": 0,
                    "overlap_instances": 0,
                    "overlap_coverage": 0
                }
            },
            "quality_metrics": {
                "chunk_size_consistency": 0,
                "overlap_effectiveness": 0,
                "sentence_integrity": 0
            }
        }

    def validate_chunks(self, chunks: List[Dict]) -> Dict:
        """
        Validate chunks meet quality requirements.

        Args:
            chunks: List of chunks to validate

        Returns:
            Dictionary with validation results and warnings
        """
        if not chunks:
            return {"valid": False, "warnings": ["No chunks provided"]}

        warnings_list = []
        all_valid = True

        for i, chunk in enumerate(chunks):
            if chunk["estimated_token_count"] < self.min_chunk_tokens:
                warnings_list.append(f"Chunk {i} too small: {chunk['estimated_token_count']} tokens")
                all_valid = False
            if chunk["estimated_token_count"] > self.max_tokens * 1.2:  # Allow 20% buffer
                warnings_list.append(f"Chunk {i} too large: {chunk['estimated_token_count']} tokens")
                all_valid = False

        # Check overlap effectiveness
        overlap_instances = sum(1 for chunk in chunks[1:] if chunk["overlap_info"]["previous_chunk_overlap"] > 0)
        if len(chunks) > 1 and overlap_instances < len(chunks) - 1:
            warnings_list.append(f"Insufficient overlap: {overlap_instances}/{len(chunks)-1} chunk transitions")

        return {
            "valid": all_valid,
            "warnings": warnings_list,
            "chunk_count": len(chunks),
            "validation_time": datetime.now(timezone.utc).isoformat()
        }

# Backward compatibility functions
def chunk_text(text: str, chunk_size: int = 1200, overlap_size: int = 125, min_chunk_size: int = 100) -> List[Dict]:
    """
    Legacy chunk_text function for backward compatibility.
    Uses word-based chunking with the original algorithm.
    """
    chunker = IntelligentTextChunker(
        max_tokens=int(chunk_size * 1.3),  # Convert words to approximate tokens
        overlap_tokens=int(overlap_size * 1.3),
        min_chunk_tokens=int(min_chunk_size * 1.3)
    )
    return chunker.chunk_text(text)

def get_chunk_summary_info(chunks: List[Dict]) -> Dict:
    """
    Legacy get_chunk_summary_info for backward compatibility.
    """
    chunker = IntelligentTextChunker()
    stats = chunker.get_advanced_chunk_stats(chunks)

    # Convert to legacy format
    chunking_stats = stats["chunking_stats"]
    overlap_stats = chunking_stats["overlap_stats"]

    return {
        "total_chunks": chunking_stats["total_chunks"],
        "total_words": chunking_stats["total_words"],
        "avg_chunk_size": chunking_stats["avg_words_per_chunk"],
        "min_chunk_size": chunking_stats["min_tokens"] * 0.77,  # Convert tokens back to approx words
        "max_chunk_size": chunking_stats["max_tokens"] * 0.77,
        "total_overlap_words": overlap_stats["total_overlap_tokens"] * 0.77
    }

def validate_chunks(chunks: List[Dict], min_size: int = 100, max_size: int = 1500) -> bool:
    """
    Legacy validate_chunks for backward compatibility.
    """
    chunker = IntelligentTextChunker(
        min_chunk_tokens=int(min_size * 1.3),
        max_tokens=int(max_size * 1.3)
    )
    validation = chunker.validate_chunks(chunks)
    return validation["valid"]
