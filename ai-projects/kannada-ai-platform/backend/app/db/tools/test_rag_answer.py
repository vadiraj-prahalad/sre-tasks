import sys

from app.services.rag_service import answer_from_rag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m app.db.tools.test_rag_answer <question>")
        return

    question = " ".join(sys.argv[1:])

    answer = answer_from_rag(question)

    if not answer:
        print("No relevant RAG context found.")
        return

    print("\nRAG Answer\n")
    print("-" * 80)
    print(answer)
    print("-" * 80)


if __name__ == "__main__":
    main()
