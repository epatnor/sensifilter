# keywords.py

from sensifilter.constants import (
    LABEL_SAFE,
    LABEL_REVIEW,
    CATEGORY_KEYWORDS,
    KEYWORDS_WHITELIST
)

# === Klassificera bildtext utifrån nyckelord ===
def classify_caption(caption, threshold=0.85, allowlist=None, blocklist=None):
    if not caption:
        return LABEL_REVIEW

    text = caption.lower()

    allowlist = set(KEYWORDS_WHITELIST + (allowlist or []))
    custom_blocklist = set(blocklist or [])

    for word in allowlist:
        if word in text:
            return LABEL_SAFE

    for word in custom_blocklist:
        if word in text:
            return LABEL_REVIEW

    for label, keywords in CATEGORY_KEYWORDS.items():
        for word in keywords:
            if word in text:
                return label

    return LABEL_SAFE

# === Enklare variant: returnerar lista av matchade nyckelord ===
def match_keywords(caption, keywords):
    if not caption:
        return []
    text = caption.lower()
    return [kw for kw in keywords if kw in text]
