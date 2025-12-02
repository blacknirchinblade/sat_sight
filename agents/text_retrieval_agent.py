import logging
from typing import Dict, Any
from sat_sight.core.state import AgentState
from sat_sight.retrieval.chroma_manager import ChromaManager
from sat_sight.core.config import CHROMA_RETRIEVAL_K, DEBUG

logger = logging.getLogger(__name__)

try:
    from sat_sight.retrieval.reranker import Reranker
    RERANK_TOP_K = 5  
    text_reranker = Reranker(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2")
    RERANKER_AVAILABLE = True
except ImportError:
    logger.warning("Reranker not available, skipping reranking")
    RERANKER_AVAILABLE = False
    RERANK_TOP_K = None

chroma_manager = ChromaManager()

def text_retrieval_node(state: AgentState) -> Dict[str, Any]:
    """
    The Text Retrieval Agent node function for LangGraph.

    This agent takes the user's query and retrieves relevant textual knowledge
    from the ChromaDB vector store. It then reranks the results based on query relevance
    and updates the state. It decides the next agent based on the multi-source flag
    or query content.

    Args:
        state (AgentState): The current state containing the query.

    Returns:
        Dict[str, Any]: Updates to the state, including retrieved_text_chunks and next_agent.
    """
    logger.info(f"Text Retrieval Agent invoked. Current agent: {state.get('current_agent', 'unknown')}")
    query = state.get("query", "")
    multi_source_needed = state.get("multi_source_needed", False) 

    if not query:
        logger.error("Text Retrieval Agent: No query found in state.")
        return {
            "retrieved_text_chunks": [],
            "current_agent": "text_retrieval_agent",
            "next_agent": state.get("next_agent", "reasoning_agent") 
        }

    try:
        retrieved_results = chroma_manager.query(query, k=CHROMA_RETRIEVAL_K)

        logger.info(f"Text Retrieval Agent: Retrieved {len(retrieved_results)} text chunks from ChromaDB.")

        if query and retrieved_results and RERANKER_AVAILABLE:
            logger.info(f"Text Retrieval Agent: Reranking {len(retrieved_results)} results")
            try:
                reranked_results = text_reranker.rerank_text_chunks(
                    query=query,
                    chunks=retrieved_results,
                    top_k=min(RERANK_TOP_K, len(retrieved_results))
                )
                logger.info(f"Text Retrieval Agent: Reranked to top {len(reranked_results)} results")
            except Exception as e:
                logger.warning(f"Reranking failed: {e}. Using original results.")
                reranked_results = retrieved_results
        else:
            reranked_results = retrieved_results

        required_sources = state.get("required_sources", [])
        next_agent_decided = "reasoning_agent"
        
        if multi_source_needed and required_sources:
            completed_sources = state.get("completed_sources", [])
            completed_sources.append("text")  
            
            remaining_sources = [s for s in required_sources if s not in completed_sources]
            
            if remaining_sources:
                next_source = remaining_sources[0]
                if next_source == "vision":
                    logger.info(f"Text Retrieval Agent: Multi-source routing to vision_agent")
                    next_agent_decided = "vision_agent"
                elif next_source == "web":
                    logger.info(f"Text Retrieval Agent: Multi-source routing to tavily_search_agent")
                    next_agent_decided = "tavily_search_agent"
                elif next_source == "wiki":
                    logger.info(f"Text Retrieval Agent: Multi-source routing to wikipedia_agent")
                    next_agent_decided = "wikipedia_agent"
                else:
                    logger.info(f"Text Retrieval Agent: All sources complete, routing to reasoning_agent")
                    next_agent_decided = "reasoning_agent"
            else:
                logger.info(f"Text Retrieval Agent: All required sources completed, routing to memory_agent")
                next_agent_decided = "memory_agent"
            
            updates = {
                "current_agent": "text_retrieval_agent",
                "retrieved_text_chunks": reranked_results,
                "completed_sources": completed_sources,
                "next_agent": next_agent_decided
            }
        else:
            logger.info(f"Text Retrieval Agent: Single source mode, routing to memory_agent")
            updates = {
                "current_agent": "text_retrieval_agent",
                "retrieved_text_chunks": reranked_results,
                "next_agent": "memory_agent"
            }

        if DEBUG:
            logger.debug(f"Text Retrieval Agent state updates: {updates}")

        return updates

    except Exception as e:
        logger.error(f"Error in Text Retrieval Agent: {e}")
        import traceback
        traceback.print_exc()
        return {
            "retrieved_text_chunks": [],
            "error_flag": True,
            "error_message": str(e),
            "current_agent": "text_retrieval_agent",
            "next_agent": "reasoning_agent"
        }
    import sys
    import os
