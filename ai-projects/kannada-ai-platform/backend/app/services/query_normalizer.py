import re


NORMALIZATION_MAP = {

    # Rajkumar
    "ಡಾ ರಾಜಕುಮಾರ್": "ಡಾ. ರಾಜ್‌ಕುಮಾರ್",
    "ಡಾ. ರಾಜಕುಮಾರ್": "ಡಾ. ರಾಜ್‌ಕುಮಾರ್",
    "ರಾಜಕುಮಾರ್": "ಡಾ. ರಾಜ್‌ಕುಮಾರ್",
    "ರಾಜ್ ಕುಮಾರ್": "ಡಾ. ರಾಜ್‌ಕುಮಾರ್",
    "ಅಣ್ಣಾವ್ರು": "ಡಾ. ರಾಜ್‌ಕುಮಾರ್",
    "ನಟಸಾರ್ವಭೌಮ": "ಡಾ. ರಾಜ್‌ಕುಮಾರ್",

    # Vishnuvardhan
    "ವಿಷ್ಣುವರ್ಧನ": "ವಿಷ್ಣುವರ್ಧನ್",
    "ಡಾ ವಿಷ್ಣುವರ್ಧನ್": "ಡಾ. ವಿಷ್ಣುವರ್ಧನ್",

    # Madhwacharya
    "ಮದ್ವಾಚಾರ್ಯ": "ಮಧ್ವಾಚಾರ್ಯ",
    "ಮಧ್ವ": "ಮಧ್ವಾಚಾರ್ಯ",

    # Kuvempu
    "kuvempu": "ಕುವೆಂಪು",
    "ಕುವೆಂಪೂ": "ಕುವೆಂಪು",

    # Purandara
    "ಪುರಂದರದಾಸ": "ಪುರಂದರ ದಾಸರು",

}


def normalize_question(question: str) -> str:
    question = question.strip()

    question = re.sub(r"\s+", " ", question)

    for original, replacement in NORMALIZATION_MAP.items():
        question = question.replace(original, replacement)

    return question