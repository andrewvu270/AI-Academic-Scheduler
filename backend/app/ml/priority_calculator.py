from datetime import datetime, date
from typing import Dict, Any

class PriorityCalculator:
    def calculate_priority_score(self, task: Dict[str, Any], current_date: date = None) -> float:
        """Calculate priority score for a task"""
        if current_date is None:
            current_date = date.today()
        
        weight_score = task.get('weight_score', 0.5)
        due_date = task.get('due_date')
        predicted_hours = task.get('predicted_hours', 4.0)
        
        # Calculate days until due
        if isinstance(due_date, str):
            due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
        elif isinstance(due_date, datetime):
            due_date = due_date.date()
        
        days_until_due = (due_date - current_date).days
        urgency_factor = 1 / max(days_until_due, 1)  # Avoid division by zero
        
        # Calculate priority
        priority = (
            0.5 * weight_score +
            0.3 * urgency_factor +
            0.2 * min(predicted_hours / 10, 1.0)  # Normalize hours (cap at 10 hours)
        )
        
        return priority