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
from app.services.draft_rewrite_service import rewrite_draft_answer
from app.services.feedback_dashboard_service import get_feedback_dashboard
from app.services.internet_knowledge_service import import_topic_as_draft
from app.services.knowledge_loader import load_knowledge_to_db
from scripts.refresh_knowledge import main as refresh_jsonl
from app.services.bulk_topic_import_service import import_topics_from_file


def print_usage() -> None:
    print("Usage: python manage.py <command>")
    print("")
    print("Available commands:")
    print("  list                                      Show knowledge library")
    print("  ingest                                    Ingest all sources from manifest")
    print("  embed                                     Generate embeddings for chunks")
    print("  sync                                      Ingest sources and generate embeddings")
    print("  evaluate                                  Run RAG evaluation")
    print("  refresh                                   Refresh knowledge, reload SQLite, embed, and evaluate")
    print("  drafts                                    Show draft knowledge review queue")
    print("  delete-draft <id>                         Delete a bad draft answer")
    print('  approve-draft <id> "<question>" "<answer>" "<category>"')
    print("                                            Approve draft into admin knowledge")
    print("  import-topic <topic> <category>           Import internet topic into draft queue")
    print("  rewrite-draft <draft_id>                  Rewrite draft into clean Kannada")
    print("  feedback                                  Show feedback dashboard")
    print("  import-topics-file <file> <category>     Import many topics into draft queue")


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


def show_feedback_dashboard() -> None:
    dashboard = get_feedback_dashboard()
    stats = dashboard["stats"]
    feedback = dashboard["feedback"]

    print("Feedback Dashboard")
    print("=" * 80)
    print(f"👍 Positive : {stats['positive']}")
    print(f"👎 Negative : {stats['negative']}")
    print("")

    if not feedback:
        print("No feedback found.")
        return

    print("Recent Feedback")
    print("-" * 80)

    for item in feedback:
        print(f"ID         : {item['id']}")
        print(f"Question   : {item['question']}")
        print(f"Rating     : {item['rating']}")
        print(f"Confidence : {item['confidence_score']}")
        print(f"Source     : {item['source']}")
        print(f"Created    : {item['created_at']}")
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
    if len(sys.argv) < 6:
        print('Usage: python manage.py approve-draft <id> "<question>" "<answer>" "<category>"')
        raise SystemExit(1)

    draft_id = int(sys.argv[2])
    approved_question = sys.argv[3]
    approved_answer = sys.argv[4]
    category = sys.argv[5]

    result = approve_draft_answer(
        draft_id=draft_id,
        approved_question=approved_question,
        approved_answer=approved_answer,
        category=category,
    )

    if result["status"] == "approved":
        print(f"Approved draft ID: {draft_id}")
        print(f"Question: {result['question']}")
        print(f"Category: {result['category']}")
        print("")
        print("Article added to admin_articles.json")
        print("Next step: run python manage.py refresh")
    else:
        print(f"Draft not found or already approved: {draft_id}")
        raise SystemExit(1)


def import_topic(topic: str, category: str) -> None:
    result = import_topic_as_draft(topic, category)

    print("Internet Knowledge Import")
    print("=" * 80)

    for key, value in result.items():
        print(f"{key}: {value}")


def rewrite_draft(draft_id: int) -> None:
    result = rewrite_draft_answer(draft_id)

    print("Draft Rewrite")
    print("=" * 80)

    for key, value in result.items():
        print(f"{key}: {value}")

def import_topics_file(topic_file: str, category: str) -> None:
    result = import_topics_from_file(topic_file, category)

    print("Bulk Internet Knowledge Import")
    print("=" * 80)
    print(f"Topic file        : {result['topic_file']}")
    print(f"Category          : {result['category']}")
    print(f"Total topics      : {result['total_topics']}")
    print(f"Successful imports: {result['successful_imports']}")
    print(f"Failed imports    : {result['failed_imports']}")
    print("")

    for item in result["results"]:
        print(f"{item.get('topic')} -> {item.get('status')}")        


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
    elif command == "feedback":
        show_feedback_dashboard()
    elif command == "import-topic":
        if len(sys.argv) < 3:
            print("Usage: python manage.py import-topic <topic> <category>")
            return

        topic = sys.argv[2]
        category = sys.argv[3] if len(sys.argv) > 3 else "general"

        import_topic(topic, category)
    elif command == "rewrite-draft":
        if len(sys.argv) < 3:
            print("Usage: python manage.py rewrite-draft <draft_id>")
            return

        rewrite_draft(int(sys.argv[2]))
    elif command == "import-topics-file":
        if len(sys.argv) < 3:
            print("Usage: python manage.py import-topics-file <file> <category>")
            return

        topic_file = sys.argv[2]
        category = sys.argv[3] if len(sys.argv) > 3 else "general"

        import_topics_file(topic_file, category)    
    else:
        print(f"Unknown command: {command}")
        print_usage()


if __name__ == "__main__":
    main()

