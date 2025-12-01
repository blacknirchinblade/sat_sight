import logging
import torch
import open_clip
from PIL import Image
from sat_sight.core.config import DEBUG

logger = logging.getLogger(__name__)

class CLIPEncoder:
    """
    A class to load the CLIP model and encode images/texts.
    Uses open_clip library which is compatible with Hugging Face models and original CLIP.
    """
    def __init__(self, model_name: str = "ViT-L-14", pretrained: str = "openai"):
        """
        Initializes the CLIP encoder.

        Args:
            model_name (str): Name of the CLIP visual model (e.g., "ViT-L-14").
            pretrained (str): Pretrained weights source (e.g., "openai").
        """
        logger.info(f"Initializing CLIP model: {model_name} from {pretrained}")
        try:
            self.model, _, self.preprocess = open_clip.create_model_and_transforms(
                model_name, pretrained=pretrained, device='cpu' # Load on CPU initially
            )
            self.model.eval() # Set to evaluation mode
            logger.info("CLIP model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load CLIP model: {e}")
            raise e

    def encode_image(self, image_path: str) -> torch.Tensor:
        """
        Encodes a single image from a file path.

        Args:
            image_path (str): Path to the image file.

        Returns:
            torch.Tensor: The image embedding (1 x embedding_dim).
        """
        try:
            logger.debug(f"Encoding image: {image_path}")
            image = Image.open(image_path).convert("RGB") # Ensure RGB
            image_tensor = self.preprocess(image).unsqueeze(0) # Add batch dimension

            with torch.no_grad(): # Disable gradient calculation for efficiency
                image_features = self.model.encode_image(image_tensor)
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)

            logger.debug(f"Encoded image shape: {image_features.shape}")
            return image_features.squeeze(0).cpu() # Remove batch dim and move to CPU for storage
        except Exception as e:
            logger.error(f"Error encoding image {image_path}: {e}")
            raise e

    def encode_text(self, text: str) -> torch.Tensor:
        """
        Encodes a single text prompt.

        Args:
            text (str): The text prompt.

        Returns:
            torch.Tensor: The text embedding (1 x embedding_dim).
        """
        try:
            logger.debug(f"Encoding text: {text[:50]}...") # Log first 50 chars
            text_tokens = open_clip.tokenize([text]) # Tokenize as a list

            with torch.no_grad():
                text_features = self.model.encode_text(text_tokens)
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)

            logger.debug(f"Encoded text shape: {text_features.shape}")
            return text_features.squeeze(0).cpu() # Remove batch dim and move to CPU
        except Exception as e:
            logger.error(f"Error encoding text '{text}': {e}")
            raise e

