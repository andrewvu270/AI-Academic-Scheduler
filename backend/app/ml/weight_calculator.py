from typing import Dict, Any, List

class TaskWeightCalculator:
    def __init__(self):
        # Base weights for different task types
        self.type_weights = {
            'Final': 0.95,
            'Exam': 0.9,
            'Midterm': 0.85,
            'Project': 0.8,
            'Assignment': 0.7,
            'Lab': 0.65,
            'Quiz': 0.6,
            'Reading': 0.4
        }
        
        # Importance keywords and their weights
        self.importance_keywords = {
            'critical': 0.9,
            'major': 0.8,
            'important': 0.7,
            'mandatory': 0.85,
            'required': 0.75,
            'key': 0.6,
            'essential': 0.8,
            'significant': 0.7
        }
    
    def calculate_weight_score(self, task_data: Dict[str, Any]) -> float:
        """Calculate weight score for a task"""
        task_type = task_data.get('task_type', 'Assignment')
        grade_percentage = task_data.get('grade_percentage', 0)
        importance_keywords = task_data.get('importance_keywords', [])
        
        # Get type importance
        type_importance = self.type_weights.get(task_type, 0.5)
        
        # Calculate instructor importance based on keywords
        instructor_importance = 0.5  # default
        for keyword in importance_keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in self.importance_keywords:
                instructor_importance = max(
                    instructor_importance, 
                    self.importance_keywords[keyword_lower]
                )
        
        # Normalize grade percentage (0-1)
        normalized_grade = min(grade_percentage / 100, 1.0) if grade_percentage else 0.5
        
        # Calculate final weight
        weight = (
            0.3 * normalized_grade +
            0.4 * type_importance +
            0.3 * instructor_importance
        )
        
        return min(weight, 1.0)  # Ensure weight doesn't exceed 1.0