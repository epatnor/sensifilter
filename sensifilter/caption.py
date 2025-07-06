# sensifilter/caption.py

from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch

# === Ladda modell och processor ===
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

# === Caption-funktion ===
def generate_caption(image_path):
    """
    Genererar en semantisk bildbeskrivning med BLIP.
    Returnerar (caption:str, confidence:float)
    """
    try:
        image = Image.open(image_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt")
        with torch.no_grad():
            output = model.generate(**inputs)
        caption = processor.decode(output[0], skip_special_tokens=True)

        # BLIP base ger inte confidence, så vi returnerar 1.0 som placeholder
        return caption, 1.0

    except Exception as e:
        return f"Error: {e}", 0.0
