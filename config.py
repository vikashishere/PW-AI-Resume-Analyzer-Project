"""
Loads settings from the .env file.

Beginners: copy .env.example to .env, then put your OpenAI API key in .env.
"""

import os
from dotenv import load_dotenv

# Load variables from a local .env file (if it exists).
load_dotenv()

# OpenAI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# FastAPI base URL used by the Streamlit frontend
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
