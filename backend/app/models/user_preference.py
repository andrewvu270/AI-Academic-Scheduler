from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..database import Base

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    daily_study_hours = Column(Float, default=3.0)
    preferred_study_times = Column(JSON, default=dict)  # {"morning": true, "afternoon": false, "evening": true}
    notification_preferences = Column(JSON, default=dict)  # {"email": true, "push": true, "reminder_hours": 24}
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")