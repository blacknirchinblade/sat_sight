import logging
from typing import Dict, Any
from sat_sight.core.state import AgentState
from sat_sight.models.llm_router import get_llm_response

logger = logging.getLogger(__name__)


def guardrail_node(state: AgentState) -> Dict[str, Any]:
    """Guardrail Agent: Checks response for safety, policy compliance, and appropriateness."""
    
    logger.info("Guardrail Agent invoked")
    
    llm_response = state.get("llm_response", "")
    
    if not llm_response:
        return {
            "current_agent": "guardrail_agent",
            "next_agent": "end",
            "error_flag": False
        }
    
    unsafe_keywords = ["harmful", "dangerous", "illegal", "violent", "explicit"]
    
    response_lower = llm_response.lower()
    is_safe = not any(keyword in response_lower for keyword in unsafe_keywords)
    
    if not is_safe:
        logger.warning("Guardrail: Potentially unsafe content detected")
        return {
            "current_agent": "guardrail_agent",
            "llm_response": "I cannot provide information that may be harmful or inappropriate.",
            "next_agent": "end",
            "error_flag": True,
            "error_message": "Content filtered by safety guardrails"
        }
    
    logger.info("Guardrail: Content passed safety checks")
    
    return {
        "current_agent": "guardrail_agent",
        "next_agent": "end"
    }
