import json
import sqlite3
from pathlib import Path
from typing import Any

BACKEND_DIR = Path(__file__).resolve().parents[2]

DEFAULT_DB_PATH = BACKEND_DIR / "data" / "knowledge.db"
DEFAULT_JSONL_PATH = BACKEND_DIR / "knowledge" / "processed" / "knowledge_base.jsonl"



def connect_db(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)


def create_knowledge_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS knowledge_articles (
            id TEXT PRIMARY KEY,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            category TEXT NOT NULL,
            source TEXT NOT NULL,
            language TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()


def read_jsonl(jsonl_path: Path = DEFAULT_JSONL_PATH) -> list[dict[str, Any]]:
    if not jsonl_path.exists():
        raise FileNotFoundError(f"Knowledge file not found: {jsonl_path}")

    records = []

    with jsonl_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON at line {line_number} in {jsonl_path}"
                ) from exc

    return records


def validate_record(record: dict[str, Any]) -> None:
    required_fields = [
        "id",
        "question",
        "answer",
        "category",
        "source",
        "language",
        "created_at",
    ]

    missing_fields = [
        field for field in required_fields if field not in record or not record[field]
    ]

    if missing_fields:
        raise ValueError(f"Invalid knowledge record. Missing: {missing_fields}")


def replace_knowledge_records(
    conn: sqlite3.Connection,
    records: list[dict[str, Any]],
) -> None:
    with conn:
        conn.execute("DELETE FROM knowledge_articles")

        for record in records:
            validate_record(record)

            conn.execute(
                """
                INSERT INTO knowledge_articles (
                    id,
                    question,
                    answer,
                    category,
                    source,
                    language,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record["id"],
                    record["question"],
                    record["answer"],
                    record["category"],
                    record["source"],
                    record["language"],
                    record["created_at"],
                ),
            )


def load_knowledge_to_db(
    jsonl_path: Path = DEFAULT_JSONL_PATH,
    db_path: Path = DEFAULT_DB_PATH,
) -> dict[str, Any]:
    records = read_jsonl(jsonl_path)

    conn = connect_db(db_path)

    try:
        create_knowledge_table(conn)
        replace_knowledge_records(conn, records)

        return {
            "status": "success",
            "records_loaded": len(records),
            "db_path": str(db_path),
            "jsonl_path": str(jsonl_path),
        }
    finally:
        conn.close()


if __name__ == "__main__":
    result = load_knowledge_to_db()

    print("Knowledge load completed")
    print(f"Records loaded: {result['records_loaded']}")
    print(f"Database: {result['db_path']}")
    print(f"Source: {result['jsonl_path']}")
