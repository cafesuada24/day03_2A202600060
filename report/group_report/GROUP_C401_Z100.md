# Group Report: Lab 3 - Production-Grade Agentic System

- **Team Name**: C401 - Z100
- **Team Members**: Hồ Sỹ Minh Hà, Đặng Hồ Hải
- **Deployment Date**: 2026-04-06

---

## 1. Executive Summary

We built and evaluated a ReAct agent that reasons about queries in a Thought-Action-Observation loop, using seven tools. The agent was tested against 18 curated queries spanning easy, medium, hard, and edge-case difficulty.

- **Success Rate**: Agent v2 solved all problems, Agent v1 solved 80% of the tests, Chatbot solved only known-fact queries.
- **Key Outcome**: Agent v2 uses ~2.5 LLM calls per query on average (vs 1.0 for chatbot), providing verifiable tool-backed answers at 37% higher token cost. Agent v1's stricter prompt caused 2 rate-limit-induced failures under sequential execution.

---

## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation

The agent follows this flow:

1. **Template loading**: Prompt file (v1 or v2) is loaded with tool descriptions injected.
2. **Query injection**: User query appended to the base template.
3. **LLM generation**: The LLM produces reasoning steps and optionally an Action/Action Input pair.
4. **Parsing**: Regex extracts `Action:` and `Action Input:` from the response.
5. **Tool execution**: If a valid action pair exists, the corresponding tool runs and its output is returned as `Observation:`.
6. **Prompt extension**: The raw LLM response + observation are appended to the prompt for the next iteration.
7. **Termination**: Loop ends when `Final Answer:` is detected or `max_steps` (5) is reached.

### 2.2 Tool Definitions (Inventory)

| Tool Name | Input Format | Use Case | Return Type |
| :--- | :--- | :--- | :--- |
| `calculator` | string (math expression) | Evaluate numeric expressions exactly | `str` |
| `wikipedia_search` | string (search query) | Retrieve factual summaries from Wikipedia | `str` |
| `web_search` | string (search query) | Get real-time information via Brave web search | `str` |
| `get_system_time` | none | Return current date context | `str` |
| `check_stock` | `str` (item name) | Verify inventory availability and quantity | `Dict[str, Any]` |
| `calc_shipping` | `str` ("weight, destination") | Compute shipping cost from weight and location | `Dict[str, Any]` |
| `get_discount` | `str` (coupon code) | Validate promotions and retrieve discount rates | `Dict[str, Any]` |


### 2.3 LLM Providers Used

- **Primary**: Gemini 3.1 Flash Lite Preview via OpenAI-compatible API
- **Framework**: OpenAIProvider adapter (routing through Google's OpenAI-compatible endpoint)

### 2.4 Compositional Tool Workflows

#### 2.4.1 Example Workflow: Complete Order Cost Estimation

The ReAct agent can chain multiple heterogeneous tools in a single query:

```
Query: "I want to order a MacBook to Hanoi, it weighs 1.5kg.
Is it in stock? I have a VIP coupon. What would shipping cost
and what would be the final price?"

Expected trace:
  Step 1 - Action: check_stock, Input: "MacBook"
           Obs: {item: "MacBook", quantity: 2, available: True}
  Step 2 - Action: get_discount, Input: "VIP"
           Obs: {coupon_code: "VIP", discount: 30, valid: True}
  Step 3 - Action: calc_shipping, Input: "1.5, Hanoi"
           Obs: {weight_kg: 1.5, destination: "Hanoi",
                shipping_cost: 8.0, currency: "USD"}
  Step 4 - Action: calculator (compute final cost)
  Step 5 - Final Answer: structured cost breakdown
```

#### 2.4.2 Why Chatbot Cannot Replicate This

| Scenario | Chatbot | ReAct Agent |
| :--- | :--- | :--- |
| "Is MacBook in stock?" | Hallucinates from training data | Reads actual inventory via `check_stock` |
| "VIP coupon discount?" | May not know promo codes | Validates via `get_discount` with `valid: True/False` |
| "Shipping to Hanoi for 1.5kg?" | Guesses | Computes exact cost via `calc_shipping` |
| Full order pipeline | Impossible -- no tool access | 4-step orchestration with interdependent results |
| Graceful out-of-stock handling | No mechanism | Can detect `available: False` and branch |

#### 2.4.3 Open/Closed Principle Demonstration

The agent core (`ReActAgent` class) was not modified to add the 3 new tools. They were added via:
- New function files in `src/tools/` (`inventory.py`, `logistics.py`, `promotion.py`)
- Import + registration in `main.py`'s `get_tool_descriptions()`
- No changes to the ReAct loop, parsing logic, or prompt structure

---

## 3. Telemetry & Performance Dashboard

Metrics collected via `PerformanceTracker` during the agent v2 test run (15 queries):

| Metric | Agent V2 | Agent V1 | Chatbot Baseline |
| :--- | :--- | :--- | :--- |
| Success Rate | 15/15 (100%) | 13/15 (87%) * | 15/15 (100%) |
| Avg LLM Calls/Query | 1.7 | 1.3 | 1.0 |
| Avg Tokens/Query | 1,227 | 896 | ~140 |
| Avg Latency/query | 4,890ms | 3,123ms | ~2,600ms |
| Max Latency | 15,336ms (Q7) | 6,070ms | ~5,000ms |
| Total Cost (est.) | $0.1841 | $0.1343 * | $0.0018 * |
| Multi-step Queries | 9/15 | 6/15 | 0/15 |

*Agent v1 costs exclude the 2 failed queries. Chatbot costs/latency tracked via PerformanceTracker (not captured in earlier run).

**Cost breakdown by difficulty (Agent V2):**

| Difficulty | Queries | Correct | Multi-step | Cost |
| :--- | :--- | :--- | :--- | :--- |
| Easy (Q1-Q3) | 3 | 3/3 | 1/3 | $0.0231 |
| Medium (Q4-Q8) | 5 | 5/5 | 4/5 | $0.0774 |
| Hard (Q9-Q12) | 4 | 4/4 | 2/4 | $0.0473 |
| Edge (Q13-Q15) | 3 | 3/3 | 2/3 | $0.0364 |

Medium-difficulty questions are the most expensive per query because they typically require 2-5 LLM calls (reasoning + tool verification).


---

## 4. Root Cause Analysis (RCA) - Failure Traces

### Case Study 1: Rate Limit Exhaustion (Agent V1 — Q12, Q13)

- **Input**: "Search for the latest news about AI regulation in the EU" (Q12), "What is the square of 999?" (Q13)
- **Observation**: Agent v1 hit 429 RESOURCE_EXHAUSTED errors on queries 12 and 13.
- **Root Cause**: The free-tier rate limit for `gemini-3.1-flash-lite` is 15 requests/minute. Agent v1 used ~3 sequential iterations for some queries, consuming the quota before the full suite completed. Agent v2's lighter prompt consumed fewer sequential calls overall and completed within limits.
- **Fix**: Implement exponential backoff retries (added to the chatbot baseline runner; should be added to the agent).

### Case Study 2: Over-Tooling (Agent V2 — Q9, Q15)

- **Input Q9**: "Split $5000 among 7 people" → Agent answered directly without using calculator (1 LLM call). Correct answer ($714.29).
- **Input Q15**: "What is 0/0 and 1/3 to 7 decimals?" → Agent answered directly (1 LLM call). Correct answer.
- **Observation**: For math questions, the v2 prompt sometimes skips tool use entirely and answers from internal reasoning, producing correct results but bypassing the ReAct loop. This is a trade-off: efficient but not verifiable through tools.

### Case Study 3: Prompt Duplication Bug (Pre-fix)

- **Bug**: In the original `agent.py`, line 83 unconditionally appended `f"Observation: {llm_response}\n"` to the prompt before checking if a tool call was needed. This created corrupted context where every LLM response was treated as an observation.
- **Fix**: Removed the premature observation append; now only `llm_response + "Observation: " + tool_output` is added after successful tool execution.

---

## 5. Ablation Studies & Experiments

### Experiment 1: Prompt v1 vs Prompt v2

**Diff**: Prompt v1 enforces strict formatting ("NEVER rely on internal knowledge", "MUST use a tool to verify"). Prompt v2 is more flexible ("Be thorough in your reasoning", "Use tools when you need more information").

| Metric | Prompt V1 | Prompt V2 |
| :--- | :--- | :--- |
| Success Rate | 13/15 (87%) | 15/15 (100%) |
| Avg LLM Calls/Query | 1.3 | 1.7 |
| Avg Tokens/Query | 896 | 1,227 |
| Avg Latency | 3,123ms | 4,890ms |
| Tool Usage (multi-step) | 6/15 | 9/15 |

**Result**: V1's stricter prompt uses fewer tokens and is faster but is more prone to tool over-use (causing rate limit hits) when forced to verify everything. V2's flexible prompt balances tool use with direct answering, achieving higher success rate at modestly higher cost.

### Experiment 2: Chatbot vs Agent

| Query | Chatbot Result | Agent V2 Result | Winner |
| :--- | :--- | :--- | :--- |
| Q1: Capital of France | Correct (Paris) | Correct (1 call) | Draw |
| Q2: 234 * 56 | Correct (13,104) | Correct, tool-backed | Chatbot (cheaper) |
| Q4: Japan pop * 2 | ~247.4M (estimated) | ~247.6M (tool-backed) | Agent (verified) |
| Q7: 15% of 89,500 + 3,200 | 16,625 (mental math) | 16,625 (tool-backed) | Draw |
| Q10: Everest vs Eiffel | ~29,032ft vs ~1,083ft | Same values, tool-verified | Agent (verified) |
| Q11: Time difference NYC-London | 5 hours | 5 hours (DST-aware) | Draw |
| Q12: EU AI regulation news | Implementation phase info | Verified via web_search | Agent (timely) |
| Q15: 0/0 and 1/3 | Correct (mental math) | Correct (direct answer) | Draw |

**Summary**: The agent provides verifiable answers (tool-backed) at ~37% higher cost. For simple factual queries the chatbot is sufficient. For queries requiring current data (Q5 weather, Q12 news) the agent's tool use is essential.

### Experiment 3: Agent with Domain-Specific Tools vs Chatbot

The original experiments used general-purpose tools (web search, math) on general knowledge queries. The agent won on verifiability and real-time data but lost on cost for simple questions.

With domain-specific e-commerce tools, the gap widens dramatically:

1. The Chatbot has no path to verify inventory, validate time-sensitive coupon codes, compute arbitrary weight/destination shipping, or chain these with interdependent math.
2. An order pipeline query would cost the chatbot ~$0.0018 (single call) but produce a hallucinated answer. The agent costs ~$0.02–0.05 (4–5 calls) but produces a verified, accurate answer. For e-commerce contexts, accuracy justifies cost.

Proposed future test queries:
- **Q16**: "Do you have AirPods?" (stock check)
- **Q17**: "Apply coupon WINNER if I buy 3 iPhones" (stock + discount)
- **Q18**: "Ship 2kg MacBook to Da Nang with VIP discount" (full chain)
- **Q19**: "I want iPhone but all coupons are invalid. Cheapest shipping?" (degraded path)

### 5.4 Agent vs Chatbot Capability Comparison

| Capability | Chatbot | Agent (4 tools) | Agent (7 tools) |
| :--- | :---: | :---: | :---: |
| Answer factual questions | Yes | Yes | Yes |
| Real-time web search | No | Yes | Yes |
| Exact math computations | Yes (small) | Yes (any) | Yes (any) |
| Check live inventory | No | No | Yes |
| Calculate shipping | No | No | Yes |
| Validate coupon codes | No | No | Yes |
| Pipeline: stock > discount > ship > total | Impossible | No | Yes |
| Conditional branching on tool output | No | No | Yes |
| Verifiable audit trail | No | Partial | Full |
| Structured per-tool telemetry | None | LLM metrics only | + per-tool execution logs |

---

## 6. Production Readiness Review

- **Security**: The calculator tool uses `eval()` with regex validation (`^[\d\.\+\-\*\/\s\(\)\%]+$`). This is safe for numeric-only input but would be unsafe with variable or function names. A safer alternative would be `ast.literal_eval` or a dedicated math parser.
- **Rate Limiting**: No built-in rate limiting or retry with backoff. The agent fails immediately on 429 errors. A production system needs exponential backoff and quota monitoring.
- **Guardrails**: `max_steps=5` prevents infinite loops but may not be sufficient for complex queries requiring 6+ tool calls. Should be configurable per query complexity.
- **Prompt Injection**: The agent appends raw LLM output to the prompt. A malicious or confused LLM response containing `Observation:` or `Final Answer:` text could corrupt the loop. Output sanitization is recommended.
- **Telemetry**: `PerformanceTracker` is now wired to every LLM call. Metrics are logged to both console and `logs/{date}.log` as structured JSON. Cost estimation uses a flat $0.01/1K tokens rate — should be updated with real provider pricing.
- **Serialization**: The new tools return structured dicts that get stringified via `str()` in `agent.py` line 87 before re-entering the LLM context. While `str({"key": "value"})` produces readable text, this is fragile: dict ordering, boolean representation (`True` vs `true`), and special characters could cause the LLM to misinterpret the observation. Production systems should use `json.dumps(result)` for consistent, LLM-friendly output.
- **Scaling**: For production, the monolithic `ReActAgent` should transition to a framework like LangGraph for multi-agent orchestration, checkpointing, and human-in-the-loop capabilities.
