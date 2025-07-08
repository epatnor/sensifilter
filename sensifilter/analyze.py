# analyze.py

import os
import cv2
import numpy as np
from PIL import Image

print("📦 analyze.py loaded from:", __file__)
print("🔧 cv2 available:", cv2.__version__)

from . import scene, utils, keywords, filters, caption, pose, boundingbox
from sensifilter.constants import KEYWORDS_NUDITY, KEYWORDS_VIOLENCE, KEYWORDS_OTHER

ALL_SENSITIVE_KEYWORDS = KEYWORDS_NUDITY + KEYWORDS_VIOLENCE + KEYWORDS_OTHER

def analyze_image(image_path, settings):
    result = {}

    # === BLIP Captioning (run early for fast filtering) ===
    try:
        caption_text, confidence = caption.generate_caption(image_path)
        result["caption"] = (caption_text, confidence)
        print(f"📝 Caption: {caption_text} ({confidence:.2f})")
    except Exception as e:
        result["caption"] = (f"Error: {e}", 0.0)

    # === Keyword matching based on caption ===
    if settings.get("enable_keyword_filter", True):
        try:
            result["keywords"] = keywords.match_keywords(result["caption"][0], ALL_SENSITIVE_KEYWORDS)
        except Exception as e:
            result["keywords"] = [f"Error: {e}"]

    # === Scene classification ===
    if settings.get("enable_scene_filter", True):
        try:
            result["scene"] = scene.classify_scene(image_path)
        except Exception as e:
            result["scene"] = f"Error: {e}"

    # === Pose-based human detection ===
    try:
        result["contains_human"] = pose.contains_human_pose(image_path)
        result["pose"] = "Yes" if result["contains_human"] else "No"
    except Exception as e:
        result["pose"] = f"Error: {e}"
        result["contains_human"] = False

    # === YOLO + skin ratio (only if needed) ===
    run_yolo = True

    # Example early exit rule (can be refined later)
    caption_lc = result["caption"][0].lower()
    if "mountain" in caption_lc or "landscape" in caption_lc:
        print("🏔️ Detected safe scene in caption. Skipping YOLO.")
        run_yolo = False

    if run_yolo:
        try:
            image_bgr = utils.load_image_bgr(image_path)
            boxes = boundingbox.detect_skin_ratio(image_bgr)
            print("🔎 Detected boxes:", boxes)

            result["skin_human_boxes"] = boxes
            result["max_skin_ratio"] = max((b["skin_ratio"] for b in boxes), default=0)

            if boxes:
                annotated_bgr = boundingbox.draw_bounding_boxes(image_bgr, boxes)
                annotated_rgb = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)

                h, w, _ = annotated_rgb.shape
                print(f"🖼 Annotated image size: {w}x{h}")

                if max(h, w) > 8192:
                    print("⚠️ Warning: Extremely high resolution image loaded (>8K)")

                max_size = 3840
                if max(h, w) > max_size:
                    scale = max_size / max(h, w)
                    annotated_rgb = cv2.resize(annotated_rgb, (int(w * scale), int(h * scale)))
                    print(f"🔧 Resized annotated image to: {annotated_rgb.shape[1]}x{annotated_rgb.shape[0]}")

                result["annotated_image"] = Image.fromarray(annotated_rgb)

                del annotated_bgr
                del annotated_rgb

            else:
                print("⚠️ No boxes found, skipping annotation.")
                result["annotated_image"] = None

            del image_bgr

        except Exception as e:
            print(f"❌ Error in YOLO/skin analysis: {e}")
            result["skin_human_boxes"] = []
            result["max_skin_ratio"] = 0.0
            result["annotated_image"] = None
    else:
        result["skin_human_boxes"] = []
        result["max_skin_ratio"] = 0.0
        result["annotated_image"] = None

    # === Final classification ===
    try:
        result["label"] = filters.apply_filters(result, settings)
    except Exception as e:
        result["label"] = f"Error: {e}"

        # === Mark if YOLO was skipped ===
        result["yolo_skipped"] = not run_yolo
        result["blip_confidence"] = result["caption"][1]


    return result
