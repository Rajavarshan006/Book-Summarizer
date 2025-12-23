#!/usr/bin/env python3
"""
Test script to verify the updated get_summary_by_book_id function behavior.
This script tests that the function returns the most recent summary when multiple exist.
"""

import os
from datetime import datetime, timezone, timedelta
from bson.objectid import ObjectId
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the updated function
from utils.database import get_summary_by_book_id, db

def test_get_summary_by_book_id():
    """Test that get_summary_by_book_id returns the most recent summary."""

    # Create a test book
    test_book = {
        "user_id": ObjectId(),
        "title": "Test Book",
        "raw_text": "This is test content",
        "uploaded_at": datetime.now(timezone.utc),
        "status": "uploaded"
    }
    book_result = db.books.insert_one(test_book)
    book_id = book_result.inserted_id

    # Create multiple summaries with different timestamps
    now = datetime.now(timezone.utc)
    older_summary = {
        "book_id": book_id,
        "user_id": ObjectId(),
        "summary_text": "Old summary",
        "summary_length": "medium",
        "summary_style": "bullet",
        "chunk_summaries": [],
        "created_at": now - timedelta(hours=2)
    }

    newer_summary = {
        "book_id": book_id,
        "user_id": ObjectId(),
        "summary_text": "New summary",
        "summary_length": "medium",
        "summary_style": "bullet",
        "chunk_summaries": [],
        "created_at": now - timedelta(hours=1)
    }

    newest_summary = {
        "book_id": book_id,
        "user_id": ObjectId(),
        "summary_text": "Newest summary",
        "summary_length": "medium",
        "summary_style": "bullet",
        "chunk_summaries": [],
        "created_at": now
    }

    # Insert summaries
    db.summaries.insert_many([older_summary, newer_summary, newest_summary])

    # Test the function
    result = get_summary_by_book_id(str(book_id))

    # Verify it returns the newest summary
    assert result is not None, "Should return a summary"
    assert result["summary_text"] == "Newest summary", f"Expected 'Newest summary', got '{result['summary_text']}'"
    assert result["created_at"] == newest_summary["created_at"], "Should return the most recent summary"

    print("✓ Test passed: get_summary_by_book_id returns the most recent summary")

    # Cleanup
    db.summaries.delete_many({"book_id": book_id})
    db.books.delete_one({"_id": book_id})

    return True

if __name__ == "__main__":
    try:
        test_get_summary_by_book_id()
        print("All tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        raise
