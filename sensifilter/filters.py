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

    # Placeholder-värden
    meta["contains_human"] = True
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

    skin_percent = result.get("skin_percent", 0)
    contains_human = result.get("contains_human", False)

    if skin_percent < min_skin:
        return "safe"

    if not contains_human:
        return "safe"

    # Kontrollera scenklassificering
    if enable_scene:
        scene = result.get("scene", "")
        if isinstance(scene, str):
            scene = scene.lower()
            if any(s in scene for s in ["bathroom", "bedroom", "beach"]):
                return "sensitive"

    # Kontrollera nyckelord
    if enable_keywords:
        keywords = result.get("keywords", [])
        if any(k in ["nude", "genitals", "topless"] for k in keywords):
            return "sensitive"

    # Kontrollera bildtext
    if enable_caption:
        caption = result.get("caption", ("", 0.0))
        if isinstance(caption, tuple):
            caption_text = caption[0].lower()
            if any(word in caption_text for word in ["naked", "lingerie"]):
                return "sensitive"

    return "safe"
