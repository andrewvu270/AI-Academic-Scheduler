"""
MCP Integration Tests

Tests for MCP orchestrator and full workflow pipelines.
"""

import pytest
from unittest.mock import AsyncMock, patch
from app.agents.mcp_orchestrator import mcp_orchestrator, WorkflowType
from app.agents.agent_base import AgentStatus


class TestMCPOrchestrator:
    """Tests for MCP Orchestrator"""
    
    @pytest.mark.asyncio
    async def test_parse_document_workflow(self):
        """Test document parsing workflow"""
        with patch('app.agents.task_parsing_agent.llm_service') as mock_llm:
            mock_llm.extract_tasks_from_text = AsyncMock(return_value=[
                {
                    "title": "Test Task",
                    "task_type": "Assignment",
                    "due_date": "2025-12-15"
                }
            ])
            
            result = await mcp_orchestrator.execute_workflow(
                WorkflowType.PARSE_DOCUMENT,
                {
                    "text": "Test document with tasks",
                    "source_type": "pdf"
                }
            )
            
            assert result["success"] is True
            assert result["workflow"] == "parse_document"
            assert result["count"] == 1
    
    @pytest.mark.asyncio
    async def test_predict_workload_workflow(self):
        """Test workload prediction workflow"""
        with patch('app.agents.workload_prediction_agent.llm_service') as mock_llm:
            mock_llm.analyze_task_workload = AsyncMock(return_value={
                "estimated_hours": 4.0,
                "stress_score": 0.5,
                "complexity": "medium",
                "explanation": "Test",
                "confidence": 0.8
            })
            
            result = await mcp_orchestrator.execute_workflow(
                WorkflowType.PREDICT_WORKLOAD,
                {
                    "task": {
                        "title": "Test Task",
                        "task_type": "Assignment"
                    }
                }
            )
            
            assert result["success"] is True
            assert result["workflow"] == "predict_workload"
            assert result["prediction"]["estimated_hours"] == 4.0
    
    @pytest.mark.asyncio
    async def test_prioritize_tasks_workflow(self):
        """Test task prioritization workflow"""
        with patch('app.agents.prioritization_agent.llm_service') as mock_llm:
            mock_llm.prioritize_tasks = AsyncMock(return_value={
                "priorities": ["task1", "task2"],
                "explanations": {},
                "recommendations": []
            })
            
            result = await mcp_orchestrator.execute_workflow(
                WorkflowType.PRIORITIZE_TASKS,
                {
                    "tasks": [
                        {"id": "task1", "title": "Task 1"},
                        {"id": "task2", "title": "Task 2"}
                    ]
                }
            )
            
            assert result["success"] is True
            assert result["workflow"] == "prioritize_tasks"
            assert len(result["priorities"]) == 2
    
    @pytest.mark.asyncio
    async def test_generate_schedule_workflow(self):
        """Test schedule generation workflow"""
        result = await mcp_orchestrator.execute_workflow(
            WorkflowType.GENERATE_SCHEDULE,
            {
                "tasks": [
                    {
                        "id": "task1",
                        "title": "Task 1",
                        "estimated_hours": 3.0,
                        "stress_score": 0.5,
                        "priority_score": 0.8,
                        "due_date": "2025-12-10"
                    }
                ],
                "days": 7
            }
        )
        
        assert result["success"] is True
        assert result["workflow"] == "generate_schedule"
        assert "schedule" in result
        assert "workload_analysis" in result
    
    @pytest.mark.asyncio
    async def test_natural_language_workflow(self):
        """Test natural language query workflow"""
        with patch('app.agents.natural_language_agent.llm_service') as mock_llm:
            mock_llm.parse_natural_language_query = AsyncMock(return_value={
                "intent": "view_schedule",
                "parameters": {},
                "action": "show_schedule",
                "response": "Here's your schedule"
            })
            
            result = await mcp_orchestrator.execute_workflow(
                WorkflowType.NATURAL_LANGUAGE_QUERY,
                {
                    "query": "Show me my schedule"
                }
            )
            
            assert result["success"] is True
            assert result["workflow"] == "natural_language_query"
            assert result["intent"] == "view_schedule"
    
    @pytest.mark.asyncio
    async def test_full_pipeline_workflow(self):
        """Test complete pipeline: Parse → Predict → Prioritize → Schedule"""
        with patch('app.agents.task_parsing_agent.llm_service') as mock_parse_llm, \
             patch('app.agents.workload_prediction_agent.llm_service') as mock_predict_llm, \
             patch('app.agents.prioritization_agent.llm_service') as mock_priority_llm:
            
            # Mock task parsing
            mock_parse_llm.extract_tasks_from_text = AsyncMock(return_value=[
                {
                    "title": "Assignment 1",
                    "task_type": "Assignment",
                    "due_date": "2025-12-15",
                    "description": "Complete homework"
                },
                {
                    "title": "Quiz 1",
                    "task_type": "Quiz",
                    "due_date": "2025-12-10",
                    "description": "Study for quiz"
                }
            ])
            
            # Mock workload prediction
            mock_predict_llm.analyze_task_workload = AsyncMock(return_value={
                "estimated_hours": 3.0,
                "stress_score": 0.5,
                "complexity": "medium",
                "explanation": "Test",
                "confidence": 0.8
            })
            
            # Mock prioritization
            mock_priority_llm.prioritize_tasks = AsyncMock(return_value={
                "priorities": ["Assignment 1", "Quiz 1"],
                "explanations": {},
                "recommendations": []
            })
            
            result = await mcp_orchestrator.execute_workflow(
                WorkflowType.FULL_PIPELINE,
                {
                    "text": "Assignment 1 due Dec 15. Quiz 1 on Dec 10.",
                    "source_type": "syllabus",
                    "schedule_days": 7
                }
            )
            
            assert result["success"] is True
            assert result["workflow"] == "full_pipeline"
            assert "stages" in result
            assert result["stages"]["parsing"]["success"] is True
            assert result["stages"]["workload_prediction"]["success"] is True
            assert result["stages"]["prioritization"]["success"] is True
            assert result["stages"]["scheduling"]["success"] is True
            assert "tasks" in result
            assert "schedule" in result
            assert len(result["tasks"]) == 2
    
    @pytest.mark.asyncio
    async def test_unknown_workflow(self):
        """Test handling of unknown workflow type"""
        result = await mcp_orchestrator.execute_workflow(
            "unknown_workflow",
            {}
        )
        
        assert result["success"] is False
        assert "error" in result
    
    def test_get_agent_status(self):
        """Test getting agent status"""
        status = mcp_orchestrator.get_agent_status()
        
        assert status["mcp_status"] == "active"
        assert "agents" in status
        assert len(status["agents"]) == 5
        assert "task_parsing" in status["agents"]
        assert "workload_prediction" in status["agents"]
        assert "prioritization" in status["agents"]
        assert "schedule_optimization" in status["agents"]
        assert "natural_language" in status["agents"]
