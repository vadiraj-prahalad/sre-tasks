import json
from pathlib import Path

from app.db.tools.ingest_text_document import ingest_text_document


SOURCES_DIR = Path(__file__).resolve().parents[2] / "data" / "sources"
MANIFEST_PATH = SOURCES_DIR / "manifest.json"


def load_manifest() -> list[dict]:
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Manifest not found: {MANIFEST_PATH}")

    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def ingest_all_sources() -> None:
    sources = load_manifest()

    if not sources:
        print("No sources found in manifest.")
        return

    for source in sources:
        file_path = SOURCES_DIR / source["file"]

        print(f"Ingesting: {source['title']}")

        ingest_text_document(
            file_path=str(file_path),
            title=source["title"],
            source_name=source["source_name"],
            category=source["category"],
            language=source.get("language", "kn"),
        )

    print("All sources ingested successfully.")


if __name__ == "__main__":
    ingest_all_sources()
