CATEGORY_TO_ARCHETYPE = {

    # ------------------------------------------------------------
    # People
    # ------------------------------------------------------------
    "person": "PERSON",
    "biography": "PERSON",
    "poet": "PERSON",
    "writer": "PERSON",
    "author": "PERSON",
    "saint": "PERSON",
    "philosopher": "PERSON",
    "reformer": "PERSON",
    "freedom_fighter": "PERSON",
    "king": "PERSON",
    "queen": "PERSON",
    "artist": "PERSON",
    "musician": "PERSON",
    "scholar": "PERSON",
    "scientist": "PERSON",
    "leader": "PERSON",

    # ------------------------------------------------------------
    # Places
    # ------------------------------------------------------------
    "location": "PLACE",
    "city": "PLACE",
    "district": "PLACE",
    "village": "PLACE",
    "state": "PLACE",
    "country": "PLACE",
    "fort": "PLACE",
    "palace": "PLACE",
    "temple": "PLACE",
    "museum": "PLACE",
    "monument": "PLACE",
    "tourist_place": "PLACE",
    "heritage_site": "PLACE",

    # ------------------------------------------------------------
    # Nature
    # ------------------------------------------------------------
    "river": "NATURE",
    "hill": "NATURE",
    "mountain": "NATURE",
    "forest": "NATURE",
    "lake": "NATURE",
    "waterfall": "NATURE",
    "wildlife": "NATURE",
    "national_park": "NATURE",

    # ------------------------------------------------------------
    # Religion & Philosophy
    # ------------------------------------------------------------
    "religion": "RELIGION_OR_PHILOSOPHY",
    "philosophy": "RELIGION_OR_PHILOSOPHY",
    "tradition": "RELIGION_OR_PHILOSOPHY",
    "spirituality": "RELIGION_OR_PHILOSOPHY",

    # ------------------------------------------------------------
    # Culture
    # ------------------------------------------------------------
    "festival": "CULTURE",
    "dance": "CULTURE",
    "music": "CULTURE",
    "art": "CULTURE",
    "food": "CULTURE",
    "custom": "CULTURE",

    # ------------------------------------------------------------
    # Education / Language
    # ------------------------------------------------------------
    "language": "LANGUAGE_OR_KNOWLEDGE",
    "grammar": "LANGUAGE_OR_KNOWLEDGE",
    "literature": "LANGUAGE_OR_KNOWLEDGE",
    "vocabulary": "LANGUAGE_OR_KNOWLEDGE",
    "education": "LANGUAGE_OR_KNOWLEDGE",
}


def get_archetype(category: str) -> str:
    """
    Maps a category to an editorial archetype.

    Unknown categories safely fall back to GENERAL.
    """

    if not category:
        return "GENERAL"

    return CATEGORY_TO_ARCHETYPE.get(
        category.strip().lower(),
        "GENERAL",
    )
