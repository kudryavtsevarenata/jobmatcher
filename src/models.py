from pydantic import BaseModel, Field
from typing import List

class Candidate(BaseModel):
    desired_position: str
    hard_skills: List[str]
    years_experience: float
    salary_expectation: int | None = None

class Vacancy(BaseModel):
    title: str
    company: str
    salary: str = "N/A"
    url: str

class MatchResult(BaseModel):
    title: str
    company: str
    salary: str
    match_percent: int = Field(..., ge=0, le=100)
    reason: str
    url: str
