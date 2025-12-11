import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME")

client = MongoClient(MONGO_URI)
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
        "created_at": datetime.utcnow(),
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
        "uploaded_at": datetime.utcnow(),
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

# -------------------------
# SUMMARY FUNCTIONS
# -------------------------

def create_summary(book_id, user_id, summary_text, summary_length, summary_style, chunk_summaries):
    summary = {
        "book_id": ObjectId(book_id),
        "user_id": ObjectId(user_id),
        "summary_text": summary_text,
        "summary_length": summary_length,
        "summary_style": summary_style,
        "chunk_summaries": chunk_summaries,
        "created_at": datetime.utcnow()
    }
    result = db.summaries.insert_one(summary)
    return str(result.inserted_id)

def get_summary_by_id(summary_id):
    return db.summaries.find_one({"_id": ObjectId(summary_id)})
