import streamlit as st
import requests
import json
from datetime import datetime
from backend.book_summarization_service import summarize_book
from backend.session import get_current_user
from utils.database import get_summary_by_book_id, get_books_by_user, get_book_by_id

def generate_summary_page():
    """Comprehensive summary generation interface with advanced options and real-time monitoring"""

    st.title("🚀 Advanced Summary Generation")
    st.markdown("""
    Generate intelligent summaries with customizable parameters and real-time progress tracking.
    """)

    # Get current user
    user = get_current_user()
    if not user:
        st.error("Please log in to generate summaries")
        return

    user_id = user["user_id"]

    # Load user's books
    books = get_books_by_user(user_id)

    if not books:
        st.info("You haven't uploaded any books yet. Please upload a book first.")
        return

    # Book selection section
    st.subheader("📚 Select Book for Summarization")

    # Status filter
    col1, col2 = st.columns([3, 1])
    with col2:
        status_filter = st.selectbox(
            "Filter by status:",
            ["All", "uploaded", "processing", "completed", "failed"]
        )

    # Apply status filter
    if status_filter != "All":
        filtered_books = [b for b in books if b['status'] == status_filter]
    else:
        filtered_books = books

    if not filtered_books:
        st.warning(f"No books found with status '{status_filter}'")
        return

    with col1:
        # Book selection dropdown
        book_options = [f"{book['title']} (ID: {str(book['_id'])})" for book in filtered_books]
        selected_book_index = st.selectbox(
            "Choose a book to summarize:",
            range(len(book_options)),
            format_func=lambda x: book_options[x]
        )

    selected_book = filtered_books[selected_book_index]

    # Display book information
    st.divider()
    st.subheader("📋 Book Information")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Title:** {selected_book['title']}")
        st.write(f"**Author:** {selected_book.get('author', 'Unknown')}")

    with col2:
        st.write(f"**Status:** {selected_book['status']}")
        st.write(f"**Uploaded:** {selected_book['uploaded_at'].strftime('%Y-%m-%d %H:%M:%S')}")

    with col3:
        st.write(f"**File Type:** {selected_book['file_type']}")
        st.write(f"**Character Count:** {len(selected_book['raw_text'])}")

    # Summary generation options
    st.divider()
    st.subheader("⚙️ Summarization Options")

    # Advanced settings expander
    with st.expander("🔧 Advanced Settings", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            summary_length = st.slider(
                "Summary Length",
                min_value=100,
                max_value=5000,
                value=1000,
                step=100,
                help="Target length of the final summary in characters"
            )

            summary_style = st.selectbox(
                "Summary Style",
                ["default", "concise", "detailed", "bullet_points", "executive"],
                help="Choose the writing style for your summary"
            )

        with col2:
            chunk_size = st.slider(
                "Chunk Size",
                min_value=500,
                max_value=5000,
                value=2000,
                step=100,
                help="Size of text chunks for processing (larger = more context, smaller = more precise)"
            )

            overlap_percentage = st.slider(
                "Chunk Overlap",
                min_value=0,
                max_value=50,
                value=20,
                step=5,
                help="Percentage of overlap between chunks to maintain context"
            )

    # Summary generation controls
    st.divider()

    # Check if book already has a summary
    existing_summary = get_summary_by_book_id(str(selected_book['_id']), user_id)

    if existing_summary:
        st.success("✅ This book already has a summary!")
        with st.expander("View Existing Summary"):
            st.text_area(
                "Current Summary",
                value=existing_summary["summary_text"],
                height=300,
                disabled=True
            )

        # Option to regenerate
        if st.button("🔄 Regenerate Summary", type="primary"):
            if st.session_state.get("generation_in_progress", False):
                st.warning("A generation is already in progress!")
            else:
                st.session_state["generation_in_progress"] = True
                st.session_state["generation_started"] = True
                st.rerun()

    else:
        # Generate new summary
        if st.button("🚀 Generate Summary", type="primary", disabled=st.session_state.get("generation_in_progress", False)):
            if st.session_state.get("generation_in_progress", False):
                st.warning("A generation is already in progress!")
            else:
                st.session_state["generation_in_progress"] = True
                st.session_state["generation_started"] = True
                st.rerun()

    # Progress monitoring section
    if st.session_state.get("generation_started", False):
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        log_placeholder = st.empty()

        # Simulate progress (in a real app, this would connect to backend progress updates)
        progress_bar = progress_placeholder.progress(0)
        status_text = status_placeholder.text("Starting summarization process...")

        # Log container
        log_container = log_placeholder.container()

        # Simulate the summarization process steps
        for i, step in enumerate([
            "Validating book data",
            "Initializing preprocessing pipeline",
            "Cleaning and normalizing text",
            "Chunking text for processing",
            "Generating chunk summaries",
            "Merging summaries with context",
            "Validating final summary",
            "Saving to database",
            "Finalizing"
        ]):
            # Update progress
            progress = (i + 1) * 10
            progress_bar.progress(min(progress, 95))
            status_text.text(f"🔄 {step}...")

            # Add to log
            log_container.write(f"📋 {datetime.now().strftime('%H:%M:%S')} - {step}")

            # Simulate work
            import time
            time.sleep(1)

        # Actual summarization call
        try:
            result = summarize_book(
                str(selected_book['_id']),
                user_id,
                summary_length=summary_length,
                summary_style=summary_style,
                chunk_size=chunk_size,
                overlap_percentage=overlap_percentage
            )

            if result["success"]:
                progress_bar.progress(100)
                status_text.text("✅ Summary generation completed successfully!")

                # Fetch and display the new summary
                new_summary = get_summary_by_book_id(str(selected_book['_id']), user_id)

                if new_summary:
                    st.success("🎉 Summary generated successfully!")
                    st.balloons()

                    with st.expander("View Generated Summary", expanded=True):
                        st.text_area(
                            "Generated Summary",
                            value=new_summary["summary_text"],
                            height=400,
                            disabled=True
                        )

                    # Summary statistics
                    st.subheader("📊 Summary Statistics")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Characters", len(new_summary["summary_text"]))
                    with col2:
                        st.metric("Words", len(new_summary["summary_text"].split()))
                    with col3:
                        st.metric("Sentences", len(new_summary["summary_text"].split('.')))
                    with col4:
                        st.metric("Chunks Processed", len(new_summary.get("chunk_summaries", [])))

                    # Download options
                    st.subheader("💾 Export Options")
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.download_button(
                            label="Download as TXT",
                            data=new_summary["summary_text"],
                            file_name=f"summary_{selected_book['title']}.txt",
                            mime="text/plain"
                        )

                    with col2:
                        # Convert to JSON format
                        summary_data = {
                            "book_title": selected_book['title'],
                            "author": selected_book.get('author', 'Unknown'),
                            "summary_text": new_summary["summary_text"],
                            "generated_at": datetime.now().isoformat(),
                            "statistics": {
                                "characters": len(new_summary["summary_text"]),
                                "words": len(new_summary["summary_text"].split()),
                                "sentences": len(new_summary["summary_text"].split('.'))
                            }
                        }
                        st.download_button(
                            label="Download as JSON",
                            data=json.dumps(summary_data, indent=2),
                            file_name=f"summary_{selected_book['title']}.json",
                            mime="application/json"
                        )

                    with col3:
                        # Convert to Markdown format
                        markdown_content = f"""# Summary of {selected_book['title']}

**Author:** {selected_book.get('author', 'Unknown')}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

{new_summary['summary_text']}

## Statistics
- Characters: {len(new_summary['summary_text'])}
- Words: {len(new_summary['summary_text'].split())}
- Sentences: {len(new_summary['summary_text'].split('.'))}
"""
                        st.download_button(
                            label="Download as Markdown",
                            data=markdown_content,
                            file_name=f"summary_{selected_book['title']}.md",
                            mime="text/markdown"
                        )

                else:
                    st.error("Failed to retrieve the generated summary")

            else:
                progress_bar.progress(100)
                status_text.text("❌ Summary generation failed")
                st.error(f"Error: {result.get('error', 'Unknown error occurred')}")

        except Exception as e:
            progress_bar.progress(100)
            status_text.text("❌ Summary generation failed")
            st.error(f"An error occurred during summarization: {str(e)}")
            log_container.error(f"Error: {str(e)}")

        # Reset generation state
        st.session_state["generation_in_progress"] = False
        st.session_state["generation_started"] = False

    # Help and tips section
    st.divider()
    with st.expander("❓ Help & Tips"):
        st.markdown("""
        ### How to get the best results:

        **For short documents (articles, chapters):**
        - Use smaller chunk sizes (1000-2000 characters)
        - Choose "concise" or "bullet_points" style
        - Target summary length: 500-1500 characters

        **For long documents (books, reports):**
        - Use larger chunk sizes (3000-5000 characters)
        - Choose "detailed" or "executive" style
        - Target summary length: 2000-5000 characters
        - Increase chunk overlap to 25-30% for better context

        **For technical content:**
        - Use "default" or "detailed" style
        - Consider smaller chunks for precision
        - Review chunk summaries for accuracy

        ### Understanding the process:
        1. **Preprocessing**: Text is cleaned, normalized, and prepared
        2. **Chunking**: Large text is divided into manageable chunks
        3. **Summarization**: Each chunk is summarized individually
        4. **Merging**: Chunk summaries are intelligently combined
        5. **Validation**: Final summary is checked for quality
        """)

    # Recent activity section
    st.divider()
    st.subheader("📅 Recent Summarization Activity")

    # Show recent books and their summary status
    recent_books = books[-5:]  # Show last 5 books
    if recent_books:
        for book in reversed(recent_books):
            summary = get_summary_by_book_id(str(book['_id']), user_id)
            status_icon = "✅" if summary else "❌"
            status_text = "Summarized" if summary else "Not summarized"

            st.write(f"""
            **{book['title']}**
            {status_icon} {status_text} | {book['status']} | Uploaded: {book['uploaded_at'].strftime('%Y-%m-%d')}
            """)
    else:
        st.info("No recent summarization activity")

# Helper function to check if user has the generate_summary function
def has_generate_summary():
    return True

# Main entry point
def main():
    if has_generate_summary():
        generate_summary_page()
    else:
        st.error("Summary generation functionality not available")

if __name__ == "__main__":
    main()
