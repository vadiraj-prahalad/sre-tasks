import sqlite3
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BACKEND_DIR / "data" / "knowledge.db"


def get_feedback_dashboard() -> dict:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT rating, COUNT(*) count
        FROM feedback
        GROUP BY rating
        """
    )

    stats = {
        "positive": 0,
        "negative": 0,
    }

    for row in cursor.fetchall():
        stats[row["rating"]] = row["count"]

    cursor.execute(
        """
        SELECT
            id,
            question,
            rating,
            confidence_score,
            source,
            created_at
        FROM feedback
        ORDER BY id DESC
        LIMIT 20
        """
    )

    feedback = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return {
        "stats": stats,
        "feedback": feedback,
    }
