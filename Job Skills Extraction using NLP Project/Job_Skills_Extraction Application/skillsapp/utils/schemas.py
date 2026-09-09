"""
utils/schemas.py

Pydantic models used for request validation and response shaping.
"""

from typing import Dict, List
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class JobDescriptionRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=5,
        description="Raw job description text pasted by the user.",
        examples=[
            "Looking for Data Analyst with SQL, Python, Power BI and Excel experience."
        ],
    )


class SkillsResponse(BaseModel):
    detected_skills: List[str]
    categories: Dict[str, List[str]]
    total_skills_found: int
