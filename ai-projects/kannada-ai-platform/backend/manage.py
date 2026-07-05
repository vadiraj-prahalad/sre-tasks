import sys

from app.db.tools.evaluate_rag import evaluate
from app.db.tools.generate_chunk_embeddings import generate_chunk_embeddings
from app.db.tools.ingest_all_sources import ingest_all_sources
from app.db.tools.list_documents import main as list_documents
from app.services.knowledge_loader import load_knowledge_to_db
from scripts.refresh_knowledge import main as refresh_jsonl


def print_usage() -> None:
    print("Usage: python manage.py <command>")
    print("")
    print("Available commands:")
    print("  list       Show knowledge library")
    print("  ingest     Ingest all sources from manifest")
    print("  embed      Generate embeddings for chunks")
    print("  sync       Ingest sources and generate embeddings")
    print("  evaluate   Run RAG evaluation")
    print("  refresh    Refresh standardized knowledge and load SQLite")


def refresh_knowledge() -> None:
    print("Starting standardized knowledge refresh...")

    refresh_jsonl()

    result = load_knowledge_to_db()

    print("SQLite load completed")
    print(f"Records loaded: {result['records_loaded']}")
    print(f"Database: {result['db_path']}")
    print("Knowledge refresh completed successfully")


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
    elif command == "refresh":
        refresh_knowledge()
    else:
        print(f"Unknown command: {command}")
        print_usage()


if __name__ == "__main__":
    main()