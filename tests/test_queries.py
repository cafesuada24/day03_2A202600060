"""15 curated test queries covering different difficulty levels and tool usage."""

TEST_QUERIES_V2 = [
    # Easy — single tool, straightforward
    {
        "id": "Q1",
        "query": "What is the capital of France?",
        "expected_tool": None,  # may answer directly
        "difficulty": "easy",
    },
    {
        "id": "Q2",
        "query": "What is 234 * 56?",
        "expected_tool": "calculator",
        "difficulty": "easy",
    },
    {
        "id": "Q3",
        "query": "Who wrote 'Romeo and Juliet'?",
        "expected_tool": None,
        "difficulty": "easy",
    },
    # Medium — may need one tool call or multi-step
    {
        "id": "Q4",
        "query": "What is the population of Japan multiplied by 2?",
        "expected_tool": "calculator",
        "difficulty": "medium",
    },
    {
        "id": "Q5",
        "query": "What is the current weather in Tokyo?",
        "expected_tool": "web_search",
        "difficulty": "medium",
    },
    {
        "id": "Q6",
        "query": "Who is the current CEO of Tesla and when was the company founded?",
        "expected_tool": "wikipedia_search",
        "difficulty": "medium",
    },
    {
        "id": "Q7",
        "query": "Calculate 15% of 89,500 and then add 3,200",
        "expected_tool": "calculator",
        "difficulty": "medium",
    },
    {
        "id": "Q8",
        "query": "What major historical event happened on July 20, 1969?",
        "expected_tool": "wikipedia_search",
        "difficulty": "medium",
    },
    # Hard — multi-step or complex reasoning
    {
        "id": "Q9",
        "query": "If I have a budget of $5000 and want to split it equally among 7 people, how much does each person get? Round to 2 decimal places.",
        "expected_tool": "calculator",
        "difficulty": "hard",
    },
    {
        "id": "Q10",
        "query": "What is the height of Mount Everest in feet compared to the height of the Eiffel Tower in feet?",
        "expected_tool": "wikipedia_search",
        "difficulty": "hard",
    },
    {
        "id": "Q11",
        "query": "What is the time difference between New York and London right now?",
        "expected_tool": "get_system_time",
        "difficulty": "hard",
    },
    {
        "id": "Q12",
        "query": "Search for the latest news about artificial intelligence regulation in the European Union",
        "expected_tool": "web_search",
        "difficulty": "hard",
    },
    # Edge — tricky, likely to confuse the agent
    {
        "id": "Q13",
        "query": "What is the square of 999?",
        "expected_tool": "calculator",
        "difficulty": "edge",
    },
    {
        "id": "Q14",
        "query": "Tell me about the philosopher who wrote 'Critique of Pure Reason' and what school of thought he belongs to.",
        "expected_tool": "wikipedia_search",
        "difficulty": "edge",
    },
    {
        "id": "Q15",
        "query": "What is 0 divided by 0? And what is 1/3 rounded to 7 decimal places?",
        "expected_tool": "calculator",
        "difficulty": "edge",
    },
]
