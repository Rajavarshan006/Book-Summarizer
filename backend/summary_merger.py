"""
Summary Merging System

This module provides advanced functionality for merging multiple chunk summaries
into a coherent, non-redundant final summary. It uses NLP techniques to analyze
semantic content, detect redundancy, and create a logically flowing summary.

Features:
- Semantic analysis of individual summaries
- Redundancy detection and elimination
- Contextual flow optimization
- Key information preservation
- Coherence enhancement
- Multi-strategy merging approaches
"""

import re
import numpy as np
from typing import List, Dict, Optional
from collections import defaultdict
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Ensure NLTK resources are available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class SummaryMerger:
    """
    Advanced summary merging system that combines multiple chunk summaries
    into a coherent final summary without redundancy.

    The merger uses multiple strategies:
    1. Semantic similarity analysis
    2. Sentence-level importance scoring
    3. Contextual flow optimization
    4. Redundancy elimination
    5. Transition generation
    """

    def __init__(self):
        """Initialize the summary merger."""
        self.stop_words = set(stopwords.words('english'))
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)

    def merge_summaries(self, chunk_summaries: List[str],
                       strategy: str = "intelligent",
                       max_length: int = 1000) -> str:
        """
        Merge multiple chunk summaries into a single coherent summary.

        Args:
            chunk_summaries: List of individual chunk summaries
            strategy: Merging strategy ('intelligent', 'simple', 'semantic')
            max_length: Maximum length for the final summary

        Returns:
            Merged summary as a string
        """
        if not chunk_summaries:
            return ""

        if strategy == "simple":
            return self._simple_merge(chunk_summaries, max_length)
        elif strategy == "semantic":
            return self._semantic_merge(chunk_summaries, max_length)
        else:  # intelligent (default)
            return self._intelligent_merge(chunk_summaries, max_length)

    def _simple_merge(self, summaries: List[str], max_length: int) -> str:
        """
        Simple merging strategy - concatenate with basic deduplication.

        Args:
            summaries: List of summaries to merge
            max_length: Maximum length for final summary

        Returns:
            Merged summary
        """
        # Basic deduplication by removing exact duplicate sentences
        unique_sentences = set()
        for summary in summaries:
            sentences = sent_tokenize(summary)
            for sentence in sentences:
                clean_sentence = sentence.strip().lower()
                if clean_sentence and clean_sentence not in unique_sentences:
                    unique_sentences.add(clean_sentence)

        # Reconstruct summary
        merged = " ".join(unique_sentences)
        return self._truncate_summary(merged, max_length)

    def _semantic_merge(self, summaries: List[str], max_length: int) -> str:
        """
        Semantic merging strategy using TF-IDF and cosine similarity.

        Args:
            summaries: List of summaries to merge
            max_length: Maximum length for final summary

        Returns:
            Merged summary
        """
        # Extract all sentences from all summaries
        all_sentences = []
        for summary in summaries:
            sentences = sent_tokenize(summary)
            all_sentences.extend(sentences)

        if not all_sentences:
            return ""

        # Create TF-IDF vectors
        try:
            tfidf_matrix = self.vectorizer.fit_transform(all_sentences)

            # Calculate similarity matrix
            similarity_matrix = cosine_similarity(tfidf_matrix)

            # Select representative sentences (least similar to others)
            selected_indices = self._select_representative_sentences(similarity_matrix)

            # Get selected sentences in order
            selected_sentences = [all_sentences[i] for i in selected_indices]

            # Create merged summary
            merged = " ".join(selected_sentences)
            return self._truncate_summary(merged, max_length)

        except Exception as e:
            logger.warning(f"Semantic merging failed, falling back to simple merge: {e}")
            return self._simple_merge(summaries, max_length)

    def _intelligent_merge(self, summaries: List[str], max_length: int) -> str:
        """
        Intelligent merging strategy combining multiple techniques.

        Args:
            summaries: List of summaries to merge
            max_length: Maximum length for final summary

        Returns:
            Merged summary
        """
        # Step 1: Extract and analyze all sentences
        sentence_data = self._extract_sentence_data(summaries)

        if not sentence_data:
            return ""

        # Step 2: Calculate importance scores
        self._calculate_importance_scores(sentence_data)

        # Step 3: Detect and resolve redundancy
        self._resolve_redundancy(sentence_data)

        # Step 4: Optimize contextual flow
        optimized_sentences = self._optimize_flow(sentence_data)

        # Step 5: Generate transitions
        final_sentences = self._generate_transitions(optimized_sentences)

        # Step 6: Create final summary
        merged = " ".join(final_sentences)
        return self._truncate_summary(merged, max_length)

    def _extract_sentence_data(self, summaries: List[str]) -> List[Dict]:
        """
        Extract sentences and their metadata from summaries.

        Args:
            summaries: List of summaries

        Returns:
            List of sentence dictionaries with metadata
        """
        sentence_data = []

        for chunk_idx, summary in enumerate(summaries):
            sentences = sent_tokenize(summary)
            for sent_idx, sentence in enumerate(sentences):
                clean_sentence = sentence.strip()
                if clean_sentence:
                    sentence_data.append({
                        "text": clean_sentence,
                        "chunk_index": chunk_idx,
                        "sentence_index": sent_idx,
                        "length": len(clean_sentence),
                        "word_count": len(clean_sentence.split()),
                        "importance_score": 0.0,
                        "is_redundant": False,
                        "similar_sentences": []
                    })

        return sentence_data

    def _calculate_importance_scores(self, sentence_data: List[Dict]):
        """
        Calculate importance scores for sentences using multiple factors.

        Args:
            sentence_data: List of sentence dictionaries
        """
        if not sentence_data:
            return

        # Extract text for TF-IDF analysis
        texts = [data["text"] for data in sentence_data]

        try:
            # TF-IDF analysis
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            tfidf_scores = np.array(tfidf_matrix.sum(axis=1)).flatten()

            # Position-based scoring (first/last sentences often more important)
            position_scores = []
            for data in sentence_data:
                chunk_idx = data["chunk_index"]
                sent_idx = data["sentence_index"]

                # First and last sentences in chunks get higher scores
                if sent_idx == 0:  # First sentence in chunk
                    position_scores.append(1.5)
                elif sent_idx == 1:  # Second sentence
                    position_scores.append(1.2)
                else:
                    position_scores.append(1.0)

            # Length-based scoring (longer sentences may contain more info)
            length_scores = [min(1.0, data["word_count"] / 15) for data in sentence_data]

            # Combine scores (normalized)
            max_tfidf = max(tfidf_scores) if max(tfidf_scores) > 0 else 1
            tfidf_normalized = [score / max_tfidf for score in tfidf_scores]

            for i, data in enumerate(sentence_data):
                # Weighted combination: 50% TF-IDF, 30% position, 20% length
                data["importance_score"] = (
                    0.5 * tfidf_normalized[i] +
                    0.3 * position_scores[i] +
                    0.2 * length_scores[i]
                )

        except Exception as e:
            logger.warning(f"Importance scoring failed: {e}")
            # Fallback: use position-based scoring only
            for i, data in enumerate(sentence_data):
                if data["sentence_index"] == 0:
                    data["importance_score"] = 1.5
                elif data["sentence_index"] == 1:
                    data["importance_score"] = 1.2
                else:
                    data["importance_score"] = 1.0

    def _resolve_redundancy(self, sentence_data: List[Dict]):
        """
        Detect and mark redundant sentences.

        Args:
            sentence_data: List of sentence dictionaries
        """
        if len(sentence_data) <= 1:
            return

        try:
            # Extract texts for similarity analysis
            texts = [data["text"] for data in sentence_data]

            # Create TF-IDF vectors
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            similarity_matrix = cosine_similarity(tfidf_matrix)

            # Find similar sentence pairs
            for i in range(len(sentence_data)):
                for j in range(i + 1, len(sentence_data)):
                    similarity = similarity_matrix[i][j]

                    # If sentences are very similar (cosine similarity > 0.8)
                    if similarity > 0.8:
                        # Mark the less important one as redundant
                        if sentence_data[i]["importance_score"] > sentence_data[j]["importance_score"]:
                            sentence_data[j]["is_redundant"] = True
                            sentence_data[j]["similar_sentences"].append(i)
                        else:
                            sentence_data[i]["is_redundant"] = True
                            sentence_data[i]["similar_sentences"].append(j)

        except Exception as e:
            logger.warning(f"Redundancy detection failed: {e}")

    def _optimize_flow(self, sentence_data: List[Dict]) -> List[str]:
        """
        Optimize the flow of sentences for better coherence.

        Args:
            sentence_data: List of sentence dictionaries

        Returns:
            List of optimized sentence texts
        """
        # Filter out redundant sentences
        non_redundant = [data for data in sentence_data if not data["is_redundant"]]

        if not non_redundant:
            return []

        # Sort by importance score (descending) and then by original order
        sorted_sentences = sorted(
            non_redundant,
            key=lambda x: (-x["importance_score"], x["chunk_index"], x["sentence_index"])
        )

        # Extract texts
        return [data["text"] for data in sorted_sentences]

    def _generate_transitions(self, sentences: List[str]) -> List[str]:
        """
        Generate transitional phrases between sentences for better flow.

        Args:
            sentences: List of sentence texts

        Returns:
            List of sentences with added transitions
        """
        if len(sentences) <= 1:
            return sentences

        enhanced_sentences = [sentences[0]]  # Start with first sentence

        for i in range(1, len(sentences)):
            prev_sentence = sentences[i-1]
            current_sentence = sentences[i]

            # Simple transition based on content
            transition = self._get_transition_phrase(prev_sentence, current_sentence)

            if transition:
                enhanced_sentences.append(transition + " " + current_sentence)
            else:
                enhanced_sentences.append(current_sentence)

        return enhanced_sentences

    def _get_transition_phrase(self, prev_sentence: str, current_sentence: str) -> str:
        """
        Generate an appropriate transition phrase between two sentences.

        Args:
            prev_sentence: Previous sentence text
            current_sentence: Current sentence text

        Returns:
            Transition phrase or empty string
        """
        # List of common transition words/phrases that sentences might start with
        sentence_starting_transitions = [
            "however", "but", "in contrast", "on the other hand",
            "furthermore", "moreover", "additionally", "also",
            "for example", "for instance", "such as",
            "therefore", "thus", "consequently", "as a result",
            "nevertheless", "nonetheless", "meanwhile", "subsequently",
            "in addition", "further", "besides", "likewise",
            "conversely", "alternatively", "whereas", "while"
        ]

        # Check if current sentence already starts with a transition word/phrase
        current_stripped = current_sentence.strip()
        current_lower = current_stripped.lower()

        # Remove punctuation from the beginning for better matching
        current_clean = current_lower.lstrip('.,;:!?"()[]{}')

        # Check if sentence starts with any transition word/phrase
        for transition in sentence_starting_transitions:
            # Check for exact match at the beginning (with possible punctuation after)
            if current_clean.startswith(transition + ' ') or current_clean.startswith(transition + ','):
                return ""

        # Simple keyword-based transition detection
        prev_lower = prev_sentence.lower()

        # Check for topic changes
        if ("however" in current_lower or "but" in current_lower or
            "in contrast" in current_lower or "on the other hand" in current_lower):
            return "Furthermore"

        # Check for continuation
        if ("also" in current_lower or "additionally" in current_lower or
            "moreover" in current_lower):
            return "Additionally"

        # Check for examples
        if ("for example" in current_lower or "for instance" in current_lower or
            "such as" in current_lower):
            return "For instance"

        # Check for conclusions
        if ("therefore" in current_lower or "thus" in current_lower or
            "consequently" in current_lower or "as a result" in current_lower):
            return "Consequently"

        # Default transitions based on sentence type
        if prev_sentence.endswith('.'):
            return "Moreover"
        elif prev_sentence.endswith('?'):
            return "Regarding this"
        elif prev_sentence.endswith('!'):
            return "Building on this"

        return ""

    def _select_representative_sentences(self, similarity_matrix: np.ndarray) -> List[int]:
        """
        Select representative sentences based on similarity matrix.

        Args:
            similarity_matrix: Cosine similarity matrix

        Returns:
            List of selected sentence indices
        """
        selected = []
        similarity_sums = similarity_matrix.sum(axis=1)

        # Select sentences that are least similar to others (most unique)
        # We want a mix of high-importance and low-similarity sentences
        scores = []
        for i in range(len(similarity_sums)):
            # Score = importance (1 - avg similarity) + position bonus
            avg_similarity = similarity_sums[i] / (len(similarity_sums) - 1) if len(similarity_sums) > 1 else 0
            position_bonus = 0.2 if i < 2 else 0.1  # Bonus for early sentences
            scores.append((1 - avg_similarity) + position_bonus)

        # Select top sentences by score
        ranked_indices = sorted(range(len(scores)), key=lambda i: -scores[i])

        # Select top 70% of sentences (or at least 3)
        num_to_select = max(3, int(len(ranked_indices) * 0.7))
        return ranked_indices[:num_to_select]

    def _truncate_summary(self, summary: str, max_length: int) -> str:
        """
        Truncate summary to maximum length while preserving sentence boundaries.

        Args:
            summary: Summary text to truncate
            max_length: Maximum allowed length

        Returns:
            Truncated summary
        """
        if len(summary) <= max_length:
            return summary

        # Split into sentences and truncate
        sentences = sent_tokenize(summary)
        truncated = []
        current_length = 0

        for sentence in sentences:
            if current_length + len(sentence) <= max_length:
                truncated.append(sentence)
                current_length += len(sentence)
            else:
                break

        return " ".join(truncated)

    def merge_with_context(self, chunk_summaries: List[str],
                          chunk_contexts: List[str],
                          max_length: int = 1000) -> str:
        """
        Merge summaries with additional context from original chunks.

        Args:
            chunk_summaries: List of chunk summaries
            chunk_contexts: List of original chunk texts for context
            max_length: Maximum length for final summary

        Returns:
            Context-aware merged summary
        """
        if len(chunk_summaries) != len(chunk_contexts):
            raise ValueError("Chunk summaries and contexts must have the same length")

        # Combine summary with key context elements
        enriched_summaries = []
        for summary, context in zip(chunk_summaries, chunk_contexts):
            # Extract key phrases from context
            key_phrases = self._extract_key_phrases(context)

            # Enhance summary with key phrases if they're not already present
            enhanced = summary
            for phrase in key_phrases:
                if phrase.lower() not in summary.lower():
                    enhanced += " " + phrase

            enriched_summaries.append(enhanced)

        return self.merge_summaries(enriched_summaries, "intelligent", max_length)

    def _extract_key_phrases(self, text: str, top_n: int = 3) -> List[str]:
        """
        Extract key phrases from text using simple heuristics.

        Args:
            text: Input text
            top_n: Number of key phrases to extract

        Returns:
            List of key phrases
        """
        try:
            # Simple approach: extract noun phrases
            sentences = sent_tokenize(text)
            key_phrases = []

            for sentence in sentences:
                # Look for capitalized phrases (often proper nouns)
                words = sentence.split()
                current_phrase = []

                for word in words:
                    if word[0].isupper() and len(word) > 3:  # Capitalized word
                        current_phrase.append(word)
                    elif current_phrase:  # End of capitalized sequence
                        if len(current_phrase) >= 2:  # At least 2 words
                            key_phrases.append(" ".join(current_phrase))
                        current_phrase = []

                # Add any remaining phrase
                if current_phrase and len(current_phrase) >= 2:
                    key_phrases.append(" ".join(current_phrase))

            # Return top unique phrases
            unique_phrases = list(set(key_phrases))
            return unique_phrases[:top_n]

        except Exception as e:
            logger.warning(f"Key phrase extraction failed: {e}")
            return []

    def validate_merged_summary(self, original_summaries: List[str],
                               merged_summary: str) -> Dict:
        """
        Validate that merged summary preserves key information.

        Args:
            original_summaries: Original chunk summaries
            merged_summary: Merged summary to validate

        Returns:
            Validation report dictionary
        """
        report = {
            "coverage_score": 0.0,
            "redundancy_reduction": 0.0,
            "coherence_score": 0.0,
            "missing_key_points": [],
            "validation_passed": False
        }

        try:
            # Calculate coverage score
            original_text = " ".join(original_summaries)
            report["coverage_score"] = self._calculate_coverage_score(original_text, merged_summary)

            # Calculate redundancy reduction
            report["redundancy_reduction"] = self._calculate_redundancy_reduction(original_summaries, merged_summary)

            # Calculate coherence score
            report["coherence_score"] = self._calculate_coherence_score(merged_summary)

            # Check for missing key points
            report["missing_key_points"] = self._find_missing_key_points(original_summaries, merged_summary)

            # Overall validation
            report["validation_passed"] = (
                report["coverage_score"] > 0.7 and
                report["redundancy_reduction"] > 0.3 and
                report["coherence_score"] > 0.6
            )

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            report["validation_passed"] = False

        return report

    def _calculate_coverage_score(self, original_text: str, merged_text: str) -> float:
        """
        Calculate how well the merged summary covers the original content.

        Args:
            original_text: Original text
            merged_text: Merged summary text

        Returns:
            Coverage score (0-1)
        """
        try:
            # Use TF-IDF to calculate coverage
            texts = [original_text, merged_text]
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

            # Coverage score is the similarity between original and merged
            return max(0.0, min(1.0, similarity))

        except Exception as e:
            logger.warning(f"Coverage calculation failed: {e}")
            return 0.5  # Default moderate score

    def _calculate_redundancy_reduction(self, original_summaries: List[str],
                                      merged_summary: str) -> float:
        """
        Calculate redundancy reduction achieved by merging.

        Args:
            original_summaries: Original summaries
            merged_summary: Merged summary

        Returns:
            Redundancy reduction score (0-1)
        """
        try:
            # Calculate original length (sum of all summaries)
            original_length = sum(len(summary) for summary in original_summaries)

            # Calculate merged length
            merged_length = len(merged_summary)

            # Redundancy reduction = 1 - (merged_length / original_length)
            # But normalized to 0-1 range
            if original_length == 0:
                return 0.0

            reduction_ratio = 1.0 - (merged_length / original_length)
            return max(0.0, min(1.0, reduction_ratio))

        except Exception as e:
            logger.warning(f"Redundancy calculation failed: {e}")
            return 0.3  # Default moderate score

    def _calculate_coherence_score(self, text: str) -> float:
        """
        Calculate coherence score for the merged summary.

        Args:
            text: Summary text to evaluate

        Returns:
            Coherence score (0-1)
        """
        try:
            sentences = sent_tokenize(text)
            if len(sentences) <= 1:
                return 1.0

            # Simple coherence metrics
            # 1. Sentence length consistency
            lengths = [len(sentence) for sentence in sentences]
            avg_length = sum(lengths) / len(lengths)
            length_variation = sum(abs(l - avg_length) for l in lengths) / len(lengths)
            length_score = 1.0 - min(1.0, length_variation / avg_length)

            # 2. Transition words presence
            transition_words = ["however", "moreover", "furthermore", "consequently",
                              "additionally", "nevertheless", "therefore", "thus"]
            transition_count = sum(1 for word in transition_words if word in text.lower())
            transition_score = min(1.0, transition_count / max(1, len(sentences) - 1))

            # 3. Pronoun consistency (simple check)
            pronoun_pattern = r'\b(he|she|it|they|we|i|you)\b'
            pronouns = re.findall(pronoun_pattern, text.lower())
            if pronouns:
                # Check if same pronoun is used consistently
                main_pronoun = max(set(pronouns), key=pronouns.count)
                consistency = pronouns.count(main_pronoun) / len(pronouns)
                pronoun_score = consistency
            else:
                pronoun_score = 1.0

            # Combined coherence score
            return 0.5 * length_score + 0.3 * transition_score + 0.2 * pronoun_score

        except Exception as e:
            logger.warning(f"Coherence calculation failed: {e}")
            return 0.7  # Default good score

    def _find_missing_key_points(self, original_summaries: List[str],
                                merged_summary: str) -> List[str]:
        """
        Identify key points from original summaries that might be missing.

        Args:
            original_summaries: Original summaries
            merged_summary: Merged summary

        Returns:
            List of potentially missing key points
        """
        missing_points = []

        try:
            # Extract key sentences from each original summary
            for i, summary in enumerate(original_summaries):
                sentences = sent_tokenize(summary)
                if sentences:
                    # Check if first sentence (often topic sentence) is represented
                    first_sentence = sentences[0].strip()
                    if first_sentence.lower() not in merged_summary.lower():
                        missing_points.append(f"Chunk {i+1} topic: {first_sentence}")

        except Exception as e:
            logger.warning(f"Missing key points detection failed: {e}")

        return missing_points

# Singleton instance for easy access
summary_merger = SummaryMerger()
