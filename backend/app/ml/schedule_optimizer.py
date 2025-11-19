from typing import List, Dict, Any
from datetime import date, datetime, timedelta

class ScheduleOptimizer:
    def generate_daily_schedule(
        self, 
        tasks: List[Dict[str, Any]], 
        available_hours: float, 
        current_date: date = None
    ) -> List[Dict[str, Any]]:
        """Generate optimized daily schedule"""
        if current_date is None:
            current_date = date.today()
        
        # Filter tasks that need work
        pending_tasks = [
            task for task in tasks 
            if task.get('status') == 'pending' and task.get('due_date')
        ]
        
        # Sort by priority score (descending)
        sorted_tasks = sorted(
            pending_tasks, 
            key=lambda x: x.get('priority_score', 0), 
            reverse=True
        )
        
        schedule = []
        remaining_hours = available_hours
        
        for task in sorted_tasks:
            if remaining_hours <= 0:
                break
            
            # Determine how much time to allocate to this task
            task_hours = min(task.get('predicted_hours', 4.0), remaining_hours)
            
            # Add to schedule
            schedule.append({
                'task_id': task.get('id'),
                'title': task.get('title'),
                'course': task.get('course_code'),
                'allocated_hours': task_hours,
                'priority': task.get('priority_score', 0),
                'due_date': task.get('due_date'),
                'task_type': task.get('task_type')
            })
            
            remaining_hours -= task_hours
        
        return schedule
    
    def generate_weekly_schedule(
        self, 
        tasks: List[Dict[str, Any]], 
        daily_hours: Dict[str, float],
        start_date: date = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Generate optimized weekly schedule"""
        if start_date is None:
            start_date = date.today()
        
        weekly_schedule = {}
        remaining_tasks = tasks.copy()
        
        # Generate schedule for each day of the week
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            day_name = current_date.strftime('%A').lower()
            available_hours = daily_hours.get(day_name, 2.0)
            
            if available_hours > 0 and remaining_tasks:
                daily_schedule = self.generate_daily_schedule(
                    remaining_tasks, available_hours, current_date
                )
                weekly_schedule[day_name] = daily_schedule
                
                # Remove allocated tasks from remaining list
                allocated_task_ids = {item['task_id'] for item in daily_schedule}
                remaining_tasks = [
                    task for task in remaining_tasks 
                    if task.get('id') not in allocated_task_ids
                ]
            else:
                weekly_schedule[day_name] = []
        
        return weekly_schedule