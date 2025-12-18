import streamlit as st
from backend.session import get_current_user
from utils.search_operations import paginate_books, get_search_statistics
from backend.text_processor import process_uploaded_book
from utils.database import delete_book

def dashboard_page():
    # ==========================================
    # HEADER CHECK
    # ==========================================
    user = get_current_user()
    if not user:
        st.error("Please login to continue.")
        return

    user_id = user["user_id"]

    # ==========================================
    # PAGE HEADER
    # ==========================================
    st.title(f"📚 Welcome back, {user['name']}!")
    st.markdown("### Your Book Library Dashboard")
    st.divider()

    # ==========================================
    # STATISTICS OVERVIEW
    # ==========================================
    stats = get_search_statistics(user_id)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📚 Total Books", stats.get("total_books", 0))

    with col2:
        processed = (
            stats.get("status_breakdown", {}).get("text_extracted", 0)
            + stats.get("status_breakdown", {}).get("completed", 0)
        )
        st.metric("📝 Processed Books", processed)

    with col3:
        st.metric("✍️ Total Words", f"{stats.get('total_words', 0):,}")

    with col4:
        st.metric("🌍 Languages", len(stats.get("languages", [])))

    st.write("---")

    # ==========================================
    # SESSION STATE INITIALIZATION
    # ==========================================
    if "page" not in st.session_state:
        st.session_state.page = 1

    if "sort_by" not in st.session_state:
        st.session_state.sort_by = "upload_date"

    if "sort_order" not in st.session_state:
        st.session_state.sort_order = "desc"

    if "status_filter" not in st.session_state:
        st.session_state.status_filter = None

    # ==========================================
    # SEARCH + FILTER BAR
    # ==========================================
    st.subheader("🔍 Search & Filters")

    search_query = st.text_input(
        "Search by Title or Author",
        value=st.session_state.get("search_query", ""),
        placeholder="Search your books..."
    )

    st.session_state.search_query = search_query

    col1, col2, col3 = st.columns(3)

    with col1:
        sort_by_label = st.selectbox(
            "Sort By",
            ["Upload Date", "Title", "Author", "Word Count", "Status"]
        )

        sort_mapping = {
            "Upload Date": "upload_date",
            "Title": "title",
            "Author": "author",
            "Word Count": "word_count",
            "Status": "status"
        }

        st.session_state.sort_by = sort_mapping[sort_by_label]

    with col2:
        order = st.selectbox("Order", ["Descending", "Ascending"])
        st.session_state.sort_order = "desc" if order == "Descending" else "asc"

    with col3:
        status = st.selectbox(
            "Status Filter",
            ["All", "Uploaded", "Processing", "Text Extracted", "Completed", "Failed"]
        )

        status_map = {
            "All": None,
            "Uploaded": "uploaded",
            "Processing": "processing",
            "Text Extracted": "text_extracted",
            "Completed": "completed",
            "Failed": "failed",
        }

        st.session_state.status_filter = status_map[status]

    st.write("---")

    # ==========================================
    # FETCH PAGINATED BOOK DATA
    # ==========================================
    result = paginate_books(
        user_id=user_id,
        page=st.session_state.page,
        per_page=6,
        search_query=search_query,
        sort_by=st.session_state.sort_by,
        sort_order=st.session_state.sort_order,
        status_filter=st.session_state.status_filter
    )

    books = result["books"]
    total = result["total_books"]
    total_pages = result["total_pages"]
    current_page = result["current_page"]

    st.subheader(f"📘 Books Found: {total}")

    # ==========================================
    # DISPLAY BOOKS
    # ==========================================
    if not books:
        st.warning("No books matched your search or filters.")
        return

    for book in books:
        with st.container():
            st.markdown(f"### 📖 {book['title']}")
            st.caption(f"👤 Author: {book['author']}")
            st.write(f"📅 Uploaded: {book.get('upload_date', 'N/A')}")
            st.write(
                f"📌 Status: **{book['status'].upper()}** "
                f" | Words: {book.get('word_count', 0):,} "
                f" | Language: {book.get('language', 'Unknown')}"
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if st.button("👁 View", key=f"v_{book['book_id']}"):
                    st.session_state["selected_book"] = book["book_id"]
                    st.session_state["current_page"] = "book_details"
                    st.rerun()

            with col2:
                if st.button("⚙ Process", key=f"p_{book['book_id']}"):
                    with st.spinner("Processing..."):
                        out = process_uploaded_book(book["book_id"])
                        if out["success"]:
                            st.success("Processing complete!")
                            st.rerun()
                        else:
                            st.error(out.get("error"))

            with col3:
                if st.button("📝 Summarize", key=f"summ_{book['book_id']}"):
                    with st.spinner("Summarizing..."):
                        from backend.book_summarization_service import summarize_book
                        result = summarize_book(book['book_id'], user['user_id'])
                        if result["success"]:
                            st.success("Summary generated!")
                            st.rerun()
                        else:
                            st.error(result["error"])

            with col4:
                if st.button("🗑 Delete", key=f"d_{book['book_id']}"):
                    st.session_state['book_to_delete'] = book['book_id']
                    st.warning("⚠️ Delete confirmation needed")

            st.write("---")
        # If a delete action is pending
    if "book_to_delete" in st.session_state and st.session_state["book_to_delete"]:
        st.error("⚠️ Are you sure you want to permanently delete this book?")

        col_d1, col_d2 = st.columns(2)

        with col_d1:
            if st.button("Yes, Delete Permanently"):
                success = delete_book(st.session_state["book_to_delete"])
                if success:
                    st.success("✓ Book deleted successfully")
                    st.session_state["book_to_delete"] = None
                    st.rerun()
                else:
                    st.error("❌ Failed to delete book. Check logs.")

        with col_d2:
            if st.button("Cancel"):
                st.session_state["book_to_delete"] = None
                st.rerun()

    # ==========================================
    # PAGINATION
    # ==========================================
    st.write(f"Page {current_page} of {total_pages}")

    col_prev, col_next = st.columns(2)

    if col_prev.button("⬅ Previous", disabled=current_page == 1):
        st.session_state.page -= 1
        st.rerun()

    if col_next.button("Next ➡", disabled=current_page >= total_pages):
        st.session_state.page += 1
        st.rerun()
