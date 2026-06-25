import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DOCS_PATH = os.path.join(BASE_DIR, "docs")

def load_documents():
    documents = []

    for filename in os.listdir(DOCS_PATH):
        if filename.endswith(".md"):
            filepath = os.path.join(DOCS_PATH, filename)

            with open(filepath, "r") as file:
                content = file.read()

            documents.append(
                {
                    "filename": filename,
                    "content": content
                }
            )

    return documents

def split_into_chunks(text, chunk_size=200, overlap=50):
    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk)

        start = end - overlap

    return chunks

docs = load_documents()

all_chunks = []

for doc in docs:

    chunks = split_into_chunks(doc["content"])

    for index, chunk in enumerate(chunks):

        chunk_data = {
            "text": chunk,
            "source": doc["filename"],
            "chunk_id": index + 1
        }

        all_chunks.append(chunk_data)


for chunk in all_chunks:

    print("=" * 50)
    print("SOURCE:", chunk["source"])
    print("CHUNK ID:", chunk["chunk_id"])
    print(chunk["text"])
