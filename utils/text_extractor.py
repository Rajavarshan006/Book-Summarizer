import pdfplumber
from docx import Document


def extract_text_from_txt(uploaded_file: object) -> str:
   
    uploaded_file.seek(0)
    text = uploaded_file.read().decode("utf-8", errors="ignore")
    return text


def extract_text_from_pdf(uploaded_file: object) -> str:
    
    uploaded_file.seek(0)
    extracted_text = []

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                extracted_text.append(page_text)

    return "\n".join(extracted_text)


def extract_text_from_docx(uploaded_file: object) -> str:
    uploaded_file.seek(0)
    doc = Document(uploaded_file)

    extracted_text = [para.text for para in doc.paragraphs if para.text]
    return "\n".join(extracted_text)
