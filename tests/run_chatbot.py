"""Run the chatbot baseline (direct LLM, no agent loop) on the test suite."""

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import get_llm
from src.telemetry.metrics import tracker
from tests.test_queries import TEST_QUERIES_V2


def call_with_retry(llm, query, max_retries=5):
    """Handle rate limits with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return llm.generate(query)
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                delay = 60 * (attempt + 1)
                print(f"  Rate limited, waiting {delay}s (attempt {attempt+1}/{max_retries})...")
                time.sleep(delay)
            else:
                raise
    return None


def run_chatbot_suite(output_path=None):
    llm = get_llm()
    results = []

    for test in TEST_QUERIES_V2:
        qid = test["id"]
        query = test["query"]
        print(f"\n{'='*60}")
        print(f"Running {qid}: {query}")
        print(f"{'='*60}")

        pre_metrics = len(tracker.session_metrics)
        start = time.time()

        resp = call_with_retry(llm, query)
        if resp:
            answer = resp["content"]
            print(f"Answer: {answer[:300]}")
        else:
            answer = "ERROR: Rate limit exceeded after retries"
            print(f"  {answer}")

        elapsed = time.time() - start
        post_metrics = len(tracker.session_metrics)
        query_metrics = tracker.session_metrics[pre_metrics:post_metrics]

        results.append({
            "id": qid,
            "query": query,
            "expected_tool": test["expected_tool"],
            "difficulty": test["difficulty"],
            "answer": answer,
            "elapsed_seconds": round(elapsed, 2),
            "total_tokens": sum(m.get("total_tokens", 0) for m in query_metrics),
            "cost_estimate": sum(m.get("cost_estimate", 0) for m in query_metrics),
            "latency_ms": sum(m.get("latency_ms", 0) for m in query_metrics),
            "metrics": query_metrics,
        })

    if output_path is None:
        output_path = f"experiments/results_chatbot_{time.strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        json.dump({"mode": "chatbot", "num_tests": len(results), "results": results}, f, indent=2)

    print(f"\n\nResults saved to {output_path}")
    return results


if __name__ == "__main__":
    run_chatbot_suite()
