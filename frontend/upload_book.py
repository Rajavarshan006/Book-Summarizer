import streamlit as st

# 10 MB in bytes
MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = ["txt", "pdf", "docx"]


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

        if st.button("Upload and process (backend will be added later)"):
            st.info("For now this only confirms front end validation. Backend saving comes in Task 4.")
            # Later we will call a backend function here to:
            #  1. Save file to disk
            #  2. Create a book record in the database
            #  3. Trigger text extraction
