import os
import chromadb


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DOCS_PATH = os.path.join(BASE_DIR, "docs")
VECTOR_PATH = os.path.join(BASE_DIR, "vectorstore")

client = chromadb.PersistentClient(
    path=VECTOR_PATH
)

collection = client.get_or_create_collection(
    name="sre_knowledge"
)

try:
    collection.delete(
        ids=collection.get()["ids"]
    )
except:
    pass

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

def split_into_chunks(text, max_length=500):

    paragraphs = text.split("\n\n")

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:
            continue

        if len(current_chunk) + len(paragraph) < max_length:

            current_chunk += paragraph + "\n\n"

        else:

            chunks.append(current_chunk.strip())
            current_chunk = paragraph + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

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

    collection.add(
        documents=[
            chunk["text"]
        ],
        metadatas=[
            {
                "source": chunk["source"],
                "chunk_id": chunk["chunk_id"]
            }
        ],
        ids=[
            f'{chunk["source"]}_{chunk["chunk_id"]}'
        ]
    )

    print(
        "Stored:",
        chunk["source"],
        chunk["chunk_id"]
    )
