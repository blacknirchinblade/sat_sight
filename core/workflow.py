import logging
from typing import Dict, Any, Tuple
import os
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
from langgraph.graph import StateGraph, END
from sat_sight.core.state import AgentState
from sat_sight.agents.planner import plan_node
from sat_sight.agents.vision_agent import vision_node
from sat_sight.agents.reasoning_agent import reasoning_node
from sat_sight.agents.text_retrieval_agent import text_retrieval_node
from sat_sight.agents.search_agent import search_node
from sat_sight.agents.tavily_search_agent import tavily_search_node
from sat_sight.agents.wikipedia_agent import wikipedia_node
from sat_sight.agents.critic_agent import critic_node
from sat_sight.agents.geo_agent import geo_node
from sat_sight.agents.memory_agent import memory_node
from sat_sight.agents.guardrail_agent import guardrail_node
from sat_sight.agents.feedback_agent import feedback_node
from sat_sight.agents.coordinator_agent import coordinator_node

logger = logging.getLogger(__name__)

def should_route_to_agent(state: AgentState) -> str:
    """Determines the next node based on the 'next_agent' key in the state."""
    next_agent = state.get("next_agent", "end")
    logger.debug(f"Routing to '{next_agent}'")
    return next_agent

def create_workflow() -> StateGraph:
    """Creates and configures the LangGraph state machine with all agent nodes and routing."""
    logger.info("Initializing LangGraph workflow...")

    workflow = StateGraph(AgentState)

    workflow.add_node("planner", plan_node)
    workflow.add_node("vision_agent", vision_node)
    workflow.add_node("text_retrieval_agent", text_retrieval_node)
    workflow.add_node("search_agent", search_node)
    workflow.add_node("tavily_search_agent", tavily_search_node)
    workflow.add_node("wikipedia_agent", wikipedia_node)
    workflow.add_node("reasoning_agent", reasoning_node)
    workflow.add_node("critic_agent", critic_node)
    workflow.add_node("geo_agent", geo_node)
    workflow.add_node("memory_agent", memory_node)
    workflow.add_node("guardrail_agent", guardrail_node)
    workflow.add_node("feedback_agent", feedback_node)
    workflow.add_node("coordinator_agent", coordinator_node)

    def end_node(state: AgentState) -> AgentState:
        logger.info("Workflow reached END node.")
        return state

    workflow.add_node("end", end_node)

    workflow.set_entry_point("planner")

    workflow.add_conditional_edges(
        "planner",
        should_route_to_agent,
        ["end", "vision_agent", "text_retrieval_agent", "search_agent", "tavily_search_agent", 
         "wikipedia_agent", "reasoning_agent", "geo_agent", "memory_agent", "coordinator_agent"]
    )

    workflow.add_conditional_edges(
        "vision_agent",
        should_route_to_agent,
        ["end", "text_retrieval_agent", "tavily_search_agent", "wikipedia_agent", "reasoning_agent", 
         "geo_agent", "memory_agent", "critic_agent", "coordinator_agent"]
    )

    workflow.add_conditional_edges(
        "text_retrieval_agent",
        should_route_to_agent,
        ["end", "tavily_search_agent", "wikipedia_agent", "reasoning_agent", "memory_agent"]
    )

    workflow.add_conditional_edges(
        "search_agent",
        should_route_to_agent,
        ["end", "reasoning_agent", "memory_agent"]
    )

    workflow.add_conditional_edges(
        "tavily_search_agent",
        should_route_to_agent,
        ["end", "reasoning_agent", "memory_agent"]
    )

    workflow.add_conditional_edges(
        "wikipedia_agent",
        should_route_to_agent,
        ["end", "text_retrieval_agent", "tavily_search_agent", "reasoning_agent", "memory_agent"]
    )

    workflow.add_conditional_edges(
        "geo_agent",
        should_route_to_agent,
        ["end", "reasoning_agent", "memory_agent", "critic_agent"]
    )

    workflow.add_conditional_edges(
        "memory_agent",
        should_route_to_agent,
        ["end", "reasoning_agent", "critic_agent", "coordinator_agent"]
    )

    workflow.add_conditional_edges(
        "guardrail_agent",
        should_route_to_agent,
        ["end", "reasoning_agent"]
    )

    workflow.add_conditional_edges(
        "feedback_agent",
        should_route_to_agent,
        ["end"]
    )

    workflow.add_conditional_edges(
        "coordinator_agent",
        should_route_to_agent,
        ["end", "vision_agent", "text_retrieval_agent", "tavily_search_agent", "reasoning_agent", 
         "geo_agent", "memory_agent", "critic_agent"]
    )

    workflow.add_conditional_edges(
        "critic_agent",
        should_route_to_agent,
        ["end", "reasoning_agent"]
    )

    workflow.add_conditional_edges(
        "reasoning_agent",
        should_route_to_agent,
        ["end", "critic_agent", "guardrail_agent"]
    )

    workflow.add_edge("end", END)

    logger.info("LangGraph workflow initialized successfully.")
    return workflow

def get_compiled_workflow():
    """Compiles the workflow graph and returns it."""
    graph = create_workflow()
    compiled_graph = graph.compile()
    logger.info("LangGraph workflow compiled successfully.")
    return compiled_graph


def run_workflow(query: str, image_path: str = "", user_id: str = "anonymous") -> Tuple[str, Dict[str, Any]]:
    """Runs the compiled LangGraph workflow with the given query and optional image path."""
    try:
        app = get_compiled_workflow()
        initial_inputs = {
            "query": query,
            "image_path": image_path,
            "user_id": user_id,
            "episode_id": None,
            "image_embedding": None,
            "query_embedding": None,
            "retrieved_image_metadata": [],
            "retrieved_image_distances": [],
            "retrieved_text_chunks": [],
            "web_snippets": [],
            "wiki_content": None,
            "wiki_source": None,
            "geo_data": None,
            "short_term_memory": [],
            "long_term_memory_id": None,
            "episodic_memory": [],
            "selected_model_route": "auto",
            "llm_response": None,
            "thinking_process": None,
            "confidence_score": None,
            "current_agent": "planner",
            "error_flag": False,
            "error_message": None,
            "fallback_triggered": False,
            "next_agent": "planner",
            "multi_source_needed": False,
            "requires_vision_and_text": False,
            "required_sources": [],
            "completed_sources": [],
            "planner_decision_category": None,
            "critic_score": None,
            "critic_feedback": None,
            "needs_revision": False,
            "user_feedback": None
        }

        final_state = None
        for output in app.stream(initial_inputs):
            final_state = output.get('end', output.get('reasoning_agent', {}))

        if final_state:
            response = final_state.get("llm_response", "No response generated.")
            return response, final_state
        else:
            return "Error: Workflow did not return a final state.", {}

    except Exception as e:
        logger.error(f"Error running workflow: {e}")
        import traceback
        traceback.print_exc()
        return f"An error occurred during processing: {str(e)}", {}

