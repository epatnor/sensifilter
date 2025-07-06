# sensifilter/filters.py

# filters.py

from sensifilter.constants import DEFAULT_SKIN_PERCENT_THRESHOLD


def quick_filter(image_path):
    """
    Runs early, fast checks to reject irrelevant images.
    Returns (passed:bool, meta:dict)
    """

    meta = {
        "width": None,
        "height": None,
        "skin_percent": None,
        "contains_human": None
    }

    from PIL import Image

    try:
        with Image.open(image_path) as img:
            width, height = img.size
            meta["width"] = width
            meta["height"] = height
            if width < 100 or height < 100:
                return False, meta
    except Exception:
        return False, meta

    # Placeholder: assume human detection
    meta["contains_human"] = contains_human(image_path)
    if not meta["contains_human"]:
        return False, meta

    # Placeholder: fake skin percent
    meta["skin_percent"] = estimate_skin_percent(image_path)
    if meta["skin_percent"] < DEFAULT_SKIN_PERCENT_THRESHOLD:
        return False, meta

    return True, meta


def contains_human(image_path):
    """
    Placeholder for human detection (YOLO etc)
    """
    return True  # TODO: Implement real detection


def estimate_skin_percent(image_path):
    """
    Placeholder for skin color area estimation
    """
    return 10.0  # TODO: Implement real skin detection
