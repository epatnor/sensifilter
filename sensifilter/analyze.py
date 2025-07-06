# analyze.py

import os
from .filters import estimate_skin_percent, detect_humans
from .scene import classify_scene
from .keywords import match_keywords
from .constants import DEFAULT_KEYWORDS

# === Kör hela analysflödet för en bild och returnera resultatet ===
def analyze_image(image_path):
    result = {}

    # Hudberäkning
    skin_percent = estimate_skin_percent(image_path)
    result["skin_percent"] = round(skin_percent, 2)

    # Persondetektion (placeholder för nu)
    contains_human = detect_humans(image_path)
    result["contains_human"] = contains_human

    # Scenklassning
    try:
        result["scene"] = classify_scene(image_path)
    except Exception as e:
        result["scene"] = f"error: {str(e)}"

    # Bildtext (placeholder)
    result["caption"] = "No caption available yet"

    # Poseanalys (placeholder)
    result["pose"] = "unknown"

    # Nyckelordsanalys
    result["matched_keywords"] = match_keywords(result["caption"], DEFAULT_KEYWORDS)

    # Final bedömning (enkel regelbaserad)
    if "nude" in result["matched_keywords"] or result["skin_percent"] > 50:
        result["label"] = "sensitive"
    else:
        result["label"] = "safe"

    return result
