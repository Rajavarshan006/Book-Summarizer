# frontend/uploaded_books_page.py
import streamlit as st
from backend.session import get_current_user
from utils.search_operations import paginate_books
from utils.database import delete_book

def uploaded_books_page():
    user = get_current_user()
    if not user:
        st.error("Please login to continue.")
        return

    user_id = user["user_id"]
    
    st.title("📚 Your Uploaded Books")
    st.write("---")

    # Initialize pagination
    if "page" not in st.session_state:
        st.session_state.page = 1

    # Fetch books
    result = paginate_books(
        user_id=user_id,
        page=st.session_state.page,
        per_page=10,
        search_query="",
        sort_by="upload_date",
        sort_order="desc"
    )

    books = result["books"]
    total_pages = result["total_pages"]
    current_page = result["current_page"]

    if not books:
        st.warning("You haven't uploaded any books yet.")
        return

    # Display books
    for book in books:
        with st.container():
            st.subheader(f"📖 {book['title']}")
            st.write(f"👤 Author: {book['author']}")
            st.write(f"📅 Uploaded: {book.get('upload_date', 'N/A')}")
            st.write(f"📌 Status: {book['status'].title()}")
            
            if book.get("summary"):
                with st.expander("View Summary"):
                    st.write(book["summary"])
            
            st.write("---")

    # Pagination controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Previous", disabled=current_page == 1):
            st.session_state.page -= 1
            st.rerun()
    with col2:
        if st.button("Next", disabled=current_page >= total_pages):
            st.session_state.page += 1
            st.rerun()