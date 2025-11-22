from fastapi import APIRouter, HTTPException
from typing import List
from datetime import date, datetime

from ..database import get_supabase
from ..schemas.schedule import (
    ScheduleItem, DailySchedule, WeeklySchedule, 
    ScheduleRequest, WeeklyScheduleRequest, ScheduleGenerationResponse
)
from ..ml.schedule_optimizer import ScheduleOptimizer

router = APIRouter()

@router.get("/daily", response_model=DailySchedule)
async def get_daily_schedule(
    available_hours: float = 3.0,
    schedule_date: date = None
):
    try:
        if schedule_date is None:
            schedule_date = date.today()
        
        supabase = get_supabase()
        
        # Get pending tasks from Supabase
        response = supabase.table("tasks").select("*").eq("status", "pending").execute()
        tasks = response.data if response.data else []
        
        # Filter tasks by due date and convert to dict format
        task_dicts = []
        for task in tasks:
            task_date = datetime.fromisoformat(task.get('due_date', '')).date() if task.get('due_date') else None
            if task_date and task_date >= schedule_date:
                task_dicts.append({
                    'id': task['id'],
                    'title': task['title'],
                    'course_code': task.get('course_id', 'Unknown'),
                    'due_date': task_date,
                    'predicted_hours': task.get('predicted_hours', 4.0),
                    'priority_score': task.get('priority_score', 0),
                    'status': task.get('status', 'pending'),
                    'task_type': task.get('task_type', 'Assignment')
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/daily", response_model=ScheduleGenerationResponse)
async def generate_daily_schedule(request: ScheduleRequest):
    try:
        schedule_date = request.start_date or date.today()
        
        supabase = get_supabase()
        
        # Get pending tasks from Supabase
        response = supabase.table("tasks").select("*").eq("status", "pending").execute()
        tasks = response.data if response.data else []
        
        if not tasks:
            return ScheduleGenerationResponse(
                success=False,
                message="No pending tasks found"
            )
        
        # Filter tasks by due date and convert to dict format
        task_dicts = []
        for task in tasks:
            task_date = datetime.fromisoformat(task.get('due_date', '')).date() if task.get('due_date') else None
            if task_date and task_date >= schedule_date:
                task_dicts.append({
                    'id': task['id'],
                    'title': task['title'],
                    'course_code': task.get('course_id', 'Unknown'),
                    'due_date': task_date,
                    'predicted_hours': task.get('predicted_hours', 4.0),
                    'priority_score': task.get('priority_score', 0),
                    'status': task.get('status', 'pending'),
                    'task_type': task.get('task_type', 'Assignment')
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/weekly", response_model=WeeklySchedule)
async def generate_weekly_schedule(request: WeeklyScheduleRequest):
    try:
        start_date = request.start_date or date.today()
        week_end = start_date.replace(day=start_date.day + 6)
        
        supabase = get_supabase()
        
        # Get pending tasks from Supabase
        response = supabase.table("tasks").select("*").eq("status", "pending").execute()
        tasks = response.data if response.data else []
        
        # Filter tasks by due date and convert to dict format
        task_dicts = []
        for task in tasks:
            task_date = datetime.fromisoformat(task.get('due_date', '')).date() if task.get('due_date') else None
            if task_date and task_date >= start_date:
                task_dicts.append({
                    'id': task['id'],
                    'title': task['title'],
                    'course_code': task.get('course_id', 'Unknown'),
                    'due_date': task_date,
                    'predicted_hours': task.get('predicted_hours', 4.0),
                    'priority_score': task.get('priority_score', 0),
                    'status': task.get('status', 'pending'),
                    'task_type': task.get('task_type', 'Assignment')
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))