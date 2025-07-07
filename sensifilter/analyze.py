# analyze.py

import os
from . import scene, utils, keywords, filters, caption, pose, boundingbox
from sensifilter.constants import KEYWORDS_NUDITY, KEYWORDS_VIOLENCE, KEYWORDS_OTHER

# Kombinera alla känsliga nyckelord till en lista
ALL_SENSITIVE_KEYWORDS = KEYWORDS_NUDITY + KEYWORDS_VIOLENCE + KEYWORDS_OTHER

# === Main analysis function ===
def analyze_image(image_path, settings):
    result = {}

    # === Scene classification ===
    if settings.get("enable_scene_filter", True):
        try:
            result["scene"] = scene.classify_scene(image_path)
        except Exception as e:
            result["scene"] = f"Error: {e}"

    # === Skin percentage (total image) ===
    try:
        result["skin_percent"] = utils.estimate_skin_percent(image_path)
    except Exception as e:
        result["skin_percent"] = f"Error: {e}"

    # === Caption generation ===
    if settings.get("enable_caption_filter", True):
        try:
            caption_text, confidence = caption.generate_caption(image_path)
            result["caption"] = (caption_text, confidence)
        except Exception as e:
            result["caption"] = (f"Error: {e}", 0.0)

    # === Keyword matching ===
    if settings.get("enable_keyword_filter", True):
        try:
            caption_text = result["caption"][0] if isinstance(result["caption"], tuple) else ""
            result["keywords"] = keywords.match_keywords(caption_text, ALL_SENSITIVE_KEYWORDS)
        except Exception as e:
            result["keywords"] = [f"Error: {e}"]

    # === Human detection (pose-based) ===
    try:
        result["contains_human"] = pose.contains_human_pose(image_path)
        result["pose"] = "Yes" if result["contains_human"] else "No"
    except Exception as e:
        result["pose"] = f"Error: {e}"
        result["contains_human"] = False

    # === Human detection (YOLO skin ratio + bounding boxes) ===
    try:
        image_bgr = utils.load_image_bgr(image_path)
        boxes = boundingbox.detect_skin_ratio(image_bgr)
        result["skin_human_boxes"] = boxes
        result["max_skin_ratio"] = max((b["skin_ratio"] for b in boxes), default=0)
        if boxes:
            result["annotated_image"] = boundingbox.draw_bounding_boxes(image_bgr, boxes)
    except Exception as e:
        result["skin_human_boxes"] = []
        result["max_skin_ratio"] = 0.0

    # === Final filter decision ===
    try:
        result["label"] = filters.apply_filters(result, settings)
    except Exception as e:
        result["label"] = f"Error: {e}"

    return result
