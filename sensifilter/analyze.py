# analyze.py

import os
from . import scene, utils, keywords, filters, caption, pose

# === Main analysis function ===
def analyze_image(image_path, settings):
    result = {}

    # === Scene classification ===
    if settings.get("enable_scene_filter", True):
        try:
            result["scene"] = scene.classify_scene(image_path)
        except Exception as e:
            result["scene"] = f"Error: {e}"

    # === Skin percentage estimation ===
    try:
        result["skin_percent"] = utils.estimate_skin_percent(image_path)
    except Exception as e:
        result["skin_percent"] = f"Error: {e}"

    # === Caption generation ===
    if settings.get("enable_caption_filter", True):
        try:
            result["caption"] = caption.generate_caption(image_path)
        except Exception as e:
            result["caption"] = f"Error: {e}"

    # === Keyword detection ===
    if settings.get("enable_keyword_filter", True):
        try:
            result["keywords"] = keywords.extract_keywords(image_path)
        except Exception as e:
            result["keywords"] = [f"Error: {e}"]

    # === Human detection (pose) ===
    try:
        result["contains_human"] = pose.contains_human_pose(image_path)
        result["pose"] = "Yes" if result["contains_human"] else "No"
    except Exception as e:
        result["pose"] = f"Error: {e}"
        result["contains_human"] = False

    # === Filtering ===
    try:
        result["label"] = filters.apply_filters(result, settings)
    except Exception as e:
        result["label"] = f"Error: {e}"

    return result
