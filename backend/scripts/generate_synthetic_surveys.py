import os
import random
from datetime import datetime, timedelta
import json
from supabase import create_client, Client
from dotenv import load_dotenv

def load_environment():
    """Load environment variables from .env file."""
    load_dotenv()
    
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_SERVICE_ROLE_KEY',
    ]
    
    for var in required_vars:
        if not os.getenv(var):
            raise ValueError(f"Missing required environment variable: {var}")

def get_supabase_client() -> Client:
    """Initialize and return a Supabase client with service role."""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    return create_client(url, key)

def generate_synthetic_data(count: int = 200):
    """Generate synthetic survey data."""
    task_types = ["Assignment", "Exam", "Quiz", "Project", "Reading", "Lab"]
    courses = ["CS101", "MATH201", "PHYS102", "ENG103", "BIO104"]
    
    data = []
    
    for _ in range(count):
        # Generate random dates within the next 3 months
        due_date = datetime.now() + timedelta(days=random.randint(1, 90))
        completion_date = due_date - timedelta(days=random.randint(0, 7))
        
        estimated_hours = round(random.uniform(1, 15), 2)
        actual_hours = round(estimated_hours * random.uniform(0.7, 1.5), 2)
        
        item = {
            "task_title": f"{random.choice(['Homework', 'Problem Set', 'Lab Report'])}_{random.randint(1, 10)}",
            "task_type": random.choice(task_types),
            "course_name": random.choice(courses),
            "due_date": due_date.strftime("%Y-%m-%d"),
            "grade_percentage": round(random.uniform(5, 30), 2),
            "estimated_hours": estimated_hours,
            "actual_hours": actual_hours,
            "difficulty_level": random.randint(1, 5),
            "priority_rating": random.randint(1, 5),
            "completed": random.choice([True, False]),
            "completion_date": completion_date.strftime("%Y-%m-%d") if random.choice([True, False]) else None,
            "notes": "" if random.random() > 0.3 else "Important task" if random.random() > 0.5 else "Group project",
            "is_synthetic": True
        }
        data.append(item)
    
    return data

def save_to_supabase(supabase: Client, data: list):
    """Save generated data to Supabase."""
    try:
        # Insert in batches of 50 to avoid timeouts
        batch_size = 50
        total_saved = 0
        
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            result = supabase.table("survey_responses").insert(batch).execute()
            total_saved += len(batch)
            print(f"Saved {total_saved}/{len(data)} records...")
            
        return total_saved
    except Exception as e:
        print(f"Error saving to Supabase: {str(e)}")
        return 0

def main():
    try:
        load_environment()
        supabase = get_supabase_client()
        
        print("Generating 200 synthetic survey responses...")
        synthetic_data = generate_synthetic_data(200)
        
        print(f"Saving {len(synthetic_data)} records to Supabase...")
        saved_count = save_to_supabase(supabase, synthetic_data)
        
        print(f"\nSuccessfully generated and saved {saved_count} synthetic survey responses!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
