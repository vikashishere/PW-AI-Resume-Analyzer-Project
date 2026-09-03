# Simple beginner-friendly Dockerfile
# This container runs the FastAPI backend only.
#
# Build:
#   docker build -t ai-document-extractor .
#
# Run:
#   docker run --env-file .env -p 8000:8000 ai-document-extractor

FROM python:3.11-slim

# Work inside /app in the container
WORKDIR /app

# Install dependencies first (better Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY config.py .
COPY document_utils.py .
COPY extractor.py .
COPY api.py .

# FastAPI listens on port 8000
EXPOSE 8000

# Start the API server
# --host 0.0.0.0 makes the app reachable from outside the container
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
