"""
Integration Tests for Agent API Endpoints

Tests the full API integration with agents.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app

client = TestClient(app)


class TestAgentAPIEndpoints:
    """Integration tests for agent API endpoints"""
    
    def test_parse_endpoint(self):
        """Test /api/v2/agents/parse endpoint"""
        with patch('app.agents.task_parsing_agent.llm_service') as mock_llm:
            mock_llm.extract_tasks_from_text = AsyncMock(return_value=[
                {
                    "title": "Assignment 1",
                    "task_type": "Assignment",
                    "due_date": "2025-12-15"
                }
            ])
            
            response = client.post(
                "/api/v2/agents/parse",
                json={
                    "text": "Assignment 1 due December 15",
                    "source_type": "document"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["count"] == 1
    
    def test_predict_endpoint(self):
        """Test /api/v2/agents/predict endpoint"""
        with patch('app.agents.workload_prediction_agent.llm_service') as mock_llm:
            mock_llm.analyze_task_workload = AsyncMock(return_value={
                "estimated_hours": 5.0,
                "stress_score": 0.6,
                "complexity": "medium",
                "explanation": "Test",
                "confidence": 0.8
            })
            
            response = client.post(
                "/api/v2/agents/predict",
                json={
                    "task": {
                        "title": "Research Paper",
                        "task_type": "Assignment"
                    }
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["prediction"]["estimated_hours"] == 5.0
    
    def test_prioritize_endpoint(self):
        """Test /api/v2/agents/prioritize endpoint"""
        with patch('app.agents.prioritization_agent.llm_service') as mock_llm:
            mock_llm.prioritize_tasks = AsyncMock(return_value={
                "priorities": ["task1", "task2"],
                "explanations": {},
                "recommendations": []
            })
            
            response = client.post(
                "/api/v2/agents/prioritize",
                json={
                    "tasks": [
                        {"id": "task1", "title": "Task 1"},
                        {"id": "task2", "title": "Task 2"}
                    ]
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["priorities"]) == 2
    
    def test_schedule_endpoint(self):
        """Test /api/v2/agents/schedule endpoint"""
        response = client.post(
            "/api/v2/agents/schedule",
            json={
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
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "schedule" in data
    
    def test_query_endpoint(self):
        """Test /api/v2/agents/query endpoint"""
        with patch('app.agents.natural_language_agent.llm_service') as mock_llm:
            mock_llm.parse_natural_language_query = AsyncMock(return_value={
                "intent": "view_schedule",
                "parameters": {},
                "action": "show_schedule",
                "response": "Here's your schedule"
            })
            
            response = client.post(
                "/api/v2/agents/query",
                json={
                    "query": "Show me my schedule"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["intent"] == "view_schedule"
    
    def test_status_endpoint(self):
        """Test /api/v2/agents/status endpoint"""
        response = client.get("/api/v2/agents/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["mcp_status"] == "active"
        assert "agents" in data
        assert len(data["agents"]) == 5
    
    def test_pipeline_endpoint(self):
        """Test /api/v2/agents/pipeline endpoint (full workflow)"""
        with patch('app.agents.task_parsing_agent.llm_service') as mock_parse, \
             patch('app.agents.workload_prediction_agent.llm_service') as mock_predict, \
             patch('app.agents.prioritization_agent.llm_service') as mock_priority:
            
            mock_parse.extract_tasks_from_text = AsyncMock(return_value=[
                {
                    "title": "Assignment 1",
                    "task_type": "Assignment",
                    "due_date": "2025-12-15"
                }
            ])
            
            mock_predict.analyze_task_workload = AsyncMock(return_value={
                "estimated_hours": 3.0,
                "stress_score": 0.5,
                "complexity": "medium",
                "explanation": "Test",
                "confidence": 0.8
            })
            
            mock_priority.prioritize_tasks = AsyncMock(return_value={
                "priorities": ["Assignment 1"],
                "explanations": {},
                "recommendations": []
            })
            
            response = client.post(
                "/api/v2/agents/pipeline",
                json={
                    "text": "Assignment 1 due December 15",
                    "source_type": "syllabus",
                    "schedule_days": 7
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "stages" in data
            assert "tasks" in data
            assert "schedule" in data
