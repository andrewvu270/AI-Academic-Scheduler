"""
Base Agent Class

Provides the foundation for all MyDesk agents with standard interface,
logging, error handling, and communication protocols.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class AgentStatus(str, Enum):
    """Agent execution status"""
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class AgentResponse(BaseModel):
    """Standardized agent response format"""
    agent_type: str = Field(..., description="Type of agent that generated this response")
    status: AgentStatus = Field(..., description="Execution status")
    data: Dict[str, Any] = Field(default_factory=dict, description="Response data")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score")
    explanation: Optional[str] = Field(None, description="Human-readable explanation")
    error: Optional[str] = Field(None, description="Error message if status is ERROR")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BaseAgent(ABC):
    """
    Base class for all MyDesk agents.
    
    All agents must implement:
    - process(): Main processing logic
    - get_state(): Return current agent state
    - update_state(): Update agent state
    """
    
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.status = AgentStatus.IDLE
        self.state: Dict[str, Any] = {}
        self.logger = logging.getLogger(f"{__name__}.{agent_type}")
        self.logger.info(f"Initialized {agent_type} agent")
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Process input data and return agent response.
        
        Args:
            input_data: Input data for the agent to process
            context: Optional context from MCP or other agents
            
        Returns:
            AgentResponse with results
        """
        pass
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get current agent state.
        
        Returns:
            Dictionary containing agent state
        """
        return {
            "agent_type": self.agent_type,
            "status": self.status.value,
            "state": self.state,
            "timestamp": datetime.now().isoformat()
        }
    
    def update_state(self, new_state: Dict[str, Any]) -> None:
        """
        Update agent state.
        
        Args:
            new_state: New state data to merge with existing state
        """
        self.state.update(new_state)
        self.logger.debug(f"Updated state: {self.state}")
    
    async def _execute_with_error_handling(
        self, 
        input_data: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Execute process with error handling wrapper.
        
        Args:
            input_data: Input data
            context: Optional context
            
        Returns:
            AgentResponse
        """
        try:
            self.status = AgentStatus.PROCESSING
            self.logger.info(f"Processing input: {input_data.get('type', 'unknown')}")
            
            response = await self.process(input_data, context)
            
            self.status = AgentStatus.COMPLETED
            return response
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.logger.error(f"Error in {self.agent_type}: {str(e)}", exc_info=True)
            
            return AgentResponse(
                agent_type=self.agent_type,
                status=AgentStatus.ERROR,
                error=str(e),
                confidence=0.0
            )
    
    def _create_response(
        self,
        data: Dict[str, Any],
        confidence: float = 1.0,
        explanation: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Helper to create standardized response.
        
        Args:
            data: Response data
            confidence: Confidence score
            explanation: Optional explanation
            metadata: Optional metadata
            
        Returns:
            AgentResponse
        """
        return AgentResponse(
            agent_type=self.agent_type,
            status=AgentStatus.COMPLETED,
            data=data,
            confidence=confidence,
            explanation=explanation,
            metadata=metadata or {}
        )
