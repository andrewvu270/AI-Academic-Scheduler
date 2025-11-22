from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Header
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

from ..database import get_supabase, get_supabase_admin
from ..services.pdf_service import pdf_service
from ..services.task_extraction_service import task_extraction_service
from ..services.ml_service import ml_service
from ..services.auth_service import AuthService
from ..ml.weight_calculator import TaskWeightCalculator
from ..ml.priority_calculator import PriorityCalculator

router = APIRouter()


@router.post("/syllabus")
async def upload_syllabus(
    file: UploadFile = File(...),
    course_id: str = Form(...),
    authorization: Optional[str] = Header(None)
):
    """
    Upload and process a syllabus file to extract tasks.
    
    Args:
        file: Uploaded syllabus file (PDF or image)
        course_id: ID of the course to associate tasks with
        
    Returns:
        Dictionary containing extracted tasks and processing status
    """
    try:
        print(f"[UPLOAD] Starting syllabus upload for course_id={course_id}, file={file.filename}")
        
        # Validate file size
        pdf_service.validate_file_size(file)
        print(f"[UPLOAD] File size validated")
        
        # Process the uploaded file
        extracted_text = await pdf_service.process_uploaded_file(file)
        
        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the uploaded file"
            )
        
        # Clean the extracted text
        cleaned_text = pdf_service.clean_extracted_text(extracted_text)
        
        # Extract tasks using OpenAI
        extracted_tasks = await task_extraction_service.extract_tasks_from_syllabus(
            cleaned_text, 
            "Unknown Course"  # Course name not available in guest mode
        )
        
        if not extracted_tasks:
            raise HTTPException(
                status_code=400,
                detail="No tasks could be extracted from the syllabus"
            )
        
        # Process and save tasks
        saved_tasks = []
        weight_calculator = TaskWeightCalculator()
        priority_calculator = PriorityCalculator()
        
        print(f"[UPLOAD] Extracted {len(extracted_tasks)} tasks from syllabus")
        
        # Determine if user is authenticated
        user_id = None
        is_authenticated = False
        
        if authorization:
            try:
                # Extract token from "Bearer <token>"
                token = authorization.split(" ")[1] if " " in authorization else authorization
                user_data = await AuthService.verify_user_session(token)
                if user_data:
                    user_id = user_data.get("id")
                    is_authenticated = True
                    print(f"[UPLOAD] Authenticated user found: {user_id}")
            except Exception as e:
                print(f"[UPLOAD] Error verifying token: {str(e)}")
        
        if not is_authenticated:
            print("[UPLOAD] Guest user - will return data without saving to Supabase")
            user_id = "guest"  # Use "guest" as placeholder for frontend

        for task_data in extracted_tasks:
            try:
                print(f"[UPLOAD] Processing task: {task_data.get('title')}")
                
                # Calculate weight score
                weight_score = weight_calculator.calculate_weight_score(task_data)
                
                # Predict workload using ML
                predicted_hours = await ml_service.predict_workload(task_data)
                
                # Calculate priority score
                task_with_predictions = {
                    **task_data,
                    "weight_score": weight_score,
                    "predicted_hours": predicted_hours
                }
                priority_score = priority_calculator.calculate_priority_score(
                    task_with_predictions
                )
                
                # Save to Supabase
                new_task = {
                    "id": str(uuid.uuid4()),
                    "course_id": course_id,
                    "user_id": user_id,
                    "title": task_data["title"],
                    "description": task_data.get("description", ""),
                    "task_type": task_data["task_type"],
                    "due_date": task_data["due_date"],
                    "weight_score": weight_score,
                    "predicted_hours": predicted_hours,
                    "priority_score": priority_score,
                    "status": "pending",
                    "grade_percentage": task_data.get("grade_percentage", 0),
                    "created_at": datetime.utcnow().isoformat()
                }
                
                print(f"[UPLOAD] Task prepared: {new_task}")
                saved_tasks.append(new_task)
                print(f"[UPLOAD] Task added to list")
                
            except Exception as e:
                import traceback
                print(f"[UPLOAD] Error processing task: {str(e)}")
                print(traceback.format_exc())
                # Continue with other tasks even if one fails
                continue
        
        if not saved_tasks:
            raise HTTPException(
                status_code=500,
                detail="Failed to extract any valid tasks"
            )
            
        # Only save to Supabase if user is authenticated
        if is_authenticated:
            try:
                # Use admin client to bypass RLS since this is a backend operation
                supabase_admin = get_supabase_admin()
                
                # Ensure user exists in public.users table
                user_check = supabase_admin.table("users").select("id").eq("id", user_id).execute()
                if not user_check.data:
                    print(f"[UPLOAD] User {user_id} not found in public.users, creating...")
                    new_user_data = {
                        "id": user_id,
                        "email": f"user_{user_id}@example.com",
                        "full_name": "",
                        "created_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat()
                    }
                    supabase_admin.table("users").insert(new_user_data).execute()
                    print(f"[UPLOAD] Created user in public.users: {user_id}")
                
                print(f"[UPLOAD] Inserting {len(saved_tasks)} tasks into Supabase for authenticated user")
                response = supabase_admin.table("tasks").insert(saved_tasks).execute()
                print(f"[UPLOAD] Insert successful")
            except Exception as e:
                print(f"[UPLOAD] Database insert failed: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to save tasks to database: {str(e)}"
                )
        else:
            print(f"[UPLOAD] Guest user - returning {len(saved_tasks)} tasks without saving to database")
        
        if not saved_tasks:
            raise HTTPException(
                status_code=500,
                detail="Failed to save any extracted tasks"
            )
        
        return {
            "success": True,
            "message": f"Successfully processed syllabus and extracted {len(saved_tasks)} tasks",
            "extracted_text_length": len(cleaned_text),
            "tasks": saved_tasks,
            "course_id": course_id,
            "processed_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[UPLOAD] Error in upload_syllabus: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Syllabus processing failed: {str(e)}"
        )


@router.get("/status/{upload_id}")
async def get_upload_status(
    upload_id: str
):
    """
    Get the status of a syllabus upload (placeholder for future implementation).
    
    Args:
        upload_id: Unique identifier for the upload
        current_user: Currently authenticated user
        
    Returns:
        Upload status information
    """
    # This is a placeholder for future implementation
    # In a real system, you would track upload status in a database
    return {
        "upload_id": upload_id,
        "status": "completed",
        "message": "Upload processing completed"
    }


@router.post("/preview")
async def preview_syllabus_extraction(
    file: UploadFile = File(...),
    course_name: str = Form("")
):
    """
    Preview task extraction from syllabus without saving to database.
    
    Args:
        file: Uploaded syllabus file
        course_name: Name of the course (for context)
        current_user: Currently authenticated user
        
    Returns:
        Extracted tasks preview without saving
    """
    try:
        # Validate file size
        pdf_service.validate_file_size(file)
        
        # Process the uploaded file
        extracted_text = await pdf_service.process_uploaded_file(file)
        
        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the uploaded file"
            )
        
        # Clean the extracted text
        cleaned_text = pdf_service.clean_extracted_text(extracted_text)
        
        # Extract tasks using OpenAI
        extracted_tasks = await task_extraction_service.extract_tasks_from_syllabus(
            cleaned_text, 
            course_name
        )
        
        # Process tasks with ML predictions (without saving)
        preview_tasks = []
        weight_calculator = TaskWeightCalculator()
        priority_calculator = PriorityCalculator()
        
        for task_data in extracted_tasks:
            try:
                # Calculate weight score
                weight_score = weight_calculator.calculate_weight_score(task_data)
                
                # Predict workload using ML
                predicted_hours = await ml_service.predict_workload(task_data)
                
                # Calculate priority score
                task_with_predictions = {
                    **task_data,
                    "weight_score": weight_score,
                    "predicted_hours": predicted_hours
                }
                priority_score = priority_calculator.calculate_priority_score(
                    task_with_predictions
                )
                
                preview_tasks.append({
                    "title": task_data["title"],
                    "description": task_data.get("description", ""),
                    "task_type": task_data["task_type"],
                    "due_date": task_data["due_date"],
                    "weight_score": weight_score,
                    "predicted_hours": predicted_hours,
                    "priority_score": priority_score,
                    "grade_percentage": task_data.get("grade_percentage", 0)
                })
                
            except Exception as e:
                print(f"Error processing preview task: {str(e)}")
                continue
        
        return {
            "success": True,
            "extracted_text_length": len(cleaned_text),
            "tasks": preview_tasks,
            "total_tasks": len(preview_tasks)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Preview generation failed: {str(e)}"
        )


@router.post("/feedback/{task_id}")
async def submit_task_feedback(
    task_id: str,
    actual_hours: float,
    difficulty_rating: int = 5,
    notes: str = ""
):
    """
    Submit feedback on actual task completion time for ML model training.
    
    Args:
        task_id: ID of the completed task
        actual_hours: Actual hours spent on the task
        difficulty_rating: User's difficulty rating (1-10)
        notes: Optional notes about the task
        
    Returns:
        Feedback submission confirmation
    """
    try:
        supabase = get_supabase()
        
        # Validate input
        if actual_hours < 0 or actual_hours > 100:
            raise HTTPException(
                status_code=400,
                detail="Actual hours must be between 0 and 100"
            )
        
        if difficulty_rating < 1 or difficulty_rating > 10:
            raise HTTPException(
                status_code=400,
                detail="Difficulty rating must be between 1 and 10"
            )
        
        # Get the task
        task_response = supabase.table("tasks").select("*").eq("id", task_id).execute()
        
        if not task_response.data:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
        
        task = task_response.data[0]
        
        # Prepare feedback data for ML training
        feedback_data = {
            "task_data": {
                "title": task.get("title"),
                "task_type": task.get("task_type"),
                "grade_percentage": task.get("grade_percentage", 0),
                "description": task.get("description", ""),
                "due_date": task.get("due_date", ""),
                "predicted_hours": task.get("predicted_hours", 0),
                "weight_score": task.get("weight_score", 0),
                "priority_score": task.get("priority_score", 0)
            },
            "actual_hours": actual_hours,
            "difficulty_rating": difficulty_rating,
            "notes": notes,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Update ML service with feedback
        await ml_service.update_model_with_feedback(feedback_data["task_data"], actual_hours)
        
        # Calculate prediction accuracy
        prediction_error = abs(task.get("predicted_hours", 0) - actual_hours)
        accuracy_percentage = max(0, 100 - (prediction_error / max(actual_hours, 1) * 100))
        
        return {
            "success": True,
            "message": "Feedback submitted successfully",
            "feedback": {
                "task_id": task_id,
                "predicted_hours": task.get("predicted_hours", 0),
                "actual_hours": actual_hours,
                "prediction_error": round(prediction_error, 2),
                "accuracy_percentage": round(accuracy_percentage, 2),
                "difficulty_rating": difficulty_rating
            },
            "model_status": {
                "is_trained": ml_service.is_trained,
                "model_type": "LightGBM" if ml_service.model else "Rule-based"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Feedback submission failed: {str(e)}"
        )