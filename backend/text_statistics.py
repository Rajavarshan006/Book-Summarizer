from typing import Dict
from backend.sentence_segmentation import segment_sentences


def calculate_text_statistics(text: str) -> dict:
    """
    Compute basic statistics from the processed text.
    """
    if not text:
        return {
            "char_count": 0,
            "word_count": 0,
            "sentence_count": 0,
            "avg_words_per_sentence": 0
        }

    sentences = segment_sentences(text)
    words = text.split()

    stats = {
        "char_count": len(text),
        "word_count": len(words),
        "sentence_count": len(sentences),
        "avg_words_per_sentence": round(len(words) / len(sentences), 2) if sentences else 0
    }

    return stats
