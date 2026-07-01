import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "knowledge.db"

SEED_ITEMS = [
    {
        "canonical_question": "ನಮಸ್ಕಾರ ಎಂದರೇನು?",
        "answer": "ನಮಸ್ಕಾರ ಎಂದರೆ ಒಬ್ಬರನ್ನು ಗೌರವದಿಂದ ಸ್ವಾಗತಿಸುವ ಪದ. ಇದನ್ನು ಸಾಮಾನ್ಯವಾಗಿ ಯಾರನ್ನಾದರೂ ಭೇಟಿಯಾದಾಗ ಅಥವಾ ಮಾತು ಆರಂಭಿಸುವಾಗ ಬಳಸುತ್ತಾರೆ.",
        "category": "language",
        "language": "kn",
        "source": "curated",
        "confidence": "verified",
    },
    {
        "canonical_question": "ಕುವೆಂಪು ಯಾರು?",
        "answer": "ಕುವೆಂಪು ಕನ್ನಡದ ಪ್ರಸಿದ್ಧ ಕವಿ, ಲೇಖಕ ಮತ್ತು ಚಿಂತಕರು. ಅವರ ಪೂರ್ಣ ಹೆಸರು ಕುಪ್ಪಳ್ಳಿ ವೆಂಕಟಪ್ಪ ಪುಟ್ಟಪ್ಪ. ಅವರು ಕನ್ನಡ ಸಾಹಿತ್ಯಕ್ಕೆ ದೊಡ್ಡ ಕೊಡುಗೆ ನೀಡಿದ್ದಾರೆ.",
        "category": "people",
        "language": "kn",
        "source": "curated",
        "confidence": "verified",
    },
    {
        "canonical_question": "ಬೆಂಗಳೂರು ಬಗ್ಗೆ ಹೇಳಿ",
        "answer": "ಬೆಂಗಳೂರು ಕರ್ನಾಟಕ ರಾಜ್ಯದ ರಾಜಧಾನಿ ಮತ್ತು ಭಾರತದ ಪ್ರಮುಖ ನಗರಗಳಲ್ಲಿ ಒಂದಾಗಿದೆ. ಇದು ತಂತ್ರಜ್ಞಾನ, ಶಿಕ್ಷಣ, ಉದ್ಯಮ, ಸಂಸ್ಕೃತಿ ಮತ್ತು ಉದ್ಯಾನಗಳಿಗಾಗಿ ಪ್ರಸಿದ್ಧವಾಗಿದೆ. ಬೆಂಗಳೂರನ್ನು ಭಾರತದ ಸಿಲಿಕಾನ್ ವ್ಯಾಲಿ ಎಂದೂ ಕರೆಯುತ್ತಾರೆ.",
        "category": "city",
        "language": "kn",
        "source": "curated",
        "confidence": "verified",
    },
    {
        "canonical_question": "ಡಾ. ರಾಜ್‌ಕುಮಾರ್ ಯಾರು?",
        "answer": "ಡಾ. ರಾಜ್‌ಕುಮಾರ್ ಕನ್ನಡ ಚಿತ್ರರಂಗದ ದಿಗ್ಗಜ ನಟ, ಗಾಯಕ ಮತ್ತು ಕರ್ನಾಟಕದ ಸಾಂಸ್ಕೃತಿಕ ಪ್ರತೀಕಗಳಲ್ಲಿ ಒಬ್ಬರು. ಅವರ ಮೂಲ ಹೆಸರು ಸಿಂಗಾನಲ್ಲೂರು ಪುಟ್ಟಸ್ವಾಮಯ್ಯ ಮುತ್ತುರಾಜು. ಅವರು ಸುಮಾರು 200ಕ್ಕೂ ಹೆಚ್ಚು ಕನ್ನಡ ಚಿತ್ರಗಳಲ್ಲಿ ನಟಿಸಿದ್ದಾರೆ ಮತ್ತು ಕನ್ನಡ ಭಾಷೆ ಹಾಗೂ ಸಂಸ್ಕೃತಿಯ ಪ್ರಸಾರಕ್ಕೆ ಮಹತ್ವದ ಕೊಡುಗೆ ನೀಡಿದ್ದಾರೆ. ಅವರಿಗೆ ಭಾರತದ ಅತ್ಯುನ್ನತ ಚಲನಚಿತ್ರ ಗೌರವವಾದ ದಾದಾಸಾಹೇಬ್ ಫಾಲ್ಕೆ ಪ್ರಶಸ್ತಿ ಲಭಿಸಿದೆ.",
        "category": "people",
        "language": "kn",
        "source": "curated",
        "confidence": "verified",
    },
]


def seed_data() -> None:
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    for item in SEED_ITEMS:
        cursor.execute(
            """
            INSERT OR IGNORE INTO knowledge_items (
                canonical_question,
                answer,
                category,
                language,
                source,
                confidence
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                item["canonical_question"],
                item["answer"],
                item["category"],
                item["language"],
                item["source"],
                item["confidence"],
            ),
        )

    connection.commit()
    connection.close()

    print("Seed data inserted successfully.")


if __name__ == "__main__":
    seed_data()
