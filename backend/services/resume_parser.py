"""
Extract text from PDF and DOCX files
"""

import io
import fitz  
from docx import Document


def parse_pdf(file_bytes: bytes) -> str:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()


def parse_docx(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    text = "\n".join([para.text for para in doc.paragraphs])
    return text.strip()


def parse_resume(file_bytes: bytes, file_type: str) -> str:
    if file_type.endswith(".pdf"):
        return parse_pdf(file_bytes)
    elif file_type.endswith(".docx"):
        return parse_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {file_type}. Use PDF or DOCX.")