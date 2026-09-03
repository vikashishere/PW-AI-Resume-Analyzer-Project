"""
Uses OpenAI to extract structured personal / business information
from text or images.

The schema is fixed inside this file. Users do not define it.
"""

from typing import Optional

from openai import OpenAI
from pydantic import BaseModel, Field

import config


# ---------------------------------------------------------------------------
# Fixed schema — keep this small so students can understand it quickly.
# Missing values must be null (None in Python).
# ---------------------------------------------------------------------------
class ExtractedInfo(BaseModel):
    """
    Structured information extracted from a document or text.

    Every field is optional. If the model cannot find a value,
    it should leave that field as null.
    """

    name: Optional[str] = Field(
        default=None,
        description="Full name of a person, if present.",
    )
    email: Optional[str] = Field(
        default=None,
        description="Email address, if present.",
    )
    phone: Optional[str] = Field(
        default=None,
        description="Phone number, if present.",
    )
    address: Optional[str] = Field(
        default=None,
        description="Postal or street address, if present.",
    )
    date: Optional[str] = Field(
        default=None,
        description="An important date such as date of birth, if present.",
    )
    organization: Optional[str] = Field(
        default=None,
        description="Company or organization name, if present.",
    )
    additional_information: Optional[str] = Field(
        default=None,
        description="Any other useful details that do not fit the fields above.",
    )


# Field names used when we count how many values were found
SCHEMA_FIELDS = [
    "name",
    "email",
    "phone",
    "address",
    "date",
    "organization",
    "additional_information",
]

EXTRACTION_PROMPT = """
You extract structured information from the user's input.

Rules:
1. Extract ONLY information that is clearly present in the input.
2. Never invent, guess, or complete missing information.
3. If a field is not available, return null for that field.
4. Keep extracted values faithful to the source (do not rewrite heavily).
5. Follow the provided schema exactly.
6. Do not add explanations outside the structured response.
""".strip()


def get_openai_client() -> OpenAI:
    """
    Creates an OpenAI client using the API key from the environment.

    Input:
        None (reads OPENAI_API_KEY from config)

    Output:
        An OpenAI client instance.

    Raises:
        ValueError if the API key is missing.
    """
    if not config.OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY is missing. "
            "Copy .env.example to .env and add your OpenAI API key."
        )
    return OpenAI(api_key=config.OPENAI_API_KEY)


def calculate_quality(data: ExtractedInfo) -> dict:
    """
    Calculates a simple extraction quality score.

    We count how many of the predefined fields are not null.
    This is intentionally simple for teaching purposes.

    Input:
        data -> ExtractedInfo object returned by the model

    Output:
        A dictionary with:
            - fields_found: number of non-null fields
            - fields_total: total number of schema fields
            - quality: "High", "Medium", or "Low"

    Example:
        {"fields_found": 5, "fields_total": 7, "quality": "High"}
    """
    values = data.model_dump()
    found = sum(1 for field in SCHEMA_FIELDS if values.get(field) is not None)
    total = len(SCHEMA_FIELDS)

    # Simple thresholds students can understand
    if found >= 5:
        quality = "High"
    elif found >= 3:
        quality = "Medium"
    else:
        quality = "Low"

    return {
        "fields_found": found,
        "fields_total": total,
        "quality": quality,
    }


def extract_from_text(text: str) -> dict:
    """
    Sends plain text to OpenAI and returns structured extraction results.

    Input:
        text -> raw text pasted by the user or extracted from PDF/DOCX

    Output:
        A dictionary with:
            - data: the extracted fields
            - fields_found, fields_total, quality

    Example:
        {
          "data": {"name": "John Doe", "email": "john@example.com", ...},
          "fields_found": 6,
          "fields_total": 7,
          "quality": "High"
        }
    """
    cleaned = (text or "").strip()
    if not cleaned:
        raise ValueError("Text input is empty. Please paste some text first.")

    client = get_openai_client()

    try:
        # parse() asks OpenAI to return data matching our Pydantic schema
        completion = client.chat.completions.parse(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": EXTRACTION_PROMPT},
                {"role": "user", "content": cleaned},
            ],
            response_format=ExtractedInfo,
        )
    except Exception as error:
        raise RuntimeError(f"OpenAI API request failed: {error}") from error

    extracted = completion.choices[0].message.parsed
    if extracted is None:
        raise RuntimeError(
            "Unexpected extraction response from OpenAI. "
            "The model did not return structured data."
        )

    quality_info = calculate_quality(extracted)
    return {
        "data": extracted.model_dump(),
        **quality_info,
    }


def extract_from_image(base64_image: str, media_type: str) -> dict:
    """
    Sends an image to an OpenAI multimodal model for structured extraction.

    Input:
        base64_image -> image encoded as a base64 string
        media_type   -> MIME type such as "image/png"

    Output:
        Same dictionary shape as extract_from_text().
    """
    if not base64_image:
        raise ValueError("Image data is empty. Please upload a valid image.")

    client = get_openai_client()
    image_url = f"data:{media_type};base64,{base64_image}"

    try:
        completion = client.chat.completions.parse(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": EXTRACTION_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Extract structured information from this image. "
                                "Follow the schema and return null for missing fields."
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url},
                        },
                    ],
                },
            ],
            response_format=ExtractedInfo,
        )
    except Exception as error:
        raise RuntimeError(f"OpenAI API request failed: {error}") from error

    extracted = completion.choices[0].message.parsed
    if extracted is None:
        raise RuntimeError(
            "Unexpected extraction response from OpenAI. "
            "The model did not return structured data."
        )

    quality_info = calculate_quality(extracted)
    return {
        "data": extracted.model_dump(),
        **quality_info,
    }
