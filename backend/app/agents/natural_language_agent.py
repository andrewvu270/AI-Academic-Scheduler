"""
Natural Language Agent

Handles natural language queries and commands.
Interprets user intent and triggers appropriate agents.
"""

from typing import Any, Dict, Optional
from ..agents.agent_base import BaseAgent, AgentResponse
from ..services.llm_service import llm_service
import logging

logger = logging.getLogger(__name__)


class NaturalLanguageAgent(BaseAgent):
    """Agent for processing natural language queries"""
    
    def __init__(self):
        super().__init__("NaturalLanguageAgent")
        self.llm = llm_service
    
    async def process(
        self, 
        input_data: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Process natural language query.
        
        Input data should contain:
        - query: User's natural language query
        
        Returns:
            AgentResponse with parsed intent and suggested action
        """
        query = input_data.get("query", "")
        
        if not query:
            return self._create_response(
                data={"intent": "unknown"},
                confidence=0.0,
                explanation="No query provided"
            )
        
        # Parse query using LLM
        parsed = await self.llm.parse_natural_language_query(query, context)
        
        # Validate and enrich parsed result
        enriched = self._enrich_parsed_query(parsed, context)
        
        return self._create_response(
            data={
                "intent": enriched["intent"],
                "parameters": enriched.get("parameters", {}),
                "action": enriched.get("action", ""),
                "response": enriched.get("response", "")
            },
            confidence=0.85,
            explanation=f"Interpreted query as: {enriched['intent']}",
            metadata={
                "query": query,
                "raw_parsed": parsed
            }
        )
    
    def _enrich_parsed_query(
        self, 
        parsed: Dict[str, Any], 
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Enrich parsed query with additional context"""
        enriched = parsed.copy()
        
        # Add context-aware defaults
        if context:
            if "user_id" in context:
                enriched.setdefault("parameters", {})["user_id"] = context["user_id"]
        
        # Normalize intent
        intent = enriched.get("intent", "unknown").lower()
        enriched["intent"] = self._normalize_intent(intent)
        
        return enriched
    
    def _normalize_intent(self, intent: str) -> str:
        """Normalize intent to standard format"""
        intent_mapping = {
            "view_schedule": ["schedule", "calendar", "view", "show"],
            "move_task": ["move", "reschedule", "shift", "defer"],
            "get_insights": ["insights", "analytics", "stats", "summary"],
            "prioritize": ["priority", "important", "urgent"],
            "add_task": ["add", "create", "new"],
            "complete_task": ["complete", "done", "finish"],
            "delete_task": ["delete", "remove", "cancel"]
        }
        
        for standard_intent, keywords in intent_mapping.items():
            if any(keyword in intent for keyword in keywords):
                return standard_intent
        
        return intent


# Create singleton instance
natural_language_agent = NaturalLanguageAgent()
