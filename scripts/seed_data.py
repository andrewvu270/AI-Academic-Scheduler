#!/usr/bin/env python3
"""
Seed data script for AI Academic Scheduler
This script creates sample data for development and testing
"""

import sys
import os
from datetime import datetime, timedelta, date
import uuid
import random

# Add the parent directory to the path so we can import our app
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models.user import User
from app.models.course import Course
from app.models.task import Task
from app.models.study_session import StudySession
from app.models.user_preference import UserPreference
from app.core.auth import get_password_hash


def create_sample_user(db: Session) -> User:
    """Create a sample user for testing."""
    user = User(
        id=str(uuid.uuid4()),
        email="demo@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Demo User",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_sample_courses(db: Session, user_id: str) -> list[Course]:
    """Create sample courses for the user."""
    courses_data = [
        {
            "name": "Introduction to Computer Science",
            "code": "CS101",
            "semester": "Fall",
            "year": 2024
        },
        {
            "name": "Data Structures and Algorithms",
            "code": "CS201",
            "semester": "Fall",
            "year": 2024
        },
        {
            "name": "Calculus I",
            "code": "MATH101",
            "semester": "Fall",
            "year": 2024
        }
    ]
    
    courses = []
    for course_data in courses_data:
        course = Course(
            id=str(uuid.uuid4()),
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            **course_data
        )
        db.add(course)
        courses.append(course)
    
    db.commit()
    for course in courses:
        db.refresh(course)
    
    return courses


def create_sample_tasks(db: Session, courses: list[Course]) -> list[Task]:
    """Create sample tasks for the courses."""
    tasks = []
    
    # Tasks for CS101
    cs101_tasks = [
        {
            "title": "Programming Assignment 1",
            "description": "Write a simple Python program that calculates factorial",
            "task_type": "Assignment",
            "due_date": datetime.utcnow() + timedelta(days=7),
            "grade_percentage": 10.0,
            "weight_score": 0.7,
            "predicted_hours": 3.5,
            "priority_score": 0.8
        },
        {
            "title": "Midterm Exam",
            "description": "Covers chapters 1-5",
            "task_type": "Exam",
            "due_date": datetime.utcnow() + timedelta(days=21),
            "grade_percentage": 25.0,
            "weight_score": 0.9,
            "predicted_hours": 8.0,
            "priority_score": 0.9
        },
        {
            "title": "Quiz 2",
            "description": "Short quiz on loops and functions",
            "task_type": "Quiz",
            "due_date": datetime.utcnow() + timedelta(days=14),
            "grade_percentage": 5.0,
            "weight_score": 0.6,
            "predicted_hours": 2.0,
            "priority_score": 0.7
        }
    ]
    
    # Tasks for CS201
    cs201_tasks = [
        {
            "title": "Algorithm Analysis Project",
            "description": "Implement and analyze sorting algorithms",
            "task_type": "Project",
            "due_date": datetime.utcnow() + timedelta(days=14),
            "grade_percentage": 20.0,
            "weight_score": 0.8,
            "predicted_hours": 12.0,
            "priority_score": 0.85
        },
        {
            "title": "Weekly Problem Set 3",
            "description": "Complete problems 3.1-3.15",
            "task_type": "Assignment",
            "due_date": datetime.utcnow() + timedelta(days=5),
            "grade_percentage": 8.0,
            "weight_score": 0.7,
            "predicted_hours": 4.0,
            "priority_score": 0.75
        }
    ]
    
    # Tasks for MATH101
    math101_tasks = [
        {
            "title": "Homework 4",
            "description": "Derivatives and limits",
            "task_type": "Assignment",
            "due_date": datetime.utcnow() + timedelta(days=3),
            "grade_percentage": 5.0,
            "weight_score": 0.7,
            "predicted_hours": 2.5,
            "priority_score": 0.8
        },
        {
            "title": "Final Exam",
            "description": "Comprehensive final exam",
            "task_type": "Exam",
            "due_date": datetime.utcnow() + timedelta(days=35),
            "grade_percentage": 30.0,
            "weight_score": 0.95,
            "predicted_hours": 15.0,
            "priority_score": 0.95
        }
    ]
    
    all_task_data = [
        (courses[0], cs101_tasks),
        (courses[1], cs201_tasks),
        (courses[2], math101_tasks)
    ]
    
    for course, task_data_list in all_task_data:
        for task_data in task_data_list:
            task = Task(
                id=str(uuid.uuid4()),
                course_id=course.id,
                status="pending",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                **task_data
            )
            db.add(task)
            tasks.append(task)
    
    db.commit()
    for task in tasks:
        db.refresh(task)
    
    return tasks


def create_sample_study_sessions(db: Session, user_id: str, tasks: list[Task]) -> list[StudySession]:
    """Create sample study sessions."""
    sessions = []
    
    # Create sessions for the first few tasks
    sample_tasks = tasks[:5]
    
    for i, task in enumerate(sample_tasks):
        # Create 1-3 sessions per task
        num_sessions = random.randint(1, 3)
        
        for j in range(num_sessions):
            session_date = date.today() - timedelta(days=random.randint(1, 10))
            minutes_spent = random.randint(30, 120)
            
            session = StudySession(
                id=str(uuid.uuid4()),
                task_id=task.id,
                user_id=user_id,
                minutes_spent=minutes_spent,
                date=session_date,
                notes=f"Study session {j+1} for {task.title}",
                created_at=datetime.utcnow()
            )
            db.add(session)
            sessions.append(session)
    
    db.commit()
    for session in sessions:
        db.refresh(session)
    
    return sessions


def create_sample_user_preferences(db: Session, user_id: str) -> UserPreference:
    """Create sample user preferences."""
    preferences = UserPreference(
        id=str(uuid.uuid4()),
        user_id=user_id,
        daily_study_hours=4.0,
        preferred_study_times={
            "morning": True,
            "afternoon": True,
            "evening": False
        },
        notification_preferences={
            "email_reminders": True,
            "push_notifications": True,
            "reminder_hours": [24, 72, 168],  # 1 day, 3 days, 1 week before
            "daily_summary": True
        },
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(preferences)
    db.commit()
    db.refresh(preferences)
    return preferences


def main():
    """Main function to create all sample data."""
    print("🌱 Creating sample data for AI Academic Scheduler...")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if demo user already exists
        existing_user = db.query(User).filter(User.email == "demo@example.com").first()
        if existing_user:
            print("⚠️  Demo user already exists. Skipping seed data creation.")
            return
        
        # Create sample data
        print("👤 Creating sample user...")
        user = create_sample_user(db)
        
        print("📚 Creating sample courses...")
        courses = create_sample_courses(db, user.id)
        
        print("📋 Creating sample tasks...")
        tasks = create_sample_tasks(db, courses)
        
        print("⏱️  Creating sample study sessions...")
        sessions = create_sample_study_sessions(db, user.id, tasks)
        
        print("⚙️  Creating sample user preferences...")
        preferences = create_sample_user_preferences(db, user.id)
        
        print("\n✅ Sample data created successfully!")
        print(f"   - User: {user.email}")
        print(f"   - Courses: {len(courses)}")
        print(f"   - Tasks: {len(tasks)}")
        print(f"   - Study Sessions: {len(sessions)}")
        print(f"   - User Preferences: 1")
        print("\n🔐 Login credentials:")
        print(f"   Email: {user.email}")
        print("   Password: password123")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()