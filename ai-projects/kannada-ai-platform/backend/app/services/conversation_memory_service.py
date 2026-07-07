import json
import sqlite3
from pathlib import Path
from typing import Any


BACKEND_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BACKEND_DIR / "data" / "knowledge.db"


ENTITY_KEYWORDS = {
    "ಮಧ್ವಾಚಾರ್ಯ": "ಮಧ್ವಾಚಾರ್ಯರು",
    "madhwacharya": "ಮಧ್ವಾಚಾರ್ಯರು",
    "madhvacharya": "ಮಧ್ವಾಚಾರ್ಯರು",

    "ಕುವೆಂಪು": "ಕುವೆಂಪು",
    "kuvempu": "ಕುವೆಂಪು",

    "ಪುರಂದರ": "ಪುರಂದರ ದಾಸರು",
    "purandara": "ಪುರಂದರ ದಾಸರು",

    "ಕೃಷ್ಣ": "ಕೃಷ್ಣ",
    "krishna": "ಕೃಷ್ಣ",

    "ರಾಮ": "ರಾಮ",
    "rama": "ರಾಮ",
}


FOLLOW_UP_WORDS = [
    "ಅವರು",
    "ಅವರ",
    "ಅವರಿಗೆ",
    "ಅವನ",
    "ಅವನು",
    "ಅವನಿಗೆ",
    "ಅದರ",
    "ಅದು",
    "he",
    "him",
    "his",
    "they",
    "them",
    "their",
]


def connect_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def create_conversation_tables() -> None:
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversation_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL UNIQUE,
            last_entity TEXT,
            memory_json TEXT DEFAULT '{}',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversation_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute("PRAGMA table_info(conversation_sessions)")
    columns = [row["name"] for row in cursor.fetchall()]

    if "memory_json" not in columns:
        cursor.execute(
            """
            ALTER TABLE conversation_sessions
            ADD COLUMN memory_json TEXT DEFAULT '{}'
            """
        )

    connection.commit()
    connection.close()


def detect_entity(question: str) -> str | None:
    cleaned_question = question.strip().lower()

    for keyword, entity in ENTITY_KEYWORDS.items():
        if keyword.lower() in cleaned_question:
            return entity

    return None


def is_follow_up_question(question: str) -> bool:
    cleaned_question = question.strip().lower()
    return any(word.lower() in cleaned_question for word in FOLLOW_UP_WORDS)


def parse_memory_json(raw_memory: str | None) -> dict[str, Any]:
    if not raw_memory:
        return {}

    try:
        return json.loads(raw_memory)
    except json.JSONDecodeError:
        return {}


def get_session(conversation_id: str) -> dict[str, Any] | None:
    create_conversation_tables()

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT conversation_id, last_entity, memory_json
        FROM conversation_sessions
        WHERE conversation_id = ?
        """,
        (conversation_id,),
    )

    row = cursor.fetchone()
    connection.close()

    if not row:
        return None

    session = dict(row)
    session["memory"] = parse_memory_json(session.get("memory_json"))

    return session


def upsert_session(
    conversation_id: str,
    last_entity: str | None,
    memory: dict[str, Any] | None = None,
) -> None:
    create_conversation_tables()

    if memory is None:
        memory = {}

    if last_entity:
        memory["last_entity"] = last_entity

    memory_json = json.dumps(memory, ensure_ascii=False)

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO conversation_sessions (
            conversation_id,
            last_entity,
            memory_json
        )
        VALUES (?, ?, ?)
        ON CONFLICT(conversation_id)
        DO UPDATE SET
            last_entity = excluded.last_entity,
            memory_json = excluded.memory_json,
            updated_at = CURRENT_TIMESTAMP
        """,
        (conversation_id, last_entity, memory_json),
    )

    connection.commit()
    connection.close()


def save_message(conversation_id: str, role: str, message: str) -> None:
    create_conversation_tables()

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO conversation_messages (
            conversation_id,
            role,
            message
        )
        VALUES (?, ?, ?)
        """,
        (conversation_id, role, message),
    )

    connection.commit()
    connection.close()


def enrich_question_with_memory(
    question: str,
    conversation_id: str = "default",
) -> dict[str, Any]:
    create_conversation_tables()

    session = get_session(conversation_id)
    memory = session["memory"] if session else {}
    detected_entity = detect_entity(question)

    save_message(conversation_id, "user", question)

    if detected_entity:
        memory["last_entity"] = detected_entity
        memory["last_question"] = question

        upsert_session(
            conversation_id=conversation_id,
            last_entity=detected_entity,
            memory=memory,
        )

        return {
            "question": question,
            "memory_used": False,
            "entity": detected_entity,
            "memory": memory,
            "conversation_id": conversation_id,
        }

    last_entity = memory.get("last_entity") or (session.get("last_entity") if session else None)

    if is_follow_up_question(question) and last_entity:
        enriched_question = f"{last_entity} ಬಗ್ಗೆ: {question}"

        memory["last_question"] = question
        memory["enriched_question"] = enriched_question

        upsert_session(
            conversation_id=conversation_id,
            last_entity=last_entity,
            memory=memory,
        )

        return {
            "question": enriched_question,
            "memory_used": True,
            "entity": last_entity,
            "memory": memory,
            "conversation_id": conversation_id,
        }

    memory["last_question"] = question

    upsert_session(
        conversation_id=conversation_id,
        last_entity=last_entity,
        memory=memory,
    )

    return {
        "question": question,
        "memory_used": False,
        "entity": last_entity,
        "memory": memory,
        "conversation_id": conversation_id,
    }


def save_assistant_message(conversation_id: str, answer: str) -> None:
    save_message(conversation_id, "assistant", answer)
