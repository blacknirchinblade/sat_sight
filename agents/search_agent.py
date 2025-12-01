import logging
from typing import Dict, Any
from sat_sight.core.state import AgentState
from sat_sight.tools.search_wrapper import DuckDuckGoSearchTool
from sat_sight.core.config import DEBUG

logger = logging.getLogger(__name__)

search_tool = DuckDuckGoSearchTool(max_results=3) # Configure max results

def search_node(state: AgentState) -> Dict[str, Any]:
    """
    The Search Agent node function for LangGraph.

    This agent takes the user's query (and potentially context from other agents)
    and performs a web search to retrieve real-time or external information.

    Args:
        state (AgentState): The current state containing the query and potentially other context.

    Returns:
        Dict[str, Any]: Updates to the state, including web_snippets.
    """
    logger.info(f"Search Agent invoked. Current agent: {state.get('current_agent', 'unknown')}")
    query = state.get("query", "")

    if not query:
        logger.error("Search Agent: No query found in state.")
        return {
            "web_snippets": [], # <-- Use the correct key name from AgentState
            "current_agent": "search_agent",
            "next_agent": state.get("next_agent", "reasoning_agent")
        }

    retrieved_snippets = search_tool.search(query)

    logger.info(f"Search Agent: Retrieved {len(retrieved_snippets)} web snippets.")

    updates = {
        "current_agent": "search_agent",
        "web_snippets": retrieved_snippets, # <-- Use the correct key name from AgentState
        "next_agent": "reasoning_agent"
    }

    if DEBUG:
        logger.debug(f"Search Agent state updates: {updates}")

    return updates

