import streamlit as st
from utils.database import get_summary_by_book_id
from backend.book_repository import get_book_by_id


def summary_viewer_page():
    st.title("📄 Book Summary")

    if "selected_book_id" not in st.session_state:
        st.warning("No book selected")
        return

    book_id = st.session_state["selected_book_id"]

    book = get_book_by_id(book_id)
    if not book:
        st.error("Book not found")
        return

    summary = get_summary_by_book_id(book_id)

    if not summary:
        st.info("Summary not available yet.")
        return

    st.subheader(book.get("title", "Untitled Book"))
    st.caption(f"Author: {book.get('author', 'Unknown')}")

    st.divider()

    st.text_area(
        "Generated Summary",
        value=summary["summary_text"],
        height=400,
        disabled=True
    )
