from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, date
import uuid

class ScheduleItem(BaseModel):
    task_id: uuid.UUID
    title: str
    course: str
    allocated_hours: float
    priority: float
    due_date: datetime
    task_type: str

class DailySchedule(BaseModel):
    date: date
    items: List[ScheduleItem]
    total_allocated_hours: float
    available_hours: float

class WeeklySchedule(BaseModel):
    week_start: date
    week_end: date
    daily_schedules: Dict[str, DailySchedule]
    total_tasks_scheduled: int
    total_hours_allocated: float

class ScheduleRequest(BaseModel):
    available_hours: float
    start_date: Optional[date] = None

class WeeklyScheduleRequest(BaseModel):
    daily_hours: Dict[str, float]  # {"monday": 3.0, "tuesday": 2.5, ...}
    start_date: Optional[date] = None

class ScheduleGenerationResponse(BaseModel):
    success: bool
    message: str
    schedule: Optional[DailySchedule] = None