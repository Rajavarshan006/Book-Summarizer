import streamlit as st
from backend.session import get_current_user
from utils.database import get_books_by_user, get_summaries_by_user

def dashboard_page():
    st.title("📘 Your Dashboard")

    user = get_current_user()
    st.subheader(f"Welcome, {user['name']} 👋")

    st.write("---")

    # Fetch user books
    uid = user.get("user_id")
    books = get_books_by_user(uid)
    summaries = get_summaries_by_user(uid)

    # Quick Stats
    col1, col2, col3 = st.columns(3)

    col1.metric("📚 Books Uploaded", len(books))
    col2.metric("📝 Summaries Created", len(summaries) if summaries else 0)

    if books:
        last_upload = books[-1].get("uploaded_at", "N/A")
        col3.metric("⏱ Last Upload", str(last_upload))
    else:
        col3.metric("⏱ Last Upload", "None")

    st.write("---")

    # Recent Activity
    st.subheader("Recent Activity")

    if not books:
        st.info("No books uploaded yet. Start by uploading your first book!")
    else:
        for book in books[-5:][::-1]:  # Last 5 uploads
            st.write(f"📘 **{book['title']}** — *Status: {book.get('status', 'unknown')}*")

    st.write("---")

    # Quick Actions
    st.subheader("Quick Actions")

    colA, colB = st.columns(2)

    if colA.button("📤 Upload New Book"):
        st.session_state["current_page"] = "upload"
        st.rerun()

    if colB.button("📄 View Summaries"):
        st.session_state["current_page"] = "summaries"
        st.rerun()
