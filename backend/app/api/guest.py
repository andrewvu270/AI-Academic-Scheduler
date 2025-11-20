"""Guest mode endpoints for unauthenticated users"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from ..database import get_db
from ..models.guest import GuestSession, GuestTask, GuestCourse

router = APIRouter(prefix="/api/guest", tags=["guest"])

class GuestTaskCreate(BaseModel):
    title: str
    description: str = ""
    task_type: str
    due_date: str
    grade_percentage: float = 0.0
    predicted_hours: float = 4.0
    status: str = "pending"

class GuestTaskResponse(BaseModel):
    id: str
    title: str
    task_type: str
    due_date: str
    grade_percentage: float
    status: str
    priority_score: float
    
    class Config:
        from_attributes = True

class GuestSessionCreate(BaseModel):
    session_id: str

@router.post("/session")
async def create_guest_session(data: GuestSessionCreate, db: Session = Depends(get_db)):
    """Create or get guest session"""
    # Check if session exists
    existing = db.query(GuestSession).filter(
        GuestSession.id == data.session_id
    ).first()
    
    if existing:
        return {"session_id": existing.id, "is_new": False}
    
    # Create new session
    new_session = GuestSession(id=data.session_id)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    return {"session_id": new_session.id, "is_new": True}

@router.post("/tasks/{guest_session_id}")
async def create_guest_task(
    guest_session_id: str,
    task: GuestTaskCreate,
    db: Session = Depends(get_db)
):
    """Create task for guest"""
    # Verify session exists
    session = db.query(GuestSession).filter(
        GuestSession.id == guest_session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Guest session not found")
    
    # Parse due_date
    try:
        due_date = datetime.fromisoformat(task.due_date.replace('Z', '+00:00'))
    except:
        due_date = datetime.fromisoformat(task.due_date)
    
    new_task = GuestTask(
        guest_session_id=guest_session_id,
        title=task.title,
        description=task.description,
        task_type=task.task_type,
        due_date=due_date,
        grade_percentage=task.grade_percentage,
        predicted_hours=task.predicted_hours,
        status=task.status
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return new_task

@router.get("/tasks/{guest_session_id}")
async def get_guest_tasks(
    guest_session_id: str,
    db: Session = Depends(get_db)
):
    """Get all tasks for guest"""
    tasks = db.query(GuestTask).filter(
        GuestTask.guest_session_id == guest_session_id
    ).order_by(GuestTask.due_date.asc()).all()
    
    return {"tasks": tasks, "total": len(tasks)}

@router.put("/tasks/{task_id}")
async def update_guest_task(
    task_id: str,
    task_update: GuestTaskCreate,
    db: Session = Depends(get_db)
):
    """Update guest task"""
    task = db.query(GuestTask).filter(GuestTask.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.title = task_update.title
    task.description = task_update.description
    task.task_type = task_update.task_type
    task.due_date = datetime.fromisoformat(task_update.due_date.replace('Z', '+00:00'))
    task.grade_percentage = task_update.grade_percentage
    task.status = task_update.status
    
    db.commit()
    db.refresh(task)
    
    return task

@router.delete("/tasks/{task_id}")
async def delete_guest_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """Delete guest task"""
    task = db.query(GuestTask).filter(GuestTask.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    
    return {"message": "Task deleted"}

@router.post("/migrate/{guest_session_id}")
async def migrate_guest_data(
    guest_session_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Migrate guest data to user account"""
    from ..models.task import Task
    from ..models.course import Course
    
    # Get all guest tasks
    guest_tasks = db.query(GuestTask).filter(
        GuestTask.guest_session_id == guest_session_id
    ).all()
    
    # Get all guest courses
    guest_courses = db.query(GuestCourse).filter(
        GuestCourse.guest_session_id == guest_session_id
    ).all()
    
    migrated_count = 0
    
    # Migrate courses first
    course_map = {}  # Map guest course ID to user course ID
    for guest_course in guest_courses:
        new_course = Course(
            user_id=user_id,
            code=guest_course.code,
            name=guest_course.name,
            semester="",
            year=datetime.now().year
        )
        db.add(new_course)
        db.flush()
        course_map[guest_course.id] = new_course.id
    
    # Migrate tasks
    for guest_task in guest_tasks:
        new_task = Task(
            user_id=user_id,
            course_id=course_map.get(guest_task.guest_session_id),
            title=guest_task.title,
            description=guest_task.description,
            task_type=guest_task.task_type,
            due_date=guest_task.due_date,
            weight_score=guest_task.weight_score,
            predicted_hours=guest_task.predicted_hours,
            priority_score=guest_task.priority_score,
            status=guest_task.status,
            grade_percentage=guest_task.grade_percentage,
            extra_data=guest_task.extra_data
        )
        db.add(new_task)
        migrated_count += 1
    
    # Delete guest data
    db.query(GuestTask).filter(
        GuestTask.guest_session_id == guest_session_id
    ).delete()
    
    db.query(GuestCourse).filter(
        GuestCourse.guest_session_id == guest_session_id
    ).delete()
    
    db.query(GuestSession).filter(
        GuestSession.id == guest_session_id
    ).delete()
    
    db.commit()
    
    return {
        "message": "Data migrated successfully",
        "migrated_tasks": migrated_count,
        "migrated_courses": len(guest_courses)
    }
