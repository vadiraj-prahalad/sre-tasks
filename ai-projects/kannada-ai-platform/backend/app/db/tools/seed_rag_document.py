import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "knowledge.db"


DOCUMENT = {
    "title": "Madhwacharya and Dvaita Vedanta - Curated Note",
    "source_name": "Curated Internal Knowledge",
    "source_url": None,
    "category": "philosophy",
    "language": "kn",
    "content": """
ಮಧ್ವಾಚಾರ್ಯರು ದ್ವೈತ ವೇದಾಂತದ ಪ್ರಮುಖ ಆಚಾರ್ಯರು. ಅವರು ಜೀವಾತ್ಮ ಮತ್ತು ಪರಮಾತ್ಮರ ನಡುವೆ ನಿತ್ಯ ಭೇದವಿದೆ ಎಂದು ವಿವರಿಸಿದರು.
ದ್ವೈತ ವೇದಾಂತದಲ್ಲಿ ಭಗವಾನ್ ವಿಷ್ಣುವನ್ನು ಪರಮ ಸತ್ಯವೆಂದು ಪರಿಗಣಿಸಲಾಗುತ್ತದೆ. ಮಧ್ವಾಚಾರ್ಯರ ಉಪದೇಶಗಳು ಭಕ್ತಿ, ತತ್ತ್ವಜ್ಞಾನ ಮತ್ತು ಶಾಸ್ತ್ರಾಧ್ಯಯನಕ್ಕೆ ಮಹತ್ವ ನೀಡುತ್ತವೆ.
ಮಧ್ವಾಚಾರ್ಯರು ಉಡುಪಿಯ ಶ್ರೀಕೃಷ್ಣ ಮಠದ ಪರಂಪರೆಯೊಂದಿಗೆ ಆಳವಾಗಿ ಸಂಬಂಧ ಹೊಂದಿದ್ದಾರೆ. ಅವರ ತತ್ತ್ವವು ನಂತರದ ಮಾಧ್ವ ಪರಂಪರೆ, ಹರಿದಾಸ ಸಾಹಿತ್ಯ ಮತ್ತು ಕರ್ನಾಟಕದ ಭಕ್ತಿ ಸಂಸ್ಕೃತಿಯ ಮೇಲೆ ಪ್ರಭಾವ ಬೀರಿತು.
""".strip(),
}


def split_into_chunks(text: str, chunk_size: int = 300) -> list[str]:
    words = text.split()
    chunks = []

    for start in range(0, len(words), chunk_size):
        chunk = " ".join(words[start : start + chunk_size])
        chunks.append(chunk)

    return chunks


def seed_rag_document() -> None:
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO documents (
            title,
            source_name,
            source_url,
            category,
            language
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            DOCUMENT["title"],
            DOCUMENT["source_name"],
            DOCUMENT["source_url"],
            DOCUMENT["category"],
            DOCUMENT["language"],
        ),
    )

    document_id = cursor.lastrowid

    chunks = split_into_chunks(DOCUMENT["content"])

    for index, chunk_text in enumerate(chunks):
        cursor.execute(
            """
            INSERT INTO chunks (
                document_id,
                chunk_text,
                chunk_index
            )
            VALUES (?, ?, ?)
            """,
            (document_id, chunk_text, index),
        )

    connection.commit()
    connection.close()

    print(f"Inserted document ID: {document_id}")
    print(f"Inserted chunks: {len(chunks)}")


if __name__ == "__main__":
    seed_rag_document()
