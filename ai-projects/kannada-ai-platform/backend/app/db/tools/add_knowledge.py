from app.services.knowledge_admin_service import create_knowledge_item


def main() -> None:
    item = {
        "canonical_question": "ಮಧ್ವಾಚಾರ್ಯರು ಯಾರು?",
        "answer": (
            "ಮಧ್ವಾಚಾರ್ಯರು ದ್ವೈತ ವೇದಾಂತದ ಪ್ರಮುಖ ಆಚಾರ್ಯರು. "
            "ಅವರು ವಿಷ್ಣುಭಕ್ತಿಯನ್ನು ಮತ್ತು ಜೀವಾತ್ಮ ಹಾಗೂ ಪರಮಾತ್ಮರ ನಡುವಿನ ಭೇದವನ್ನು ಸ್ಪಷ್ಟವಾಗಿ ವಿವರಿಸಿದವರು. "
            "ಮಧ್ವಾಚಾರ್ಯರು ಉಡುಪಿಯ ಶ್ರೀಕೃಷ್ಣ ಮಠದ ಪರಂಪರೆಯೊಂದಿಗೆ ಆಳವಾಗಿ ಸಂಬಂಧ ಹೊಂದಿದ್ದಾರೆ."
        ),
        "category": "people",
        "canonical_key": "madhwacharya",
        "title": "ಶ್ರೀ ಮಧ್ವಾಚಾರ್ಯರು",
        "domain": "philosophy",
        "subdomain": "dvaita_vedanta",
        "keywords": "madhwacharya,madhwa,dvaita,udupi,vedanta,ಮಧ್ವಾಚಾರ್ಯ",
        "related_topics": "udupi krishna,dvaita vedanta,jayatirtha,vyasatirtha",
        "item_type": "entity",
        "status": "published",
    }

    create_knowledge_item(item)

    print("Knowledge item added successfully.")


if __name__ == "__main__":
    main()
