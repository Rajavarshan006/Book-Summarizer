import re
from typing import List
import nltk
from nltk.tokenize import sent_tokenize

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


def segment_sentences(text: str) -> List[str]:
    """
    Segment text into sentences using NLTK.
    Handles abbreviations (Dr., Mr., etc.) and decimals (25.6) correctly.
    
    Args:
        text: Text to segment into sentences
        
    Returns:
        List of clean sentences
    """
    if not text or not isinstance(text, str):
        return []
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    if not text:
        return []
    
    try:
        # Use NLTK's sent_tokenize which handles abbreviations well
        sentences = sent_tokenize(text)
        
        # Clean up each sentence
        cleaned_sentences = []
        for sentence in sentences:
            # Strip whitespace
            sentence = sentence.strip()
            
            # Skip empty sentences
            if sentence:
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
        
    except Exception as e:
        # Fallback to simple splitting if NLTK fails
        print(f"NLTK tokenization failed: {e}. Using fallback method.")
        return _fallback_segment_sentences(text)


def _fallback_segment_sentences(text: str) -> List[str]:
    """
    Fallback sentence segmentation using regex patterns.
    Used if NLTK tokenization fails.
    """
    # Handle common abbreviations
    abbreviations = [
        r'Dr\.',
        r'Mr\.',
        r'Mrs\.',
        r'Ms\.',
        r'Prof\.',
        r'Jr\.',
        r'Sr\.',
        r'St\.',
        r'Ave\.',
        r'Blvd\.',
        r'Inc\.',
        r'Ltd\.',
        r'Corp\.',
        r'vs\.',
        r'etc\.',
        r'e\.g\.',
        r'i\.e\.',
    ]
    
    # Protect abbreviations
    placeholder = "___ABBREVIATION___"
    for abbr in abbreviations:
        pattern = re.escape(abbr.replace(r'\.', '.'))
        text = re.sub(pattern, abbr.replace('.', placeholder), text, flags=re.IGNORECASE)
    
    # Split on sentence boundaries (. ! ?) followed by space and uppercase
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    
    # Restore abbreviations and clean
    result = []
    for sentence in sentences:
        sentence = sentence.replace(placeholder, '.')
        sentence = sentence.strip()
        
        if sentence:
            result.append(sentence)
    
    return result


def get_sentence_count(text: str) -> int:
    """
    Get the number of sentences in text.
    
    Args:
        text: Text to count sentences in
        
    Returns:
        Number of sentences
    """
    sentences = segment_sentences(text)
    return len(sentences)
