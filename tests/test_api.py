"""
Simple beginner-friendly tests for the AI Document Information Extractor.

These tests do NOT call the real OpenAI API.
"""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from api import app
from extractor import ExtractedInfo, calculate_quality, extract_from_text


client = TestClient(app)


def test_health_endpoint():
    """
    Checks that GET /health returns a simple OK response.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_calculate_quality_high():
    """
    Checks that finding many fields results in High quality.
    """
    data = ExtractedInfo(
        name="John Doe",
        email="john@example.com",
        phone="+1 555 123 4567",
        address="123 Main Street",
        date="12 March 1995",
        organization="ABC Corporation",
        additional_information=None,
    )
    result = calculate_quality(data)
    assert result["fields_found"] == 6
    assert result["fields_total"] == 7
    assert result["quality"] == "High"


def test_extract_from_text_with_mocked_openai():
    """
    Checks structured extraction behavior using a fake OpenAI response.

    This teaches students how the extractor turns model output into
    our fixed schema + quality fields.
    """
    fake_parsed = ExtractedInfo(
        name="John Doe",
        email="john@example.com",
        phone=None,
        address=None,
        date=None,
        organization="ABC Corporation",
        additional_information=None,
    )

    fake_completion = MagicMock()
    fake_completion.choices = [MagicMock()]
    fake_completion.choices[0].message.parsed = fake_parsed

    fake_client = MagicMock()
    fake_client.chat.completions.parse.return_value = fake_completion

    sample_text = (
        "John Doe\n"
        "Email: john@example.com\n"
        "Company: ABC Corporation"
    )

    with patch("extractor.get_openai_client", return_value=fake_client):
        result = extract_from_text(sample_text)

    assert result["data"]["name"] == "John Doe"
    assert result["data"]["email"] == "john@example.com"
    assert result["data"]["organization"] == "ABC Corporation"
    assert result["data"]["phone"] is None
    assert result["fields_found"] == 3
    assert result["fields_total"] == 7
    assert result["quality"] == "Medium"


def test_extract_endpoint_rejects_empty_input():
    """
    Checks that /extract returns an error when no text and no file are sent.
    """
    response = client.post("/extract", data={})
    assert response.status_code == 400
