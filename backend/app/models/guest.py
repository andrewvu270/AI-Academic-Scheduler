from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..database import Base

class GuestSession(Base):
    __tablename__ = "guest_sessions"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_accessed = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tasks = relationship("GuestTask", back_populates="session", cascade="all, delete-orphan")
    courses = relationship("GuestCourse", back_populates="session", cascade="all, delete-orphan")

class GuestTask(Base):
    __tablename__ = "guest_tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    guest_session_id = Column(String, ForeignKey("guest_sessions.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    task_type = Column(String, nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False)
    weight_score = Column(Float, default=0.5)
    predicted_hours = Column(Float, default=4.0)
    priority_score = Column(Float, default=0.5)
    status = Column(String, default="pending")
    grade_percentage = Column(Float, default=0.0)
    extra_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    session = relationship("GuestSession", back_populates="tasks")

class GuestCourse(Base):
    __tablename__ = "guest_courses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    guest_session_id = Column(String, ForeignKey("guest_sessions.id"), nullable=False, index=True)
    code = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    session = relationship("GuestSession", back_populates="courses")
