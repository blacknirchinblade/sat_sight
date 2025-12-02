import logging
from typing import Dict, Any
from sat_sight.core.state import AgentState
from sat_sight.core.config import DEBUG

logger = logging.getLogger(__name__)

def coordinator_node(state: AgentState) -> Dict[str, Any]:
    """
    The Coordinator Agent node function for LangGraph.

    This agent manages complex, multi-step agent workflows that might involve
    parallel or sequential execution of multiple retrieval agents (Vision, Text, Search, Geo)
    before a synthesis step. It reads the state to understand the desired outcome
    and orchestrates the necessary sub-flows.

    This is a more advanced agent, potentially replacing complex conditional logic
    in the Planner or being used for specific, intricate queries.

    Args:
        state (AgentState): The current state containing query, image, flags for needed sources, etc.

    Returns:
        Dict[str, Any]: Updates to the state, primarily deciding the next agent(s) to run.
    """
    logger.info(f"Coordinator Agent invoked. Current agent: {state.get('current_agent', 'unknown')}")
    query = state.get("query", "")
    image_path = state.get("image_path", "")
    needs_image_context = bool(image_path) 
    needs_text_context = state.get("requires_text_knowledge", False) 
    needs_web_context = state.get("requires_web_search", False) 
    needs_geo_context = state.get("requires_geo_data", False) 


    required_sources = state.get("required_sources", [])
    completed_sources = state.get("completed_sources", [])

    logger.debug(f"Coordinator: Required sources: {required_sources}, Completed sources: {completed_sources}")

    next_agent = "reasoning_agent" 
    for source in required_sources:
        if source not in completed_sources:
            if source == "vision":
                next_agent = "vision_agent"
                break 
            elif source == "text":
                next_agent = "text_retrieval_agent"
                break
            elif source == "web":
                next_agent = "tavily_search_agent"
                break
            elif source == "geo":
                next_agent = "geo_agent"
                break
            else:
                logger.warning(f"Coordinator: Unknown source type '{source}' in required_sources list.")

    if next_agent != "reasoning_agent":
        updated_completed_sources = completed_sources + [next_agent.replace("_agent", "")] 
        updates = {
            "current_agent": "coordinator_agent",
            "completed_sources": updated_completed_sources,
            "next_agent": next_agent 
        }
        logger.info(f"Coordinator: Scheduled next agent '{next_agent}' for source '{next_agent.replace('_agent', '')}'.")
    else:
        updates = {
            "current_agent": "coordinator_agent",
            "next_agent": "reasoning_agent" 
        }
        logger.info("Coordinator: All required sources completed. Proceeding to reasoning_agent.")

    if DEBUG:
        logger.debug(f"Coordinator Agent state updates: {updates}")

    return updates

