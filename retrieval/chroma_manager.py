import logging
import chromadb
from chromadb.utils.embedding_functions import EmbeddingFunction, SentenceTransformerEmbeddingFunction # Import the correct class
from sat_sight.core.config import CHROMA_DB_PATH, CHROMA_RETRIEVAL_K

logger = logging.getLogger(__name__)

class ChromaManager:
    """
    A class to manage the ChromaDB vector store for text metadata.
    Uses ChromaDB's SentenceTransformerEmbeddingFunction for local compatibility.
    """
    def __init__(self, db_path: str = None, embedding_model_name: str = "BAAI/bge-small-en-v1.5"):
        """
        Initializes the ChromaDB manager.

        Args:
            db_path (str, optional): Path to the ChromaDB directory. If None, uses config.
            embedding_model_name (str): Name of the SentenceTransformers model for embeddings.
        """
        self.db_path = db_path or CHROMA_DB_PATH
        self.embedding_model_name = embedding_model_name
        self.client = None
        self.collection = None
        self.embedding_function = None
        self._initialize_db()

    def _initialize_db(self):
        """
        Initializes the ChromaDB client and loads the collection.
        """
        try:
            self.client = chromadb.PersistentClient(path=self.db_path)

            self.embedding_function = SentenceTransformerEmbeddingFunction(model_name=self.embedding_model_name)

            collection_name = "satellite_metadata_text"
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"ChromaDB collection '{collection_name}' loaded successfully from {self.db_path}.")
            logger.info(f"Collection contains {self.collection.count()} documents.")

        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            logger.warning("ChromaDB will be unavailable. Text retrieval will return empty results.")
            self.collection = None

    def query(self, query_text: str, k: int = None) -> list:
        """
        Queries the ChromaDB collection for relevant text chunks.

        Args:
            query_text (str): The query text.
            k (int, optional): Number of nearest neighbors to retrieve. Defaults to config.

        Returns:
            list: List of retrieved text chunks as dictionaries.
                  Returns empty list if collection is unavailable.
        """
        if not self.collection:
            logger.warning("ChromaDB collection is not available. Returning empty results.")
            return []

        k = k or CHROMA_RETRIEVAL_K
        logger.debug(f"Querying ChromaDB for: {query_text[:50]}... (k={k})")

        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=k
            )
            retrieved_docs = []
            for i in range(len(results['ids'][0])):
                doc = {
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else None
                }
                retrieved_docs.append(doc)

            logger.debug(f"ChromaDB query returned {len(retrieved_docs)} results.")
            return retrieved_docs

        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")
            return []

