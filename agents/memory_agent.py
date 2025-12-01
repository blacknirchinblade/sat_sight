import logging
from typing import Dict, Any
from sat_sight.core.state import AgentState
from sat_sight.memory.short_term import ShortTermMemory
from sat_sight.memory.long_term import LongTermMemory
from sat_sight.memory.episodic import EpisodicMemory

logger = logging.getLogger(__name__)

stm = ShortTermMemory(max_turns=10)
ltm = LongTermMemory()
episodic = EpisodicMemory()


def memory_node(state: AgentState) -> Dict[str, Any]:
    """Memory Agent: Manages short-term, long-term, and episodic memory operations."""
    
    logger.info("Memory Agent invoked")
    
    query = state.get("query", "")
    user_id = state.get("user_id", "anonymous")
    episode_id = state.get("episode_id")
    
    user_profile = ltm.get_or_create_user(user_id)
    preferences = user_profile.get("preferences", {})
    
    if episode_id:
        query_patterns = ltm.get_query_patterns(user_id, limit=5)
        if query_patterns:
            logger.info(f"Found {len(query_patterns)} frequent query patterns for user")
    
    memory_context = stm.format_for_llm(num_turns=5)
    
    logger.info(f"Memory context prepared for user {user_id}")
    logger.debug(f"User preferences: {preferences}")
    
    return {
        "current_agent": "memory_agent",
        "next_agent": "reasoning_agent"
    }
