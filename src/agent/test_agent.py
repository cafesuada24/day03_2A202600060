# -*- coding: utf-8 -*-
import os
import sys

from dotenv import load_dotenv

load_dotenv()

from src.agent import ReActAgent
from src.tools.tools import get_tool_descriptions


def get_provider():
    """Lấy LLM Provider (Ưu tiên OpenAI/OpenRouter)"""
    if api_key := os.getenv("OPENAI_API_KEY"):
        from src.core.openai_provider import OpenAIProvider

        return OpenAIProvider(
            model_name="gpt-4o-mini",
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )

    if api_key := os.getenv("GEMINI_API_KEY"):
        from src.core.gemini_provider import GeminiProvider

        return GeminiProvider(model_name="gemini-2.0-flash", api_key=api_key)

    return None


def test_agent_run():
    print(f"\n{'=' * 25} 🤖 [AGENT REACT FINAL TEST] {'=' * 25}\n")

    provider = get_provider()
    if not provider:
        print("[ERROR] No provider found! Please check your .env file.")
        return

    tools = get_tool_descriptions()

    print(f"📦 Loaded {len(tools)} tools: {', '.join([t['name'] for t in tools])}")

    agent = ReActAgent(
        llm=provider, tools=tools, max_steps=10
    )  # Tăng max_steps cho các câu hỏi khó

    # 3. Danh sách các câu hỏi thử thách đa kỹ năng
    queries = [
        "Kiểm tra xem còn iPhone trong kho không? Nếu tôi mua 3 chiếc với giá 999 USD mỗi chiếc thì tổng cộng là bao nhiêu?",
        "Do you have iPhone in stock?",
        "How much to ship a 2kg package to Hanoi?",
        "Is the coupon 'WINNER' still valid and how much is the discount?",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n🚀 [TEST {i}] Query: {query}")
        print("-" * 60)
        try:
            # Chạy Agent
            answer = agent.run(query)
            print(f"\n✅ [FINAL ANSWER]: {answer}")
        except Exception as e:
            print(f"❌ [ERROR]: {e}")
        print("=" * 70)


if __name__ == "__main__":
    try:
        test_agent_run()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user.")
        sys.exit(0)
