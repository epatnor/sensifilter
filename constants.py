# constants.py

# Klassificeringsetiketter
LABEL_SAFE = "safe"
LABEL_REVIEW = "review"
LABEL_NUDITY = "nudity"
LABEL_VIOLENCE = "violence"
LABEL_OTHER_SENSITIVE = "other_sensitive"

# Tröskelvärden
DEFAULT_CONFIDENCE_THRESHOLD = 0.85
DEFAULT_SKIN_PERCENT_THRESHOLD = 5.0

# Nyckelord (kan laddas från config senare)
KEYWORDS_NUDITY = [
    "nude", "naked", "bare", "topless", "genitals", "breasts",
    "sex", "erotic", "lingerie", "underwear", "intimate"
]

KEYWORDS_VIOLENCE = [
    "blood", "gore", "gun", "weapon", "knife", "wound", "murder",
    "corpse", "war", "explosion", "dead body", "assault"
]

KEYWORDS_OTHER = [
    "drug", "cocaine", "syringe", "cigarette", "vape", "alcohol",
    "joint", "marijuana", "pill", "bong"
]

# Trygga ord (för att undvika falska positiva)
KEYWORDS_WHITELIST = [
    "bikini", "swimsuit", "beach", "swimming pool"
]

# Etikettbas per kategori
CATEGORY_KEYWORDS = {
    LABEL_NUDITY: KEYWORDS_NUDITY,
    LABEL_VIOLENCE: KEYWORDS_VIOLENCE,
    LABEL_OTHER_SENSITIVE: KEYWORDS_OTHER
}
