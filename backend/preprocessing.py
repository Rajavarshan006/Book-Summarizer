import re
from typing import List
from backend.sentence_segmentation import segment_sentences, get_sentence_count
from backend.language_detection import detect_language
from backend.text_statistics import calculate_text_statistics
from backend.text_chunking import chunk_text, get_chunk_summary_info

def clean_text(text: str) -> str:
    """
    Clean raw extracted text by normalizing whitespace,
    fixing line breaks, and removing unwanted characters.
    """

    if not text or not isinstance(text, str):
        return ""

    # 1. Replace Windows/Mac line endings with \n
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 2. Remove tabs and multiple spaces
    text = re.sub(r"[ \t]+", " ", text)

    # 3. Replace multiple blank lines with a single blank line
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 4. Remove strange unicode characters
    text = re.sub(r"[^\x00-\x7F]+", " ", text)

    # 5. Strip leading/trailing whitespace
    text = text.strip()

    return text


def preprocess_text(text: str) -> dict:
    """
    Complete preprocessing pipeline: clean text, detect language, segment into sentences,
    calculate statistics, and chunk for summarization.
    
    Args:
        text: Raw extracted text
        
    Returns:
        Dictionary containing:
        - cleaned_text: Cleaned version of text
        - language: Language detection results
        - sentences: List of segmented sentences
        - sentence_count: Number of sentences
        - statistics: Basic text statistics
        - chunks: List of text chunks for summarization
        - chunk_info: Summary information about chunks
    """
    # Step 1: Clean the text
    cleaned = clean_text(text)
    
    # Step 2: Detect language
    language = detect_language(cleaned)
    
    # Step 3: Segment into sentences
    sentences = segment_sentences(cleaned)
    
    # Step 4: Calculate statistics
    statistics = calculate_text_statistics(cleaned)
    
    # Step 5: Create chunks for summarization
    chunks = chunk_text(cleaned, chunk_size=1200, overlap_size=125)
    chunk_info = get_chunk_summary_info(chunks)
    
    return {
        "cleaned_text": cleaned,
        "language": language,
        "sentences": sentences,
        "sentence_count": len(sentences),
        "statistics": statistics,
        "chunks": chunks,
        "chunk_info": chunk_info
    }


def _get_difficulty_level(flesch_score: float) -> str:
    """
    Get difficulty level based on Flesch Reading Ease score.
    
    90-100: Very Easy
    80-90: Easy
    70-80: Fairly Easy
    60-70: Standard
    50-60: Fairly Difficult
    30-50: Difficult
    0-30: Very Difficult
    """
    if flesch_score >= 90:
        return "Very Easy"
    elif flesch_score >= 80:
        return "Easy"
    elif flesch_score >= 70:
        return "Fairly Easy"
    elif flesch_score >= 60:
        return "Standard"
    elif flesch_score >= 50:
        return "Fairly Difficult"
    elif flesch_score >= 30:
        return "Difficult"
    else:
        return "Very Difficult"
