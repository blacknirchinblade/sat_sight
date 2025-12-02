import logging
import json
from typing import Dict, Any
from sat_sight.core.state import AgentState
from sat_sight.models.llm_router import get_llm_response
from sat_sight.core.config import DEBUG
import uuid

logger = logging.getLogger(__name__)


def classify_query(query: str, has_image: bool) -> Dict[str, Any]:
    """Classifies the user query to determine routing strategy using heuristics."""
    
    query_lower = query.lower()
    
    image_request_keywords = ["show me", "display", "view", "find images", "show images", "find pictures", "examples of"]
    image_keywords = ["image", "picture", "photo", "this", "shown", "see", "visible", "satellite", "aerial"]
    web_keywords = ["latest", "recent", "news", "current", "today", "update", "new", "2024", "2025"]
    location_keywords = ["coordinates", "latitude", "longitude", " gps ", " degree", " near ", " in ", " around ", " within ", " km from", " distance from", "paris", "poland", "switzerland", "germany", "france", "stuttgart", "czech", "brazil", "amazon", "california"]
    risk_keywords = ["risk", "threat", "danger", "vulnerable", "impact", "effect", "consequence"]
    
    category = "general_knowledge"
    confidence = 0.8
    
    has_image_request = any(kw in query_lower for kw in image_request_keywords)
    if has_image_request:
        category = "image_search"
        confidence = 0.95
    elif any(kw in query_lower for kw in web_keywords):
        category = "web_search"
        confidence = 0.95
    elif any(kw in query_lower for kw in location_keywords):
        category = "location_query"
        confidence = 0.95
    elif has_image:
        has_image_ref = any(kw in query_lower for kw in image_keywords)
        has_risk_ref = any(kw in query_lower for kw in risk_keywords)
        
        if has_image_ref and not has_risk_ref:
            category = "image_analysis"
            confidence = 0.9
        elif has_image_ref or has_risk_ref:
            category = "contextual_analysis"
            confidence = 0.85
        else:
            category = "image_analysis"
            confidence = 0.7
    
    needs_image = has_image and category in ["image_analysis", "contextual_analysis"]
    needs_text_kb = category in ["contextual_analysis", "general_knowledge"]
    needs_web_search = category == "web_search"
    needs_wikipedia = category == "general_knowledge" and not needs_web_search and not has_image
    
    logger.info(f"Query classified as: {category} (confidence: {confidence:.2f})")
    logger.info(f"Needs - Image: {needs_image}, Text KB: {needs_text_kb}, Web: {needs_web_search}, Wiki: {needs_wikipedia}")
    
    return {
        "category": category,
        "needs_image": needs_image,
        "needs_text_kb": needs_text_kb,
        "needs_web_search": needs_web_search,
        "needs_wikipedia": needs_wikipedia,
        "confidence": confidence
    }


def plan_node(state: AgentState) -> Dict[str, Any]:
    """Planner Agent: Analyzes query and decides routing strategy."""
    
    logger.info(f"Planner Agent invoked. Current agent: {state.get('current_agent', 'unknown')}")
    query = state.get("query", "")
    image_path = state.get("image_path", "")
    episode_id = state.get("episode_id", None)
    user_id = state.get("user_id", "anonymous")

    if not query:
        logger.error("Planner: No query found in state.")
        return {"error_flag": True, "error_message": "Input query is missing.", "next_agent": "end"}

    has_image = bool(image_path)
    classification = classify_query(query, has_image)
    
    category = classification["category"]
    needs_image = classification["needs_image"]
    needs_text_kb = classification["needs_text_kb"]
    needs_web_search = classification["needs_web_search"]
    needs_wikipedia = classification["needs_wikipedia"]

    next_agent = "end"
    multi_source_needed = False
    required_sources = []

    if category == "general_knowledge":
        if needs_text_kb and needs_wikipedia:
            next_agent = "text_retrieval_agent"
            multi_source_needed = True
            required_sources = ["text", "wiki"]
        elif needs_text_kb:
            next_agent = "text_retrieval_agent"
        elif needs_wikipedia:
            next_agent = "wikipedia_agent"
        elif needs_web_search:
            next_agent = "tavily_search_agent"
        else:
            next_agent = "reasoning_agent"
    
    elif category == "image_search":
        next_agent = "vision_agent"
    
    elif category == "image_analysis":
        if needs_image and has_image:
            next_agent = "vision_agent"
        else:
            next_agent = "text_retrieval_agent"
    
    elif category == "contextual_analysis":
        if needs_image and has_image:
            next_agent = "vision_agent"
            multi_source_needed = True
            required_sources = ["vision"]
            if needs_text_kb:
                required_sources.append("text")
            if needs_web_search:
                required_sources.append("web")
        else:
            next_agent = "text_retrieval_agent"
    
    elif category == "web_search":
        next_agent = "tavily_search_agent"
    
    elif category == "location_query":
        next_agent = "geo_agent"
    
    else:
        if has_image:
            next_agent = "vision_agent"
        else:
            next_agent = "wikipedia_agent"

    logger.info(f"Planner: Next agent is '{next_agent}' based on category '{category}'")
    
    updates = {
        "current_agent": "planner",
        "next_agent": next_agent,
        "planner_decision_category": category,
        "multi_source_needed": multi_source_needed,
        "required_sources": required_sources,
        "completed_sources": [],
        "episode_id": episode_id or str(uuid.uuid4()),
        "user_id": user_id,
    }

    if DEBUG:
        logger.debug(f"Planner updates: {updates}")

    return updates