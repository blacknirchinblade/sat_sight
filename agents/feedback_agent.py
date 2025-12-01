import logging
from typing import Dict, Any
from sat_sight.core.state import AgentState

logger = logging.getLogger(__name__)


def feedback_node(state: AgentState) -> Dict[str, Any]:
    """Feedback Agent: Processes user feedback for continuous improvement."""
    
    logger.info("Feedback Agent invoked")
    
    user_feedback = state.get("user_feedback", None)
    query = state.get("query", "")
    llm_response = state.get("llm_response", "")
    episode_id = state.get("episode_id", None)
    
    if user_feedback:
        logger.info(f"Feedback received for episode {episode_id}: {user_feedback}")
        
    return {
        "current_agent": "feedback_agent",
        "next_agent": "end"
    }
