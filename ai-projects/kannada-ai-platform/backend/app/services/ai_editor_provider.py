from email.mime import text
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from app.llm.local_llm import get_llm_response


BACKEND_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BACKEND_DIR / ".env"
AI_LOG_PATH = BACKEND_DIR / "data" / "ai_usage_logs.jsonl"

load_dotenv(ENV_PATH)


def generate_editorial_text(prompt: str) -> str:
    provider = os.getenv("EDITOR_PROVIDER", "ollama").lower()

    if provider == "openai":
        try:
            return generate_with_openai(prompt)
        except Exception as error:
            print(f"[AI Provider] OpenAI failed, falling back to Ollama: {error}")
            return get_llm_response(prompt)

    return get_llm_response(prompt)


def generate_with_openai(prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing")

    model = os.getenv("OPENAI_EDITOR_MODEL", "gpt-5-mini")
    budget_usd = float(os.getenv("OPENAI_EDITOR_BUDGET_USD", "10"))
    max_cost_per_article = float(
        os.getenv("OPENAI_EDITOR_MAX_COST_PER_ARTICLE", "0.02")
    )

    current_spend = get_total_openai_spend()

    if current_spend >= budget_usd:
        raise RuntimeError(
            f"OpenAI editor budget exceeded. Current spend: ${current_spend:.4f}"
        )

    client = OpenAI(api_key=api_key)

    start_time = time.time()

    response = client.responses.create(
        model=model,
        input=prompt,
        reasoning={"effort": "low"},
        max_output_tokens=1800,
    )


    latency_seconds = round(time.time() - start_time, 2)

    text = response.output_text.strip()
    if not text:
        raise RuntimeError("OpenAI returned empty visible output")

    usage = response.usage
    prompt_tokens = getattr(usage, "input_tokens", 0) or 0
    completion_tokens = getattr(usage, "output_tokens", 0) or 0
    total_tokens = getattr(usage, "total_tokens", 0) or (
        prompt_tokens + completion_tokens
    )

    estimated_cost = estimate_cost(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
    )

    log_ai_usage(
        provider="openai",
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        estimated_cost=estimated_cost,
        latency_seconds=latency_seconds,
        success=True,
        error_message="",
    )

    print("")
    print("AI Editorial Usage")
    print("=" * 80)
    print(f"Provider          : OpenAI")
    print(f"Model             : {model}")
    print(f"Prompt tokens     : {prompt_tokens}")
    print(f"Completion tokens : {completion_tokens}")
    print(f"Total tokens      : {total_tokens}")
    print(f"Estimated cost    : ${estimated_cost:.6f}")
    print(f"Total spend so far: ${get_total_openai_spend():.6f}")
    print(f"Latency           : {latency_seconds}s")
    print("=" * 80)
    print("")

    if estimated_cost > max_cost_per_article:
        print(
            f"[AI Provider Warning] Article cost ${estimated_cost:.6f} "
            f"exceeded max ${max_cost_per_article:.6f}"
        )

    return text


def estimate_cost(prompt_tokens: int, completion_tokens: int) -> float:
    input_cost_per_1m = float(
        os.getenv("OPENAI_EDITOR_INPUT_COST_PER_1M", "0.25")
    )
    output_cost_per_1m = float(
        os.getenv("OPENAI_EDITOR_OUTPUT_COST_PER_1M", "2.00")
    )

    input_cost = (prompt_tokens / 1_000_000) * input_cost_per_1m
    output_cost = (completion_tokens / 1_000_000) * output_cost_per_1m

    return round(input_cost + output_cost, 8)


def log_ai_usage(
    provider: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    estimated_cost: float,
    latency_seconds: float,
    success: bool,
    error_message: str,
) -> None:
    AI_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "provider": provider,
        "model": model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "estimated_cost": estimated_cost,
        "latency_seconds": latency_seconds,
        "success": success,
        "error_message": error_message,
    }

    with AI_LOG_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(entry, ensure_ascii=False) + "\n")


def get_total_openai_spend() -> float:
    if not AI_LOG_PATH.exists():
        return 0.0

    total = 0.0

    with AI_LOG_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            if entry.get("provider") == "openai" and entry.get("success"):
                total += float(entry.get("estimated_cost", 0))

    return round(total, 8)