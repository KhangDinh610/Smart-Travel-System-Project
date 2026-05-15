from __future__ import annotations

import io
import torch
from PIL import Image
from rembg import remove
from transformers import CLIPModel, CLIPProcessor


class ImageVectorExtractor:
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32") -> None:
        self.device = self._select_device()
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.model.eval()

    def _select_device(self) -> torch.device:
        if torch.cuda.is_available():
            return torch.device("cuda")
        if hasattr(torch, "xpu") and torch.xpu.is_available():
            return torch.device("xpu")
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")

    def load_image(self, file_obj) -> Image.Image:
        return Image.open(file_obj).convert("RGB")

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        removed = remove(image)
        if not isinstance(removed, Image.Image):
            removed = Image.open(io.BytesIO(removed))

        removed = removed.convert("RGBA")
        white_background = Image.new("RGBA", removed.size, (255, 255, 255, 255))
        white_background.paste(removed, (0, 0), removed)
        return white_background.convert("RGB")

    def extract_vector(self, image: Image.Image) -> np.ndarray:
        inputs = self.processor(images=image, return_tensors="pt")
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
        pixel_values = inputs.get("pixel_values")
        if pixel_values is None:
            raise ValueError("Missing pixel_values for CLIP image encoder.")

        with torch.no_grad():
            features = None
            if hasattr(self.model, "get_image_features"):
                features = self.model.get_image_features(pixel_values=pixel_values)
            if not torch.is_tensor(features):
                vision_outputs = self.model.vision_model(pixel_values=pixel_values)
                features = getattr(vision_outputs, "pooler_output", None)
            if not torch.is_tensor(features):
                raise ValueError("Unable to extract image features from CLIP model.")

            features = features / features.norm(dim=-1, keepdim=True)

        return features[0].cpu().numpy()
