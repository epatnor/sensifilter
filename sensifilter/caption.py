# sensifilter/caption.py

from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch

# === Globala cache-variabler ===
_processor = None
_model = None


# === Ladda BLIP-modellen vid behov ===
def _load_blip():
    global _processor, _model
    if _processor is None or _model is None:
        _processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        _model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        _model.eval()


# === Caption-funktion ===
def generate_caption(image_path):
    """
    Genererar en semantisk bildbeskrivning med BLIP.
    Returnerar (caption:str, confidence:float)
    """
    try:
        _load_blip()

        image = Image.open(image_path).convert("RGB")
        inputs = _processor(images=image, return_tensors="pt")

        with torch.no_grad():
            output = _model.generate(**inputs)

        caption = _processor.decode(output[0], skip_special_tokens=True)

        # BLIP ger inte confidence, så vi returnerar 1.0 som placeholder
        return caption, 1.0

    except Exception as e:
        return f"Error: {e}", 0.0
