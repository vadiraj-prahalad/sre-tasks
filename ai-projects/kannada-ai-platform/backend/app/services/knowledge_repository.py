import json
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "kannada_facts.json"


def load_all_facts() -> dict:
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)
