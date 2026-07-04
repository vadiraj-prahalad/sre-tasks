from pathlib import Path


def clean_markdown(content: str) -> str:
    lines = []

    for line in content.splitlines():
        cleaned = line.strip()

        if cleaned.startswith("#"):
            cleaned = cleaned.lstrip("#").strip()

        if cleaned:
            lines.append(cleaned)

    return "\n".join(lines)


def load_text_file(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Source file not found: {file_path}")

    content = path.read_text(encoding="utf-8").strip()

    if not content:
        raise ValueError(f"Source file is empty: {file_path}")

    return content


def load_markdown_file(file_path: str) -> str:
    content = load_text_file(file_path)
    return clean_markdown(content)


def load_document(file_path: str) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".txt":
        return load_text_file(file_path)

    if suffix == ".md":
        return load_markdown_file(file_path)

    raise ValueError(f"Unsupported document type: {suffix}")