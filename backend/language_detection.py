from typing import Dict, List
from langdetect import detect, detect_langs, LangDetectException

# Mapping of language codes to full names
LANGUAGE_NAMES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh-cn': 'Chinese (Simplified)',
    'zh-tw': 'Chinese (Traditional)',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'bn': 'Bengali',
    'pa': 'Punjabi',
    'te': 'Telugu',
    'mr': 'Marathi',
    'ta': 'Tamil',
    'gu': 'Gujarati',
    'kn': 'Kannada',
    'ml': 'Malayalam',
    'or': 'Odia',
    'uk': 'Ukrainian',
    'pl': 'Polish',
    'nl': 'Dutch',
    'tr': 'Turkish',
    'vi': 'Vietnamese',
    'th': 'Thai',
    'id': 'Indonesian',
}


def detect_language(text: str) -> Dict[str, any]:
    """
    Detect the primary language of the text.
    
    Args:
        text: Text to detect language for
        
    Returns:
        Dictionary containing:
        - language_code: ISO 639-1 language code (e.g., 'en', 'fr')
        - language_name: Full language name (e.g., 'English', 'French')
        - confidence: Confidence score between 0 and 1
        - all_languages: List of detected languages with probabilities
    """
    if not text or not isinstance(text, str) or len(text.strip()) < 10:
        return {
            "language_code": "unknown",
            "language_name": "Unknown",
            "confidence": 0.0,
            "all_languages": []
        }
    
    try:
        # Detect primary language
        primary_lang = detect(text)
        
        # Get all detected languages with probabilities
        all_langs = detect_langs(text)
        
        # Convert to list of dicts
        all_languages = [
            {
                "code": str(lang).split(':')[0],
                "probability": float(str(lang).split(':')[1])
            }
            for lang in all_langs
        ]
        
        # Get language name
        language_name = LANGUAGE_NAMES.get(primary_lang, primary_lang.upper())
        
        # Get confidence (probability of primary language)
        confidence = all_languages[0]['probability'] if all_languages else 0.0
        
        return {
            "language_code": primary_lang,
            "language_name": language_name,
            "confidence": confidence,
            "all_languages": all_languages
        }
        
    except LangDetectException as e:
        return {
            "language_code": "unknown",
            "language_name": "Unknown",
            "confidence": 0.0,
            "all_languages": [],
            "error": str(e)
        }


def is_language(text: str, language_code: str) -> bool:
    """
    Check if text is in a specific language.
    
    Args:
        text: Text to check
        language_code: ISO 639-1 language code (e.g., 'en', 'fr')
        
    Returns:
        True if text is detected as the specified language with high confidence
    """
    result = detect_language(text)
    return result["language_code"] == language_code and result["confidence"] > 0.5


def get_language_name(language_code: str) -> str:
    """
    Get the full language name from language code.
    
    Args:
        language_code: ISO 639-1 language code
        
    Returns:
        Full language name
    """
    return LANGUAGE_NAMES.get(language_code, language_code.upper())
