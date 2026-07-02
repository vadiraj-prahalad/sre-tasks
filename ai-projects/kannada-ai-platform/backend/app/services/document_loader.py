from pathlib import Path
from app.services.document_loader import load_document  

def load_text_file(file_path: str) -> str:
    content = load_document(file_path)


def load_document(file_path: str) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".txt":
        return load_text_file(file_path)

    raise ValueError(f"Unsupported document type: {suffix}")
