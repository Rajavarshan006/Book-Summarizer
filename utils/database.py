import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timezone
from bson.objectid import ObjectId
from bson.errors import InvalidId

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME")

client = MongoClient(MONGO_URI,
    tls=True,
    retryWrites=True,
    w='majority',
    tlsAllowInvalidCertificates=os.getenv('ENV') == 'DEV'
)
db = client[DB_NAME]

def get_database():
    return db

# -------------------------
# USER FUNCTIONS
# -------------------------

def create_user(name, email, password_hash, role="user"):
    user = {
        "name": name,
        "email": email,
        "password_hash": password_hash,
        "created_at": datetime.now(timezone.utc),
        "role": role
    }
    result = db.users.insert_one(user)
    return str(result.inserted_id)

def get_user_by_email(email):
    return db.users.find_one({"email": email})

# -------------------------
# BOOK FUNCTIONS
# -------------------------

def create_book(user_id, title, raw_text, author=None, chapter=None, file_type="text", file_path=None):
    book = {
        "user_id": ObjectId(user_id),
        "title": title,
        "author": author,
        "chapter": chapter,
        "file_type": file_type,
        "file_path": file_path,
        "raw_text": raw_text,
        "uploaded_at": datetime.now(timezone.utc),
        "status": "uploaded"
    }
    result = db.books.insert_one(book)
    return str(result.inserted_id)

def get_book_by_id(book_id):
    return db.books.find_one({"_id": ObjectId(book_id)})

def update_book_status(book_id, status):
    db.books.update_one(
        {"_id": ObjectId(book_id)},
        {"$set": {"status": status}}
    )

def conditional_update_book_status(book_id, expected_status, new_status):
    result = db.books.update_one(
        {"_id": ObjectId(book_id), "status": expected_status},
        {"$set": {"status": new_status}}
    )
    return result.modified_count > 0

def get_book_status(book_id):
    book = db.books.find_one(
        {"_id": ObjectId(book_id)},
        {"status": 1}
    )
    return book.get("status") if book else None

# -------------------------
# SUMMARY FUNCTIONS
# -------------------------

def create_summary(book_id, user_id, summary_text, summary_length, summary_style, chunk_summaries, summary_metadata=None):
    summary = {
        "book_id": ObjectId(book_id),
        "user_id": ObjectId(user_id),
        "summary_text": summary_text,
        "summary_length": summary_length,
        "summary_style": summary_style,
        "chunk_summaries": chunk_summaries,
        "created_at": datetime.now(timezone.utc)
    }

    # Add metadata if provided
    if summary_metadata is not None:
        summary["summary_metadata"] = summary_metadata
    result = db.summaries.insert_one(summary)
    return str(result.inserted_id)

def get_summary_by_id(summary_id):
    return db.summaries.find_one({"_id": ObjectId(summary_id)})

def get_summary_by_book_id(book_id, user_id=None):
    """Get the most recent summary for a book by book_id with optional ownership validation.

    Returns the most recently created summary for the specified book.
    If no summaries exist for the book, returns None.
    Note: Multiple summaries can exist per book (as evidenced by delete_many usage).

    Args:
        book_id: The book ID (string or ObjectId) to get summaries for
        user_id: Optional user ID for ownership validation. If provided, only returns
                summaries that belong to the specified user.

    Returns:
        The most recent summary document, or None if no summaries exist or ownership check fails
    """
    # Validate and convert book_id with specific error handling
    try:
        bid = ObjectId(book_id) if isinstance(book_id, str) else book_id
    except InvalidId:
        return None

    query = {"book_id": bid}

    # Validate and convert user_id with specific error handling
    if user_id is not None:
        try:
            uid = ObjectId(user_id) if isinstance(user_id, str) else user_id
            query["user_id"] = uid
        except InvalidId:
            return None

    return db.summaries.find_one(
        query,
        sort=[("created_at", -1)]
    )

def get_books_by_user(user_id):
    """Return list of books for the given user id."""
    try:
        uid = ObjectId(user_id) if isinstance(user_id, str) else user_id
    except Exception:
        return []
    return list(db.books.find({"user_id": uid}))

def get_summaries_by_user(user_id):
    """Return list of summaries for the given user id."""
    try:
        uid = ObjectId(user_id) if isinstance(user_id, str) else user_id
    except Exception:
        return []
    return list(db.summaries.find({"user_id": uid}))

# Add these
books_collection = db.books
summaries_collection = db.summaries

def delete_book(book_id):
    try:
        db.books.delete_one({"_id": ObjectId(book_id)})
        # Also delete summaries for this book
        db.summaries.delete_many({"book_id": ObjectId(book_id)})
        return True
    except Exception as e:
        print("Error deleting book:", e)
        return False
