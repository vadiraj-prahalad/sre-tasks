import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "knowledge.db"


METADATA_UPDATES = [
    {
        "canonical_question": "ನಮಸ್ಕಾರ ಎಂದರೇನು?",
        "item_type": "qa",
        "canonical_key": "namaskara",
        "title": "ನಮಸ್ಕಾರ",
        "domain": "language",
        "subdomain": "greeting",
        "keywords": "namaskara,greeting,kannada greeting,ನಮಸ್ಕಾರ,ಸ್ವಾಗತ",
        "related_topics": "greetings,kannada language",
        "status": "published",
    },
    {
        "canonical_question": "ಕುವೆಂಪು ಯಾರು?",
        "item_type": "entity",
        "canonical_key": "kuvempu",
        "title": "ಕುವೆಂಪು",
        "domain": "literature",
        "subdomain": "kannada_literature",
        "keywords": "kuvempu,kannada poet,kannada literature,ಕುವೆಂಪು",
        "related_topics": "kannada literature,jnanpith,rashtrakavi",
        "status": "published",
    },
    {
        "canonical_question": "ಬೆಂಗಳೂರು ಬಗ್ಗೆ ಹೇಳಿ",
        "item_type": "entity",
        "canonical_key": "bengaluru",
        "title": "ಬೆಂಗಳೂರು",
        "domain": "geography",
        "subdomain": "karnataka_city",
        "keywords": "bengaluru,bangalore,karnataka capital,ಬೆಂಗಳೂರು",
        "related_topics": "karnataka,technology,city",
        "status": "published",
    },
    {
        "canonical_question": "ಡಾ. ರಾಜ್‌ಕುಮಾರ್ ಯಾರು?",
        "item_type": "entity",
        "canonical_key": "dr_rajkumar",
        "title": "ಡಾ. ರಾಜ್‌ಕುಮಾರ್",
        "domain": "culture",
        "subdomain": "kannada_cinema",
        "keywords": "dr rajkumar,kannada actor,kannada cinema,annavru,ಡಾ ರಾಜ್‌ಕುಮಾರ್",
        "related_topics": "kannada cinema,culture,music",
        "status": "published",
    },
]


def backfill_metadata() -> None:
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    for item in METADATA_UPDATES:
        cursor.execute(
            """
            UPDATE knowledge_items
            SET
                item_type = ?,
                canonical_key = ?,
                title = ?,
                domain = ?,
                subdomain = ?,
                keywords = ?,
                related_topics = ?,
                status = ?
            WHERE canonical_question = ?
            """,
            (
                item["item_type"],
                item["canonical_key"],
                item["title"],
                item["domain"],
                item["subdomain"],
                item["keywords"],
                item["related_topics"],
                item["status"],
                item["canonical_question"],
            ),
        )

    connection.commit()
    connection.close()

    print("Metadata backfill completed successfully.")


if __name__ == "__main__":
    backfill_metadata()
