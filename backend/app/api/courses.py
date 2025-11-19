from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..schemas.course import Course, CourseCreate, CourseUpdate, CourseWithTasks
from ..models.course import Course as CourseModel

router = APIRouter()

@router.get("/", response_model=List[Course])
async def get_courses(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    courses = db.query(CourseModel).offset(skip).limit(limit).all()
    return courses

@router.post("/", response_model=Course)
async def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db)
):
    db_course = CourseModel(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@router.get("/{course_id}", response_model=CourseWithTasks)
async def get_course(
    course_id: str,
    db: Session = Depends(get_db)
):
    course = db.query(CourseModel).filter(
        CourseModel.id == course_id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=404, 
            detail="Course not found"
        )
    
    return course

@router.put("/{course_id}", response_model=Course)
async def update_course(
    course_id: str,
    course_update: CourseUpdate,
    db: Session = Depends(get_db)
):
    db_course = db.query(CourseModel).filter(
        CourseModel.id == course_id
    ).first()
    
    if not db_course:
        raise HTTPException(
            status_code=404, 
            detail="Course not found"
        )
    
    update_data = course_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_course, field, value)
    
    db.commit()
    db.refresh(db_course)
    return db_course

@router.delete("/{course_id}")
async def delete_course(
    course_id: str,
    db: Session = Depends(get_db)
):
    db_course = db.query(CourseModel).filter(
        CourseModel.id == course_id
    ).first()
    
    if not db_course:
        raise HTTPException(
            status_code=404, 
            detail="Course not found"
        )
    
    db.delete(db_course)
    db.commit()
    return {"message": "Course deleted successfully"}