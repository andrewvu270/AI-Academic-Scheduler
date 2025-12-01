"""
Agent Unit Tests

Tests for individual MyDesk agents.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.agents.task_parsing_agent import task_parsing_agent
from app.agents.workload_prediction_agent import workload_prediction_agent
from app.agents.prioritization_agent import prioritization_agent
from app.agents.schedule_optimization_agent import schedule_optimization_agent
from app.agents.natural_language_agent import natural_language_agent
from app.agents.agent_base import AgentStatus


class TestTaskParsingAgent:
    """Tests for Task Parsing Agent"""
    
    @pytest.mark.asyncio
    async def test_parse_simple_text(self):
        """Test parsing simple text with tasks"""
        with patch('app.agents.task_parsing_agent.llm_service') as mock_llm:
            mock_llm.extract_tasks_from_text = AsyncMock(return_value=[
                {
                    "title": "Assignment 1",
                    "task_type": "Assignment",
                    "due_date": "2025-12-15",
                    "description": "Complete homework"
                }
            ])
            
            response = await task_parsing_agent._execute_with_error_handling({
                "text": "Assignment 1 due December 15",
                "source_type": "document"
            })
            
            assert response.status == AgentStatus.COMPLETED
            assert response.data["count"] == 1
            assert response.data["tasks"][0]["title"] == "Assignment 1"
    
    @pytest.mark.asyncio
    async def test_parse_empty_text(self):
        """Test parsing empty text"""
        response = await task_parsing_agent._execute_with_error_handling({
            "text": "",
            "source_type": "document"
        })
        
        assert response.status == AgentStatus.COMPLETED
        assert response.data["count"] == 0
        assert response.confidence == 0.0


class TestWorkloadPredictionAgent:
    """Tests for Workload Prediction Agent"""
    
    @pytest.mark.asyncio
    async def test_predict_workload_llm_only(self):
        """Test workload prediction using LLM only"""
        with patch('app.agents.workload_prediction_agent.llm_service') as mock_llm:
            mock_llm.analyze_task_workload = AsyncMock(return_value={
                "estimated_hours": 5.0,
                "stress_score": 0.6,
                "complexity": "medium",
                "explanation": "Test explanation",
                "confidence": 0.8
            })
            
            task = {
                "title": "Research Paper",
                "description": "Write 10-page research paper",
                "task_type": "Assignment"
            }
            
            response = await workload_prediction_agent._execute_with_error_handling({
                "task": task,
                "use_hybrid": False
            })
            
            assert response.status == AgentStatus.COMPLETED
            assert response.data["estimated_hours"] == 5.0
            assert response.data["stress_score"] == 0.6
            assert response.data["complexity"] == "medium"
    
    @pytest.mark.asyncio
    async def test_predict_workload_hybrid(self):
        """Test hybrid LLM + ML prediction"""
        with patch('app.agents.workload_prediction_agent.llm_service') as mock_llm, \
             patch('app.agents.workload_prediction_agent.ml_service') as mock_ml:
            
            mock_llm.analyze_task_workload = AsyncMock(return_value={
                "estimated_hours": 5.0,
                "stress_score": 0.6,
                "complexity": "medium",
                "explanation": "Test explanation",
                "confidence": 0.8
            })
            
            mock_ml.is_trained = True
            mock_ml.predict_workload = AsyncMock(return_value=4.5)
            
            task = {
                "title": "Research Paper",
                "task_type": "Assignment"
            }
            
            response = await workload_prediction_agent._execute_with_error_handling({
                "task": task,
                "use_hybrid": True
            })
            
            assert response.status == AgentStatus.COMPLETED
            # Should be weighted average of LLM (5.0) and ML (4.5)
            assert 4.5 <= response.data["estimated_hours"] <= 5.0


class TestPrioritizationAgent:
    """Tests for Prioritization Agent"""
    
    @pytest.mark.asyncio
    async def test_prioritize_tasks(self):
        """Test task prioritization"""
        with patch('app.agents.prioritization_agent.llm_service') as mock_llm:
            mock_llm.prioritize_tasks = AsyncMock(return_value={
                "priorities": ["task1", "task2"],
                "explanations": {
                    "task1": "High priority due to deadline",
                    "task2": "Medium priority"
                },
                "recommendations": ["Focus on task1 first"]
            })
            
            tasks = [
                {
                    "id": "task1",
                    "title": "Urgent Assignment",
                    "due_date": "2025-12-05",
                    "grade_percentage": 30
                },
                {
                    "id": "task2",
                    "title": "Reading",
                    "due_date": "2025-12-20",
                    "grade_percentage": 10
                }
            ]
            
            response = await prioritization_agent._execute_with_error_handling({
                "tasks": tasks
            })
            
            assert response.status == AgentStatus.COMPLETED
            assert len(response.data["priorities"]) == 2
            assert response.data["priorities"][0]["task_id"] == "task1"
    
    @pytest.mark.asyncio
    async def test_prioritize_empty_tasks(self):
        """Test prioritization with no tasks"""
        response = await prioritization_agent._execute_with_error_handling({
            "tasks": []
        })
        
        assert response.status == AgentStatus.COMPLETED
        assert len(response.data["priorities"]) == 0


class TestScheduleOptimizationAgent:
    """Tests for Schedule Optimization Agent"""
    
    @pytest.mark.asyncio
    async def test_generate_schedule(self):
        """Test schedule generation"""
        tasks = [
            {
                "id": "task1",
                "title": "Assignment 1",
                "estimated_hours": 3.0,
                "stress_score": 0.5,
                "priority_score": 0.8,
                "due_date": "2025-12-10"
            },
            {
                "id": "task2",
                "title": "Reading",
                "estimated_hours": 2.0,
                "stress_score": 0.3,
                "priority_score": 0.5,
                "due_date": "2025-12-15"
            }
        ]
        
        response = await schedule_optimization_agent._execute_with_error_handling({
            "tasks": tasks,
            "start_date": "2025-12-01",
            "days": 7
        })
        
        assert response.status == AgentStatus.COMPLETED
        assert "schedule" in response.data
        assert "workload_analysis" in response.data
        assert len(response.data["schedule"]) == 7
    
    @pytest.mark.asyncio
    async def test_detect_overload(self):
        """Test overload detection"""
        # Create tasks that exceed daily limit
        tasks = [
            {
                "id": f"task{i}",
                "title": f"Task {i}",
                "estimated_hours": 3.0,
                "stress_score": 0.7,
                "priority_score": 0.8,
                "due_date": "2025-12-02"
            }
            for i in range(5)  # 15 hours total
        ]
        
        response = await schedule_optimization_agent._execute_with_error_handling({
            "tasks": tasks,
            "start_date": "2025-12-01",
            "days": 7
        })
        
        assert response.status == AgentStatus.COMPLETED
        assert len(response.data["overload_days"]) > 0


class TestNaturalLanguageAgent:
    """Tests for Natural Language Agent"""
    
    @pytest.mark.asyncio
    async def test_parse_query(self):
        """Test natural language query parsing"""
        with patch('app.agents.natural_language_agent.llm_service') as mock_llm:
            mock_llm.parse_natural_language_query = AsyncMock(return_value={
                "intent": "view_schedule",
                "parameters": {"days": 7},
                "action": "show_schedule",
                "response": "Here's your schedule for the next 7 days"
            })
            
            response = await natural_language_agent._execute_with_error_handling({
                "query": "Show me my schedule for the next week"
            })
            
            assert response.status == AgentStatus.COMPLETED
            assert response.data["intent"] == "view_schedule"
            assert "response" in response.data
    
    @pytest.mark.asyncio
    async def test_empty_query(self):
        """Test empty query"""
        response = await natural_language_agent._execute_with_error_handling({
            "query": ""
        })
        
        assert response.status == AgentStatus.COMPLETED
        assert response.data["intent"] == "unknown"
        assert response.confidence == 0.0
