import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import openai
from ..config import settings


class TaskExtractionService:
    """Service for extracting academic tasks from syllabus text using OpenAI API."""
    
    def __init__(self):
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
        else:
            print("Warning: OpenAI API key not configured. Study plan generation will not work.")
    
    async def extract_tasks_from_syllabus(self, syllabus_text: str, course_name: str = "") -> List[Dict[str, Any]]:
        """
        Extract academic tasks from syllabus text using OpenAI GPT.
        
        Args:
            syllabus_text: Raw text content from syllabus
            course_name: Name of the course (for context)
            
        Returns:
            List of extracted tasks with their properties
        """
        try:
            # Prepare the prompt for OpenAI
            prompt = self._build_extraction_prompt(syllabus_text, course_name)
            
            # Call OpenAI API
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an academic assistant that extracts assignment and exam information from course syllabi. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent results
                max_tokens=2000
            )
            
            # Parse the response
            extracted_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON from the response
            tasks = self._parse_tasks_from_response(extracted_text)
            
            # Process and validate the extracted tasks
            processed_tasks = []
            for task in tasks:
                processed_task = self._process_extracted_task(task)
                if processed_task:
                    processed_tasks.append(processed_task)
            
            return processed_tasks
            
        except Exception as e:
            raise Exception(f"Task extraction failed: {str(e)}")
    
    def _build_extraction_prompt(self, syllabus_text: str, course_name: str) -> str:
        """
        Build the prompt for OpenAI API to extract tasks from syllabus.
        
        Args:
            syllabus_text: Text content from syllabus
            course_name: Name of the course
            
        Returns:
            Formatted prompt string
        """
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        prompt = f"""
        Extract all assignments, exams, quizzes, projects, and important deadlines from the following syllabus text.
        
        Course: {course_name}
        Current Date: {current_date}
        
        Syllabus Text:
        {syllabus_text[:4000]}  # Limit text to avoid token limits
        
        Please extract the following information for each task and return as a JSON array:
        
        {{
            "tasks": [
                {{
                    "title": "Task title",
                    "description": "Brief description",
                    "task_type": "Assignment|Exam|Quiz|Project|Reading|Lab",
                    "due_date": "YYYY-MM-DD",
                    "due_time": "HH:MM",
                    "grade_percentage": 0.0,
                    "instructor_keywords": ["important", "mandatory", "critical"],
                    "notes": "Additional notes"
                }}
            ]
        }}
        
        Guidelines:
        1. Look for due dates and deadlines
        2. Identify task types (assignments, exams, quizzes, etc.)
        3. Extract grade percentages when available
        4. Include instructor emphasis keywords
        5. If date is ambiguous, use context to determine the most likely date
        6. If time is not specified, use "23:59" as default
        7. If grade percentage is not specified, estimate based on task type
        8. Return valid JSON only, no additional text
        """
        
        return prompt
    
    def _parse_tasks_from_response(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Parse and extract JSON tasks from OpenAI response.
        
        Args:
            response_text: Raw response text from OpenAI
            
        Returns:
            List of task dictionaries
        """
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                return data.get("tasks", [])
            else:
                # Try to parse the entire response as JSON
                data = json.loads(response_text)
                return data.get("tasks", [])
                
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract tasks manually
            return self._fallback_task_extraction(response_text)
    
    def _fallback_task_extraction(self, text: str) -> List[Dict[str, Any]]:
        """
        Fallback method to extract tasks when JSON parsing fails.
        
        Args:
            text: Response text from OpenAI
            
        Returns:
            List of basic task dictionaries
        """
        # This is a simple fallback - in production, you might want more sophisticated parsing
        tasks = []
        
        # Look for common patterns
        lines = text.split('\n')
        current_task = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for task patterns
            if any(keyword in line.lower() for keyword in ['assignment', 'exam', 'quiz', 'project']):
                if current_task:
                    tasks.append(current_task)
                current_task = {"title": line, "task_type": "Assignment"}
            
            # Look for dates
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', line)
            if date_match and current_task:
                current_task["due_date"] = date_match.group(1)
        
        if current_task:
            tasks.append(current_task)
        
        return tasks
    
    def _process_extracted_task(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process and validate an extracted task.
        
        Args:
            task: Raw task dictionary from extraction
            
        Returns:
            Processed task dictionary or None if invalid
        """
        try:
            # Required fields
            if not task.get("title"):
                return None
            
            # Set defaults for missing fields
            processed_task = {
                "title": task["title"],
                "description": task.get("description", ""),
                "task_type": self._normalize_task_type(task.get("task_type", "Assignment")),
                "due_date": self._parse_date(task.get("due_date")),
                "due_time": task.get("due_time", "23:59"),
                "grade_percentage": float(task.get("grade_percentage", 0)),
                "instructor_keywords": task.get("instructor_keywords", []),
                "notes": task.get("notes", "")
            }
            
            # Validate the processed task
            if not processed_task["due_date"]:
                return None
            
            return processed_task
            
        except Exception as e:
            # Log the error and skip this task
            print(f"Error processing task: {str(e)}")
            return None
    
    def _normalize_task_type(self, task_type: str) -> str:
        """
        Normalize task type to standard values.
        
        Args:
            task_type: Raw task type string
            
        Returns:
            Normalized task type
        """
        task_type = task_type.lower().strip()
        
        type_mapping = {
            "assignment": "Assignment",
            "assignments": "Assignment",
            "exam": "Exam",
            "exams": "Exam",
            "midterm": "Exam",
            "final": "Exam",
            "quiz": "Quiz",
            "quizzes": "Quiz",
            "test": "Quiz",
            "project": "Project",
            "projects": "Project",
            "reading": "Reading",
            "readings": "Reading",
            "lab": "Lab",
            "labs": "Lab"
        }
        
        return type_mapping.get(task_type, "Assignment")
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """
        Parse and normalize date string.
        
        Args:
            date_str: Raw date string
            
        Returns:
            Normalized date string in YYYY-MM-DD format or None
        """
        if not date_str:
            return None
        
        try:
            # Try to parse common date formats
            date_formats = [
                "%Y-%m-%d",
                "%m/%d/%Y",
                "%m-%d-%Y",
                "%B %d, %Y",
                "%b %d, %Y"
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    return parsed_date.strftime("%Y-%m-%d")
                except ValueError:
                    continue
            
            # If no format matches, return None
            return None
            
        except Exception:
            return None


# Create a singleton instance
task_extraction_service = TaskExtractionService()