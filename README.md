# AI Document Information Extractor

A beginner-friendly GenAI application that extracts structured information from pasted text, PDF files, Word documents (`.docx`), and images (`.png`, `.jpg`, `.jpeg`).

The application uses **OpenAI** for information extraction and demonstrates the journey from local GenAI development to **Docker, Azure deployment, and GitHub Actions CI/CD**.

> **Important:** The Streamlit UI runs locally. The FastAPI backend is the component deployed to Azure Container Apps.

---

## 1. What This Project Does

The application allows a user to provide document information in two ways:

1. Enter or paste text
2. Upload a document/image

The application then:

1. Sends the input from Streamlit to FastAPI.
2. FastAPI prepares the document content.
3. The extraction logic creates a prompt based on a fixed internal schema.
4. FastAPI sends the request to the OpenAI API.
5. OpenAI extracts the requested information.
6. FastAPI returns structured JSON.
7. Streamlit displays the extracted information and quality summary.

The user does **not** define the extraction schema. The schema is predefined inside the application.

---

## 2. High-Level Architecture

```text
                         LOCAL MACHINE
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   User                                                       │
│    │                                                         │
│    │ Enter text OR upload PDF/DOCX/Image                    │
│    ▼                                                         │
│  Streamlit UI                                                │
│  localhost:8501                                              │
│    │                                                         │
│    │ HTTP request                                            │
│    ▼                                                         │
│  FastAPI Backend                                              │
│  localhost:8000                                              │
│    │                                                         │
│    │ Process document + build prompt                         │
│    ▼                                                         │
│  OpenAI API                                                   │
│    │                                                         │
│    │ Structured information                                  │
│    ▼                                                         │
│  FastAPI                                                     │
│    │                                                         │
│    │ JSON response                                           │
│    ▼                                                         │
│  Streamlit UI                                                 │
│    │                                                         │
│    ▼                                                         │
│  User sees extracted information                              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. Local Application Components

### Streamlit

The Streamlit application is the user-facing UI.

It allows users to:

- Enter/paste text
- Upload supported documents
- Start extraction
- View extracted fields
- View extraction quality
- Download the resulting JSON

Local URL:

```text
http://localhost:8501
```

### FastAPI

FastAPI acts as the backend API.

Important endpoints:

```text
GET  /health
GET  /docs
POST /extract
```

Local URL:

```text
http://localhost:8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

### OpenAI

OpenAI is used by the backend to understand the input and extract the requested information according to the predefined schema.

---

## 4. Project Structure

```text
.
├── app.py                     # Streamlit frontend
├── api.py                     # FastAPI backend
├── extractor.py               # OpenAI structured extraction
├── document_utils.py          # PDF / DOCX / image helpers
├── config.py                  # Environment/settings configuration
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile
├── .dockerignore
├── README.md
├── .github/
│   └── workflows/
│       └── azure-deploy.yml   # GitHub Actions CI/CD workflow
├── data/
└── tests/
    └── test_api.py
```

---

## 5. Local Setup

### Step 1 — Clone or Copy the Repository

```bash
git clone <repository-url>
cd <project-folder>
```

### Step 2 — Create a Virtual Environment

#### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 6. Configure Environment Variables

Copy `.env.example` to `.env`.

### Windows

```powershell
copy .env.example .env
```

### macOS / Linux

```bash
cp .env.example .env
```

Configure:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
API_BASE_URL=http://127.0.0.1:8000
```

> Never commit the real `.env` file to GitHub. The project `.gitignore` should exclude it.

---

## 7. Run the Application Locally

The project uses two processes during local development.

### Start FastAPI

Open Terminal 1:

```bash
uvicorn api:app --reload --port 8000
```

Test:

```text
http://localhost:8000/health
http://localhost:8000/docs
```

Expected health response:

```json
{"status":"ok"}
```

### Start Streamlit

Open Terminal 2:

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

---

## 8. How to Use the Application

Choose either:

- **Paste Text**
- **Upload File**

Supported files:

- PDF
- DOCX
- PNG
- JPG
- JPEG

Then click:

```text
Extract Information
```

The application sends the request to FastAPI, which processes the input and calls OpenAI.

The extracted information is returned to Streamlit.

### Example Input

```text
John Doe
Email: john@example.com
Phone: +1 555 123 4567
Address: 123 Main Street, New York
Date of Birth: 12 March 1995
Company: ABC Corporation
```

---

## 9. Fixed Extraction Schema

The extraction schema is predefined internally. Users do not create their own schema.

```json
{
  "name": null,
  "email": null,
  "phone": null,
  "address": null,
  "date": null,
  "organization": null,
  "additional_information": null
}
```

Rules:

- If information is present → extract it.
- If information is missing → return `null`.
- Do not invent missing information.

---

## 10. Extraction Quality

The application provides a simple quality indicator:

```text
High   → 5 or more fields
Medium → 3 or 4 fields
Low    → fewer than 3 fields
```

The UI also shows information such as:

```text
Fields Found: 5 / 7
```

---

## 11. Run Tests

From the project root:

```bash
pytest -q
```

The tests cover areas such as:

- `/health` endpoint
- Structured extraction behavior using a mocked OpenAI response

---

## 12. Docker

The Docker image contains the **FastAPI backend**.

The Streamlit application continues to run separately during local development.

### Build

```bash
docker build -t ai-document-extractor .
```

### Run

Make sure `.env` exists and contains a valid OpenAI API key.

```bash
docker run --env-file .env -p 8000:8000 ai-document-extractor
```

Test:

```text
http://localhost:8000/health
http://localhost:8000/docs
```

Streamlit can still be started separately:

```bash
streamlit run app.py
```

> **The Streamlit UI is not deployed to Azure in this project.**

---

# 13. Azure Deployment

The FastAPI backend is deployed to Azure.

```text
Azure Resource Group
        │
        ├── Azure Container Registry
        │
        └── Azure Container Apps
                │
                └── FastAPI : 8000
```

Resources used:

```text
Resource Group:
rg-ai-extractor

Azure Container Registry:
ekaextractoracr

ACR Login Server:
ekaextractoracr.azurecr.io

Azure Container Apps:
eka-container-env

Region:
East US
```

---

## 14. Azure Container Registry

Azure Container Registry stores the Docker images used for deployment.

Repository:

```text
ai-document-extractor
```

CI/CD image tags use the Git commit SHA:

```text
ekaextractoracr.azurecr.io/ai-document-extractor:<commit-sha>
```

---

## 15. Azure Container Apps

The FastAPI Docker container is deployed to:

```text
eka-container-env
```

The application listens on:

```text
Port 8000
```

Ingress accepts traffic from anywhere.

The Container App provides a public HTTPS application URL:

```text
https://<your-container-app-url>
```

API endpoints:

```text
https://<your-container-app-url>/health
https://<your-container-app-url>/docs
https://<your-container-app-url>/extract
```

---

## 16. OpenAI API Key in Azure

For the Azure deployment, configure the OpenAI API key as a Container App environment variable.

Navigation:

```text
Azure Portal
    ↓
Container Apps
    ↓
eka-container-env
    ↓
Application
    ↓
Containers
    ↓
Environment Variables
```

Add:

```text
Name:
OPENAI_API_KEY

Source:
Manual Entry

Value:
<your OpenAI API key>
```

Do not put the actual key into source code, Dockerfile, or GitHub.

---

## 17. Test the Azure API

Open the Azure Container App's Application URL.

Test:

```text
/health
```

Then:

```text
/docs
```

Use Swagger UI to test:

```text
POST /extract
```

Example input:

```text
John Doe
Email: john.doe@example.com
Phone: +1 555-123-4567
Address: 123 Main Street, New York, NY 10001
Date of Birth: January 15, 1995
```

Confirm that the API returns structured information.

---

# 18. GitHub Actions CI/CD

The project uses GitHub Actions to automate deployment.

The deployment flow is:

```text
Developer changes code
        ↓
git push
        ↓
GitHub
        ↓
GitHub Actions
        ↓
Azure Login using OIDC
        ↓
Build Docker Image
        ↓
Push Image to ACR
        ↓
Update Azure Container App
        ↓
New Container App Revision
        ↓
New version becomes live
```

This means Docker build, ACR push, and Azure deployment do not have to be performed manually for every code change.

---

## 19. Azure Managed Identity

A user-assigned managed identity is used by GitHub Actions:

```text
github-actions-identity
```

It has the permissions required for CI/CD.

### ACR Permission

```text
AcrPush
```

Allows GitHub Actions to push Docker images to ACR.

### Container App Permission

```text
Container Apps Contributor
```

Allows GitHub Actions to update the Container App.

---

## 20. GitHub / Azure OIDC

GitHub Actions authenticates to Azure using OpenID Connect (OIDC).

This avoids storing an Azure client secret/password in GitHub.

The federated credential is configured for:

```text
Organization:
vikashishere

Repository:
AI-Doc-Extractor-Azure-CICD

Branch:
main
```

The federated credential uses GitHub's immutable organization and repository identifiers.

---

## 21. GitHub Actions Secrets

The repository contains:

```text
AZURE_CLIENT_ID
AZURE_TENANT_ID
AZURE_SUBSCRIPTION_ID
```

These are configured under:

```text
GitHub Repository
    ↓
Settings
    ↓
Secrets and variables
    ↓
Actions
```

The values are used by the workflow to authenticate to Azure.

---

## 22. GitHub Actions Workflow

The CI/CD workflow is stored at:

```text
.github/workflows/azure-deploy.yml
```

It:

1. Checks out the repository.
2. Logs into Azure using OIDC.
3. Logs into Azure Container Registry.
4. Builds the Docker image.
5. Pushes the image to ACR.
6. Updates Azure Container Apps.

The Docker image is tagged with:

```text
${{ github.sha }}
```

This gives every GitHub commit a unique image version.

---

## 23. Triggering CI/CD

The workflow runs automatically when code is pushed to:

```text
main
```

Example:

```bash
git add .
git commit -m "Update application"
git push origin main
```

Then open:

```text
GitHub Repository
    ↓
Actions
```

The workflow should appear as:

```text
Build and Deploy to Azure
```

A successful run means:

```text
Code
 ↓
GitHub Actions
 ↓
Docker Build
 ↓
ACR Push
 ↓
Azure Container App Update
```

---

## 24. Verify the New Azure Revision

After a successful GitHub Actions run:

```text
Azure Portal
    ↓
Container Apps
    ↓
eka-container-env
    ↓
Application
    ↓
Revisions and replicas
```

A new revision should appear.

Confirm that:

- The new revision is running.
- The revision is healthy.
- Traffic is directed to the new revision.

---

## 25. End-to-End CI/CD Demonstration

A simple code change demonstrates the complete CI/CD process.

For example, change `/health` from:

```json
{"status": "ok"}
```

to:

```json
{"status": "ok", "version": "v1"}
```

Then:

```bash
git add .
git commit -m "Update health endpoint"
git push origin main
```

Observe:

```text
Local Code Change
        ↓
Git Push
        ↓
GitHub
        ↓
GitHub Actions Starts
        ↓
Docker Image Builds
        ↓
Image Pushes to ACR
        ↓
Container App Updates
        ↓
New Revision Created
        ↓
New Revision Receives Traffic
        ↓
/health Shows New Version
```

Finally open:

```text
https://<your-container-app-url>/health
```

The response should contain:

```json
{
  "status": "ok",
  "version": "v1"
}
```

This demonstrates that no manual Docker build, manual ACR push, or manual Azure deployment was required.

---

# 26. Final End-to-End Architecture

```text
                         USER
                           │
                           ▼
                    Streamlit UI
                  localhost:8501
                           │
                           │ HTTP / JSON
                           ▼
                     FastAPI API
                   localhost:8000
                           │
                           ▼
                      OpenAI API
                           │
                           ▼
                  Structured JSON
                           │
                           ▼
                    Streamlit UI


                CI/CD DEPLOYMENT FLOW

Developer
    │
    │ git push
    ▼
GitHub Repository
    │
    ▼
GitHub Actions
    │
    │ OIDC
    ▼
Azure Managed Identity
    │
    ├──────────────────────┐
    ▼                      ▼
Azure Container       Azure Container
Registry              Apps
    │                      │
    │ Docker Image         │ FastAPI :8000
    └─────────────────────►│
                           │
                           ▼
                       OpenAI API
```

---

# 27. Important Architecture Note

The project has two application components.

### Local

```text
Streamlit UI
localhost:8501
```

### Azure

```text
FastAPI API
Port 8000
```

The Streamlit application is **not deployed to Azure** in this project.

During local development:

```text
Streamlit → FastAPI → OpenAI
```

The Azure backend is:

```text
Client → Azure Container Apps / FastAPI → OpenAI
```

---

# 28. What This Project Demonstrates

### Application Development

- Python
- Streamlit
- FastAPI
- REST API concepts
- Environment variables
- API testing
- pytest

### GenAI

- LLM-powered information extraction
- Prompt construction
- Structured output
- Fixed extraction schema
- Multimodal document handling

### Docker

- Dockerfile
- Docker image
- Docker container
- Environment variables inside containers
- Containerized FastAPI application

### Azure

- Resource Groups
- Azure Container Registry
- Azure Container Apps
- Container App revisions
- Managed Identity
- Azure RBAC

### CI/CD

- GitHub Actions
- OIDC authentication
- GitHub Secrets
- Automated Docker builds
- Automated image pushes
- Automated Azure deployment
- Automatic revision creation

---

# 29. Final Learning Outcome

The most important takeaway is:

```text
A developer can make a code change locally,
push the code to GitHub, and have the updated
FastAPI application automatically built,
containerized, pushed to Azure Container Registry,
and deployed to Azure Container Apps.
```

In short:

```text
Code
  ↓
GitHub
  ↓
GitHub Actions
  ↓
Docker Build
  ↓
Azure Container Registry
  ↓
Azure Container Apps
  ↓
Live FastAPI Application
```

---

# 30. Notes and Limitations

- PDF support is for text-based PDFs only; OCR is not included.
- Images are sent to an OpenAI multimodal model.
- A valid OpenAI API key and internet access are required.
- The extraction schema is fixed and cannot be customized by the user.
- The project intentionally keeps the architecture small and beginner-friendly.
- Streamlit is kept local; only the FastAPI backend is deployed to Azure.
