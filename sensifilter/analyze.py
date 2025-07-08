import os
import cv2
import numpy as np
from PIL import Image
import time

print("📦 analyze.py loaded from:", __file__)
print("🔧 cv2 available:", cv2.__version__)

from . import scene, utils, keywords, filters, caption, pose, boundingbox
from sensifilter.constants import KEYWORDS_NUDITY, KEYWORDS_VIOLENCE, KEYWORDS_OTHER

ALL_SENSITIVE_KEYWORDS = KEYWORDS_NUDITY + KEYWORDS_VIOLENCE + KEYWORDS_OTHER

def analyze_image(image_path, settings):
    result = {}

    # === Optional: timing dictionary for step durations ===
    timings = {}

    start = time.time()
    try:
        caption_text, confidence = caption.generate_caption(image_path)
        result["caption"] = (caption_text, confidence)
        print(f"📝 Caption: {caption_text} ({confidence:.2f})")
    except Exception as e:
        result["caption"] = (f"Error: {e}", 0.0)
    timings["caption"] = time.time() - start

    start = time.time()
    if settings.get("enable_keyword_filter", True):
        try:
            result["keywords"] = keywords.match_keywords(result["caption"][0], ALL_SENSITIVE_KEYWORDS)
        except Exception as e:
            result["keywords"] = [f"Error: {e}"]
    timings["keyword_matching"] = time.time() - start

    start = time.time()
    if settings.get("enable_scene_filter", True):
        try:
            result["scene"] = scene.classify_scene(image_path)
        except Exception as e:
            result["scene"] = f"Error: {e}"
    timings["scene_classification"] = time.time() - start

    start = time.time()
    try:
        result["contains_human"] = pose.contains_human_pose(image_path)
        result["pose"] = "Yes" if result["contains_human"] else "No"
    except Exception as e:
        result["pose"] = f"Error: {e}"
        result["contains_human"] = False
    timings["pose_detection"] = time.time() - start

    run_yolo = True
    caption_lc = result["caption"][0].lower() if isinstance(result["caption"], (list, tuple)) else ""
    if "mountain" in caption_lc or "landscape" in caption_lc:
        print("🏔️ Detected safe scene in caption. Skipping YOLO.")
        run_yolo = False

    start = time.time()
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
    timings["yolo_skin_detection"] = time.time() - start

    result["yolo_skipped"] = not run_yolo
    result["blip_confidence"] = result["caption"][1] if isinstance(result["caption"], (list, tuple)) else 0.0
    result["timings"] = timings

    try:
        result["label"] = filters.apply_filters(result, settings)
    except Exception as e:
        result["label"] = f"Error: {e}"

    return result
