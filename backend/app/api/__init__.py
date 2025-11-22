from fastapi import APIRouter
from . import courses, tasks, schedule, upload, ml, study_plan

api_router = APIRouter()

# Include all routers
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(courses.router, prefix="/courses", tags=["Courses"])
api_router.include_router(schedule.router, prefix="/schedule", tags=["Schedule"])
api_router.include_router(upload.router, prefix="/upload", tags=["File Upload"])
api_router.include_router(ml.router, prefix="/ml", tags=["Machine Learning"])
api_router.include_router(study_plan.router, prefix="/study-plan", tags=["Study Plan"])

__all__ = ["api_router", "courses", "tasks", "schedule", "upload", "ml", "study_plan"]