from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    course_id = Column(String, ForeignKey("courses.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    task_type = Column(String, nullable=False)  # 'Assignment', 'Exam', 'Quiz', 'Project', 'Reading'
    due_date = Column(DateTime(timezone=True), nullable=False)
    weight_score = Column(Float, default=0.5)
    predicted_hours = Column(Float, default=4.0)
    priority_score = Column(Float, default=0.5)
    status = Column(String, default="pending")  # 'pending', 'in_progress', 'completed'
    grade_percentage = Column(Float, default=0.0)
    extra_data = Column(JSON)  # Store additional extracted data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    course = relationship("Course", back_populates="tasks")
    study_sessions = relationship("StudySession", back_populates="task", cascade="all, delete-orphan")