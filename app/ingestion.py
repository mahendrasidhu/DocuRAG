from pathlib import Path
import pymupdf
from docx import Document

from app.config import DOCUMENTS_DIR


SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx"}


def discover_documents():
    documents_dir = Path(DOCUMENTS_DIR)

    return [
        file for file in documents_dir.iterdir()
        if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS
    ]


def load_document(file):
    if file.suffix.lower() == ".txt":
        return [{
            "page_number":None,
            "content":file.read_text(encoding="utf-8")
            }]
    elif file.suffix.lower() == ".pdf":
        pdf=pymupdf.open(file)
        
        pages=[]
        
        for page_number,page in enumerate(pdf,start=1):
            pages.append({
                "page_number":page_number,
                "content": page.get_text()
            })
        
        return pages
    
    elif file.suffix.lower() == ".docx":
        document=Document(file)
        text="\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )
        return [{
            "page_number":None,
            "content":text
        }]
    
    else:
        raise ValueError(f"Unsupported File type : {file.suffix}")