from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime

from ..database import get_db
from ..schemas.schedule import (
    ScheduleItem, DailySchedule, WeeklySchedule, 
    ScheduleRequest, WeeklyScheduleRequest, ScheduleGenerationResponse
)
from ..models.task import Task as TaskModel
from ..models.course import Course
from ..ml.schedule_optimizer import ScheduleOptimizer

router = APIRouter()

@router.get("/daily", response_model=DailySchedule)
async def get_daily_schedule(
    available_hours: float = 3.0,
    schedule_date: date = None,
    db: Session = Depends(get_db)
):
    if schedule_date is None:
        schedule_date = date.today()
    
    # Get pending tasks
    tasks = db.query(TaskModel).filter(
        TaskModel.status == 'pending',
        TaskModel.due_date >= schedule_date
    ).all()
    
    # Convert to dict format for optimizer
    task_dicts = []
    for task in tasks:
        task_dicts.append({
            'id': str(task.id),
            'title': task.title,
            'course_code': task.course.code,
            'due_date': task.due_date,
            'predicted_hours': task.predicted_hours,
            'priority_score': task.priority_score,
            'status': task.status,
            'task_type': task.task_type
        })
    
    # Generate schedule
    optimizer = ScheduleOptimizer()
    schedule_items = optimizer.generate_daily_schedule(
        task_dicts, available_hours, schedule_date
    )
    
    total_allocated = sum(item['allocated_hours'] for item in schedule_items)
    
    return DailySchedule(
        date=schedule_date,
        items=schedule_items,
        total_allocated_hours=total_allocated,
        available_hours=available_hours
    )

@router.post("/daily", response_model=ScheduleGenerationResponse)
async def generate_daily_schedule(
    request: ScheduleRequest,
    db: Session = Depends(get_db)
):
    schedule_date = request.start_date or date.today()
    
    # Get pending tasks
    tasks = db.query(TaskModel).filter(
        TaskModel.status == 'pending',
        TaskModel.due_date >= schedule_date
    ).all()
    
    if not tasks:
        return ScheduleGenerationResponse(
            success=False,
            message="No pending tasks found"
        )
    
    # Convert to dict format for optimizer
    task_dicts = []
    for task in tasks:
        task_dicts.append({
            'id': str(task.id),
            'title': task.title,
            'course_code': task.course.code,
            'due_date': task.due_date,
            'predicted_hours': task.predicted_hours,
            'priority_score': task.priority_score,
            'status': task.status,
            'task_type': task.task_type
        })
    
    # Generate schedule
    optimizer = ScheduleOptimizer()
    schedule_items = optimizer.generate_daily_schedule(
        task_dicts, request.available_hours, schedule_date
    )
    
    total_allocated = sum(item['allocated_hours'] for item in schedule_items)
    
    daily_schedule = DailySchedule(
        date=schedule_date,
        items=schedule_items,
        total_allocated_hours=total_allocated,
        available_hours=request.available_hours
    )
    
    return ScheduleGenerationResponse(
        success=True,
        message="Schedule generated successfully",
        schedule=daily_schedule
    )

@router.post("/weekly", response_model=WeeklySchedule)
async def generate_weekly_schedule(
    request: WeeklyScheduleRequest,
    db: Session = Depends(get_db)
):
    start_date = request.start_date or date.today()
    week_end = start_date.replace(day=start_date.day + 6)
    
    # Get user's pending tasks
    tasks = db.query(TaskModel).join(Course).filter(
        Course.user_id == current_user.id,
        TaskModel.status == 'pending',
        TaskModel.due_date >= start_date
    ).all()
    
    # Convert to dict format for optimizer
    task_dicts = []
    for task in tasks:
        task_dicts.append({
            'id': str(task.id),
            'title': task.title,
            'course_code': task.course.code,
            'due_date': task.due_date,
            'predicted_hours': task.predicted_hours,
            'priority_score': task.priority_score,
            'status': task.status,
            'task_type': task.task_type
        })
    
    # Generate weekly schedule
    optimizer = ScheduleOptimizer()
    weekly_schedules = optimizer.generate_weekly_schedule(
        task_dicts, request.daily_hours, start_date
    )
    
    # Convert to proper format
    daily_schedules = {}
    total_tasks = 0
    total_hours = 0
    
    for day_name, items in weekly_schedules.items():
        current_date = start_date
        for i in range(7):
            if current_date.strftime('%A').lower() == day_name:
                break
            current_date = current_date.replace(day=current_date.day + 1)
        
        daily_schedules[day_name] = DailySchedule(
            date=current_date,
            items=items,
            total_allocated_hours=sum(item['allocated_hours'] for item in items),
            available_hours=request.daily_hours.get(day_name, 0)
        )
        
        total_tasks += len(items)
        total_hours += sum(item['allocated_hours'] for item in items)
    
    return WeeklySchedule(
        week_start=start_date,
        week_end=week_end,
        daily_schedules=daily_schedules,
        total_tasks_scheduled=total_tasks,
        total_hours_allocated=total_hours
    )