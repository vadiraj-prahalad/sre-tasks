from app.services.rag_service import answer_from_rag


FALLBACK_TEXT = "ಉತ್ತರವನ್ನು ಸಿದ್ಧಪಡಿಸಲು ಸ್ವಲ್ಪ ಹೆಚ್ಚು ಸಮಯ ತೆಗೆದುಕೊಳ್ಳುತ್ತಿದೆ"

GLOBAL_MUST_NOT_CONTAIN = [

    "ಭೇದವಿಲ್ಲ",
    "ಭೇದಿಲ್ಲ",
    "ಭೇದ ಇಲ್ಲ",

]


TEST_CASES = [
    {
        "question": "ವಿಷ್ಣು ಭಕ್ತಿ ಮತ್ತು ದ್ವೈತ ತತ್ವ",
        "must_contain": ["ನಿತ್ಯ ಭೇದವಿದೆ", "ಮೂಲ:"],
        "must_not_contain": [],
    },
    {
        "question": "ಉಡುಪಿ ಮಠದ ಜೊತೆ ಮಧ್ವರ ಸಂಬಂಧ ಏನು",
        "must_contain": ["ಉಡುಪಿ", "ಮೂಲ:"],
        "must_not_contain": ["ಮೂಲ ಮಾಹಿತಿಯಲ್ಲಿ ಇದಕ್ಕೆ ಸ್ಪಷ್ಟ ಉತ್ತರ ಇಲ್ಲ"],
    },
]


def evaluate() -> None:
    passed = 0
    failed = 0

    for test in TEST_CASES:
        question = test["question"]
        answer = answer_from_rag(question)

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