import os
import sys
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import API_MODEL_PROVIDER, LOCAL_LLM_PATH
from utils.hardware import check_gpu, check_internet

logger = logging.getLogger(__name__)

def check_env_vars():
    """Checks if necessary environment variables are set."""
    api_key_name = f"{API_MODEL_PROVIDER.upper()}_API_KEY".replace('-', '_')
    api_key = os.getenv(api_key_name)

    api_available = bool(api_key)
    local_model_available = os.path.exists(LOCAL_LLM_PATH)
    
    if api_available:
        logger.info(f"{api_key_name} found in environment")
    else:
        logger.warning(f"{api_key_name} not found. API mode unavailable")
    
    if local_model_available:
        logger.info(f"Local model found at {LOCAL_LLM_PATH}")
    else:
        logger.warning(f"Local model not found at {LOCAL_LLM_PATH}")

    return api_available, local_model_available

def check_readiness():
    """
    Performs all checks and determines inference mode.
    Returns: str - 'api', 'local', 'local_cpu', or 'none'
    """
    logger.info("Performing environment check")
    gpu_ok = check_gpu()
    internet_ok = check_internet()
    api_available, local_model_available = check_env_vars()

    if api_available and internet_ok:
        logger.info("MCP Decision: API Mode (Groq)")
        selected_route = "api"
    elif local_model_available and gpu_ok:
        logger.info("MCP Decision: Local Mode with GPU")
        selected_route = "local"
    elif local_model_available:
        logger.info("MCP Decision: Local Mode with CPU (slower)")
        selected_route = "local_cpu"
    else:
        logger.error("No inference method available")
        selected_route = "none"

    logger.info(f"Final inference route: {selected_route}")
    return selected_route

