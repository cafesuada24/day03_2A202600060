"""Run the ReAct agent (v2 prompt) on the test suite and collect telemetry."""

import json
import os
import sys
import time
from pathlib import Path

# Ensure we can import from src
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import get_llm, get_tool_descriptions
from src.agent.agent import ReActAgent
from src.telemetry.logger import logger
from src.telemetry.metrics import tracker
from tests.test_queries import TEST_QUERIES_V2


def run_test_suite(mode="agent_v2", output_path=None):
    """
    Run all test queries and return results.

    Args:
        mode: "agent_v2", "agent_v1", or "chatbot"
        output_path: where to save JSON results
    """
    llm = get_llm()
    tools = get_tool_descriptions()

    results = []

    for test in TEST_QUERIES_V2:
        qid = test["id"]
        query = test["query"]
        print(f"\n{'='*60}")
        print(f"Running {qid}: {query}")
        print(f"{'='*60}")

        pre_metrics_count = len(tracker.session_metrics)
        pre_logs_count = len(getattr(logger, '_logs', []))

        start_time = time.time()

        try:
            if mode == "chatbot":
                response = llm.generate(query)
                answer = response["content"]
                print(f"Answer: {answer[:300]}")
            else:
                # Set prompt version
                if mode == "agent_v1":
                    os.environ["REACT_PROMPT"] = "src/prompts/ReAct.v1.txt"
                else:
                    os.environ.pop("REACT_PROMPT", None)

                agent = ReActAgent(
                    llm=llm,
                    tools=tools,
                    max_steps=5,
                )
                answer = agent.run(query)
                print(f"Final Answer: {answer[:300]}")
        except Exception as e:
            answer = f"ERROR: {e}"
            print(f"Error: {e}")

        elapsed = time.time() - start_time
        post_metrics_count = len(tracker.session_metrics)

        # Pull metrics for this query
        query_metrics = tracker.session_metrics[pre_metrics_count:post_metrics_count]

        result = {
            "id": qid,
            "query": query,
            "expected_tool": test["expected_tool"],
            "difficulty": test["difficulty"],
            "mode": mode,
            "answer": answer,
            "elapsed_seconds": round(elapsed, 2),
            "num_llm_calls": len(query_metrics),
            "total_tokens": sum(
                m.get("total_tokens", 0) for m in query_metrics
            ),
            "total_cost": sum(
                m.get("cost_estimate", 0) for m in query_metrics
            ),
            "latency_ms": sum(
                m.get("latency_ms", 0) for m in query_metrics
            ),
            "llm_response_count": len(query_metrics),
            "metrics": query_metrics,
        }
        results.append(result)

    # Save results
    if output_path is None:
        output_path = f"experiments/results_{mode}_{time.strftime('%Y%m%d_%H%M%S')}.json"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        json.dump({"mode": mode, "num_tests": len(results), "results": results}, f, indent=2)

    print(f"\n\nResults saved to {output_path}")
    return results


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "agent_v2"
    run_test_suite(mode=mode)
