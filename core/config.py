import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

API_MODEL_NAME = "llama-3.3-70b-versatile" # Groq model name
API_MODEL_PROVIDER = "groq" # e.g., "groq", "openrouter", "azure"

LOCAL_LLM_PATH = os.getenv("LOCAL_LLM_PATH", os.path.join(BASE_DIR, "data/models/Phi-3-mini-4k-instruct-q4.gguf"))
LOCAL_LLM_TYPE = "llama-cpp" # or "transformers" if using different loader
LOCAL_LLM_PARAMS = {
    "n_gpu_layers": 40, # Offload as much as possible to GPU
    "n_ctx": 4096,
    "verbose": False
}

RERANK_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2" # Model for cross-encoder reranking
RERANK_TOP_K = 5 # Number of results to keep after reranking (increased from 3)



USE_LOCAL_FALLBACK = True # If API fails or is unavailable, use local model
PREFER_API_IF_AVAILABLE = True # If both are available, use API

STM_SIZE = 5 # Number of turns to keep in Short-Term Memory
LTM_COLLECTION_NAME = "sat_sight_ltm"
EPISODIC_DB_PATH = os.path.join(BASE_DIR, "data/episodic_memory.db") # If using SQLite, otherwise connection string

IMAGE_DATA_DIR = os.path.join(BASE_DIR, "data/images")
METADATA_DIR = os.path.join(BASE_DIR, "data/metadata")
VECTOR_STORE_DIR = os.path.join(BASE_DIR, "data/vector_stores")
FAISS_INDEX_PATH = os.path.join(VECTOR_STORE_DIR, "faiss_index.bin")
CHROMA_DB_PATH = os.path.join(VECTOR_STORE_DIR, "chroma_db")

FAISS_RETRIEVAL_K = 10 # Number of similar images to retrieve (increased from 5)
CHROMA_RETRIEVAL_K = 10 # Number of relevant text chunks to retrieve (increased from 5)
WEB_SEARCH_ENABLED = True # Toggle for search agent
WEB_SEARCH_K = 3 # Number of web snippets to retrieve

UI_TITLE = "Sat-Sight: Agentic Satellite QA"
UI_DESCRIPTION = "Ask questions about satellite images with AI."




DEBUG = os.getenv("DEBUG", "False").lower() == "true"