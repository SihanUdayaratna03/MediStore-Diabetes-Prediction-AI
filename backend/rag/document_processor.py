"""
document_processor.py
======================
Handles text extraction from uploaded medical documents.
Supports PDFs (via PyMuPDF) and images (via Gemini Vision OCR).

Returns a DocumentContent dataclass consumed by the chunker and routes.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ── DocumentContent ────────────────────────────────────────────────────────────

@dataclass
class DocumentContent:
    """Structured result from processing an uploaded file."""
    text:               str
    doc_type:           str          # "pdf" | "image"
    total_pages:        int
    preview_text:       str          # first ~300 chars for UI preview
    extraction_method:  str          # "pymupdf" | "gemini-vision" | "fallback"
    page_map:           dict = field(default_factory=dict)  # {page_num: text}


def _extract_pdf(file_path: Path) -> DocumentContent:
    """Extract text from a PDF using PyMuPDF."""
    try:
        import fitz  # PyMuPDF

        doc      = fitz.open(str(file_path))
        pages    = {}
        full_text = ""

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            pages[page_num + 1] = text
            full_text += f"\n--- Page {page_num + 1} ---\n{text}"

        doc.close()

        preview = full_text.strip()[:300]

        return DocumentContent(
            text=full_text,
            doc_type="pdf",
            total_pages=len(pages),
            preview_text=preview,
            extraction_method="pymupdf",
            page_map=pages,
        )

    except ImportError:
        raise ValueError(
            "PyMuPDF is not installed. Run: pip install pymupdf"
        )
    except Exception as e:
        raise ValueError(f"PDF extraction failed: {str(e)}")


def _extract_image(file_path: Path) -> DocumentContent:
    """Extract text from a medical image using Gemini Vision."""
    try:
        import os
        import base64
        import google.generativeai as genai
        from dotenv import load_dotenv

        load_dotenv()
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

        with open(file_path, "rb") as f:
            image_bytes = f.read()

        b64_image = base64.b64encode(image_bytes).decode("utf-8")
        suffix    = file_path.suffix.lower().lstrip(".")
        mime_map  = {"jpg": "image/jpeg", "jpeg": "image/jpeg",
                     "png": "image/png",  "webp": "image/webp",
                     "tiff": "image/tiff", "tif": "image/tiff",
                     "bmp": "image/bmp"}
        mime_type = mime_map.get(suffix, "image/jpeg")

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([
            {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": b64_image,
                }
            },
            (
                "You are a medical document OCR assistant. "
                "Extract ALL text from this medical document image exactly as it appears. "
                "Preserve formatting, headings, values, and units. "
                "If you see tables, preserve their structure. "
                "Include page numbers if visible."
            ),
        ])

        extracted = response.text
        preview   = extracted.strip()[:300]

        return DocumentContent(
            text=extracted,
            doc_type="image",
            total_pages=1,
            preview_text=preview,
            extraction_method="gemini-vision",
            page_map={1: extracted},
        )

    except Exception as e:
        raise ValueError(f"Image OCR failed: {str(e)}")


# ── Public API ─────────────────────────────────────────────────────────────────

def process_upload(file_path: Path, original_filename: str) -> DocumentContent:
    """
    Entry point: detect file type and extract text.

    Args:
        file_path:          Absolute path to the saved upload.
        original_filename:  Original filename (used to detect extension).

    Returns:
        DocumentContent with extracted text and metadata.

    Raises:
        ValueError: for unsupported types or extraction failures.
    """
    suffix = Path(original_filename).suffix.lower()

    if suffix == ".pdf":
        return _extract_pdf(file_path)
    elif suffix in {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".bmp"}:
        return _extract_image(file_path)
    else:
        raise ValueError(
            f"Unsupported file type '{suffix}'. "
            "Supported: .pdf, .jpg, .jpeg, .png, .webp, .tiff, .tif, .bmp"
        )
