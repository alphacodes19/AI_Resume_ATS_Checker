ATS Resume Scorer

A web-based resume analysis tool that checks a resume for ATS-related issues, extracts important information from it, compares it with a job description, and gives practical suggestions for improvement.

The application is built with Streamlit, FastAPI, spaCy, Sentence Transformers, Groq, and Supabase. The current Streamlit deployment runs the analysis pipeline directly inside the Streamlit process, so a separate FastAPI server is not required for the normal hosted setup.

What it does

The project has two analysis modes:

1. General ATS Score

Upload a resume and get an overall score based on:

Resume structure and formatting

Keywords and skills

Content quality

Skill validation through projects/experience

ATS compatibility

The result also includes detected strengths, issues, detailed feedback, and suggestions.

2. Job Description Comparison

Upload a resume and provide a job description. The application additionally calculates:

Job-description keyword match

Semantic similarity between the resume and JD

Matched keywords

Missing keywords

Potential skills gaps

The JD can currently be entered by pasting text or by uploading a .txt file.

Main Features

PDF, DOC, and DOCX resume upload

Maximum resume file size of 5 MB

Resume text extraction

LLM-based resume parsing using Groq

Automatic extraction of:

Contact information

Professional summary

Skills

Experience

Education

Certifications

Projects

Action verbs

ATS keywords

Weighted ATS-style scoring

Skill validation against projects and work experience

Fuzzy keyword matching

Semantic similarity using Sentence Transformers

Job-description comparison

Missing keyword and skill-gap detection

Detailed improvement recommendations

User authentication through Supabase

Email/password sign-up and sign-in

Google OAuth

Analysis history

Delete previous analyses

PDF report generation

Text summary export

Streamlit interface

FastAPI backend/API for standalone backend usage

Docker configuration for backend deployment

Tech Stack

Area

Technology

Frontend

Streamlit

Backend/API

FastAPI

Resume parsing

pdfplumber, PyPDF2, python-docx

LLM parsing

Groq API

LLM model

llama-3.3-70b-versatile

NLP

spaCy

Embeddings

Sentence Transformers

Default embedding model

all-MiniLM-L6-v2

Keyword matching

RapidFuzz + custom matching

Authentication

Supabase Auth

Database

Supabase/PostgreSQL

PDF generation

WeasyPrint

Configuration

.env / Streamlit Secrets

Containerization

Docker

How the Analysis Works

At a high level, the pipeline is:

Resume PDF / DOC / DOCX
          |
          v
   Text Extraction
          |
          v
     Groq Parser
          |
          v
Structured Resume Data
          |
          +----------------------+
          |                      |
          v                      v
   ATS Score Engine       Skill Validation
          |                      |
          +----------+-----------+
                     |
                     v
              Feedback Engine
                     |
                     v
              Final Analysis
                     |
          +----------+----------+
          |                     |
          v                     v
     Streamlit UI         PDF / TXT Export

When a job description is supplied:

Resume
   |
   +--------------------+
   |                    |
   v                    v
Resume Keywords     Resume Embedding
   |                    |
   |                    |
JD Keywords        JD Embedding
   |                    |
   +---------+----------+
             |
             v
     Keyword + Semantic
        JD Comparison
             |
             v
   Match % / Missing Keywords
        / Skills Gap

ATS Score

The overall score is normalized to 100 points.

The main score components are:

Component

Maximum

Formatting

20

Keywords

25

Content

25

Skill Validation

15

ATS Compatibility

15

Total

100

The implementation combines the component percentages with the following overall weighting:

Skills/keyword performance: 40%

Content: 30%

Formatting: 15%

ATS compatibility: 15%

Additional bonuses or penalties can be applied by the scoring logic. For example, the current implementation can reward strong skill validation and penalize large gaps in JD keywords.

Important

The score is a project-specific heuristic score. It is not an official score produced by a particular company's ATS.

Different ATS platforms use different parsing and ranking systems, so the score should be treated as an analysis and improvement signal rather than a guarantee that a resume will pass a real recruitment system.

Skill Validation

The application does more than simply count the skills listed in a resume.

For every extracted skill, it checks whether that skill can be supported by:

A project description

Work/experience information

It first checks for a direct text match. If a direct match is not found, the application uses sentence embeddings and cosine similarity to look for semantic evidence.

The result separates skills into:

Validated skills
Unvalidated skills

For validated skills, the application also shows the project or experience section that supports the skill.

Job Description Matching

The JD comparison uses two signals:

Keyword matching

Resume terms are compared with JD terms using fuzzy matching.

The current implementation uses an 80-point fuzzy matching threshold.

Semantic similarity

The resume and JD are converted into embeddings using:

all-MiniLM-L6-v2

Cosine similarity is then calculated between the two representations.

The current JD match calculation uses:

60% keyword overlap
40% semantic similarity

This is useful because a resume does not always use exactly the same wording as a job description.

Project Structure

AI_Resume_ATS_Checker/
│
├── backend/
│   ├── api/
│   │   ├── auth.py
│   │   └── routes.py
│   │
│   ├── core/
│   │   └── config.py
│   │
│   ├── database/
│   │   └── supabase_db.py
│   │
│   ├── models/
│   │   └── schemas.py
│   │
│   ├── services/
│   │   ├── ats_scorer.py
│   │   ├── feedback_engine.py
│   │   ├── groq_parser.py
│   │   ├── jd_matcher.py
│   │   ├── pdf_export.py
│   │   ├── recommendation_engine.py
│   │   ├── report_generator.py
│   │   ├── resume_analyzer.py
│   │   └── resume_parser.py
│   │
│   ├── templates/
│   │   ├── action_items.html
│   │   ├── jd_comparison.html
│   │   ├── quick_actions.html
│   │   └── summary.html
│   │
│   ├── utils/
│   │   ├── file_utils.py
│   │   └── matching.py
│   │
│   └── main.py
│
├── frontend/
│   ├── components/
│   │   ├── action_items.py
│   │   ├── dashboard.py
│   │   ├── detailed_feedback.py
│   │   ├── jd_comparison.py
│   │   ├── recommendations.py
│   │   ├── score_display.py
│   │   ├── skill_validation.py
│   │   └── strengths_issues.py
│   │
│   ├── services/
│   │   ├── api_client.py
│   │   ├── local_backend.py
│   │   └── supabase_client.py
│   │
│   ├── views/
│   │   ├── history.py
│   │   ├── landing.py
│   │   ├── resources.py
│   │   └── scorer.py
│   │
│   ├── assets/
│   │   ├── style.css
│   │   └── styles.css
│   │
│   └── streamlit_app.py
│
├── jupyter notebooks/
│   ├── 01_EDA_and_DATA_prep.ipynb
│   ├── 02_BERT_EMBEDDINGS.ipynb
│   └── 03_BERT_FINETUNE.ipynb
│
├── packages.txt
├── requirements.txt
├── supabase_schema.sql
├── Dockerfile
└── README.md

Local Setup

1. Clone the repository

git clone https://github.com/alphacodes19/ai_resume_ats_checker.git
cd ai_resume_ats_checker

If your repository URL is different, use your repository's URL instead.

2. Create a virtual environment

Windows

python -m venv .venv
.venv\Scripts\activate

Linux/macOS

python3 -m venv .venv
source .venv/bin/activate

3. Install Python dependencies

pip install --upgrade pip
pip install -r requirements.txt

The requirements include the spaCy model directly, so you normally do not need to run:

python -m spacy download ...

separately.

4. Install system dependencies

WeasyPrint and python-magic require Linux system libraries.

For Debian/Ubuntu, install:

sudo apt update
sudo apt install -y \
    libcairo2 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf-xlib-2.0-0 \
    libffi-dev \
    libmagic1

For Streamlit Community Cloud, these packages are listed in:

packages.txt

The package name libgdk-pixbuf2.0-0 should not be used with the current Debian environment used by the deployment; the repository uses:

libgdk-pixbuf-xlib-2.0-0

Environment Variables

Create a .env file in the project root for local development:

GROQ_API_KEY=your_groq_api_key

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key
SUPABASE_ANON_KEY=your_anon_key

SUPABASE_JWT_SECRET=your_jwt_secret

What each variable is used for

Variable

Purpose

GROQ_API_KEY

Resume and JD parsing through Groq

SUPABASE_URL

Supabase project URL

SUPABASE_KEY

Backend database access

SUPABASE_ANON_KEY

Frontend Supabase authentication

SUPABASE_JWT_SECRET

JWT verification when using HS256 tokens

Do not commit real API keys, service-role keys, JWT secrets, or passwords to Git.

Supabase Setup

The project uses Supabase for authentication and storing analysis history.

1. Create a Supabase project

Create a project in Supabase and copy:

Project URL

Anonymous/public key

Service-role key

JWT secret if your project uses HS256 token verification

2. Create the analyses table

Open the Supabase SQL editor and run:

create table if not exists analyses (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  filename text,
  ats_score numeric,
  keyword_match numeric,
  missing_keywords jsonb default '[]'::jsonb,
  created_at timestamptz default now(),
  analysis_result jsonb
);

alter table analyses enable row level security;

The application stores the complete analysis result in analysis_result so that previous reports can be reconstructed later.

3. Configure authentication

The application supports:

Email/password authentication

Google OAuth

For Google OAuth, configure the Google provider inside Supabase and set the redirect URL to your deployed Streamlit application's URL.

For local development, the default redirect is:

http://localhost:8501

Running the Streamlit Application

From the project root:

streamlit run frontend/streamlit_app.py

The application normally starts at:

http://localhost:8501

Sign in or create an account first. Resume analysis and history are tied to the signed-in Supabase user.

How the Streamlit Deployment Works

The project originally contains a FastAPI backend, but the current Streamlit frontend uses the backend service layer directly.

The important part is:

Streamlit
   |
   v
frontend/services/local_backend.py
   |
   v
backend/services/*
   |
   +--> spaCy
   +--> Sentence Transformers
   +--> Groq
   +--> Supabase

This avoids running a second HTTP service just for the analysis pipeline.

The file:

frontend/services/api_client.py

keeps a backend-like interface for the frontend, while internally forwarding calls to:

frontend/services/local_backend.py

This was done mainly to keep deployment simpler and reduce the memory overhead of hosting a separate FastAPI process.

Streamlit Cloud Configuration

The repository includes:

frontend/.streamlit/secrets.toml.example

Use it as a template for Streamlit Cloud secrets.

A typical configuration is:

[env]
GROQ_API_KEY = "gsk_..."
SUPABASE_URL = "https://YOURPROJECT.supabase.co"
SUPABASE_KEY = "your-service-role-key"
SUPABASE_ANON_KEY = "your-anon-key"

[supabase]
url = "https://YOURPROJECT.supabase.co"
anon_key = "your-anon-key"
redirect_url = "https://YOUR-APP.streamlit.app"

Do not commit the real secrets.toml.

FastAPI Backend

The project also contains a standalone FastAPI application.

Run it locally with:

uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

The API will be available at:

http://localhost:8000

Interactive API documentation:

http://localhost:8000/docs

ReDoc:

http://localhost:8000/redoc

API Endpoints

Method

Endpoint

Purpose

GET

/

API information

GET

/api/v1/health

Check model/API status

POST

/api/v1/analyze-resume

Analyze a resume

GET

/api/v1/history

Get the signed-in user's analyses

DELETE

/api/v1/history/{analysis_id}

Delete an analysis

POST

/api/v1/generate-pdf

Generate a PDF report

GET

/api/v1/history/{analysis_id}/pdf

Generate PDF for a saved analysis

Protected endpoints expect a Supabase access token in:

Authorization: Bearer <access_token>

Docker

A Dockerfile is included for running the FastAPI backend.

Build the image:

docker build -t ats-resume-scorer .

Run it:

docker run --env-file .env -p 8000:7860 ats-resume-scorer

The container starts:

uvicorn backend.main:app

on port 7860.

The normal Streamlit deployment does not require this Docker backend because the current frontend uses local_backend.py and runs the analysis pipeline in-process.

Resume File Requirements

Supported resume formats:

.pdf
.doc
.docx

Maximum file size:

5 MB

The parser extracts text from the uploaded document before sending it to the analysis pipeline.

A resume with selectable text generally gives more reliable extraction than a scanned image-only PDF.

Job Description Requirements

The current Streamlit interface supports:

Option 1 — Paste text

Paste the complete job description into the text area.

Option 2 — Upload a text file

Upload:

.txt

PDF and DOCX job-description uploads are not currently enabled in the Streamlit UI. If the JD is stored as a PDF or DOCX, extract/copy its text first.

PDF Reports

After an analysis, the application can generate a PDF report using:

WeasyPrint

The report is assembled from HTML templates in:

backend/templates/

The generated report can include the analysis summary, JD comparison, and recommended actions.

A plain-text summary can also be downloaded from the scorer page.

Authentication and History

Supabase handles user authentication.

After signing in, the application stores the user's Supabase user ID in the Streamlit session.

When an analysis is completed, the result is saved to the analyses table.

History contains information such as:

Resume filename

ATS score

Keyword match

Date

Component scores

JD comparison

Full analysis result

Users can open previous analyses and delete individual history entries.

Machine Learning / NLP Components

spaCy

The project uses:

en_core_web_sm

for NLP tasks such as entity extraction and job-description skill analysis.

Sentence Transformers

The default embedding model is:

all-MiniLM-L6-v2

It is used for semantic similarity and skill validation.

The model can be changed through:

SENTENCE_TRANSFORMER_MODEL=your-model-name

Groq

Groq is used to turn extracted resume/JD text into structured information.

The current parser uses:

llama-3.3-70b-versatile

The resume parser asks the model to return structured JSON containing fields such as skills, experience, projects, education, certifications, action verbs, and keywords.

Notebooks

The repository also contains notebooks used during the project's experimentation/data work:

jupyter notebooks/
├── 01_EDA_and_DATA_prep.ipynb
├── 02_BERT_EMBEDDINGS.ipynb
└── 03_BERT_FINETUNE.ipynb

These are separate from the production scoring pipeline. The current application primarily uses the rule-based scoring logic, Groq parsing, spaCy, and Sentence Transformers.

Limitations

There are a few things worth knowing before using the project in production:

The ATS score is heuristic. It should not be interpreted as an official ATS score.

Different ATS systems behave differently. A high score here does not guarantee selection by a real ATS.

JD file support is currently limited to .txt uploads or pasted text.

Scanned/image-only resumes may not extract cleanly.

The application depends on the Groq API for structured resume/JD parsing.

The Sentence Transformer model is loaded into memory when analysis starts, so the first analysis can take longer.

PDF generation depends on the required system libraries for WeasyPrint.

The FastAPI backend and the Streamlit in-process backend are two deployment paths; the normal Streamlit setup does not need both running simultaneously.

Troubleshooting

GROQ_API_KEY environment variable not set

Make sure the key exists in your .env file:

GROQ_API_KEY=your_key

For Streamlit Cloud, add it to the app's Secrets.

WeasyPrint import/library errors

Install the Linux packages listed earlier:

sudo apt install -y \
    libcairo2 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf-xlib-2.0-0 \
    libffi-dev

On Streamlit Cloud, check packages.txt.

libgdk-pixbuf2.0-0 has no installation candidate

Use:

libgdk-pixbuf-xlib-2.0-0

instead of:

libgdk-pixbuf2.0-0

in the current Debian-based Streamlit environment.

Supabase authentication errors

Check:

SUPABASE_URL

SUPABASE_ANON_KEY

Supabase Auth configuration

Google OAuth provider configuration

Redirect URL

Streamlit secrets

For local Google OAuth, make sure the local callback URL is allowed by the Supabase project.

Analysis is slow on the first run

The application loads:

spaCy

Sentence Transformers

when the analysis service starts.

The Streamlit implementation uses st.cache_resource so the models can be reused between reruns instead of being loaded from scratch every time.

Security Notes

Never commit the following to Git:

.env
secrets.toml
GROQ_API_KEY
SUPABASE_SERVICE_ROLE_KEY
SUPABASE_KEY
SUPABASE_JWT_SECRET

The service-role key has elevated database privileges and should only be used in trusted server-side code.

For production deployment, also review:

Supabase RLS policies

API authentication

CORS origins

file upload limits

logging

secret management

Development Notes

The project is separated into three main layers:

frontend/
    Streamlit UI and user interaction

backend/services/
    Resume parsing, scoring, matching and reporting

backend/api/
    FastAPI routes and authentication

Most scoring changes should be made in:

backend/services/ats_scorer.py

JD matching logic is primarily in:

backend/services/jd_matcher.py

LLM-based extraction is handled in:

backend/services/groq_parser.py

The overall analysis pipeline is coordinated by:

backend/services/resume_analyzer.py

Possible Future Improvements

Some natural next steps for the project are:

Support PDF/DOCX job-description uploads

Improve scanned PDF handling with OCR

Add configurable ATS scoring profiles

Add industry/job-role specific scoring

Improve grammar checking instead of using the current fallback result

Add stronger resume section detection

Improve semantic JD matching

Add more detailed achievement/metric detection

Add resume version comparison

Add side-by-side resume/JD highlighting

Add exportable improvement checklist

Add automated tests for the scoring pipeline

Add background processing for larger models/files

Add more granular Supabase RLS policies

Add monitoring and structured application logs

Why this project?

Resume screening is often the first filter in a hiring process. The goal of this project is not to reproduce one particular ATS, but to give a candidate a practical way to inspect their resume before submitting it.

Instead of returning only a single number, the application tries to answer:

What is already working?

Which skills are actually supported by the resume?

Which keywords are missing from a target JD?

Where is the resume weak?

What can be changed?

That makes the score more useful as a resume-improvement tool rather than just a pass/fail checker.

License

Add the project's license here if/when one is selected.

Author

Sambodh Gupta

GitHub: https://github.com/alphacodes19

LinkedIn: https://www.linkedin.com/in/sambodh-gupta-2aa946284
