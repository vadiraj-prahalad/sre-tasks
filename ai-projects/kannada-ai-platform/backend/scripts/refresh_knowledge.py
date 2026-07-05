import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone


BACKEND_DIR = Path(__file__).resolve().parents[1]

RAW_DIR = BACKEND_DIR / "knowledge" / "raw"
OUTPUT_FILE = BACKEND_DIR / "knowledge" / "processed" / "knowledge_base.jsonl"

REQUIRED_FIELDS = ["question", "answer", "category", "source"]


def normalize_text(text: str) -> str:
    return " ".join(str(text).strip().split())


def generate_id(question: str, answer: str) -> str:
    raw = f"{question}|{answer}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def validate_record(record: dict, filename: str, index: int) -> dict:
    errors = []

    for field in REQUIRED_FIELDS:
        if field not in record or not str(record[field]).strip():
            errors.append(f"Missing or empty field: {field}")

    if errors:
        raise ValueError(
            f"Invalid record in {filename} at index {index}: {', '.join(errors)}"
        )

    question = normalize_text(record["question"])
    answer = normalize_text(record["answer"])

    return {
        "id": generate_id(question, answer),
        "question": question,
        "answer": answer,
        "category": normalize_text(record["category"]),
        "source": normalize_text(record["source"]),
        "language": normalize_text(record.get("language", "kn")),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def load_raw_files() -> list[dict]:
    records = []

    if not RAW_DIR.exists():
        raise FileNotFoundError(f"Raw knowledge directory not found: {RAW_DIR}")

    for file_path in sorted(RAW_DIR.glob("*.json")):
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError(f"{file_path} must contain a JSON list")

        for index, record in enumerate(data):
            records.append(validate_record(record, file_path.name, index))

    return records


def deduplicate(records: list[dict]) -> list[dict]:
    seen_ids = set()
    unique_records = []

    for record in records:
        if record["id"] not in seen_ids:
            seen_ids.add(record["id"])
            unique_records.append(record)

    return unique_records


def write_jsonl(records: list[dict]) -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    records = load_raw_files()
    unique_records = deduplicate(records)
    write_jsonl(unique_records)

    print("Knowledge refresh completed")
    print(f"Raw records: {len(records)}")
    print(f"Unique records: {len(unique_records)}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()