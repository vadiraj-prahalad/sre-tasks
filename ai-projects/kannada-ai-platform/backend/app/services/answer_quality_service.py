def clean_final_answer(answer: str) -> str:
    cleaned = " ".join(answer.split())

    cleaned = remove_repeated_start(cleaned)
    cleaned = fix_common_repetitions(cleaned)

    return cleaned.strip()


def remove_repeated_start(text: str) -> str:
    words = text.split()

    if len(words) < 4:
        return text

    first_two = words[:2]
    second_two = words[2:4]

    if first_two == second_two:
        return " ".join(words[2:])

    first_three = words[:3]
    second_three = words[3:6]

    if first_three == second_three:
        return " ".join(words[3:])

    return text


def fix_common_repetitions(text: str) -> str:
    replacements = {
        "ಡಾ. ವಿಷ್ಣುವರ್ಧನ್ ಡಾ. ವಿಷ್ಣುವರ್ಧನ್": "ಡಾ. ವಿಷ್ಣುವರ್ಧನ್",
        "ಪುರಂದರ ದಾಸರು ಪುರಂದರ ದಾಸರು": "ಪುರಂದರ ದಾಸರು",
        "ಕುವೆಂಪು ಮತ್ತು ಕನ್ನಡ ಸಾಹಿತ್ಯ ಕುವೆಂಪು": "ಕುವೆಂಪು",
    }

    for repeated, fixed in replacements.items():
        text = text.replace(repeated, fixed)

    return text
