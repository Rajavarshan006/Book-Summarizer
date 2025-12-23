# backend/services/book_summarization_service.py

import logging


from utils.database import (
    get_book_by_id,
    update_book_status,
    create_summary
)
from backend.pipeline import PreprocessingPipeline
from backend.summary_merger import summary_merger
from models.t5_summarizer import summarize_text

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def summarize_book(book_id: str, user_id: str, summary_length: int = 1000,
                  summary_style: str = "default", chunk_size: int = 2000,
                  overlap_percentage: int = 20) -> dict:
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
        # 4. Preprocess text with custom chunking parameters
        # Convert overlap percentage to overlap size (20% of chunk_size)
        overlap_size = int(chunk_size * overlap_percentage / 100)
        pipeline = PreprocessingPipeline(chunk_size=chunk_size, overlap_size=overlap_size)
        processed = pipeline.process(book["raw_text"])

        if not processed["success"]:
            raise Exception("Preprocessing failed")

        # 5. Summarize chunks
        summaries = []
        chunk_texts = []  # Store original chunk texts for context-aware merging

        for chunk in processed["chunks"]:
            chunk_text = chunk["text"] if isinstance(chunk, dict) else str(chunk)
            summary = summarize_text(chunk_text)
            summaries.append(summary)
            chunk_texts.append(chunk_text)

        # 6. Merge summaries intelligently instead of simple concatenation
        if len(summaries) > 1:
            # Use context-aware merging for better results with custom summary length
            final_summary = summary_merger.merge_with_context(
                chunk_summaries=summaries,
                chunk_contexts=chunk_texts,
                max_length=summary_length
            )

            # Validate the merged summary
            validation_report = summary_merger.validate_merged_summary(summaries, final_summary)

            if not validation_report["validation_passed"]:
                logger.warning(f"Summary merging validation issues: {validation_report}")
                # Fallback to intelligent merging without context if validation fails
                final_summary = summary_merger.merge_summaries(summaries, "intelligent", summary_length)
        else:
            # Single chunk, no need to merge
            final_summary = summaries[0] if summaries else ""

        # 7. Save summary with additional metadata
        summary_metadata = {
            "merging_strategy": "intelligent_context_aware" if len(summaries) > 1 else "single_chunk",
            "chunk_count": len(summaries),
            "validation_report": validation_report if len(summaries) > 1 else None
        }

        create_summary(
            book_id=book_id,
            user_id=user_id,
            summary_text=final_summary,
            summary_length="medium",
            summary_style="default",
            chunk_summaries=summaries,
            summary_metadata=summary_metadata
        )

        # 7. Update status → completed
        update_book_status(book_id, "completed")

        return {"success": True}

    except Exception as e:
        update_book_status(book_id, "failed")
        return {"success": False, "error": str(e)}
