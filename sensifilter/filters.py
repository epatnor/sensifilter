# filters.py

import cv2
import numpy as np
from PIL import Image
from sensifilter.constants import DEFAULT_SKIN_PERCENT_THRESHOLD

# === Kör snabba filter (upplösning, människa, hudprocent) ===
def quick_filter(image_path):
    meta = {
        "width": None,
        "height": None,
        "skin_percent": None,
        "contains_human": None
    }

    try:
        with Image.open(image_path) as img:
            width, height = img.size
            meta["width"] = width
            meta["height"] = height
            if width < 100 or height < 100:
                return False, meta
    except Exception:
        return False, meta

    meta["contains_human"] = detect_humans(image_path)
    if not meta["contains_human"]:
        return False, meta

    meta["skin_percent"] = estimate_skin_percent(image_path)
    if meta["skin_percent"] < DEFAULT_SKIN_PERCENT_THRESHOLD:
        return False, meta

    return True, meta

# === Riktigt HSV-baserad hudanalys ===
def estimate_skin_percent(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return 0.0

    img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 40, 60], dtype=np.uint8)
    upper = np.array([25, 255, 255], dtype=np.uint8)
    mask = cv2.inRange(img, lower, upper)

    skin_pixels = cv2.countNonZero(mask)
    total_pixels = img.shape[0] * img.shape[1]

    if total_pixels == 0:
        return 0.0

    return (skin_pixels / total_pixels) * 100

# === Placeholder för framtida persondetektion (t.ex. YOLOv8) ===
def detect_humans(image_path):
    return True
