# sensifilter/analyze.py

# analyze.py

from sensifilter import filters, caption, scene, pose, keywords
from sensifilter.constants import LABEL_SAFE, LABEL_REVIEW, DEFAULT_CONFIDENCE_THRESHOLD


def analyze_image(image_path, settings=None, progress_callback=None):
    """
    Analyzes a single image and returns a result dictionary.

    :param image_path: Path to image file
    :param settings: Optional dict with settings (keywords, thresholds, etc)
    :param progress_callback: Optional function(step:str, progress:float)
    :return: dict with label, caption, metadata, etc
    """

    result = {
        "path": image_path,
        "label": LABEL_SAFE,
        "caption": None,
        "scene": None,
        "skin_percent": None,
        "confidence": None
    }

    # Step 1: Early filters
    if progress_callback: progress_callback("filters", 0.1)
    passed, meta = filters.quick_filter(image_path)
    if not passed:
        result["label"] = LABEL_SAFE
        return result
    result.update(meta)

    # Step 2: Scene classification
    if progress_callback: progress_callback("scene", 0.3)
    result["scene"] = scene.classify_scene(image_path)

    # Step 3: Pose detection (optional)
    if progress_callback: progress_callback("pose", 0.4)
    result["pose"] = pose.analyze_pose(image_path)

    # Step 4: Captioning (BLIP)
    if progress_callback: progress_callback("caption", 0.6)
    result["caption"], result["confidence"] = caption.generate_caption(image_path)

    # Step 5: Keyword classification
    if progress_callback: progress_callback("keywords", 0.8)
    result["label"] = keywords.classify_caption(
        result["caption"],
        threshold=settings.get("confidence_threshold", DEFAULT_CONFIDENCE_THRESHOLD),
        allowlist=settings.get("allowlist", []),
        blocklist=settings.get("blocklist", [])
    )

    if progress_callback: progress_callback("done", 1.0)
    return result

