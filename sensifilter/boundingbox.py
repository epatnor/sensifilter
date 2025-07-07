# boundingbox.py

import torch
import cv2
print("📦 boundingbox.py loaded from:", __file__)
import numpy as np
from ultralytics import YOLO

# === Välj device automatiskt (GPU om möjligt) ===
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# === Byt till större YOLOv8-modell för bättre persondetektering ===
MODEL = YOLO("yolov8s.pt").to(DEVICE)

print("✅ YOLOv8 model loaded on device:", DEVICE)

def detect_skin_ratio(image_bgr):
    """
    Analyserar bilden och returnerar skin/human-ratio för varje person som hittas.
    Returnerar en lista med:
    [
        {"box": (x1, y1, x2, y2), "skin_ratio": float},
        ...
    ]
    """
    print("🔍 Running YOLOv8 on input image...")
    try:
        results = MODEL(image_bgr)
    except Exception as e:
        print(f"❌ Error running YOLO model: {e}")
        return []

    if not results or not hasattr(results[0], "boxes"):
        print("⚠️ YOLO did not return any valid boxes.")
        return []

    results = results[0]
    boxes_raw = results.boxes
    if boxes_raw is None:
        print("⚠️ YOLO result.boxes is None.")
        return []

    try:
        xyxy = boxes_raw.xyxy.cpu().numpy()
        classes = boxes_raw.cls.cpu().numpy()
    except Exception as e:
        print(f"❌ Failed to parse YOLO output: {e}")
        return []

    print("== YOLO raw output ==")
    print(f"Total detections: {len(classes)}")
    print("Classes:", classes)

    output = []

    for i, (box, cls_id) in enumerate(zip(xyxy, classes)):
        print(f"→ Detection {i}: class_id={cls_id}, box={box}")
        if int(cls_id) != 0:
            print("   Skipped (not a person)")
            continue

        x1, y1, x2, y2 = map(int, box)
        crop = image_bgr[y1:y2, x1:x2]
        if crop.size == 0:
            print("   Skipped (empty crop)")
            continue

        skin_mask = detect_skin(crop)
        skin_area = np.count_nonzero(skin_mask)
        total_area = crop.shape[0] * crop.shape[1]
        ratio = skin_area / total_area if total_area > 0 else 0

        print(f"   → skin_ratio = {round(ratio, 3)}")

        output.append({
            "box": (x1, y1, x2, y2),
            "skin_ratio": round(ratio, 3)
        })

    print(f"==> Final person boxes: {len(output)}")
    return output



def detect_skin(image_bgr):
    """
    Enkel YCrCb-baserad huddetektion. Returnerar binär mask.
    """
    img_ycrcb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2YCrCb)
    lower = np.array([0, 133, 77], dtype=np.uint8)
    upper = np.array([255, 173, 127], dtype=np.uint8)
    mask = cv2.inRange(img_ycrcb, lower, upper)
    return mask


def draw_bounding_boxes(image_bgr, boxes):
    """
    Returnerar en kopia av bilden med ritade bounding boxes.
    """
    output_img = image_bgr.copy()

    for box in boxes:
        x1, y1, x2, y2 = box["box"]
        ratio = box["skin_ratio"]
        label = f"Skin {round(ratio * 100)}%"
        color = (0, 255, 0) if ratio > 0.15 else (0, 0, 255)
        cv2.rectangle(output_img, (x1, y1), (x2, y2), color, 2)
        cv2.putText(output_img, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)

    return output_img
