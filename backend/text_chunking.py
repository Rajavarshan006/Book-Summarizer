from typing import List, Dict
from backend.sentence_segmentation import segment_sentences


def chunk_text(text: str, chunk_size: int = 1200, overlap_size: int = 125, min_chunk_size: int = 100) -> List[Dict]:
    """
    Split text into chunks with overlapping sentences.
    
    Args:
        text: Text to chunk
        chunk_size: Target words per chunk (default 1200, range 1000-1500)
        overlap_size: Overlap words between chunks (default 125, range 100-150)
        min_chunk_size: Minimum words for a valid chunk
        
    Returns:
        List of chunk dictionaries with:
        - chunk_id: Sequential chunk number
        - text: Chunk content
        - word_count: Words in chunk
        - sentence_count: Sentences in chunk
        - start_index: Character start position in original text
        - end_index: Character end position in original text
    """
    if not text or not isinstance(text, str):
        return []
    
    # Segment text into sentences
    sentences = segment_sentences(text)
    
    if not sentences:
        return []
    
    chunks = []
    chunk_id = 0
    sentence_index = 0
    
    while sentence_index < len(sentences):
        # Start new chunk with overlap from previous chunk
        chunk_sentences = []
        chunk_word_count = 0
        chunk_start_index = sentence_index
        
        # Add sentences until we reach target chunk size
        while sentence_index < len(sentences):
            sentence = sentences[sentence_index]
            sentence_word_count = len(sentence.split())
            
            # If adding this sentence would exceed chunk size and we have some content, break
            if chunk_word_count + sentence_word_count > chunk_size and chunk_sentences:
                break
            
            chunk_sentences.append(sentence)
            chunk_word_count += sentence_word_count
            sentence_index += 1
        
        # If we have a valid chunk, save it
        if chunk_sentences and chunk_word_count >= min_chunk_size:
            chunk_text = " ".join(chunk_sentences)
            
            # Find actual character indices in original text
            start_char = text.find(chunk_sentences[0])
            end_char = text.find(chunk_sentences[-1]) + len(chunk_sentences[-1])
            
            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text,
                "word_count": chunk_word_count,
                "sentence_count": len(chunk_sentences),
                "start_index": start_char if start_char != -1 else 0,
                "end_index": end_char if end_char != -1 else len(text),
                "sentences": chunk_sentences
            })
            
            chunk_id += 1
            
            # Move back by overlap amount for next chunk
            overlap_word_count = 0
            sentences_to_keep = 0
            
            for i in range(len(chunk_sentences) - 1, -1, -1):
                sentence_words = len(chunk_sentences[i].split())
                if overlap_word_count + sentence_words <= overlap_size:
                    overlap_word_count += sentence_words
                    sentences_to_keep += 1
                else:
                    break
            
            # Move sentence index back for overlap
            sentence_index = max(chunk_start_index + len(chunk_sentences) - sentences_to_keep, chunk_start_index + 1)
        else:
            # If chunk is too small, add remaining sentences and break
            if chunk_sentences:
                chunk_text = " ".join(chunk_sentences)
                start_char = text.find(chunk_sentences[0])
                end_char = text.find(chunk_sentences[-1]) + len(chunk_sentences[-1])
                
                chunks.append({
                    "chunk_id": chunk_id,
                    "text": chunk_text,
                    "word_count": chunk_word_count,
                    "sentence_count": len(chunk_sentences),
                    "start_index": start_char if start_char != -1 else 0,
                    "end_index": end_char if end_char != -1 else len(text),
                    "sentences": chunk_sentences
                })
            break
    
    return chunks


def get_chunk_summary_info(chunks: List[Dict]) -> Dict:
    """
    Get summary information about chunks.
    
    Args:
        chunks: List of chunks from chunk_text()
        
    Returns:
        Dictionary with:
        - total_chunks: Number of chunks
        - total_words: Total words across all chunks
        - avg_chunk_size: Average words per chunk
        - min_chunk_size: Smallest chunk word count
        - max_chunk_size: Largest chunk word count
        - total_overlap_words: Total overlapping words
    """
    if not chunks:
        return {
            "total_chunks": 0,
            "total_words": 0,
            "avg_chunk_size": 0,
            "min_chunk_size": 0,
            "max_chunk_size": 0,
            "total_overlap_words": 0
        }
    
    word_counts = [c["word_count"] for c in chunks]
    total_words = sum(word_counts)
    
    # Estimate overlap words
    total_overlap_words = 0
    for i in range(len(chunks) - 1):
        # Find overlapping sentences
        current_last_sentences = chunks[i]["sentences"][-3:]  # Last 3 sentences typically
        next_first_sentences = chunks[i + 1]["sentences"][:3]  # First 3 sentences typically
        
        # Count common words in overlap
        overlap_text = " ".join(current_last_sentences)
        overlap_word_count = len(overlap_text.split())
        total_overlap_words += overlap_word_count
    
    return {
        "total_chunks": len(chunks),
        "total_words": total_words,
        "avg_chunk_size": round(total_words / len(chunks), 2),
        "min_chunk_size": min(word_counts),
        "max_chunk_size": max(word_counts),
        "total_overlap_words": total_overlap_words
    }


def validate_chunks(chunks: List[Dict], min_size: int = 100, max_size: int = 1500) -> bool:
    """
    Validate that chunks meet size requirements.
    
    Args:
        chunks: List of chunks
        min_size: Minimum words per chunk
        max_size: Maximum words per chunk
        
    Returns:
        True if all chunks are within bounds
    """
    for chunk in chunks:
        if chunk["word_count"] < min_size or chunk["word_count"] > max_size:
            return False
    return True
