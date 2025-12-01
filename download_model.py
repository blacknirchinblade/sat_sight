# download_model.py
from huggingface_hub import hf_hub_download
import os

# Define model details
repo_id = "TheBloke/LLaMA-Pro-8B-Instruct-GGUF"
filename = "llama-pro-8b-instruct.Q4_K_M.gguf" # Quantization level
local_dir = "data/models"

# Download the file
try:
    print(f"Downloading {filename} from {repo_id}...")
    local_filename = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        local_dir=local_dir,
        local_dir_use_symlinks=False # Ensures a copy is made
    )
    print(f"✅ Model downloaded successfully to {local_filename}")
    print(f"File size: {os.path.getsize(local_filename) / (1024**3):.2f} GB")
except Exception as e:
    print(f"❌ Error downloading model: {e}")
    # Fallback to Phi-3-mini if Llama-3 fails for some reason
    print("\n--- Trying Phi-3-mini as an alternative... ---")
    repo_id_alt = "microsoft/Phi-3-mini-4k-instruct-gguf"
    filename_alt = "Phi-3-mini-4k-instruct-q4.gguf" # Or another quantization if preferred
    try:
        print(f"Downloading {filename_alt} from {repo_id_alt}...")
        local_filename_alt = hf_hub_download(
            repo_id=repo_id_alt,
            filename=filename_alt,
            local_dir=local_dir,
            local_dir_use_symlinks=False
        )
        print(f"✅ Alternative model (Phi-3-mini) downloaded successfully to {local_filename_alt}")
        print(f"File size: {os.path.getsize(local_filename_alt) / (1024**3):.2f} GB")
        # Update config or note the new file
        print(f"\nNote: Update your config.py LOCAL_LLM_PATH to: {local_filename_alt}")
    except Exception as e2:
        print(f"❌ Error downloading alternative model: {e2}")
        print("Please check your internet connection and Hugging Face access.")