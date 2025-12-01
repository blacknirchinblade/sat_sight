import logging
from typing import Dict, Any
from sat_sight.core.state import AgentState
from sat_sight.tools.tavily_search_wrapper import TavilySearchTool
from sat_sight.core.config import DEBUG

logger = logging.getLogger(__name__)

try:
    tavily_search_tool = TavilySearchTool(max_results=3) # Configure max results
except ValueError as e:
    logger.error(f"Failed to initialize TavilySearchTool: {e}")
    tavily_search_tool = None # Mark as unavailable if API key is missing

def tavily_search_node(state: AgentState) -> Dict[str, Any]:
    """
    The Tavily Search Agent node function for LangGraph.

    This agent takes the user's query (and potentially context from other agents)
    and performs a web search using Tavily to retrieve relevant, structured information.
    In a multi-source flow, this is typically the last retrieval step before reasoning.

    Args:
        state (AgentState): The current state containing the query and potentially other context.

    Returns:
        Dict[str, Any]: Updates to the state, including web_snippets from Tavily.
    """
    logger.info(f"Tavily Search Agent invoked. Current agent: {state.get('current_agent', 'unknown')}")
    query = state.get("query", "")

    if not query:
        logger.error("Tavily Search Agent: No query found in state.")
        return {
            "web_snippets": [], # Use the correct key name from AgentState
            "current_agent": "tavily_search_agent",
            "next_agent": state.get("next_agent", "reasoning_agent")
        }

    if not tavily_search_tool:
         logger.error("Tavily Search Agent: Tavily client is not available (missing API key?). Returning empty results.")
         return {
            "web_snippets": [], # Use the correct key name from AgentState
            "current_agent": "tavily_search_agent",
            "next_agent": "reasoning_agent",
            "error_flag": True,
            "error_message": "Tavily API client not initialized (check TAVILY_API_KEY)."
        }

    retrieved_snippets = tavily_search_tool.search(query)

    logger.info(f"Tavily Search Agent: Retrieved {len(retrieved_snippets)} web snippets.")

    logger.debug(f"DEBUG: Tavily Search Agent retrieved snippets: {retrieved_snippets}")

    updates = {
        "current_agent": "tavily_search_agent",
        "web_snippets": retrieved_snippets, # Use the correct key name from AgentState
        "next_agent": "reasoning_agent"
    }

    if DEBUG:
        logger.debug(f"Tavily Search Agent state updates: {updates}")

    return updates

