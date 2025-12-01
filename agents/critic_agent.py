import logging
import json
from typing import Dict, Any
from sat_sight.core.state import AgentState
from sat_sight.models.llm_router import get_llm_response
from sat_sight.core.config import DEBUG

logger = logging.getLogger(__name__)


def critic_node(state: AgentState) -> Dict[str, Any]:
    """Critic Agent: Evaluates the quality of the reasoning agent's response."""
    
    logger.info("Critic Agent invoked")
    
    query = state.get("query", "")
    llm_response = state.get("llm_response", "")
    
    if not llm_response:
        logger.error("Critic Agent: No response to evaluate")
        return {
            "critic_score": 0.0,
            "critic_feedback": "No response generated",
            "needs_revision": True,
            "current_agent": "critic_agent",
            "next_agent": "end"
        }

    critic_prompt = f"""Evaluate this AI response for a satellite imagery Q&A system.

QUERY: {query}
RESPONSE: {llm_response}

Rate on 0-1 scale and respond in JSON:
{{
    "score": <0.0-1.0>,
    "feedback": "<brief assessment>",
    "needs_revision": <true/false>
}}"""

    try:
        result = get_llm_response(critic_prompt, max_tokens=150, temperature=0.2)
        response_text = result.get("response", "").strip()
        
        try:
            evaluation = json.loads(response_text)
            critic_score = float(evaluation.get("score", 0.7))
            critic_feedback = evaluation.get("feedback", "Evaluation completed")
            needs_revision = evaluation.get("needs_revision", False)
        except (json.JSONDecodeError, ValueError):
            logger.warning("Failed to parse critic JSON")
            critic_score = 0.7
            critic_feedback = "Default evaluation"
            needs_revision = False

        logger.info(f"Critic score: {critic_score:.2f}, revision: {needs_revision}")

        return {
            "current_agent": "critic_agent",
            "critic_score": critic_score,
            "critic_feedback": critic_feedback,
            "needs_revision": needs_revision,
            "next_agent": "reasoning_agent" if needs_revision and critic_score < 0.6 else "end"
        }

    except Exception as e:
        logger.error(f"Critic Agent error: {e}")
        return {
            "critic_score": 0.5,
            "critic_feedback": f"Error: {str(e)}",
            "needs_revision": False,
            "current_agent": "critic_agent",
            "next_agent": "end"
        }
