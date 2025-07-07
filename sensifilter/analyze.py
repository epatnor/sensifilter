# analyze.py

import os
import cv2
import numpy as np
from PIL import Image
import io
import base64

print("📦 analyze.py loaded from:", __file__)
print("🔧 cv2 available:", cv2.__version__)

from . import scene, utils, keywords, filters, caption, pose, boundingbox
from sensifilter.constants import KEYWORDS_NUDITY, KEYWORDS_VIOLENCE, KEYWORDS_OTHER

ALL_SENSITIVE_KEYWORDS = KEYWORDS_NUDITY + KEYWORDS_VIOLENCE + KEYWORDS_OTHER

def analyze_image(image_path, settings):
    result = {}

    # Scene classification
    if settings.get("enable_scene_filter", True):
        try:
            result["scene"] = scene.classify_scene(image_path)
        except Exception as e:
            result["scene"] = f"Error: {e}"

    # Skin % for entire image
    try:
        result["skin_percent"] = utils.estimate_skin_percent(image_path)
    except Exception as e:
        result["skin_percent"] = f"Error: {e}"

    # Caption
    if settings.get("enable_caption_filter", True):
        try:
            caption_text, confidence = caption.generate_caption(image_path)
            result["caption"] = (caption_text, confidence)
        except Exception as e:
            result["caption"] = (f"Error: {e}", 0.0)

    # Keyword matching
    if settings.get("enable_keyword_filter", True):
        try:
            caption_text = result["caption"][0] if isinstance(result["caption"], tuple) else ""
            result["keywords"] = keywords.match_keywords(caption_text, ALL_SENSITIVE_KEYWORDS)
        except Exception as e:
            result["keywords"] = [f"Error: {e}"]

    # Human detection via pose
    try:
        result["contains_human"] = pose.contains_human_pose(image_path)
        result["pose"] = "Yes" if result["contains_human"] else "No"
    except Exception as e:
        result["pose"] = f"Error: {e}"
        result["contains_human"] = False

    # YOLO + skin analysis
    try:
        image_bgr = utils.load_image_bgr(image_path)
        boxes = boundingbox.detect_skin_ratio(image_bgr)
        print("🔎 Detected boxes:", boxes)
    
        result["skin_human_boxes"] = boxes
        result["max_skin_ratio"] = max((b["skin_ratio"] for b in boxes), default=0)
    
        if boxes:
            annotated_bgr = boundingbox.draw_bounding_boxes(image_bgr, boxes)
            annotated_rgb = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)
    
            # Begränsa storlek
            h, w, _ = annotated_rgb.shape
            print(f"🖼 Annotated image size: {w}x{h}")
            max_size = 1280
            if max(h, w) > max_size:
                scale = max_size / max(h, w)
                annotated_rgb = cv2.resize(annotated_rgb, (int(w * scale), int(h * scale)))
                print(f"🔧 Resized annotated image to: {annotated_rgb.shape[1]}x{annotated_rgb.shape[0]}")
    
            # Komprimera via Pillow till JPEG och läs tillbaka som NumPy-array
            pil_image = Image.fromarray(annotated_rgb)
            with io.BytesIO() as buffer:
                pil_image.save(buffer, format="JPEG", quality=85)
                compressed = buffer.getvalue()
                pil_reloaded = Image.open(io.BytesIO(compressed)).convert("RGB")
                result["annotated_image"] = np.array(pil_reloaded)
    
        else:
            print("⚠️ No boxes found, skipping annotation.")
            result["annotated_image"] = None
    
        result["original_image_rgb"] = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    
    except Exception as e:
        print(f"❌ Error in YOLO/skin analysis: {e}")
        result["skin_human_boxes"] = []
        result["max_skin_ratio"] = 0.0
        result["annotated_image"] = None
        result["original_image_rgb"] = None


    try:
        result["label"] = filters.apply_filters(result, settings)
    except Exception as e:
        result["label"] = f"Error: {e}"

    return result
