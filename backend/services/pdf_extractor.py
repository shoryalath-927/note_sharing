"""
PDF text extraction using PyMuPDF (local, free, no API needed).
Also extracts page count and basic metadata.
"""
import fitz  # PyMuPDF
from pathlib import Path


def extract_text_from_pdf(pdf_path: str) -> dict:
    """
    Extract text and metadata from a PDF file.
    Returns dict with text, page_count, has_images, word_count.
    """
    path = Path(pdf_path)
    if not path.exists():
        return {"text": "", "page_count": 0, "has_images": False, "word_count": 0}

    doc = fitz.open(pdf_path)
    full_text = []
    has_images = False

    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Extract text
        text = page.get_text("text")
        if text.strip():
            full_text.append(f"[Page {page_num + 1}]\n{text}")
        
        # Check for images/diagrams
        if page.get_images():
            has_images = True

    doc.close()

    combined_text = "\n\n".join(full_text)
    word_count = len(combined_text.split())

    return {
        "text": combined_text,
        "page_count": len(doc) if not doc.is_closed else fitz.open(pdf_path).page_count,
        "has_images": has_images,
        "word_count": word_count,
    }


def get_pdf_page_count(pdf_path: str) -> int:
    try:
        doc = fitz.open(pdf_path)
        count = len(doc)
        doc.close()
        return count
    except Exception:
        return 0
