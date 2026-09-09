# Job Skill Extraction API (Day 19)

A FastAPI application that takes a pasted **job description**, extracts the
skills mentioned in it, normalizes them, and groups them into categories.

Includes **user registration and login (JWT auth)** — the skill-extraction
endpoint is protected, so a user must log in to use it.

## Architecture

```
User
  ↓
Web Interface / API (FastAPI - app.py)
  ↓
Preprocessing (lowercase, normalize separators)
  ↓
Skill Extraction Model (model/skill_extractor.py — alias matching against data/skills_db.json)
  ↓
Skill Normalization (aliases → canonical skill name, e.g. "powerbi" → "Power BI")
  ↓
Category Mapping (Programming, Database, BI, Analytics, Cloud, DevOps, Data Science, Tools, Big Data)
  ↓
Final Skills Deliverable (JSON response)
```

## Project structure

```
skillsapp/
├── app.py                  # FastAPI app: auth routes + /analyze endpoint
├── model/
│   ├── __init__.py
│   └── skill_extractor.py  # preprocessing + extraction + normalization + category mapping
├── data/
│   └── skills_db.json      # skill -> {category, aliases} knowledge base
├── utils/
│   ├── __init__.py
│   ├── database.py         # SQLAlchemy engine/session + User model (SQLite)
│   ├── auth.py              # password hashing + JWT create/verify
│   └── schemas.py          # Pydantic request/response models
├── requirements.txt
└── README.md
```

## Setup

```bash
cd skillsapp
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app:app --reload
```

Open the interactive docs at: http://127.0.0.1:8000/docs

## Usage

### 1. Register

`POST /register`

```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "secret123"
}
```

### 2. Login

`POST /login` (form-encoded, not JSON — this is what the Swagger UI
"Authorize" button sends automatically)

```
username=alice
password=secret123
```

Response:

```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

Use this token as a **Bearer token** for all subsequent requests
(in Swagger UI: click "Authorize" and paste the token).

### 3. Analyze a job description

`POST /analyze`

```json
{
  "text": "Looking for Data Analyst with SQL, Python, Power BI and Excel experience."
}
```

Response:

```json
{
  "detected_skills": ["Excel", "Power BI", "Python", "SQL"],
  "categories": {
    "Programming": ["Python"],
    "Database": ["SQL"],
    "BI": ["Power BI"],
    "Analytics": ["Excel"]
  },
  "total_skills_found": 4
}
```

## Notes / next steps

- The skill knowledge base lives in `data/skills_db.json` — add more skills
  or aliases there without touching any code.
- `model/skill_extractor.py` is intentionally decoupled from the API layer,
  so it can later be swapped for a spaCy/NER or embedding-based matcher
  while keeping the same `extract_skills()` contract.
- SQLite (`data/app.db`) is used for simplicity; swap the
  `SQLALCHEMY_DATABASE_URL` in `utils/database.py` for Postgres/MySQL in
  production.
- Set a real `SECRET_KEY` environment variable before deploying
  (`utils/auth.py` currently falls back to a placeholder).
- A Streamlit front-end can call this same API (`/register`, `/login`,
  `/analyze`) for a simple UI — CORS is already enabled in `app.py`.
