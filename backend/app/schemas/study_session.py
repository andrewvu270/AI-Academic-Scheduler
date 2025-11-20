from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class StudySessionBase(BaseModel):
    task_id: str
    minutes_spent: int
    date: datetime
    notes: Optional[str] = None

class StudySessionCreate(StudySessionBase):
    pass

class StudySessionUpdate(BaseModel):
    minutes_spent: Optional[int] = None
    notes: Optional[str] = None

class StudySessionInDBBase(StudySessionBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class StudySession(StudySessionInDBBase):
    task_title: Optional[str] = None
    course_code: Optional[str] = None

class StudySessionStats(BaseModel):
    total_sessions: int
    total_minutes: int
    average_session_length: float
    tasks_completed: int