from utils.database import get_book_by_id, db, update_book_status
from backend.preprocessing import preprocess_text
from bson import ObjectId

def process_uploaded_book(book_id: str) -> dict:
    """
    Processes an uploaded book using the existing preprocessing pipeline
    (cleaning, language detection, statistics, chunking).
    
    Saves results back into MongoDB.
    """
    try:
        # 1. Fetch book
        book = get_book_by_id(book_id)
        if not book:
            return {"success": False, "error": "Book not found"}
        
        raw_text = book.get("raw_text")
        if not raw_text:
            return {"success": False, "error": "Book has no raw_text"}

        # 2. Run preprocessing
        results = preprocess_text(raw_text)

        # 3. Build metadata to save
        metadata = {
            "language_name": results["language"].get("language_name"),
            "word_count": results["statistics"]["word_count"],
            "sentence_count": results["sentence_count"],
            "chunk_count": len(results["chunks"]),
            "reading_time_minutes": round(
                results["statistics"]["word_count"] / 225, 2
            )
        }

        # 4. Update MongoDB with processed data
        db.books.update_one(
            {"_id": ObjectId(book_id)},
            {
                "$set": {
                    "cleaned_text": results["cleaned_text"],
                    "chunks": results["chunks"],
                    "preprocessing_metadata": metadata,
                    "status": "text_extracted",
                }
            }
        )

        return {"success": True, "message": "Book processed successfully"}

    except Exception as e:
        update_book_status(book_id, "failed")
        return {"success": False, "error": str(e)}
