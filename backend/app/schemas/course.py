from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CourseBase(BaseModel):
    name: str
    code: str
    semester: str
    year: int

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    semester: Optional[str] = None
    year: Optional[int] = None

class CourseInDBBase(CourseBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Course(CourseInDBBase):
    pass

class CourseWithTasks(Course):
    tasks: list = []