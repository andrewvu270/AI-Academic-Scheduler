"""Survey endpoints for collecting training data for LightGBM model"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
from pathlib import Path

router = APIRouter(prefix="/api/survey", tags=["survey"])

class SurveyResponse(BaseModel):
    """Survey response data for model training"""
    task_title: str
    task_type: str  # Assignment, Exam, Quiz, Project, etc.
    due_date: str  # YYYY-MM-DD
    grade_percentage: float  # 0-100
    estimated_hours: float  # Hours needed to complete
    actual_hours: float  # Actual hours spent
    difficulty_level: int  # 1-5 scale
    priority_rating: int  # 1-5 scale (how important user felt it was)
    completed: bool
    completion_date: Optional[str] = None  # YYYY-MM-DD if completed
    notes: Optional[str] = None

class SurveySubmission(BaseModel):
    """Container for survey submissions"""
    responses: List[SurveyResponse]
    user_feedback: Optional[str] = None

# Store survey data in JSON file (can be migrated to database later)
SURVEY_DATA_DIR = Path("survey_data")
SURVEY_DATA_DIR.mkdir(exist_ok=True)
SURVEY_FILE = SURVEY_DATA_DIR / "responses.jsonl"

@router.post("/submit")
async def submit_survey(submission: SurveySubmission):
    """Submit survey responses for model training"""
    try:
        # Append to JSONL file (one JSON object per line)
        with open(SURVEY_FILE, "a") as f:
            for response in submission.responses:
                f.write(response.model_dump_json() + "\n")
        
        return {
            "message": "Survey submitted successfully",
            "count": len(submission.responses),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save survey: {str(e)}")

@router.get("/data/count")
async def get_survey_count():
    """Get count of survey responses collected"""
    try:
        if not SURVEY_FILE.exists():
            return {"count": 0}
        
        with open(SURVEY_FILE, "r") as f:
            count = sum(1 for _ in f)
        
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data/export")
async def export_survey_data():
    """Export all survey data for model training (admin only)"""
    try:
        if not SURVEY_FILE.exists():
            return {"data": []}
        
        data = []
        with open(SURVEY_FILE, "r") as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        
        return {"data": data, "count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def survey_status():
    """Get survey collection status"""
    try:
        count = 0
        if SURVEY_FILE.exists():
            with open(SURVEY_FILE, "r") as f:
                count = sum(1 for _ in f)
        
        return {
            "active": True,
            "responses_collected": count,
            "min_responses_for_training": 100,
            "ready_for_training": count >= 100,
            "survey_url": "http://localhost:3000/survey"  # Hidden from public
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
