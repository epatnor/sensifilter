def detect_skin_ratio(image_bgr):
    """
    Analyserar bilden och returnerar skin/human-ratio för varje person som hittas.
    """
    print("🔍 Running YOLOv8 on input image...")
    results = MODEL(image_bgr)[0]
    boxes = results.boxes.xyxy.cpu().numpy()
    classes = results.boxes.cls.cpu().numpy()

    print("== YOLO raw output ==")
    print(f"Total detections: {len(classes)}")
    print("Classes:", classes)

    output = []
    h, w = image_bgr.shape[:2]

    for i, (box, cls_id) in enumerate(zip(boxes, classes)):
        print(f"→ Detection {i}: class_id={cls_id}, box={box}")
        if int(cls_id) != 0:
            print("   Skipped (not a person)")
            continue

        # Begränsa till bildens storlek
        x1, y1, x2, y2 = map(int, box)
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)

        if x2 <= x1 or y2 <= y1:
            print("   Skipped (invalid box after clipping)")
            continue

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

def draw_bounding_boxes(image_bgr, boxes):
    """
    Tar in en BGR-bild och en lista av boxar som [{box: (x1, y1, x2, y2), skin_ratio: float}]
    och returnerar en annoterad bild med rektanglar och procenttext.
    """
    annotated = image_bgr.copy()
    for b in boxes:
        x1, y1, x2, y2 = b["box"]
        ratio = b["skin_ratio"]
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            annotated,
            f"{ratio:.1%}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1,
            cv2.LINE_AA
        )
    return annotated
