# AI Resume Analyzer

A beginner-friendly GenAI project. Upload a resume, paste a Job Description, and get a
written analysis of how well the two match.

This is Project 2 in the learning path. Project 1 was a CLI chatbot with a single LLM
call. This project adds file handling, a Streamlit user interface, and a **two-step LLM
workflow**.

---

## 1. What are we building?

A single-page web app.

You upload your resume as a PDF or a Word document, paste the Job Description of a role
you are interested in, and click **Analyze Resume**. The app reads your resume, sends it
to OpenAI together with the Job Description, and shows you:

- what your resume already matches well,
- what looks missing or weak,
- what you could change to line up better with the role,
- a short overall summary.

You can then download the whole thing as a Markdown file.

The interesting part is not the app itself, it is the **workflow**. The app does not ask
the LLM one big question. It asks two smaller questions, and the answer to the first one
becomes the input to the second one. That pattern is called **prompt chaining**, and it is
the foundation of almost every real GenAI application.

Everything lives in one file, `app.py`, so you can read the whole program from top to
bottom.

---

## 2. What will I learn?

- **Streamlit basics** — how to build a web page with `st.title`, `st.text_area`,
  `st.button` and `st.markdown`, without writing any HTML, CSS or JavaScript.
- **File upload** — how `st.file_uploader` gives you an uploaded file in Python, and how
  to restrict which file types are allowed.
- **PDF and DOCX text extraction** — how to pull plain text out of a PDF with `pypdf` and
  out of a Word document with `python-docx`.
- **Calling an LLM** — how to use the official OpenAI Python SDK with an API key that is
  loaded from a `.env` file instead of being typed into your code.
- **Structured output** — how to ask a model to reply with JSON instead of prose, so that
  your Python code can actually work with the answer.
- **A multi-step LLM workflow** — how to split one hard task into two easier steps.
- **Prompt chaining** — how to feed the output of one LLM call into the next one.
- **Generating a downloadable report** — how to build a Markdown string in Python and
  hand it to the user with `st.download_button`.

---

## 3. Project workflow

```text
Resume + JD
    ↓
Text Extraction
    ↓
LLM Call #1
    ↓
Structured Data
    ↓
LLM Call #2
    ↓
Final Report
```

### Step 1 — Text extraction

`extract_resume_text()` looks at the uploaded file name. If it ends in `.pdf` it uses
`pypdf` to read every page; if it ends in `.docx` it uses `python-docx` to read every
paragraph. Either way the function returns one plain Python string.

An LLM cannot read a PDF file directly, so this step has nothing to do with AI. It is
ordinary file handling, and it is the step beginners usually underestimate.

### Step 2 — LLM call #1: structure the information

`analyze_resume()` sends the resume text and the Job Description to OpenAI and asks for
**JSON only**, with a fixed set of keys:

```json
{
  "candidate_skills": [],
  "candidate_experience": [],
  "candidate_qualifications": [],
  "required_skills": [],
  "preferred_skills": [],
  "matching_skills": [],
  "missing_skills": [],
  "gaps": []
}
```

This is the key idea of the whole project:

> The first LLM call converts unstructured resume and JD text into structured information.

Two long, messy documents go in. A small, tidy Python dictionary comes out. `json.loads()`
turns the model's reply into that dictionary.

The prompt also tells the model not to invent anything. It may only use skills, employers
and qualifications that actually appear in the text it was given.

### Step 3 — LLM call #2: write the report

`generate_final_report()` does **not** see the resume again. It only sees the JSON from
Step 2. Its job is to turn that structured data into friendly, readable feedback, again
returned as JSON with five keys: `strengths`, `gaps`, `missing_or_weak_skills`,
`improvement_suggestions` and `overall_summary`.

Why two calls instead of one? Because each call has a single, narrow job. Step 2 only has
to find facts; Step 3 only has to explain them. Small, focused prompts are easier to write,
easier to debug and give steadier results than one giant prompt that tries to do everything.

### Step 4 — Display

`main()` loops over the five sections, shows each one with `st.markdown()`, and offers a
download button. The JSON from Step 2 is never shown to the user — it is an intermediate
result that exists only to feed Step 3.

---

## 4. Project structure

```text
ai-resume-analyzer/
│
├── app.py             The entire application: UI, text extraction, both LLM calls
├── .env.example       Template for your secrets. Copy it to .env and fill it in
├── .gitignore         Tells git to never commit .env, the virtual env or __pycache__/
├── requirements.txt   The five Python packages this project needs
├── README.md          This file
└── data/              Two sample resumes to try the app with
```

- **`app.py`** — there is deliberately no `utils.py`, `llm.py` or `prompts.py`. Five short
  functions sit in one file so that you can follow the whole program in one read:
  `extract_resume_text()`, `analyze_resume()`, `generate_final_report()`,
  `create_downloadable_report()` and `main()`.
- **`.env.example`** — a safe file you can commit, because it holds no real key.
- **`.gitignore`** — the line that matters most is `.env`. It stops you from accidentally
  publishing your API key.
- **`requirements.txt`** — `streamlit`, `openai`, `python-dotenv`, `pypdf`, `python-docx`.
- **`README.md`** — the instructions you are reading.
- **`data/`** — two made-up resumes so you can try the app before using your own:
  `sample_resume_data_analyst.pdf` (tests the PDF path) and
  `sample_resume_backend_developer.docx` (tests the Word path). The app never reads this
  folder on its own; you upload these files through the browser like any other resume.

---

## 5. Installation

Open a terminal in the `ai-resume-analyzer` folder.

Create a virtual environment, which is a private copy of Python just for this project:

```bash
python -m venv .venv
```

Activate it.

**Windows (PowerShell):**

```powershell
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**

```cmd
.venv\Scripts\activate.bat
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

You will know it worked because your prompt now starts with `(.venv)`.

Then install the packages:

```bash
pip install -r requirements.txt
```

---

## 6. Environment setup

Your API key is a password. It does not belong in your code.

Copy the template to a real `.env` file.

**Windows (PowerShell):**

```powershell
copy .env.example .env
```

**macOS / Linux:**

```bash
cp .env.example .env
```

Open `.env` and fill it in:

```text
OPENAI_API_KEY=sk-your-real-key-here
OPENAI_MODEL=gpt-4o-mini
```

- `OPENAI_API_KEY` — create one at <https://platform.openai.com/api-keys>.
- `OPENAI_MODEL` — which model to use. `gpt-4o-mini` is a good, cheap default. If you
  leave this blank, `app.py` falls back to `gpt-4o-mini` on its own.

`load_dotenv()` in `app.py` reads this file at startup, and `os.getenv()` picks the two
values out of it. `.env` is listed in `.gitignore`, so it will never be committed.

---

## 7. Running the application

```bash
streamlit run app.py
```

Streamlit prints a local URL, usually <http://localhost:8501>, and normally opens it in
your browser for you. Press `Ctrl+C` in the terminal to stop the app.

---

## 8. How to use the application

1. **Upload your resume.** Click the upload box and pick a `.pdf` or `.docx` file. If you
   just want to see the app work, use one of the sample resumes in `data/`.
2. **Paste the Job Description.** Copy the full job posting into the text area.
3. **Click Analyze Resume.** A spinner appears while the two LLM calls run. Expect a few
   seconds.
4. **Review the results.** Five sections appear: Strengths, Gaps, Missing or Weak Skills,
   Improvement Suggestions and Overall Summary.
5. **Download the report.** Click **Download Report** to save `resume_analysis.md`. You
   can open that file in any text editor, or in VS Code for a nicely formatted preview.

---

## 9. Example workflow

Say your resume mentions Python, SQL, pandas and two years at a retail analytics company,
and the Job Description asks for Python, SQL, Airflow and AWS.

**LLM call #1** might return something like:

```json
{
  "candidate_skills": ["Python", "SQL", "pandas"],
  "candidate_experience": ["2 years as a data analyst in retail analytics"],
  "candidate_qualifications": ["B.Sc. in Statistics"],
  "required_skills": ["Python", "SQL", "Airflow", "AWS"],
  "preferred_skills": ["dbt"],
  "matching_skills": ["Python", "SQL"],
  "missing_skills": ["Airflow", "AWS"],
  "gaps": ["No cloud or data pipeline work described in the resume"]
}
```

**LLM call #2** then turns that into readable feedback:

> **Strengths**
> - Python and SQL are both required by the role and both appear in your resume.
> - Two years of hands-on retail analytics experience is directly relevant.
>
> **Missing or Weak Skills**
> - Airflow was not identified in the provided resume.
> - AWS was not identified in the provided resume.
>
> **Improvement Suggestions**
> - If you have scheduled or automated any data jobs, describe that work using the
>   tooling names, as the role asks for Airflow.

Notice the wording: *"AWS was not identified in the provided resume"*, not *"the candidate
does not know AWS"*. The app only knows what is written in the file you uploaded. You may
well know AWS and simply not have mentioned it. That distinction is a deliberate part of
the prompt, and it is a habit worth carrying into every GenAI project you build.

---

## 10. Common errors

**"No OpenAI API key found."**
You have not created `.env`, or the key line is empty. Copy `.env.example` to `.env`, paste
your key, and restart the app. Streamlit only reads `.env` when it starts up.

**"Please upload your resume." / "Please paste the Job Description."**
One of the two inputs is empty. The app checks both before calling OpenAI, so you never
pay for an incomplete request.

**Unsupported file**
`st.file_uploader(..., type=["pdf", "docx"])` rejects anything else before your code runs.
Note that old `.doc` files are not supported — open them in Word and save as `.docx`.

**"No text could be read from this file."**
The PDF is almost certainly a scan or a photo, so the page contains an image of text
rather than text itself. `pypdf` has nothing to extract. This project does not do OCR, so
export a text-based PDF from Word or Google Docs instead.

**"The analysis failed: ..."**
The message after the colon tells you which problem it is. Common causes: an invalid or
revoked key, no credit on the account, a model name in `.env` your account cannot access,
or no internet connection.

**`streamlit: command not found`**
Your virtual environment is not active, or `pip install -r requirements.txt` has not been
run yet.

---

## 11. What this project does NOT cover

This project is deliberately kept small. It does not use:

- **RAG** (retrieval-augmented generation)
- **Embeddings**
- **Vector databases**
- **Agents**
- **Tool calling / function calling**
- **Fine-tuning**
- **Multi-agent systems**
- **Persistent memory or a database**

The resume and the Job Description are simply pasted into the prompt, and the flow is
fixed: two LLM calls, always in the same order. Nothing is stored. Close the browser tab
and the analysis is gone.

That is the right choice for now. A fixed workflow is predictable, cheap to run and easy to
debug, and a very large share of real production GenAI features are exactly this: a couple
of well-written prompts chained together. The topics above solve problems this project does
not have yet, and they come later in the learning path.
