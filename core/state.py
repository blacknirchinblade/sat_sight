from typing import TypedDict, List, Dict, Any, Optional
import numpy as np

class AgentState(TypedDict):
    """State structure for the LangGraph workflow enabling agent-to-agent communication."""
    
    query: str
    image_path: str
    
    image_embedding: Optional[np.ndarray]
    query_embedding: Optional[np.ndarray]
    
    retrieved_image_metadata: List[Dict[str, Any]]
    retrieved_image_distances: List[float]
    retrieved_text_chunks: List[Dict[str, Any]]
    web_snippets: List[Dict[str, Any]]
    wiki_content: Optional[str]
    wiki_source: Optional[str]
    geo_data: Optional[Dict[str, Any]]
    
    short_term_memory: List[Dict[str, str]]
    long_term_memory_id: Optional[str]
    episodic_memory: List[Dict[str, Any]]
    episode_id: Optional[str]
    user_id: str
    
    selected_model_route: str
    llm_response: Optional[str]
    thinking_process: Optional[List[Dict[str, Any]]]  # For UI "Show Thinking" dropdown
    confidence_score: Optional[float]
    
    current_agent: str
    error_flag: bool
    error_message: Optional[str]
    fallback_triggered: bool
    
    next_agent: str
    
    multi_source_needed: bool
    requires_vision_and_text: bool
    required_sources: List[str]
    completed_sources: List[str]
    planner_decision_category: Optional[str]
    
    critic_score: Optional[float]
    critic_feedback: Optional[str]
    needs_revision: bool
    
    user_feedback: Optional[str]