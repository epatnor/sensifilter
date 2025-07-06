# filters.py

from sensifilter.constants import DEFAULT_SKIN_PERCENT_THRESHOLD
from sensifilter.utils import estimate_skin_percent
from PIL import Image


def quick_filter(image_path):
    """
    Kör snabba, tidiga filter för att direkt slänga ointressanta bilder.
    Returnerar (True, meta) om bilden passerar.
    """

    meta = {
        "width": None,
        "height": None,
        "skin_percent": None,
        "contains_human": None,
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

    meta["contains_human"] = True  # placeholder
    meta["skin_percent"] = estimate_skin_percent(image_path)

    if meta["skin_percent"] < DEFAULT_SKIN_PERCENT_THRESHOLD:
        return False, meta

    return True, meta


def apply_filters(result: dict, settings: dict = None):
    """
    Kör hela filtersystemet på ett analysresultat.
    Returnerar etiketten (safe/sensitive) eller 'review'.
    """
    if settings is None:
        settings = {}

    min_skin = settings.get("min_skin_percent", 15)
    enable_scene = settings.get("enable_scene_filter", True)
    enable_keywords = settings.get("enable_keyword_filter", True)
    enable_caption = settings.get("enable_caption_filter", True)

    # För många kläder? = safe
    if result.get("skin_percent", 0) < min_skin:
        return "safe"

    # Inget mänskligt? = safe
    if not result.get("contains_human", False):
        return "safe"

    # Sensitiv scen?
    if enable_scene and isinstance(result.get("scene"), str):
        scene = result["scene"].lower()
        if "bathroom" in scene or "bedroom" in scene or "beach" in scene:
            return "sensitive"

    # Nyckelord?
    if enable_keywords:
        keywords = result.get("keywords", [])
        if any(k in ["nude", "genitals", "topless"] for k in keywords):
            return "sensitive"

    # Bildtext
    if enable_caption and isinstance(result.get("caption"), tuple):
        caption_text, conf = result["caption"]
        if "naked" in caption_text.lower() or "lingerie" in caption_text.lower():
            return "sensitive"

    return "safe"
