# backend/services/book_processing_service.py

from utils.database import (
    get_book_by_id,
    update_book_status,
    create_summary,
    conditional_update_book_status,
    get_book_status
)

from backend.pipeline import preprocess
from models.t5_summarizer import summarize_chunks


def process_book_once(book_id: str, user_id: str) -> dict:
    """
    Process and summarize a book exactly once.
    """

    book = get_book_by_id(book_id)

    if not book:
        return {"success": False, "error": "Book not found"}

    if str(book["user_id"]) != str(user_id):
        return {"success": False, "error": "Unauthorized"}

    # Atomically transition from 'uploaded' to 'processing'
    if not conditional_update_book_status(book_id, "uploaded", "processing"):
        # Get fresh status from database
        current_status = get_book_status(book_id)
        if not current_status:
            return {"success": False, "error": "Book status unavailable"}
        if current_status == "completed":
            return {"success": False, "error": "Already processed"}
        return {"success": False, "error": "Already being processed"}

    # Validate raw_text exists and is non-empty
    raw_text = book.get("raw_text")
    if not raw_text or not raw_text.strip():
        update_book_status(book_id, "uploaded")
        return {
            "success": False, 
            "error": "Cannot process book - missing or empty text content"
        }

    # Run preprocessing with error handling
    try:
        pipeline_result = preprocess(raw_text)
    except Exception as e:
        update_book_status(book_id, "uploaded")
        return {
            "success": False,
            "error": f"Preprocessing error: {str(e)}"
        }

    if not pipeline_result.get("success"):
        update_book_status(book_id, "uploaded")
        return {"success": False, "error": "Preprocessing failed"}

    # Validate chunks exist and are non-empty
    chunks = pipeline_result.get("chunks")
    if not chunks or not isinstance(chunks, list) or len(chunks) == 0:
        update_book_status(book_id, "uploaded")
        return {
            "success": False,
            "error": "Preprocessing failed - no text chunks generated"
        }

    # Run summarization
    summary_text = summarize_chunks(chunks)

    # Save summary
    create_summary(
        book_id=book_id,
        user_id=user_id,
        summary_text=summary_text,
        summary_length="auto",
        summary_style="t5",
        chunk_summaries=None
    )

    # Lock book forever
    update_book_status(book_id, "completed")

    return {"success": True}
