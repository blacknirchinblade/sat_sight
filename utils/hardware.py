import torch
import logging

logger = logging.getLogger(__name__)

def check_gpu():
    """
    Checks if CUDA is available and if the GPU has sufficient memory.
    """
    if not torch.cuda.is_available():
        logger.warning("CUDA not available. Cannot use GPU")
        return False

    gpu_name = torch.cuda.get_device_name(0)
    total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)

    logger.info(f"CUDA available. GPU: {gpu_name}, Total Memory: {total_memory:.2f} GB")
    if total_memory >= 14.0:
        logger.info("Sufficient GPU memory detected")
        return True
    else:
        logger.warning(f"GPU memory ({total_memory:.2f} GB) might be insufficient for large models")
        return False

def check_internet():
    """
    Checks basic internet connectivity.
    """
    import requests
    try:
        requests.get("https://httpbin.org/get", timeout=3)
        logger.info("Internet connection is available")
        return True
    except requests.ConnectionError:
        logger.warning("No internet connection detected")
        return False
    except requests.Timeout:
        logger.warning("Internet connection is slow or unreliable")
        return False

