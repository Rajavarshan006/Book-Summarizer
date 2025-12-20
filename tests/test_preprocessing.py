import pytest
from backend.preprocessing import clean_text, normalize_text, remove_stopwords, lemmatize_text

def test_text_preprocessing_pipeline():
    # Test input with various edge cases
    input_text = """   This is a TEST sentence!  It's got extra   spaces, 
  special characters @#$%, numbers like 123, UPPER CASE, and contractions like can't."""
    
    # Test cleaning
    cleaned = clean_text(input_text)
    assert "  " not in cleaned
    assert "@#$" not in cleaned
    
    # Enhanced cleaning assertions
    assert "it's" not in cleaned  # Should become "it is"
    assert "123" not in cleaned  # Numbers should be removed
    
    # Restore normalization section
    normalized = normalize_text(cleaned)
    assert normalized.islower()
    
    # Restore original stopwords removal
    without_stopwords = remove_stopwords(normalized)
    
    # Test lemmatization
    lemmatized = lemmatize_text(without_stopwords)
    assert "sentence" in lemmatized  # Verify lemma contains base form
    assert "got" not in lemmatized  # Should be 'get'
    
    # Enhanced lemmatization assertions
    assert "get" in lemmatized  # Lemma of 'got'
    assert "can" in lemmatized  # Lemma of "can't"
    
    # Test empty input
    assert clean_text("") == ""
    
    # Test special unicode characters
    assert clean_text("“Curly quotes” and em dash —") == "Curly quotes and em dash "
    # Enhanced special characters test
    assert clean_text("àçcéntéd chars") == "accented chars"
    assert clean_text("Preserve: hyphens-in-words") == "preserve hyphens in words"