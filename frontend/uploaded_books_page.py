# frontend/uploaded_books_page.py
import streamlit as st
from backend.session import get_current_user
from utils.search_operations import paginate_books
from utils.database import delete_book, get_summary_by_book_id
from backend.book_summarization_service import summarize_book

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

            # Check if book has a summary with ownership verification
            summary = get_summary_by_book_id(str(book['book_id']), user_id)

            # Explicit ownership verification
            if summary and str(summary.get('user_id')) != str(user_id):
                st.error("Authorization error: You don't have permission to access this summary")
                summary = None

            if summary:
                with st.expander("View Summary"):
                    st.write(summary["summary_text"])

                    # Add download button for the summary with unique key
                    st.download_button(
                        label="💾 Download Summary",
                        data=summary["summary_text"],
                        file_name=f"summary_{book['title']}.txt",
                        mime="text/plain",
                        key=f"download_{book['book_id']}"
                    )
            else:
                    # Add summarize button for books without summaries with ownership verification
                if st.button(f"🚀 Summarize {book['title']}", key=f"summarize_{book['book_id']}"):
                    # Explicit ownership verification before summarization
                    if str(book['user_id']) != str(user_id):
                        st.error("Authorization error: You don't have permission to summarize this book")
                    else:
                        # Show progress while summarizing
                        with st.spinner(f"Summarizing {book['title']}..."):
                            try:
                                result = summarize_book(str(book['book_id']), user_id)
                                if result["success"]:
                                    st.success(f"✅ Successfully summarized {book['title']}!")
                                    # Refresh the page to show the new summary
                                    st.rerun()
                                else:
                                    st.error(f"❌ Failed to summarize {book['title']}: {result.get('error', 'Unknown error')}")
                            except Exception as e:
                                st.error(f"❌ Error summarizing {book['title']}: {str(e)}")

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
