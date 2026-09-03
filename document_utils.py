"""
Helpers for reading text from PDFs and Word documents,
and for preparing uploaded images for the OpenAI API.
"""

import base64
from pathlib import Path

from pypdf import PdfReader
from docx import Document


# File types we accept from the user
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".png", ".jpg", ".jpeg"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def is_supported_file(filename: str) -> bool:
    """
    Checks whether a file name has a supported extension.

    Input:
        filename -> name of the uploaded file (for example: "resume.pdf")

    Output:
        True if the file type is supported, otherwise False.

    Example:
        is_supported_file("notes.docx") -> True
        is_supported_file("notes.txt")  -> False
    """
    extension = Path(filename).suffix.lower()
    return extension in SUPPORTED_EXTENSIONS


def is_image_file(filename: str) -> bool:
    """
    Checks whether a file name points to an image.

    Input:
        filename -> name of the uploaded file

    Output:
        True for .png / .jpg / .jpeg, otherwise False.
    """
    extension = Path(filename).suffix.lower()
    return extension in IMAGE_EXTENSIONS


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Reads a normal text-based PDF and combines its pages into one string.

    Input:
        file_bytes -> raw bytes of the uploaded PDF

    Output:
        A single string containing the extracted text.

    Example:
        "Name: John Doe\\nEmail: john@example.com"

    Raises:
        ValueError if the PDF cannot be read.
    """
    import io

    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        pages = []
        for page in reader.pages:
            # page.extract_text() can return None for some pages
            text = page.extract_text() or ""
            pages.append(text)
        combined = "\n".join(pages).strip()
        if not combined:
            raise ValueError(
                "No text found in this PDF. "
                "Scanned/image-only PDFs are not supported (no OCR)."
            )
        return combined
    except ValueError:
        raise
    except Exception as error:
        raise ValueError(f"Could not read this PDF file. Details: {error}") from error


def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Reads a Word (.docx) file and returns all paragraph text as one string.

    Input:
        file_bytes -> raw bytes of the uploaded DOCX

    Output:
        A single string containing the extracted text.

    Example:
        "John Doe\\nEmail: john@example.com"

    Raises:
        ValueError if the DOCX cannot be read.
    """
    import io

    try:
        document = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
        combined = "\n".join(paragraphs).strip()
        if not combined:
            raise ValueError("No text found in this Word document.")
        return combined
    except ValueError:
        raise
    except Exception as error:
        raise ValueError(f"Could not read this Word document. Details: {error}") from error


def encode_image_to_base64(file_bytes: bytes) -> str:
    """
    Converts image bytes into a base64 string for the OpenAI vision API.

    Input:
        file_bytes -> raw bytes of the uploaded image

    Output:
        A base64-encoded string.

    Example:
        "iVBORw0KGgoAAAANSUhEUg..."
    """
    return base64.b64encode(file_bytes).decode("utf-8")


def get_image_media_type(filename: str) -> str:
    """
    Returns the correct MIME type for an image file name.

    Input:
        filename -> name of the image file

    Output:
        A MIME type string such as "image/png" or "image/jpeg".
    """
    extension = Path(filename).suffix.lower()
    if extension == ".png":
        return "image/png"
    # .jpg and .jpeg both use image/jpeg
    return "image/jpeg"


def prepare_file_content(filename: str, file_bytes: bytes) -> dict:
    """
    Prepares an uploaded file so the extractor can process it.

    For PDF/DOCX: extracts text.
    For images: keeps base64 data for the multimodal model.

    Input:
        filename   -> original file name
        file_bytes -> raw uploaded bytes

    Output:
        A dictionary with keys:
            - input_type: "text" or "image"
            - content: extracted text OR base64 image data
            - media_type: only set for images

    Example:
        {"input_type": "text", "content": "John Doe\\nEmail: ..."}
    """
    if not is_supported_file(filename):
        raise ValueError(
            "Unsupported file type. Please upload a PDF, DOCX, PNG, JPG, or JPEG file."
        )

    extension = Path(filename).suffix.lower()

    if extension == ".pdf":
        text = extract_text_from_pdf(file_bytes)
        return {"input_type": "text", "content": text, "media_type": None}

    if extension == ".docx":
        text = extract_text_from_docx(file_bytes)
        return {"input_type": "text", "content": text, "media_type": None}

    # Image path: send the image itself to the multimodal model
    return {
        "input_type": "image",
        "content": encode_image_to_base64(file_bytes),
        "media_type": get_image_media_type(filename),
    }
