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
    """
    Memory Agent: Manages short-term, long-term, and episodic memory operations.
    
    Responsibilities:
    1. Add current query to short-term conversation history
    2. Retrieve relevant past conversations from episodic memory
    3. Get user preferences from long-term memory
    4. Format memory context for reasoning agent
    5. Update user interaction patterns
    """
    
    logger.info("Memory Agent invoked")
    
    query = state.get("query", "")
    user_id = state.get("user_id", "anonymous")
    episode_id = state.get("episode_id")
    llm_response = state.get("llm_response", "")
    

    stm.add_turn(
        role="user",
        content=query,
        metadata={
            "episode_id": episode_id,
            "category": state.get("planner_decision_category", "unknown")
        }
    )
    logger.info(f"Added user query to short-term memory")
    
 
    if llm_response:
        stm.add_turn(
            role="assistant",
            content=llm_response,
            metadata={
                "episode_id": episode_id,
                "confidence": state.get("confidence_score", 0.0),
                "model": state.get("selected_model_route", "unknown")
            }
        )
        logger.info(f"Added assistant response to short-term memory")
    

    user_profile = ltm.get_or_create_user(user_id)
    preferences = user_profile.get("preferences", {})
    logger.info(f"Retrieved user profile for {user_id}")
    

    if episode_id and query:
        query_category = state.get("planner_decision_category", "unknown")
        ltm.record_query_pattern(
            user_id=user_id,
            query_type=query_category,
            query_text=query[:200]  
        )
        logger.info(f"Recorded query pattern to long-term memory: {query_category}")
    

    similar_episodes = []
    if query:
        try:
           
            search_terms = [word for word in query.split() if len(word) > 3]
            if search_terms:
                
                similar_episodes = episodic.search_interactions(
                    user_id=user_id, 
                    search_term=search_terms[0],
                    limit=3
                )
                logger.info(f"Found {len(similar_episodes)} similar past interactions")
        except Exception as e:
            logger.warning(f"Failed to search episodic memory: {e}")
    

    memory_context = stm.format_for_llm(num_turns=5)
    

    memory_summary = {
        "conversation_history": memory_context,
        "user_preferences": preferences,
        "similar_past_queries": [ep.get("query", "") for ep in similar_episodes[:3]],
        "user_id": user_id,
        "session_turn_count": len(stm.conversation_history)
    }
    
    logger.info(f"Memory context prepared: {len(memory_context)} chars, "
                f"{len(similar_episodes)} similar episodes")
    logger.debug(f"User preferences: {preferences}")
    
    return {
        "current_agent": "memory_agent",
        "next_agent": "reasoning_agent",
        "memory_context": memory_context,
        "memory_summary": memory_summary,
        "short_term_memory": stm.get_context(num_turns=5),
        "episodic_memory": similar_episodes[:3]
    }
