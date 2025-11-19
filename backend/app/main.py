from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .config import settings

# Import routers
from .api import courses, tasks, schedule, upload, ml

app = FastAPI(title="AI Academic Scheduler", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(courses.router, prefix="/api/courses", tags=["courses"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(schedule.router, prefix="/api/schedule", tags=["schedule"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(ml.router, prefix="/api/ml", tags=["ml"])

@app.get("/")
async def root():
    return {"message": "AI Academic Scheduler API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)