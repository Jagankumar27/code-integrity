from typing import List, Optional
from pydantic import BaseModel
class LoginIn(BaseModel):
    username: str
    password: str
class AnalyzeOne(BaseModel):
    submission_id: int
    compare_with: Optional[List[int]] = None  # default: every other submission
class AnalyzeMany(BaseModel):
    submission_ids: List[int]
