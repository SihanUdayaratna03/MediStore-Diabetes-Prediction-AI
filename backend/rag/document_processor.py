"""
document_processor.py
======================
Extracts text from uploaded medical PDFs and images.

Supports two extraction strategies:
  1. Native PDF text extraction via PyMuPDF (fitz)
  2. Image OCR via Gemini Vision API (primary) with pytesseract fallback
     - Used for: image-only PDFs, scanned documents, and uploaded images

Returns a list of PageContent objects, each containing:
  - page_number: int (1-indexed)
  - text: str
  - has_images: bool
  - image_description: Optional[str]  # from Gemini Vision if images found
"""

import io
import os
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, field

import fitz                          # PyMuPDF
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Use Gemini Flash for fast multimodal processing
_vision_model = genai.GenerativeModel("gemini-1.5-flash")


@dataclass
class PageContent:
    page_number: int
    text: str
    has_images: bool = False
    image_description: Optional[str] = None
    word_count: int = 0

    def __post_init__(self):
        self.word_count = len(self.text.split())

    @property
    def combined_text(self) -> str:
        """Returns text + image descriptions for embedding."""
        parts = [self.text]
        if self.image_description:
            parts.append(f"\n[Image Content on Page {self.page_number}]: {self.image_description}")
        return "\n".join(parts).strip()


@dataclass
class DocumentContent:
    filename: str
    total_pages: int
    pages: List[PageContent] = field(default_factory=list)
    doc_type: str = "pdf"   # 'pdf' | 'image'
    extraction_method: str = "native"  # 'native' | 'gemini_vision' | 'tesseract'

    @property
    def full_text(self) -> str:
        return "\n\n".join(p.combined_text for p in self.pages)

    @property
    def preview_text(self) -> str:
        """First ~500 chars for UI display."""
        return self.full_text[:500] + ("..." if len(self.full_text) > 500 else "")


def extract_from_pdf(file_path: Path) -> DocumentContent:
    """
    Extract text from a PDF file.
    
    Strategy:
    1. Use PyMuPDF to extract native text from each page.
    2. If a page has embedded images AND minimal text (<50 words),
       pass the page as an image to Gemini Vision for OCR/description.
    """
    doc = fitz.open(str(file_path))
    pages = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        native_text = page.get_text("text").strip()
        image_list = page.get_images(full=True)
        has_images = len(image_list) > 0

        # If very little native text but images exist → use Gemini Vision
        image_description = None
        if has_images and len(native_text.split()) < 50:
            image_description = _describe_page_with_gemini(page, page_num + 1)

        pages.append(PageContent(
            page_number=page_num + 1,
            text=native_text,
            has_images=has_images,
            image_description=image_description,
        ))

    doc.close()
    
    # Determine extraction method
    methods_used = set()
    for p in pages:
        if p.image_description:
            methods_used.add("gemini_vision")
        if p.text:
            methods_used.add("native")
    
    return DocumentContent(
        filename=file_path.name,
        total_pages=len(pages),
        pages=pages,
        doc_type="pdf",
        extraction_method="+".join(sorted(methods_used)) or "native",
    )


def extract_from_image(file_path: Path) -> DocumentContent:
    """
    Extract medical information from a standalone image file.
    Uses Gemini Vision for comprehensive medical image understanding.
    
    Handles: JPG, PNG, WEBP, TIFF, BMP
    """
    with open(file_path, "rb") as f:
        image_bytes = f.read()

    mime_type = _get_image_mime_type(file_path.suffix.lower())
    
    prompt = """You are analyzing a medical document or doctor's report image.
    
Please extract and describe ALL of the following that you can identify:
1. All text present in the image (transcribe it exactly)
2. Any medical values, lab results, or measurements
3. Diagnoses or medical conditions mentioned
4. Medications listed (with dosages if visible)
5. Doctor's notes or recommendations
6. Dates and patient identifiers (if any)
7. Charts, graphs, or visual data (describe what they show)

Format your response as a structured, comprehensive text extraction.
Preserve all numerical values exactly as they appear.
"""
    
    try:
        image_part = {"mime_type": mime_type, "data": image_bytes}
        response = _vision_model.generate_content([prompt, image_part])
        extracted_text = response.text
        method = "gemini_vision"
    except Exception as e:
        # Fallback to pytesseract
        try:
            import pytesseract
            img = Image.open(file_path)
            extracted_text = pytesseract.image_to_string(img)
            method = "tesseract"
        except Exception:
            extracted_text = f"[Image could not be processed: {str(e)}]"
            method = "failed"

    return DocumentContent(
        filename=file_path.name,
        total_pages=1,
        pages=[PageContent(
            page_number=1,
            text=extracted_text,
            has_images=True,
            image_description=extracted_text,
        )],
        doc_type="image",
        extraction_method=method,
    )


def process_upload(file_path: Path, filename: str) -> DocumentContent:
    """
    Main entry point. Auto-detects file type and extracts content.
    
    Args:
        file_path: Path to the saved file on disk
        filename:  Original filename from the upload
    
    Returns:
        DocumentContent with all pages extracted
    """
    suffix = file_path.suffix.lower()
    
    if suffix == ".pdf":
        return extract_from_pdf(file_path)
    elif suffix in (".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".bmp"):
        return extract_from_image(file_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}. "
                         f"Supported: PDF, JPG, PNG, WEBP, TIFF, BMP")


def _describe_page_with_gemini(page: fitz.Page, page_num: int) -> Optional[str]:
    """Render a PDF page as image and send to Gemini Vision for OCR/description."""
    try:
        mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better OCR quality
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")
        
        prompt = f"""This is page {page_num} of a medical document (rendered as image because it contains embedded images/charts/handwriting).

Please:
1. Transcribe any text visible on this page
2. Describe any charts, graphs, or visual medical data
3. Note any lab values, vital signs, or medical measurements shown

Return a comprehensive text representation of everything on this page."""

        image_part = {"mime_type": "image/png", "data": img_bytes}
        response = _vision_model.generate_content([prompt, image_part])
        return response.text
    except Exception:
        return None


def _get_image_mime_type(suffix: str) -> str:
    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".tiff": "image/tiff",
        ".tif": "image/tiff",
        ".bmp": "image/bmp",
    }
    return mime_map.get(suffix, "image/jpeg")

