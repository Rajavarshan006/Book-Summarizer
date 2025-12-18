# backend/services/book_summarization_service.py

from utils.database import (
    get_book_by_id,
    update_book_status,
    create_summary
)
from backend.pipeline import PreprocessingPipeline
from models.t5_summarizer import summarize_text


def summarize_book(book_id: str, user_id: str) -> dict:
    """
    Summarization workflow verifies:
    1. Fetch book document from MongoDB
    2. Validate user ownership via session
    3. Preprocess text using pipeline.py
    4. Generate summary via T5 model
    5. Save summary to database
    6. Update book status to 'processed'
    7. Return success/error payload
    """

    # 1. Fetch book
    book = get_book_by_id(book_id)
    if not book:
        return {"success": False, "error": "Book not found"}

    # 2. Authorization check
    if str(book["user_id"]) != str(user_id):
        return {"success": False, "error": "Unauthorized access"}

    # 3. Update status → processing
    update_book_status(book_id, "processing")

    try:
        # 4. Preprocess text
        pipeline = PreprocessingPipeline()
        processed = pipeline.process(book["raw_text"])

        if not processed["success"]:
            raise Exception("Preprocessing failed")

        # 5. Summarize chunks
        summaries = []
        for chunk in processed["chunks"]:
            summary = summarize_text(chunk)
            summaries.append(summary)

        final_summary = "\n\n".join(summaries)

        # 6. Save summary
        create_summary(
            book_id=book_id,
            user_id=user_id,
            summary_text=final_summary,
            summary_length="medium",
            summary_style="default",
            chunk_summaries=summaries
        )

        # 7. Update status → completed
        update_book_status(book_id, "completed")

        return {"success": True}

    except Exception as e:
        update_book_status(book_id, "failed")
        return {"success": False, "error": str(e)}
