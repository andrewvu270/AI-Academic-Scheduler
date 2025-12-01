"""
Schedule Optimization Agent

Generates optimized daily/weekly schedules while avoiding burnout.
Balances workload and detects stress thresholds.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from ..agents.agent_base import BaseAgent, AgentResponse
import logging

logger = logging.getLogger(__name__)


class ScheduleOptimizationAgent(BaseAgent):
    """Agent for optimizing task schedules"""
    
    def __init__(self):
        super().__init__("ScheduleOptimizationAgent")
        self.max_daily_hours = 8.0  # Maximum recommended work hours per day
        self.stress_threshold = 0.7  # Stress threshold for warnings
    
    async def process(
        self, 
        input_data: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Generate optimized schedule for tasks.
        
        Input data should contain:
        - tasks: List of tasks with priorities and estimates
        - start_date: Schedule start date (optional)
        - days: Number of days to schedule (default: 7)
        
        Returns:
            AgentResponse with optimized schedule
        """
        tasks = input_data.get("tasks", [])
        start_date_str = input_data.get("start_date")
        days = input_data.get("days", 7)
        
        if not tasks:
            return self._create_response(
                data={"schedule": {}},
                confidence=0.0,
                explanation="No tasks to schedule"
            )
        
        # Parse start date
        if start_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        else:
            start_date = datetime.now()
        
        # Generate schedule
        schedule = self._generate_schedule(tasks, start_date, days)
        
        # Analyze workload
        workload_analysis = self._analyze_workload(schedule)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            schedule, 
            workload_analysis
        )
        
        return self._create_response(
            data={
                "schedule": schedule,
                "workload_analysis": workload_analysis,
                "recommendations": recommendations,
                "overload_days": workload_analysis["overload_days"]
            },
            confidence=0.8,
            explanation=f"Generated {days}-day schedule with workload balancing",
            metadata={
                "total_tasks": len(tasks),
                "total_hours": workload_analysis["total_hours"],
                "avg_daily_hours": workload_analysis["avg_daily_hours"]
            }
        )
    
    def _generate_schedule(
        self, 
        tasks: List[Dict[str, Any]], 
        start_date: datetime, 
        days: int
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Generate optimized schedule"""
        schedule = {}
        
        # Initialize days
        for i in range(days):
            date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            schedule[date] = []
        
        # Sort tasks by priority and deadline
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (
                -t.get("priority_score", 0.5),
                t.get("due_date", "9999-12-31")
            )
        )
        
        # Distribute tasks across days
        for task in sorted_tasks:
            best_day = self._find_best_day(task, schedule, start_date, days)
            if best_day:
                schedule[best_day].append({
                    "task_id": task.get("id", task.get("title")),
                    "title": task.get("title", "Untitled"),
                    "estimated_hours": task.get("estimated_hours", 3.0),
                    "stress_score": task.get("stress_score", 0.5),
                    "priority_score": task.get("priority_score", 0.5),
                    "due_date": task.get("due_date")
                })
        
        return schedule
    
    def _find_best_day(
        self, 
        task: Dict[str, Any], 
        schedule: Dict[str, List[Dict[str, Any]]],
        start_date: datetime,
        days: int
    ) -> Optional[str]:
        """Find the best day to schedule a task"""
        due_date = task.get("due_date")
        estimated_hours = task.get("estimated_hours", 3.0)
        
        # Determine deadline constraint
        if due_date:
            try:
                due = datetime.strptime(due_date, "%Y-%m-%d")
                max_day = min(days, (due - start_date).days + 1)
            except:
                max_day = days
        else:
            max_day = days
        
        # Find day with lowest workload that's before deadline
        best_day = None
        min_workload = float('inf')
        
        for i in range(max(max_day, 1)):
            date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            if date not in schedule:
                continue
            
            current_workload = sum(
                t.get("estimated_hours", 0) for t in schedule[date]
            )
            
            # Check if adding this task would exceed max hours
            if current_workload + estimated_hours <= self.max_daily_hours:
                if current_workload < min_workload:
                    min_workload = current_workload
                    best_day = date
        
        # If no suitable day found, use earliest available day
        if not best_day and max_day > 0:
            best_day = (start_date + timedelta(days=0)).strftime("%Y-%m-%d")
        
        return best_day
    
    def _analyze_workload(
        self, 
        schedule: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Analyze workload across schedule"""
        daily_hours = {}
        daily_stress = {}
        overload_days = []
        
        for date, tasks in schedule.items():
            total_hours = sum(t.get("estimated_hours", 0) for t in tasks)
            avg_stress = (
                sum(t.get("stress_score", 0.5) for t in tasks) / len(tasks)
                if tasks else 0.0
            )
            
            daily_hours[date] = round(total_hours, 1)
            daily_stress[date] = round(avg_stress, 2)
            
            if total_hours > self.max_daily_hours or avg_stress > self.stress_threshold:
                overload_days.append({
                    "date": date,
                    "hours": round(total_hours, 1),
                    "stress": round(avg_stress, 2),
                    "reason": "High workload" if total_hours > self.max_daily_hours else "High stress"
                })
        
        total_hours = sum(daily_hours.values())
        avg_daily_hours = total_hours / len(schedule) if schedule else 0
        
        return {
            "daily_hours": daily_hours,
            "daily_stress": daily_stress,
            "total_hours": round(total_hours, 1),
            "avg_daily_hours": round(avg_daily_hours, 1),
            "overload_days": overload_days,
            "peak_day": max(daily_hours.items(), key=lambda x: x[1])[0] if daily_hours else None
        }
    
    def _generate_recommendations(
        self, 
        schedule: Dict[str, List[Dict[str, Any]]],
        workload_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate schedule recommendations"""
        recommendations = []
        
        # Check for overload
        if workload_analysis["overload_days"]:
            recommendations.append(
                f"⚠️ {len(workload_analysis['overload_days'])} day(s) have high workload or stress. Consider redistributing tasks."
            )
        
        # Check for uneven distribution
        daily_hours = list(workload_analysis["daily_hours"].values())
        if daily_hours:
            variance = max(daily_hours) - min(daily_hours)
            if variance > 4.0:
                recommendations.append(
                    "📊 Workload is unevenly distributed. Consider balancing tasks across days."
                )
        
        # Check average workload
        avg_hours = workload_analysis["avg_daily_hours"]
        if avg_hours > 6.0:
            recommendations.append(
                f"⏰ Average daily workload is {avg_hours} hours. Consider extending the schedule or deferring low-priority tasks."
            )
        elif avg_hours < 2.0:
            recommendations.append(
                "✅ Workload is manageable. You have capacity for additional tasks if needed."
            )
        
        return recommendations


# Create singleton instance
schedule_optimization_agent = ScheduleOptimizationAgent()
