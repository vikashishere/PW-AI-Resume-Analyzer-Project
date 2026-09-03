"""
FastAPI backend for the AI Document Information Extractor.

Endpoints:
    GET  /health  -> simple health check
    POST /extract -> extract structured information from text or a file
"""

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from document_utils import prepare_file_content
from extractor import extract_from_text, extract_from_image


app = FastAPI(
    title="AI Document Information Extractor",
    description="Extracts structured information from text, PDFs, Word docs, and images.",
    version="1.0.0",
)

# Allow the Streamlit frontend (and local tools) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExtractionResponse(BaseModel):
    """
    Response returned by the /extract endpoint.
    """

    data: dict
    fields_found: int
    fields_total: int
    quality: str


@app.get("/health")
def health_check():
    """
    Simple health check used by students and later by Docker / cloud platforms.

    Input:
        None

    Output:
        {"status": "ok"}
    """
    # return {"status": "ok"}
    return {"status": "ok", "version": "v2"}


@app.post("/extract", response_model=ExtractionResponse)
async def extract_information(
    text: Optional[str] = Form(default=None),
    file: Optional[UploadFile] = File(default=None),
):
    """
    Extracts structured information from pasted text OR an uploaded file.

    How to call it:
        - Send form field "text" for pasted text, OR
        - Send form field "file" for PDF / DOCX / image upload.

    Input:
        text -> optional pasted text
        file -> optional uploaded file

    Output:
        ExtractionResponse with data, quality, and fields_found.
    """
    try:
        # Case 1: user uploaded a file
        if file is not None and file.filename:
            file_bytes = await file.read()
            if not file_bytes:
                raise HTTPException(status_code=400, detail="Uploaded file is empty.")

            prepared = prepare_file_content(file.filename, file_bytes)

            if prepared["input_type"] == "image":
                result = extract_from_image(
                    prepared["content"],
                    prepared["media_type"],
                )
            else:
                result = extract_from_text(prepared["content"])

            return result

        # Case 2: user pasted text
        if text is not None and text.strip():
            result = extract_from_text(text)
            return result

        raise HTTPException(
            status_code=400,
            detail="Please provide either non-empty text or an uploaded file.",
        )

    except HTTPException:
        raise
    except ValueError as error:
        # User mistakes: empty text, bad file type, corrupt PDF, missing API key, etc.
        raise HTTPException(status_code=400, detail=str(error)) from error
    except RuntimeError as error:
        # OpenAI / unexpected response problems
        raise HTTPException(status_code=502, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected server error: {error}",
        ) from error
