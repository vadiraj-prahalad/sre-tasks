from app.llm.router import route_llm


FALLBACK_TEXT = "ಉತ್ತರವನ್ನು ಸಿದ್ಧಪಡಿಸಲು ಸ್ವಲ್ಪ ಹೆಚ್ಚು ಸಮಯ ತೆಗೆದುಕೊಳ್ಳುತ್ತಿದೆ"

GLOBAL_MUST_NOT_CONTAIN = [

    "ಭೇದವಿಲ್ಲ",
    "ಭೇದಿಲ್ಲ",
    "ಭೇದ ಇಲ್ಲ",

]


TEST_CASES = [

    # ==========================
    # Madhwacharya
    # ==========================

    {
        "question": "ವಿಷ್ಣು ಭಕ್ತಿ ಮತ್ತು ದ್ವೈತ ತತ್ವ",
        "must_contain": [
            "ನಿತ್ಯ ಭೇದವಿದೆ",
            "ವಿಷ್ಣುವನ್ನು ಪರಮ ಸತ್ಯ",
            "ಮೂಲ:"
        ],
        "must_not_contain": [],
    },

    {
        "question": "ಉಡುಪಿ ಮಠದ ಜೊತೆ ಮಧ್ವರ ಸಂಬಂಧ ಏನು",
        "must_contain": [
            "ಉಡುಪಿ",
            "ಶ್ರೀಕೃಷ್ಣ",
            "ಮೂಲ:"
        ],
        "must_not_contain": [
            "ಮೂಲ ಮಾಹಿತಿಯಲ್ಲಿ ಇದಕ್ಕೆ ಸ್ಪಷ್ಟ ಉತ್ತರ ಇಲ್ಲ"
        ],
    },

    {
        "question": "ಮಧ್ವಾಚಾರ್ಯರು ಯಾರು?",
        "must_contain": [
            "ದ್ವೈತ ವೇದಾಂತ",
            "ಮೂಲ:"
        ],
        "must_not_contain": [],
    },

    # ==========================
    # Purandara Dasa
    # ==========================

    {
        "question": "ಪುರಂದರ ದಾಸರು ಯಾರು?",
        "must_contain": [
            "ಕರ್ನಾಟಕ ಸಂಗೀತದ ಪಿತಾಮಹ",
            "ಮೂಲ:"
        ],
        "must_not_contain": [],
    },

    {
        "question": "ಪುರಂದರ ದಾಸರ ಕೊಡುಗೆ",
        "must_contain": [
            "ಸರಳಿ",
            "ಜಂಟಿ",
            "ಮೂಲ:"
        ],
        "must_not_contain": [],
    },

    # ==========================
    # Kuvempu
    # ==========================

    {
        "question": "ಕುವೆಂಪು ಯಾರು?",
        "must_contain": [
            "ಜ್ಞಾನಪೀಠ",
            "ಮೂಲ:"
        ],
        "must_not_contain": [],
    },

    {
        "question": "ಕುವೆಂಪು ಕನ್ನಡ ಸಾಹಿತ್ಯಕ್ಕೆ ನೀಡಿದ ಕೊಡುಗೆ",
        "must_contain": [
            "ಕನ್ನಡ",
            "ಸಾಹಿತ್ಯ",
            "ಮೂಲ:"
        ],
        "must_not_contain": [],
    },

    # ==========================
    # Rajkumar
    # ==========================

    {
        "question": "ಡಾ ರಾಜಕುಮಾರ್ ಯಾರು?",
        "must_contain": [
            "ಕನ್ನಡ",
            "ಚಿತ್ರರಂಗ",
            "ಮೂಲ:"
        ],
        "must_not_contain": [],
    },

    # ==========================
    # Vishnuvardhan
    # ==========================

    {
        "question": "ವಿಷ್ಣುವರ್ಧನ್ ಯಾರು?",
        "must_contain": [
            "ಸಾಹಸ ಸಿಂಹ",
            "ಮೂಲ:"
        ],
        "must_not_contain": [],
    },

    {
        "question": "ಡಾ ವಿಷ್ಣುವರ್ಧನ್ ಬಗ್ಗೆ ಹೇಳಿ",
        "must_contain": [
            "ಕನ್ನಡ",
            "ಚಿತ್ರರಂಗ",
            "ಮೂಲ:"
        ],
        "must_not_contain": [],
    },

]

def evaluate() -> None:
    passed = 0
    failed = 0

    for test in TEST_CASES:
        question = test["question"]
        answer = route_llm(question)
        print("\nQuestion:", question)
        print("Answer:", answer)
        print("-" * 80)

        if not answer:
            print("FAILED: Retrieval failed or no RAG answer returned")
            failed += 1
            continue

        if FALLBACK_TEXT in answer:
            print("FAILED: LLM timeout/fallback response")
            failed += 1
            continue

        errors = []

        for text in test["must_contain"]:
            if text not in answer:
                errors.append(f"Missing expected text: {text}")

        forbidden_texts = test["must_not_contain"] + GLOBAL_MUST_NOT_CONTAIN

        for text in forbidden_texts:
            if text in answer:
                errors.append(f"Contains forbidden text: {text}")

        if errors:
            print("FAILED: Answer quality issue")
            for error in errors:
                print("-", error)
            failed += 1
        else:
            print("PASSED")
            passed += 1

    print("\nEvaluation Summary")
    print("=" * 80)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")


if __name__ == "__main__":
    evaluate()