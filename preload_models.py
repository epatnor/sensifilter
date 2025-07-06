# preload_models.py

import os
from transformers import BlipProcessor, BlipForConditionalGeneration


def download_blip():
    print("[BLIP] Downloading model and processor...")

    # Download and cache BLIP model
    BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

    print("[BLIP] Done.")


if __name__ == "__main__":
    print("[🔽] Preloading models for sensifilter...")
    download_blip()
    print("[✅] All models ready.")
