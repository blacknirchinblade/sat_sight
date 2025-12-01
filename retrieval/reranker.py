import logging
import numpy as np
from typing import List, Dict, Any, Tuple
from sentence_transformers import CrossEncoder # Import the cross-encoder model type

logger = logging.getLogger(__name__)

class Reranker:
    """
    A class to handle reranking of retrieved results (images or text) based on
    their semantic relevance to a given query using a cross-encoder model.
    """
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initializes the reranker with a cross-encoder model.

        Args:
            model_name (str): Name of the Hugging Face cross-encoder model to use for reranking.
                             Default is a fast, reasonably effective model for passage ranking.
        """
        self.model_name = model_name
        logger.info(f"Initializing Cross-Encoder Reranker with model: {self.model_name}")
        try:
            self.model = CrossEncoder(self.model_name)
            logger.info("Cross-Encoder Reranker model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load cross-encoder model {self.model_name}: {e}")
            raise e # Re-raise to halt initialization if reranker is critical

    def rerank_text_chunks(self, query: str, chunks: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Reranks a list of text chunks based on their relevance to the query.

        Args:
            query (str): The user's query.
            chunks (List[Dict[str, Any]]): List of retrieved text chunks from ChromaDB.
                                           Each chunk is expected to have a 'content' key.
            top_k (int): Number of top reranked results to return.

        Returns:
            List[Dict[str, Any]]: The top-k reranked text chunks, sorted by relevance score (highest first).
                                 The original chunk dictionaries are returned with an added 'rerank_score'.
        """
        if not chunks:
            logger.warning("Reranker: Empty list of text chunks provided for reranking.")
            return []

        logger.debug(f"Reranking {len(chunks)} text chunks for query: '{query[:50]}...'")

        texts_to_rerank = [chunk.get("content", "") for chunk in chunks]
        query_text_pairs = [[query, text] for text in texts_to_rerank]

        scores = self.model.predict(query_text_pairs)

        scored_chunks = [(chunk, score) for chunk, score in zip(chunks, scores)]
        scored_chunks.sort(key=lambda x: x[1], reverse=True) # Sort by score (x[1]) descending

        reranked_chunks = []
        for chunk, score in scored_chunks[:top_k]:
            updated_chunk = chunk.copy() # Shallow copy to avoid modifying original list items
            updated_chunk["rerank_score"] = float(score) # Ensure it's a Python float for JSON serializability
            reranked_chunks.append(updated_chunk)

        logger.debug(f"Reranked and selected top {top_k} text chunks.")
        return reranked_chunks

    def rerank_image_metadata(self, query: str, metadata_list: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Reranks a list of image metadata dictionaries based on their relevance to the query.
        The relevance is determined by the semantic similarity between the query and the
        'description' field within each metadata dictionary.

        Args:
            query (str): The user's query.
            metadata_list (List[Dict[str, Any]]): List of retrieved image metadata from FAISS.
                                                 Each metadata dict is expected to have a 'description' key.
            top_k (int): Number of top reranked results to return.

        Returns:
            List[Dict[str, Any]]: The top-k reranked metadata dictionaries, sorted by relevance score (highest first).
                                  The original metadata dictionaries are returned with an added 'rerank_score'.
        """
        if not metadata_list:
            logger.warning("Reranker: Empty list of image metadata provided for reranking.")
            return []

        logger.debug(f"Reranking {len(metadata_list)} image metadata entries for query: '{query[:50]}...'")

        descriptions_to_rerank = [meta.get("description", "") for meta in metadata_list]
        query_desc_pairs = [[query, desc] for desc in descriptions_to_rerank]

        scores = self.model.predict(query_desc_pairs)

        scored_metadata = [(meta, score) for meta, score in zip(metadata_list, scores)]
        scored_metadata.sort(key=lambda x: x[1], reverse=True) # Sort by score (x[1]) descending

        reranked_metadata = []
        for meta, score in scored_metadata[:top_k]:
            updated_meta = meta.copy() # Shallow copy
            updated_meta["rerank_score"] = float(score) # Ensure it's a Python float
            reranked_metadata.append(updated_meta)

        logger.debug(f"Reranked and selected top {top_k} image metadata entries.")
        return reranked_metadata

