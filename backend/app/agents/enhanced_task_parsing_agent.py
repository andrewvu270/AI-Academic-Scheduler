"""
Enhanced Task Parsing Agent with MCP Integration

Uses MCP servers for file operations, web search, and memory.
"""

from typing import Any, Dict, Optional, List
from ..agents.agent_base import BaseAgent, AgentResponse
from ..services.llm_service import llm_service
from ..services.mcp_service import mcp_service
import logging

logger = logging.getLogger(__name__)


class EnhancedTaskParsingAgent(BaseAgent):
    """Enhanced task parsing agent with MCP capabilities"""
    
    def __init__(self):
        super().__init__("EnhancedTaskParsingAgent")
        self.llm = llm_service
        self.mcp = mcp_service
        
        # MCP tools this agent can use
        self.mcp_tools = {
            "filesystem": ["read_file", "write_file", "list_directory"],
            "web_search": ["web_search", "open_url"],
            "memory": ["save_memory", "retrieve_memory", "search_memory"],
            "wikipedia": ["wikipedia_summary"],
            "arxiv": ["arxiv_search"],
            "scholar": ["scholar_lookup"],
            "stackexchange": ["stackexchange_query"],
        }
    
    async def process(
        self, 
        input_data: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Enhanced task processing with MCP tools
        
        Can handle:
        - PDF files (via filesystem MCP)
        - Web research (via web search MCP)
        - Memory of past parsing (via memory MCP)
        """
        
        try:
            source_type = input_data.get("source_type", "document")
            text = input_data.get("text", "")
            file_path = input_data.get("file_path")
            user_id = input_data.get("user_id", "guest")
            
            # Step 1: Extract text using MCP if file path provided
            if file_path and not text:
                text = await self._extract_text_with_mcp(file_path)
            
            # Step 2: Retrieve memory of similar documents
            memory_context = await self._get_relevant_memory(text, user_id)
            
            # Step 3: Enhanced LLM processing with memory context
            enhanced_context = {
                **(context or {}),
                "memory_context": memory_context,
                "mcp_capabilities": list(self.mcp_tools.keys())
            }
            
            # Step 4: Parse tasks using LLM
            parsed_tasks = await self.llm.extract_tasks_from_text(text, source_type, enhanced_context)
            
            # Step 5: Enhance tasks with web research if needed
            enhanced_tasks = await self._enhance_tasks_with_research(parsed_tasks)
            
            # Step 6: Save parsing results to memory
            await self._save_parsing_memory(text, enhanced_tasks, user_id)
            
            return self._create_response(
                data={"tasks": enhanced_tasks},
                confidence=0.9,
                explanation=f"Enhanced task parsing using MCP tools. Extracted {len(enhanced_tasks)} tasks."
            )
            
        except Exception as e:
            logger.error(f"Enhanced task parsing failed: {str(e)}")
            return self._create_response(
                data={"tasks": []},
                confidence=0.0,
                explanation=f"Parsing failed: {str(e)}"
            )
    
    async def _extract_text_with_mcp(self, file_path: str) -> str:
        """Extract text from file using MCP filesystem server"""
        try:
            # Start filesystem MCP server
            await self.mcp.start_server("filesystem")
            
            # Read file using MCP
            result = await self.mcp.execute_tool(
                "filesystem", 
                "read_file", 
                {"path": file_path}
            )
            
            if "error" in result:
                raise Exception(f"Failed to read file: {result['error']}")
            
            return result["content"]
            
        except Exception as e:
            logger.error(f"MCP file extraction failed: {str(e)}")
            # Fallback to regular processing
            return ""
    
    async def _get_relevant_memory(self, text: str, user_id: str) -> Dict[str, Any]:
        """Retrieve relevant parsing memories"""
        try:
            await self.mcp.start_server("memory")
            
            # Search for similar document memories
            result = await self.mcp.execute_tool(
                "memory",
                "search_memory",
                {"query": f"document_parsing_{user_id}", "limit": 5}
            )
            
            if "error" not in result and "value" in result:
                return result["value"]
            
            return {}
            
        except Exception as e:
            logger.error(f"Memory retrieval failed: {str(e)}")
            return {}
    
    async def _enhance_tasks_with_research(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance tasks with web research using MCP"""
        try:
            await self.mcp.start_server("web_search")
            enhanced_tasks = []
            
            for task in tasks:
                enhanced_task = task.copy()
                research_sources: List[Dict[str, Any]] = []
                topic = self._derive_topic_from_task(task)
                
                # General web context for workload estimates
                if task.get("task_type"):
                    search_query = f"typical hours needed for {task['task_type']} {topic or 'assignment'}"
                    result = await self.mcp.execute_tool("web_search", "web_search", {"query": search_query})
                    if "error" not in result and "results" in result:
                        enhanced_task["research_insights"] = self._extract_time_insights(result["results"])
                        research_sources.append({
                            "source": "web_search",
                            "query": search_query,
                            "result_count": len(result["results"])
                        })

                # Subject-matter background from Wikipedia
                if topic:
                    await self.mcp.start_server("wikipedia")
                    wiki = await self.mcp.execute_tool("wikipedia", "wikipedia_summary", {"topic": topic})
                    if "error" not in wiki:
                        enhanced_task["wiki_summary"] = wiki.get("summary")
                        research_sources.append({
                            "source": "wikipedia",
                            "title": wiki.get("topic"),
                            "reference": wiki.get("references", [])
                        })

                # Deeper research for advanced/research tasks
                if self._needs_academic_sources(task):
                    await self.mcp.start_server("arxiv")
                    arxiv = await self.mcp.execute_tool("arxiv", "arxiv_search", {"query": topic or task.get("title", "")})
                    if "error" not in arxiv:
                        enhanced_task.setdefault("academic_sources", []).extend(arxiv.get("papers", []))
                        research_sources.append({"source": "arxiv", "query": arxiv.get("query")})

                    await self.mcp.start_server("scholar")
                    scholar = await self.mcp.execute_tool("scholar", "scholar_lookup", {"query": topic or task.get("title", "")})
                    if "error" not in scholar:
                        enhanced_task.setdefault("academic_sources", []).extend(scholar.get("articles", []))
                        research_sources.append({"source": "scholar", "query": scholar.get("query")})

                # Technical troubleshooting support via StackExchange
                if self._looks_like_stem_task(task):
                    await self.mcp.start_server("stackexchange")
                    stack = await self.mcp.execute_tool("stackexchange", "stackexchange_query", {"query": topic or task.get("title", "")})
                    if "error" not in stack:
                        enhanced_task.setdefault("community_answers", []).extend(stack.get("answers", []))
                        research_sources.append({"source": "stackexchange", "query": stack.get("query")})

                if research_sources:
                    enhanced_task["research_sources"] = research_sources
                enhanced_tasks.append(enhanced_task)

            return enhanced_tasks

        except Exception as e:
            logger.error(f"Web/knowledge research enhancement failed: {str(e)}")
            return tasks  # Return original tasks if enhancement fails

    def _derive_topic_from_task(self, task: Dict[str, Any]) -> Optional[str]:
        """Infer a topic keyword from the task"""
        title = task.get("title", "").strip()
        task_type = task.get("task_type", "").strip()
        if title:
            return title.split(':')[0][:60]
        if task_type:
            return task_type
        return None

    def _needs_academic_sources(self, task: Dict[str, Any]) -> bool:
        keywords = ["research", "paper", "thesis", "capstone", "project"]
        title = task.get("title", "").lower()
        description = (task.get("description", "") or "").lower()
        return any(k in title or k in description for k in keywords)

    def _looks_like_stem_task(self, task: Dict[str, Any]) -> bool:
        keywords = ["math", "physics", "chem", "cs", "program", "algorithm", "engineering"]
        title = task.get("title", "").lower()
        description = (task.get("description", "") or "").lower()
        return any(k in title or k in description for k in keywords)
    
    def _extract_time_insights(self, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract time estimates from web search results"""
        insights = {
            "typical_hours": None,
            "difficulty_factors": [],
            "recommendations": []
        }
        
        # Simple keyword-based extraction (in real implementation, use LLM)
        for result in search_results:
            snippet = result.get("snippet", "").lower()
            
            # Look for time patterns
            if "hour" in snippet or "hours" in snippet:
                insights["recommendations"].append(f"Research suggests: {snippet}")
            
            if "difficult" in snippet or "challenging" in snippet:
                insights["difficulty_factors"].append("May require extra time")
        
        return insights
    
    async def _save_parsing_memory(self, text: str, tasks: List[Dict[str, Any]], user_id: str):
        """Save parsing results to memory for future reference"""
        try:
            await self.mcp.start_server("memory")
            
            memory_key = f"parsing_{user_id}_{hash(text) % 10000}"
            memory_data = {
                "text_preview": text[:200],  # First 200 chars
                "task_count": len(tasks),
                "task_types": [task.get("task_type") for task in tasks],
                "timestamp": str(asyncio.get_event_loop().time())
            }
            
            await self.mcp.execute_tool(
                "memory",
                "save_memory",
                {"key": memory_key, "value": memory_data}
            )
            
        except Exception as e:
            logger.error(f"Memory saving failed: {str(e)}")
    
    async def get_capabilities(self) -> Dict[str, List[str]]:
        """Return MCP capabilities of this agent"""
        return self.mcp_tools


# Create enhanced instance
enhanced_task_parsing_agent = EnhancedTaskParsingAgent()
