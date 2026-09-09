"""
app.py

FastAPI application implementing:

  User -> Web Interface / API -> Preprocessing -> Skill Extraction Model
       -> Skill Normalization -> Category Mapping -> Final Skills Deliverable

Includes JWT-based Register / Login so /analyze is a protected endpoint.

Run with:
    uvicorn app:app --reload
Then open:
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from utils.database import init_db, get_db, User
from utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)
from utils.schemas import UserCreate, UserOut, Token, JobDescriptionRequest, SkillsResponse
from model.skill_extractor import skill_extractor

app = FastAPI(
    title="Job Skill Extraction API",
    description="Paste a job description and get detected skills, normalized "
    "and grouped by category (Programming, Database, BI, Analytics, ...).",
    version="1.0.0",
)

# Allow a Streamlit / frontend client running on a different port to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


# ---------------------------------------------------------------------------
# Auth: Register & Login
# ---------------------------------------------------------------------------

@app.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED, tags=["auth"])
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(User)
        .filter((User.username == user.username) | (User.email == user.email))
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/login", response_model=Token, tags=["auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    OAuth2-compatible login. Send as form data:
        username=<username>&password=<password>
    (This is what the /docs 'Authorize' button and OAuth2PasswordRequestForm expect.)
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me", response_model=UserOut, tags=["auth"])
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


# ---------------------------------------------------------------------------
# Core feature: Skill extraction / categorization
# ---------------------------------------------------------------------------

@app.post("/analyze", response_model=SkillsResponse, tags=["skills"])
def analyze_job_description(
    payload: JobDescriptionRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Protected endpoint. Requires a valid Bearer token from /login.

    Pipeline: Preprocessing -> Skill Extraction -> Normalization -> Category Mapping.
    """
    result = skill_extractor.extract_skills(payload.text)
    return result


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok"}
