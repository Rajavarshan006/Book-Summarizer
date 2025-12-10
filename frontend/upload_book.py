import streamlit as st
import pdfplumber
from docx import Document
from backend.book_repository import create_book
from backend.session import get_current_user

###temporary
from utils.text_extractor import (
    extract_text_from_txt,
    extract_text_from_pdf,
    extract_text_from_docx
)
###temporary
# 10 MB in bytes
MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = ["txt", "pdf", "docx"]

ext = None
def format_size(bytes_value: int) -> str:
    """Return human readable size like 1.2 MB."""
    if bytes_value < 1024:
        return f"{bytes_value} B"
    kb = bytes_value / 1024
    if kb < 1024:
        return f"{kb:.1f} KB"
    mb = kb / 1024
    return f"{mb:.2f} MB"


def is_file_corrupted(uploaded_file) -> tuple[bool, str | None]:
    """
    Try a basic read to detect obvious corruption.
    Returns (ok, error_message).
    """
    try:
        # Read a small chunk and reset file pointer
        _ = uploaded_file.read(4096)
        uploaded_file.seek(0)
        return True, None
    except Exception as e:
        return False, str(e)


def upload_book_page():
    st.title("Upload Book for Summarization")
    st.write("Supported formats: .txt, .pdf, .docx. Maximum size 10 MB")

    uploaded_file = st.file_uploader(
        "Choose a book file",
        type=ALLOWED_EXTENSIONS,
        help="Maximum file size: 10MB",
    )

    # Only show metadata fields after a file is chosen
    if uploaded_file is not None:
        file_size = uploaded_file.size
        file_name = uploaded_file.name

        # Extract extension
        if "." in file_name:
            ext = file_name.rsplit(".", 1)[1].lower()
        else:
            ext = ""

        # 1. Validate extension
        if ext not in ALLOWED_EXTENSIONS:
            st.error("Unsupported file type. Only .txt, .pdf, .docx are allowed.")
            return

        # 2. Validate size
        if file_size > MAX_FILE_SIZE:
            st.error(
                f"File is too large. Size is {format_size(file_size)}. "
                "Maximum allowed size is 10 MB."
            )
            return

        # 3. Basic corruption check
        ok, error_message = is_file_corrupted(uploaded_file)
        if not ok:
            st.error(f"File appears to be corrupted or unreadable. Details: {error_message}")
            return

        # 4. Metadata inputs
        default_title = file_name.rsplit(".", 1)[0]
        st.subheader("Book details")
        title = st.text_input("Book title", value=default_title)
        author = st.text_input("Author (optional)")
        chapter = st.text_input("Chapter or section (optional)")

        # Simple confirmation section for now
        st.success("File passed all validations.")
        st.write(f"**Filename:** {file_name}")
        st.write(f"**Size:** {format_size(file_size)}")
        st.write(f"**Detected type:** {ext.upper()}")

    if st.button("Upload and process"):
    
    # ---------- TEXT EXTRACTION ----------
        with st.spinner("Extracting text ..."):
            if ext == "txt":
                raw_text = extract_text_from_txt(uploaded_file)

            elif ext == "pdf":
                raw_text = extract_text_from_pdf(uploaded_file)

            elif ext == "docx":
                raw_text = extract_text_from_docx(uploaded_file)

    # ---------- POST EXTRACTION VALIDATION ----------
        if not raw_text or not raw_text.strip():
            st.warning(
                "No text could be extracted. "
                "This file may be scanned or unreadable."
            )
            return

    # ---------- DATABASE INSERT ----------
        user = get_current_user()

        book_id = create_book(
            user_id=user["user_id"],
            title=title,
            author=author if author else None,
            chapter=chapter if chapter else None,
            file_type=ext,
            raw_text=raw_text
        )

    # ---------- SUCCESS UI ----------
        st.success("Text extracted and saved successfully")
        st.write("Extracted text length:", len(raw_text))
        st.write(f"Book ID: {book_id}")


    #st.success("File passed all validations.")
    st.subheader("File Preview")
    ext = None

    if uploaded_file is not None:
        file_name = uploaded_file.name
        ext = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else None

        if ext not in ALLOWED_EXTENSIONS:
            st.error("Unsupported file type")
            return

    # TXT PREVIEW
    if ext == "txt":
        try:
            text_content = uploaded_file.read().decode("utf-8", errors="ignore")
            uploaded_file.seek(0)

            preview_text = text_content[:500]
            st.text(preview_text)

            if len(text_content) > 500:
                st.caption("Showing first 500 characters")
        except Exception:
            st.warning("Unable to preview this TXT file")

    # PDF PREVIEW
    elif ext == "pdf":
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                page_count = len(pdf.pages)

            uploaded_file.seek(0)
            st.write(f"Number of pages: {page_count}")
        except Exception:
            st.warning("Unable to read PDF preview")

    # DOCX PREVIEW
    elif ext == "docx":
        try:
            document = Document(uploaded_file)
            paragraph_count = len(document.paragraphs)

            uploaded_file.seek(0)
            st.write(f"Paragraphs detected: {paragraph_count}")
        except Exception:
            st.warning("Unable to read DOCX preview")

