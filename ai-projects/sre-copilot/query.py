import os
import chromadb


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VECTOR_PATH = os.path.join(BASE_DIR, "vectorstore")


client = chromadb.PersistentClient(
    path=VECTOR_PATH
)


collection = client.get_collection(
    name="sre_knowledge"
)


query = input("Ask SRE question: ")


results = collection.query(
    query_texts=[query],
    n_results=3
)


print("\nRelevant Knowledge:\n")


for i, doc in enumerate(results["documents"][0]):

    print("=" * 50)
    print("Result:", i + 1)
    print(doc)
