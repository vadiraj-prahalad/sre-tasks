import sys
import time

from app.db.tools.evaluate_rag import evaluate
from app.db.tools.generate_chunk_embeddings import generate_chunk_embeddings
from app.db.tools.ingest_all_sources import ingest_all_sources
from app.db.tools.list_documents import main as list_documents
from app.db.tools.sync_standardized_articles import sync_standardized_articles
from app.services.draft_knowledge_service import (
    approve_draft_answer,
    delete_draft_answer,
    list_draft_answers,
)
from app.services.knowledge_loader import load_knowledge_to_db
from scripts.refresh_knowledge import main as refresh_jsonl


def print_usage() -> None:
    print("Usage: python manage.py <command>")
    print("")
    print("Available commands:")
    print("  list                                  Show knowledge library")
    print("  ingest                                Ingest all sources from manifest")
    print("  embed                                 Generate embeddings for chunks")
    print("  sync                                  Ingest sources and generate embeddings")
    print("  evaluate                              Run RAG evaluation")
    print("  refresh                               Refresh knowledge, reload SQLite, embed, and evaluate")
    print("  drafts                                Show draft knowledge captured from Ollama fallback")
    print("  delete-draft <id>                     Delete a bad draft answer")
    print('  approve-draft <id> "<answer>" "<category>"   Approve draft into knowledge')


def show_drafts() -> None:
    drafts = list_draft_answers()

    if not drafts:
        print("No draft knowledge found.")
        return

    print("Draft Knowledge Review Queue")
    print("=" * 80)

    for draft in drafts:
        print(f"ID        : {draft['id']}")
        print(f"Question  : {draft['question']}")
        print(f"Status    : {draft['status']}")
        print(f"Hit Count : {draft['hit_count']}")
        print(f"Updated   : {draft['updated_at']}")
        print("Answer:")
        print(draft["answer"])
        print("-" * 80)


def refresh_knowledge() -> None:
    start_time = time.time()

    print("Starting full knowledge refresh...")
    print("")

    print("Step 1/5: Standardizing raw knowledge...")
    refresh_jsonl()
    print("")

    print("Step 2/5: Loading standardized knowledge into SQLite...")
    load_result = load_knowledge_to_db()
    print(f"Records loaded: {load_result['records_loaded']}")
    print(f"Database: {load_result['db_path']}")
    print("")

    print("Step 3/5: Syncing standardized articles into RAG documents...")
    sync_result = sync_standardized_articles()
    print(f"Articles synced: {sync_result['articles_synced']}")
    print("")

    print("Step 4/5: Generating embeddings...")
    generate_chunk_embeddings()
    print("")

    print("Step 5/5: Running evaluation...")
    evaluation_result = evaluate()
    print("")

    duration = round(time.time() - start_time, 2)

    print("Refresh Summary")
    print("---------------")
    print(f"Records loaded : {load_result['records_loaded']}")
    print(f"Articles synced: {sync_result['articles_synced']}")
    print("Embeddings     : Generated")
    print(
        f"Evaluation     : {evaluation_result['passed']} passed, "
        f"{evaluation_result['failed']} failed"
    )
    print(f"Duration       : {duration} seconds")
    print("")

    if evaluation_result["success"]:
        print("Full knowledge refresh completed successfully")
    else:
        print("Refresh completed with evaluation failures")
        raise SystemExit(1)


def delete_draft_command() -> None:
    if len(sys.argv) < 3:
        print("Usage: python manage.py delete-draft <id>")
        raise SystemExit(1)

    draft_id = int(sys.argv[2])
    result = delete_draft_answer(draft_id)

    if result["status"] == "deleted":
        print(f"Deleted draft ID: {draft_id}")
    else:
        print(f"Draft not found: {draft_id}")
        raise SystemExit(1)


def approve_draft_command() -> None:
    if len(sys.argv) < 5:
        print('Usage: python manage.py approve-draft <id> "<answer>" "<category>"')
        raise SystemExit(1)

    draft_id = int(sys.argv[2])
    approved_answer = sys.argv[3]
    category = sys.argv[4]

    result = approve_draft_answer(draft_id, approved_answer, category)

    if result["status"] == "approved":
        print(f"Approved draft ID: {draft_id}")
        print(f"Question: {result['question']}")
        print(f"Category: {result['category']}")
        print("")
        print("Next step: run python manage.py refresh")
    else:
        print(f"Draft not found or already approved: {draft_id}")
        raise SystemExit(1)


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
        result = evaluate()
        if not result["success"]:
            raise SystemExit(1)
    elif command == "refresh":
        refresh_knowledge()
    elif command == "drafts":
        show_drafts()
    elif command == "delete-draft":
        delete_draft_command()
    elif command == "approve-draft":
        approve_draft_command()
    else:
        print(f"Unknown command: {command}")
        print_usage()


if __name__ == "__main__":
    main()