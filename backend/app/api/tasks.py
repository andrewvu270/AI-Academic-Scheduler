from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database import get_db
from ..schemas.task import Task, TaskCreate, TaskUpdate, TaskWithCourse, TaskList
from ..models.task import Task as TaskModel
from ..models.course import Course
from ..ml.weight_calculator import TaskWeightCalculator
from ..ml.priority_calculator import PriorityCalculator

router = APIRouter()

@router.get("/", response_model=TaskList)
async def get_tasks(
    skip: int = 0, 
    limit: int = 100,
    course_id: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(TaskModel)
    
    if course_id:
        query = query.filter(TaskModel.course_id == course_id)
    
    tasks = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return TaskList(tasks=tasks, total=total)

@router.post("/", response_model=Task)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db)
):
    # Verify course exists
    course = db.query(Course).filter(
        Course.id == task.course_id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=404, 
            detail="Course not found"
        )
    
    # Calculate weight and priority scores
    weight_calculator = TaskWeightCalculator()
    priority_calculator = PriorityCalculator()
    
    task_data = task.dict()
    weight_score = weight_calculator.calculate_weight_score(task_data)
    
    # Create task with calculated scores
    db_task = TaskModel(
        **task_data,
        weight_score=weight_score,
        priority_score=priority_calculator.calculate_priority_score({
            **task_data,
            'weight_score': weight_score
        })
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Add course info to response
    db_task.course_code = course.code
    return db_task

@router.get("/{task_id}", response_model=TaskWithCourse)
async def get_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    task = db.query(TaskModel).filter(
        TaskModel.id == task_id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=404, 
            detail="Task not found"
        )
    
    return task

@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    db: Session = Depends(get_db)
):
    db_task = db.query(TaskModel).filter(
        TaskModel.id == task_id
    ).first()
    
    if not db_task:
        raise HTTPException(
            status_code=404, 
            detail="Task not found"
        )
    
    update_data = task_update.dict(exclude_unset=True)
    
    # Recalculate weight and priority if relevant fields changed
    if any(field in update_data for field in ['task_type', 'grade_percentage']):
        weight_calculator = TaskWeightCalculator()
        priority_calculator = PriorityCalculator()
        
        task_data = {
            'task_type': update_data.get('task_type', db_task.task_type),
            'grade_percentage': update_data.get('grade_percentage', db_task.grade_percentage)
        }
        
        weight_score = weight_calculator.calculate_weight_score(task_data)
        update_data['weight_score'] = weight_score
        update_data['priority_score'] = priority_calculator.calculate_priority_score({
            **task_data,
            'weight_score': weight_score,
            'due_date': update_data.get('due_date', db_task.due_date),
            'predicted_hours': update_data.get('predicted_hours', db_task.predicted_hours)
        })
    
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task

@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    db_task = db.query(TaskModel).filter(
        TaskModel.id == task_id
    ).first()
    
    if not db_task:
        raise HTTPException(
            status_code=404, 
            detail="Task not found"
        )
    
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted successfully"}

@router.post("/{task_id}/complete", response_model=Task)
async def complete_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    db_task = db.query(TaskModel).filter(
        TaskModel.id == task_id
    ).first()
    
    if not db_task:
        raise HTTPException(
            status_code=404, 
            detail="Task not found"
        )
    
    db_task.status = "completed"
    db_task.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_task)
    return db_task