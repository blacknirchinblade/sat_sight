import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import API_MODEL_PROVIDER, LOCAL_LLM_PATH # Now this should work
from utils.hardware import check_gpu, check_internet

def check_env_vars():
    """
    Checks if necessary environment variables are set.
    """
    api_key_name = f"{API_MODEL_PROVIDER.upper()}_API_KEY".replace('-', '_')
    api_key = os.getenv(api_key_name)

    if api_key:
        print(f"✅ {api_key_name} found in environment.")
        api_available = True
    else:
        print(f"⚠️  {api_key_name} not found in environment. API mode will be unavailable.")
        api_available = False

    if os.path.exists(LOCAL_LLM_PATH):
        print(f"✅ Local model found at {LOCAL_LLM_PATH}")
        local_model_available = True
    else:
        print(f"❌ Local model not found at {LOCAL_LLM_PATH}. Please download it.")
        local_model_available = False

    return api_available, local_model_available

def check_readiness():
    """
    Performs all checks: GPU, Internet, Env Vars.
    Determines readiness for API vs Local mode (MCP logic).
    """
    print("--- Environment Check ---")
    gpu_ok = check_gpu()
    internet_ok = check_internet()
    api_available, local_model_available = check_env_vars()

    if api_available and internet_ok:
        print("\n--- MCP Decision: API Mode Preferred ---")
        print("Status: API key available, internet OK, GPU status irrelevant for API call.")
        print("Action: System configured for API-based inference (e.g., Groq).")
        selected_route = "api"
    elif local_model_available and gpu_ok:
        print("\n--- MCP Decision: Local Mode Selected (Fallback) ---")
        print("Status: API unavailable or no internet, but local model and GPU OK.")
        print("Action: System configured for local inference (e.g., LLaMA-3 GGUF).")
        selected_route = "local"
    elif local_model_available:
        print("\n--- MCP Decision: Local Mode (CPU) Selected (Fallback) ---")
        print("Status: API unavailable, no GPU, but local model exists.")
        print("Action: System configured for local inference (LLaMA-3 GGUF) on CPU. Performance may be slow.")
        selected_route = "local_cpu" # Could be handled differently later
    else:
        print("\n--- MCP Decision: No Inference Method Available ---")
        print("Status: No API key/internet AND no local model found.")
        print("Action: Cannot proceed. Please set API key or download a local model.")
        selected_route = "none"

    print(f"--- Final Inference Route: {selected_route} ---")
    return selected_route

