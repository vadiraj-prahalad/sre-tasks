import sys

from app.db.tools.evaluate_rag import evaluate
from app.db.tools.generate_chunk_embeddings import generate_chunk_embeddings
from app.db.tools.ingest_all_sources import ingest_all_sources
from app.db.tools.list_documents import main as list_documents


def print_usage() -> None:
    print("Usage: python manage.py <command>")
    print("")
    print("Available commands:")
    print("  list       Show knowledge library")
    print("  ingest     Ingest all sources from manifest")
    print("  embed      Generate embeddings for chunks")
    print("  sync       Ingest sources and generate embeddings")
    print("  evaluate   Run RAG evaluation")


def main() -> None:
    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1]

    if command == "list":
        list_documents()
    elif command == "ingest":
        ingest_all_sources()
    elif command == "embed":
        generate_chunk_embeddings()
    elif command == "sync":
        ingest_all_sources()
        generate_chunk_embeddings()
    elif command == "evaluate":
        evaluate()
    else:
        print(f"Unknown command: {command}")
        print_usage()


if __name__ == "__main__":
    main()
