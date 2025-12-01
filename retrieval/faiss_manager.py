import logging
import numpy as np
import faiss
import pickle
from pathlib import Path
from sat_sight.core.config import FAISS_INDEX_PATH, DEBUG

logger = logging.getLogger(__name__)

class FAISSManager:
    """
    A class to manage the FAISS index for image embeddings.
    Handles loading, saving, adding vectors, and searching.
    """
    def __init__(self, index_path: str = None, dimension: int = 768): # CLIP ViT-L/14 outputs 768-dim vectors
        """
        Initializes the FAISS manager.

        Args:
            index_path (str, optional): Path to the FAISS index file. If None, uses config.
            dimension (int): Dimensionality of the embeddings (e.g., 768 for CLIP ViT-L/14).
        """
        self.index_path = index_path or FAISS_INDEX_PATH
        self.dimension = dimension
        self.index = None
        self.metadata_map = {} # Map FAISS ID -> metadata (e.g., image path, class, description)
        self.load_index()

    def load_index(self):
        """
        Loads the FAISS index and associated metadata map from disk.
        If the index file doesn't exist, it creates an empty one.
        """
        index_file = Path(self.index_path)
        metadata_file = index_file.with_suffix('.meta.pkl') # Store metadata separately

        if index_file.exists():
            logger.info(f"Loading existing FAISS index from {self.index_path}")
            try:
                self.index = faiss.read_index(str(index_file))
                logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors.")
            except Exception as e:
                logger.error(f"Failed to load FAISS index: {e}. Creating a new one.")
                self.index = faiss.IndexFlatIP(self.dimension) # Inner Product (Cosine similarity after normalization)
        else:
            logger.info(f"FAISS index not found at {self.index_path}. Creating a new one.")
            self.index = faiss.IndexFlatIP(self.dimension) # Inner Product (Cosine similarity after normalization)

        if metadata_file.exists():
            logger.info(f"Loading metadata map from {metadata_file}")
            try:
                with open(metadata_file, 'rb') as f:
                    self.metadata_map = pickle.load(f)
                logger.info(f"Loaded metadata for {len(self.metadata_map)} vectors.")
            except Exception as e:
                logger.error(f"Failed to load metadata map: {e}. Starting with empty map.")
                self.metadata_map = {}
        else:
            logger.info(f"Metadata map not found at {metadata_file}. Starting with empty map.")
            self.metadata_map = {}

    def save_index(self):
        """
        Saves the current FAISS index and metadata map to disk.
        """
        index_file = Path(self.index_path)
        metadata_file = index_file.with_suffix('.meta.pkl')

        logger.info(f"Saving FAISS index to {self.index_path}")
        faiss.write_index(self.index, str(self.index_path))
        logger.info(f"Saving metadata map to {metadata_file}")
        with open(metadata_file, 'wb') as f:
            pickle.dump(self.metadata_map, f)

    def add_embedding(self, embedding: np.ndarray, metadata: dict, id: int = None):
        """
        Adds a single embedding and its metadata to the index.

        Args:
            embedding (np.ndarray): The image embedding (1 x dimension).
            metadata (dict): Associated metadata (e.g., {'path': '...', 'class': '...', 'description': '...'}).
            id (int, optional): Specific ID for the embedding. If None, FAISS assigns one.
        """
        if embedding.ndim == 1:
            embedding = embedding.reshape(1, -1) # Ensure it's 2D (N, D)


        if id is not None:
            logger.warning("Setting specific ID not directly supported with IndexFlat. Adding and mapping auto ID.")
            self.index.add(embedding.astype('float32'))
            assigned_id = self.index.ntotal - 1 # The ID assigned by FAISS
            self.metadata_map[assigned_id] = metadata
        else:
            self.index.add(embedding.astype('float32'))
            assigned_id = self.index.ntotal - 1
            self.metadata_map[assigned_id] = metadata

        logger.debug(f"Added embedding with FAISS ID {assigned_id} and metadata: {metadata}")

    def search(self, query_embedding: np.ndarray, k: int = 5) -> tuple:
        """
        Searches the index for the k most similar embeddings.

        Args:
            query_embedding (np.ndarray): The query embedding (1 x dimension), should be normalized.
            k (int): Number of nearest neighbors to retrieve.

        Returns:
            tuple: (distances, metadata_list)
                   distances (np.ndarray): Similarity scores (inner product, higher is more similar).
                   metadata_list (list): List of metadata dictionaries corresponding to the retrieved IDs.
        """
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)


        if self.index.ntotal == 0:
            logger.warning("FAISS index is empty. Returning empty results.")
            return np.array([]), []

        logger.debug(f"Searching for {k} nearest neighbors.")
        distances, indices = self.index.search(query_embedding.astype('float32'), k)

        if isinstance(self.metadata_map, dict):
            metadata_list = [self.metadata_map.get(i, {}) for i in indices[0]]
        elif isinstance(self.metadata_map, list):
            metadata_list = [self.metadata_map[i] if i < len(self.metadata_map) else {} for i in indices[0]]
        else:
            metadata_list = [{} for _ in indices[0]]

        logger.debug(f"Search returned {len(metadata_list)} results.")
        return distances[0], metadata_list # Return first query's results (distances, metadatas)

