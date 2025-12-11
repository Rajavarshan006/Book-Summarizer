from datetime import datetime
from bson.objectid import ObjectId
from utils.database import db


def create_book(
    user_id: str,
    title: str,
    author: str | None,
    chapter: str | None,
    file_type: str,
    raw_text: str
):
    """
    Store uploaded book and its raw extracted text in database.
    """

    book_doc = {
        "user_id": ObjectId(user_id),
        "title": title,
        "author": author,
        "chapter": chapter,
        "file_type": file_type,
        "raw_text": raw_text,
        "uploaded_at": datetime.utcnow(),
        "status": "uploaded"
    }

    result = db.books.insert_one(book_doc)
    return result.inserted_id
