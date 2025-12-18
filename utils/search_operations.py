"""
SaaS-Level Search, Filter, Sorting & Pagination
Integrated with Dashboard Schema
"""

from typing import Dict, List, Optional
from bson import ObjectId
from utils.database import books_collection
from datetime import datetime


# ===========================
# TEXT SEARCH
# ===========================

def search_books(
    user_id: str,
    search_query: Optional[str] = None,
    search_fields: List[str] = ["title", "author"],
) -> List[Dict]:

    query = {"user_id": ObjectId(user_id)}

    if search_query and search_query.strip():
        query["$or"] = [
            {field: {"$regex": search_query, "$options": "i"}}
            for field in search_fields
        ]

    books = list(books_collection.find(query))
    return _format_books(books)


# ===========================
# FILTER + SORT
# ===========================

def filter_and_sort_books(
    user_id: str,
    sort_by: str = "uploaded_at",
    sort_order: str = "desc",
    status_filter: Optional[str] = None
) -> List[Dict]:

    query = {"user_id": ObjectId(user_id)}

    if status_filter:
        query["status"] = status_filter

    sort_direction = 1 if sort_order == "asc" else -1

    field_map = {
        "uploaded_at": "uploaded_at",
        "title": "title",
        "author": "author",
        "word_count": "preprocessing_metadata.word_count",
        "reading_time": "preprocessing_metadata.reading_time_minutes",
        "status": "status"
    }

    sort_field = field_map.get(sort_by, "uploaded_at")

    books = list(books_collection.find(query).sort(sort_field, sort_direction))
    return _format_books(books)


# ===========================
# PAGINATION ENGINE
# ===========================

def paginate_books(
    user_id: str,
    page: int = 1,
    per_page: int = 10,
    search_query: Optional[str] = None,
    sort_by: str = "uploaded_at",
    sort_order: str = "desc",
    status_filter: Optional[str] = None
) -> Dict:

    query = {"user_id": ObjectId(user_id)}

    if search_query and search_query.strip():
        query["$or"] = [
            {"title": {"$regex": search_query, "$options": "i"}},
            {"author": {"$regex": search_query, "$options": "i"}}
        ]

    if status_filter:
        query["status"] = status_filter

    total_books = books_collection.count_documents(query)

    total_pages = (total_books + per_page - 1) // per_page
    page = max(1, min(page, total_pages if total_pages else 1))
    skip = (page - 1) * per_page

    sort_direction = 1 if sort_order == "asc" else -1

    sort_map = {
        "uploaded_at": "uploaded_at",
        "title": "title",
        "author": "author",
    }

    sort_field = sort_map.get(sort_by, "uploaded_at")

    cursor = (
        books_collection.find(query)
        .sort(sort_field, sort_direction)
        .skip(skip)
        .limit(per_page)
    )

    books = _format_books(list(cursor))

    return {
        "books": books,
        "total_books": total_books,
        "total_pages": total_pages,
        "current_page": page,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


# ===========================
# STATISTICS
# ===========================

def get_search_statistics(user_id: str) -> Dict:
    user_id = ObjectId(user_id)

    books = list(books_collection.find({"user_id": user_id}))

    total = len(books)

    status_breakdown = {}
    languages = set()
    total_words = 0

    for b in books:
        status_breakdown[b.get("status", "unknown")] = status_breakdown.get(b.get("status", "unknown"), 0) + 1

        meta = b.get("preprocessing_metadata", {})
        if meta:
            languages.add(meta.get("language_name"))
            total_words += meta.get("word_count", 0)

    return {
        "total_books": total,
        "status_breakdown": status_breakdown,
        "languages": list(languages),
        "total_words": total_words,
    }


# ===========================
# FORMAT RETURN OBJECTS
# ===========================

def _format_books(books: List[Dict]) -> List[Dict]:
    formatted = []

    for b in books:
        meta = b.get("preprocessing_metadata", {})

        formatted.append({
            "book_id": str(b["_id"]),
            "title": b.get("title", "Untitled"),
            "author": b.get("author", "Unknown"),
            "uploaded_at": b.get("uploaded_at"),
            "status": b.get("status", "unknown"),
            "word_count": meta.get("word_count", 0),
            "language": meta.get("language_name", "Unknown"),
            "reading_time": meta.get("reading_time_minutes", 0),
            "is_processed": b.get("status") in ["text_extracted", "completed"]
        })

    return formatted
