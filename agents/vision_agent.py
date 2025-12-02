import logging
import numpy as np
import os
from sat_sight.core.state import AgentState
from sat_sight.retrieval.clip_encoder import CLIPEncoder
from sat_sight.retrieval.faiss_manager import FAISSManager
from sat_sight.core.config import FAISS_RETRIEVAL_K, DEBUG

logger = logging.getLogger(__name__)

try:
    from sat_sight.retrieval.reranker import Reranker
    RERANK_TOP_K = 5  # Increased from 3
    vision_reranker = Reranker(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2")
    RERANKER_AVAILABLE = True
except ImportError:
    logger.warning("Reranker not available, skipping reranking")
    RERANKER_AVAILABLE = False
    RERANK_TOP_K = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

clip_encoder = CLIPEncoder()
faiss_manager = FAISSManager()


def vision_node(state: AgentState) -> dict:
    """
    The Vision Agent node function for LangGraph.

    This agent processes the input image, encodes it using CLIP,
    searches the FAISS index for similar images, retrieves their metadata,
    reranks the metadata based on query relevance, and updates the state.
    It then decides the next agent based on the 'multi_source_needed' flag
    or the specific query content.

    Args:
        state (AgentState): The current state containing image_path and potentially other context.

    Returns:
        Dict[str, Any]: Updates to the state, including retrieved_image_metadata and next_agent.
    """
    logger.info(f"Vision Agent invoked. Current agent: {state.get('current_agent', 'unknown')}")
    image_path = state.get("image_path", "")
    query = state.get("query", "") 
    multi_source_needed = state.get("multi_source_needed", False) 

    is_text_search = not image_path and query
    
    if not image_path and not query:
        logger.error("Vision Agent: No image_path or query found in state.")
        return {
            "error_flag": True,
            "error_message": "Input image path or search query is missing.",
            "current_agent": "vision_agent",
            "next_agent": state.get("next_agent", "reasoning_agent")
        }
    
    try:
        if is_text_search:
            logger.info(f"Vision Agent: Performing text-based image search for: '{query}'")
            embedding = clip_encoder.encode_text(query)
            image_embedding_np = embedding.numpy()
        else:
            if not os.path.isabs(image_path):
                image_path = os.path.join(BASE_DIR, image_path)
            
            logger.info(f"Vision Agent: Looking for image at: {image_path}")

            if not os.path.exists(image_path):
                logger.error(f"Vision Agent: Image file not found at {image_path}")
                return {
                    "retrieved_image_metadata": [],
                    "retrieved_image_distances": [],
                    "error_flag": True,
                    "error_message": f"Image file not found: {image_path}",
                    "current_agent": "vision_agent",
                    "next_agent": "text_retrieval_agent"
                }
            
            image_embedding = clip_encoder.encode_image(image_path)
            image_embedding_np = image_embedding.numpy()

        distances, retrieved_metadata_list = faiss_manager.search(image_embedding_np, k=FAISS_RETRIEVAL_K)

        logger.info(f"Vision Agent: Retrieved {len(retrieved_metadata_list)} similar images from FAISS.")

        if query and retrieved_metadata_list and RERANKER_AVAILABLE:
            logger.info(f"Vision Agent: Reranking {len(retrieved_metadata_list)} results")
            try:
                reranked_metadata_list = vision_reranker.rerank_image_metadata(
                    query=query,
                    metadata_list=retrieved_metadata_list,
                    top_k=min(RERANK_TOP_K, len(retrieved_metadata_list))
                )
                logger.info(f"Vision Agent: Reranked to top {len(reranked_metadata_list)} results")
            except Exception as e:
                logger.warning(f"Reranking failed: {e}. Using original results.")
                reranked_metadata_list = retrieved_metadata_list
        else:
            reranked_metadata_list = retrieved_metadata_list

        logger.info(f"Vision Agent: Retrieved {len(reranked_metadata_list)} similar images")

        updates = {
            "current_agent": "vision_agent",
            "image_embedding": image_embedding_np, 
            "retrieved_image_metadata": retrieved_metadata_list, 
            "retrieved_image_distances": distances, 
        }

        query = state.get("query", "").lower() 
        multi_source_needed = state.get("multi_source_needed", False)

        next_agent_decided = "reasoning_agent"  
        required_sources = state.get("required_sources", [])
        
        if multi_source_needed and required_sources:
            completed_sources = state.get("completed_sources", [])
            completed_sources.append("vision")  
            
            remaining_sources = [s for s in required_sources if s not in completed_sources]
            
            if remaining_sources:
                next_source = remaining_sources[0]
                if next_source == "text":
                    logger.info(f"Vision Agent: Multi-source routing to text_retrieval_agent")
                    next_agent_decided = "text_retrieval_agent"
                elif next_source == "web":
                    logger.info(f"Vision Agent: Multi-source routing to tavily_search_agent")
                    next_agent_decided = "tavily_search_agent"
                else:
                    logger.info(f"Vision Agent: Multi-source routing to reasoning_agent (all sources complete)")
                    next_agent_decided = "reasoning_agent"
            else:
                logger.info(f"Vision Agent: All required sources completed, routing to reasoning_agent")
                next_agent_decided = "reasoning_agent"
            
            updates["completed_sources"] = completed_sources
        else:
            primary_image_meta = retrieved_metadata_list[0] if retrieved_metadata_list else {}
            image_class = primary_image_meta.get("class", "")
            
            web_search_indicators = ["recent", "latest", "news", "report", "current", "today"]
            
            if image_class and not any(ind in query.lower() for ind in web_search_indicators):
                logger.info(f"Vision Agent: Found class '{image_class}', routing to wikipedia_agent")
                next_agent_decided = "wikipedia_agent"
            elif any(indicator in query.lower() for indicator in web_search_indicators):
                logger.info(f"Vision Agent: Web search indicators found, routing to tavily_search_agent")
                next_agent_decided = "tavily_search_agent"
            else:
                logger.info(f"Vision Agent: Routing to reasoning_agent")
                next_agent_decided = "reasoning_agent"

        updates["next_agent"] = next_agent_decided

        if DEBUG:
            logger.debug(f"Vision Agent state updates: {updates}")

        return updates

    except FileNotFoundError:
        error_msg = f"Vision Agent: Image file not found at {image_path}"
        logger.error(error_msg)
        return {
            "retrieved_image_metadata": [],
            "retrieved_image_distances": [],
            "error_flag": True,
            "error_message": error_msg,
            "current_agent": "vision_agent",
            "next_agent": "reasoning_agent" 
        }
    except Exception as e:
        logger.error(f"Error in Vision Agent: {e}")
        import traceback
        traceback.print_exc()
        return {
            "retrieved_image_metadata": [],
            "retrieved_image_distances": [],
            "error_flag": True,
            "error_message": str(e),
            "current_agent": "vision_agent",
            "next_agent": "reasoning_agent"
        }