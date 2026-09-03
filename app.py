"""
Streamlit frontend for the AI Document Information Extractor.

This UI talks to the FastAPI backend. It does NOT call OpenAI directly.
That keeps the architecture simple:

    Streamlit  ->  FastAPI  ->  Extraction Logic  ->  OpenAI
"""

import json
import requests
import streamlit as st

import config


# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Document Information Extractor",
    page_icon="📄",
    layout="centered",
)

st.title("AI Document Information Extractor")
st.write(
    "Extract structured information from text, PDFs, Word documents and images."
)

# Friendly labels for displaying fields in the UI
FIELD_LABELS = {
    "name": "Name",
    "email": "Email",
    "phone": "Phone",
    "address": "Address",
    "date": "Date",
    "organization": "Organization",
    "additional_information": "Additional Information",
}


def call_extract_api(text: str = None, uploaded_file=None) -> dict:
    """
    Sends text or a file to the FastAPI /extract endpoint.

    Input:
        text          -> optional pasted text
        uploaded_file -> optional Streamlit UploadedFile object

    Output:
        A dictionary with extraction results from the API.

    Raises:
        RuntimeError with a beginner-friendly message if the request fails.
    """
    url = f"{config.API_BASE_URL.rstrip('/')}/extract"

    try:
        if uploaded_file is not None:
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type or "application/octet-stream",
                )
            }
            response = requests.post(url, files=files, timeout=120)
        else:
            # FastAPI expects form data for the /extract endpoint
            response = requests.post(url, data={"text": text or ""}, timeout=120)
    except requests.exceptions.ConnectionError as error:
        raise RuntimeError(
            "Could not connect to the FastAPI backend. "
            "Make sure you started it with: "
            "uvicorn api:app --reload --port 8000"
        ) from error
    except requests.exceptions.Timeout as error:
        raise RuntimeError(
            "The extraction request timed out. Please try again."
        ) from error

    if response.status_code != 200:
        # Prefer the API's "detail" message when available
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        raise RuntimeError(f"Extraction failed: {detail}")

    return response.json()


def display_results(result: dict) -> None:
    """
    Shows extracted fields, quality indicator, and a Download JSON button.

    Input:
        result -> dictionary returned by the FastAPI /extract endpoint

    Output:
        None (writes directly to the Streamlit page)
    """
    st.subheader("Extracted Information")

    data = result.get("data", {})
    for key, label in FIELD_LABELS.items():
        value = data.get(key)
        # Show a dash when the value is null / missing
        display_value = value if value is not None else "—"
        left, right = st.columns([1, 3])
        left.write(f"**{label}**")
        right.write(display_value)

    quality = result.get("quality", "Low")
    found = result.get("fields_found", 0)
    total = result.get("fields_total", 7)

    st.write("")
    st.write(f"**Extraction Quality:** {quality}")
    st.write(f"**Fields Found:** {found} / {total}")

    # Let the user download the structured result as a .json file
    json_bytes = json.dumps(result, indent=2).encode("utf-8")
    st.download_button(
        label="Download JSON",
        data=json_bytes,
        file_name="extracted_information.json",
        mime="application/json",
    )


# ---------------------------------------------------------------------------
# Main UI
# ---------------------------------------------------------------------------
st.subheader("Input Method")
input_method = st.radio(
    "Choose how you want to provide information:",
    options=["Paste Text", "Upload File"],
    horizontal=True,
    label_visibility="collapsed",
)

uploaded_file = None
text_input = ""

if input_method == "Paste Text":
    text_input = st.text_area(
        "Paste your text here",
        height=200,
        placeholder=(
            "John Doe\n"
            "Email: john@example.com\n"
            "Phone: +1 555 123 4567\n"
            "Address: 123 Main Street, New York\n"
            "Date of Birth: 12 March 1995\n"
            "Company: ABC Corporation"
        ),
    )
else:
    uploaded_file = st.file_uploader(
        "Upload a PDF, Word document, or image",
        type=["pdf", "docx", "png", "jpg", "jpeg"],
    )

st.write("")
extract_clicked = st.button("Extract Information", type="primary")

if extract_clicked:
    # Basic validation before calling the API
    if input_method == "Paste Text" and not text_input.strip():
        st.error("Please paste some text before extracting.")
    elif input_method == "Upload File" and uploaded_file is None:
        st.error("Please upload a file before extracting.")
    else:
        with st.spinner("Extracting information with OpenAI..."):
            try:
                if input_method == "Paste Text":
                    result = call_extract_api(text=text_input)
                else:
                    result = call_extract_api(uploaded_file=uploaded_file)

                # Keep the latest result in session state for re-runs
                st.session_state["last_result"] = result
            except RuntimeError as error:
                st.error(str(error))
            except Exception as error:
                st.error(f"Something went wrong: {error}")

# Show previous / latest results if available
if "last_result" in st.session_state:
    st.divider()
    display_results(st.session_state["last_result"])
