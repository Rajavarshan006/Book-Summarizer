# Intelligent Book Summarization Platform

This project is part of my internship.  
It is a Streamlit-based application that allows users to upload book files, extract text, and generate AI-powered summaries.

---

## Project Setup Instructions

### 1. Clone or open the project folder
Make sure you are inside the main project directory:
C:\Users\ADMIN\Desktop\InternshipProject

### 2. Create & Activate Virtual Environment
python -m venv venv
For Activating ENVIRONMENT -> python -m venv venv


### 3. Install Required Python Libraries
pip install
' ' ' 
streamlit 
transformers 
pdfplumber 
python-docx 
bcrypt 
python-dotenv 
pymongo
'  '  '

### 4. Project Folder Structure

project_root/
│
├── frontend/        # Streamlit UI pages
│
├── backend/         # Core business logic (authentication, text extraction, summarization)
│
├── utils/           # Helper functions (database connection, validators, utilities)
│
├── models/          # AI model integration (Hugging Face summarizer, tokenizer)
│
├── data/            # Uploaded files, temporary storage, cached data
│
├── config/          # Configuration files (.env loading, initialization scripts)
│
├── tests/           # Unit tests and integration tests
│
├── venv/            # Virtual environment (do not edit manually)
│
├── README.md        # Project documentation
│
├── .gitignore       # Files and folders ignored by Git
│
└── .env             # Environment variables (MongoDB URI, secrets)

##  Environment Variables 
Create a ".env" file in the project root and add:
  ## MONGO_URI= 
  "mongodb+srv://BookSummarizerDB:eFR5bBaLoX4InEOQ@booksummarizercluster.1hecn1r.mongodb.net/"
  ## DB_NAME=
  "BookSummarizerDB"


## 5. DataBase Handling
    # -------------------------
    # USER COLLECTION FUNCTIONS
    # -------------------------
      -> create_user(name,email,password_hash,role)
      -> get_user_by_email(email)

    # -------------------------
    # BOOK COLLECTION FUNCTIONS
    # -------------------------
      """
      create_book(user_id,title,author,chapter,file_path)->
        Create a new book entry.
        - user_id: which user uploaded the book
        - file_path: where the file is stored
        - raw_text: will be added after extraction
        - status: tracking processing steps
        """
      update_book_text(book_id,text) ->Updates the raw text of book.

      update_book_status(book_id,status) ->
        """
        Update status of a book.
        Allowed values:
        - uploaded
        - processing
        - text_extracted
        - completed
        - failed
        """
      get_book_by_id(book_id)-> Obtain book through id.
      get_books_by_user(user_id) -> gets the list of books stored in the name of user id.

    # -------------------------
    # SUMMARY COLLECTION FUNCTIONS
    # -------------------------
      create_summary(book_id,user_id,summary_text,summary_length,summary_style,chunk_summaries,created_at=None) ->
      '''
      Fields included:
      - book_id: book reference
      - user_id: who generated the summary
      - summary_text: final combined summary
      - chunk_summaries: list of chunk-level summaries
      - summary_length: short/medium/long
      - summary_style: paragraphs/bullets
      - created_at: timestamp
      '''
      get_summaries_by_user(user_id)->
        Returns the list of summaries created by the user using user_id;
      get_summary_by_id(summary_id)->
        Returns the particular summary using the summary_id.
      













##  Features (Planned)
- User Registration & Login
- Secure authentication with bcrypt
- File upload (TXT, PDF, DOCX)
- Text extraction backend
- AI summarization using Transformers
- User dashboard
- Save and view past summaries


## Status
 Task 1 Completed  
 Task 2 in Completed

## Author
Rajavarshan R R