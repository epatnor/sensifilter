# sensifilter/keywords.py

# Keyword matching for label classification
# keywords.py

from sensifilter.constants import (
    LABEL_SAFE,
    LABEL_REVIEW,
    CATEGORY_KEYWORDS,
    KEYWORDS_WHITELIST
)


def classify_caption(caption, threshold=0.85, allowlist=None, blocklist=None):
    """
    Classifies the caption based on sensitive keywords.
    Returns one of: safe, review, nudity, violence, other_sensitive
    """

    if not caption:
        return LABEL_REVIEW

    # Normalize
    text = caption.lower()

    # Merge allow/blocklist with defaults
    allowlist = set(KEYWORDS_WHITELIST + (allowlist or []))
    custom_blocklist = set(blocklist or [])

    # Allowlist check (early exit)
    for word in allowlist:
        if word in text:
            return LABEL_SAFE

    # Check custom blocklist
    for word in custom_blocklist:
        if word in text:
            return LABEL_REVIEW

    # Check per-category keywords
    for label, keywords in CATEGORY_KEYWORDS.items():
        for word in keywords:
            if word in text:
                return label

    return LABEL_SAFE
