import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load .env variables
load_dotenv()

MONGO_URL = os.getenv("mongodb+srv://BookSummarizerDB:eFR5bBaLoX4InEOQ@booksummarizercluster.1hecn1r.mongodb.net/")
DB_NAME = os.getenv("BookSummarizerDB")

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

def get_database():
    return db
# -------------------------
# USER COLLECTION FUNCTIONS
# -------------------------
from datetime import datetime 
def create_user(name, email, password_hash, role="user",created_at=None):
    db = get_database()
    user = {
        "name": name,
        "email": email,
        "password_hash": password_hash,
        "created_at": datatime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "role": role
    }
    result = db.users.insert_one(user)
    return str(result.inserted_id)


def get_user_by_email(email):
    db = get_database()
    user = db.users.find_one({"email": email})
    return user
# -------------------------
# BOOK COLLECTION FUNCTIONS
# -------------------------
def create_book(user_id,title,author,chapter,file_path):
    new_book = {
        "user_id": user_id,
        "title": title,
        "author": author,
        "chapter": chapter,
        "file_path": file_path,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "uploaded"
    }
    result = db.books.insert_one(new_book)
    return str(result.inserted_id)
def update_book_text(book_id, text):
    db.books.update_one(
        {"_id": book_id},
        {"$set": {"raw_text": text}}
    )
        

def update_book_status(book_id, status):
    """
    Update status of a book.
    Allowed values:
    - uploaded
    - processing
    - text_extracted
    - completed
    - failed
    """
    db.books.update_one(
        {"_id": book_id},
        {"$set": {"status":status}}
    )
def get_book_by_id(book_id):
    book = db.books.find_one({"_id": book_id})
    return book
def get_books_by_user(user_id):
    books = list(db.books.find({"user_id": user_id}))
    return books



# -------------------------
# SUMMARY COLLECTION FUNCTIONS
# -------------------------
from bson import ObjectId
def create_summary(book_id,user_id,summary_text,summary_length,summary_style,chunk_summaries,created_at=None):
    new_summary = {
        "book_id": ObjectId(book_id),
        "user_id": ObjectId(user_id),
        "summary_text": summary_text,
        "summary_length": summary_length,
        "summary_style": summary_style,
        "chunk_summaries": chunk_summaries,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    result = db.summaries.insert_one(new_summary)
    return str(result.inserted_id)

def get_summaries_by_user(user_id):
    summaries = list(db.summaries.find_one({"user_id": user_id}))
    return summaries
    
def get_summary_by_id(summary_id):
    summary = db.summaries.find_one({"_id": ObjectId(summary_id)})
    return summary

