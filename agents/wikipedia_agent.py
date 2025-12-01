import logging
from typing import Dict, Any
from sat_sight.core.state import AgentState
from sat_sight.retrieval.wiki_fetcher import WikiFetcher
from sat_sight.core.config import DEBUG

logger = logging.getLogger(__name__)

wiki_fetcher = WikiFetcher(max_sentences=8) # Configure summary length (reduced for conciseness)

def wikipedia_node(state: AgentState) -> Dict[str, Any]:
    """
    The Wikipedia Agent node function for LangGraph.
    
    Fetches Wikipedia content based on either image metadata or direct query terms.
    """
    logger.info(f"Wikipedia Agent invoked. Current agent: {state.get('current_agent', 'unknown')}")

    retrieved_image_metadata = state.get("retrieved_image_metadata", [])
    query = state.get("query", "")

    wiki_content = ""
    wiki_source_title = ""
    search_term = ""

    if retrieved_image_metadata:
        primary_image_meta = retrieved_image_metadata[0] if retrieved_image_metadata else {}
        class_label = primary_image_meta.get("class", "")
        
        if class_label:
            search_term = class_label
            logger.info(f"Wikipedia Agent: Using class label '{class_label}' for search.")
    
    if not search_term and query:
        stop_words = {
            "what", "is", "are", "the", "a", "an", "how", "why", "when", "where", "about",
            "this", "that", "these", "those", "can", "could", "would", "should", "do", "does",
            "in", "on", "at", "to", "for", "of", "with", "from", "by", "and", "or", "but"
        }
        words = [w.strip("?.,!") for w in query.lower().split() if w not in stop_words and len(w) > 3]
        
        priority_keywords = ["deforestation", "climate", "agriculture", "forest", "land", "crop", 
                            "environmental", "conservation", "biodiversity", "erosion"]
        priority_words = [w for w in words if w in priority_keywords]
        
        if priority_words:
            search_term = " ".join(priority_words[:2])
        elif words:
            search_term = " ".join(words[:2])  # Reduced to 2 words for more focused results
        
        logger.info(f"Wikipedia Agent: Extracted search term '{search_term}' from query.")
    
    if search_term:
        logger.info(f"Wikipedia Agent: Fetching content for '{search_term}'")
        wiki_content = wiki_fetcher.fetch_summary(search_term)
        if wiki_content:
            wiki_source_title = f"Wikipedia: {search_term}"
            logger.info(f"Wikipedia Agent: Retrieved {len(wiki_content)} chars from Wikipedia.")
        else:
            logger.info(f"Wikipedia Agent: No content found for '{search_term}'")
    else:
        logger.warning("Wikipedia Agent: No search term available, skipping fetch.")

    multi_source_needed = state.get("multi_source_needed", False)
    required_sources = state.get("required_sources", [])
    next_agent_decided = "reasoning_agent"
    
    if multi_source_needed and required_sources:
        completed_sources = state.get("completed_sources", [])
        completed_sources.append("wiki")
        
        remaining_sources = [s for s in required_sources if s not in completed_sources]
        if remaining_sources:
            next_source = remaining_sources[0]
            if next_source == "text":
                next_agent_decided = "text_retrieval_agent"
            elif next_source == "vision":
                next_agent_decided = "vision_agent"
            elif next_source == "web":
                next_agent_decided = "tavily_search_agent"
            logger.info(f"Wikipedia Agent: Multi-source routing to {next_agent_decided}")
        else:
            logger.info(f"Wikipedia Agent: All sources complete, routing to reasoning_agent")
        
        updates = {
            "current_agent": "wikipedia_agent",
            "wiki_content": wiki_content,
            "wiki_source": wiki_source_title,
            "completed_sources": completed_sources,
            "next_agent": next_agent_decided
        }
    else:
        updates = {
            "current_agent": "wikipedia_agent",
            "wiki_content": wiki_content,
            "wiki_source": wiki_source_title,
            "next_agent": "reasoning_agent"
        }

    if DEBUG:
        logger.debug(f"Wikipedia Agent state updates: {updates}")

    return updates

