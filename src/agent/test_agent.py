# -*- coding: utf-8 -*-
import os
import sys

from dotenv import load_dotenv

# Nạp environment
load_dotenv()

from src.tools.inventory import check_stock
from src.tools.logistics import calc_shipping
from src.tools.promotion import get_discount

from .agent import ReActAgent


def get_provider():
    """Tận dụng hàm lấy provider bạn đã viết"""
    if api_key := os.getenv("OPENAI_API_KEY"):
        from src.core.openai_provider import OpenAIProvider

        return OpenAIProvider(
            model_name="gpt-4o-mini",
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )
    return None


def test_agent_run():
    print(f"\n{'=' * 20} [AGENT REACT TEST] {'=' * 20}\n")

    provider = get_provider()
    if not provider:
        print("[ERROR] No provider found!")
        return

    # 1. Định nghĩa danh sách Tools
    # Lưu ý: 'func' là đối tượng hàm (không có ngoặc đơn)
    tools = [
        {
            "name": "check_stock",
            "func": check_stock,
            "description": "Checks the inventory for a specific item. Input should be the item name.",
        },
        {
            "name": "calc_shipping",
            "func": calc_shipping,
            "description": 'Calculate shipping cost. Input MUST be a JSON: {{"weight_kg": number, "destination": "string"}}',
        },
        {
            "name": "get_discount",
            "func": get_discount,
            "description": "Get discount percentage for a coupon code.",
        },
    ]

    # 2. Khởi tạo Agent
    agent = ReActAgent(llm=provider, tools=tools, max_steps=5)

    # 3. Danh sách các câu hỏi "khó" để thử thách Agent
    queries = [
        "Do you have iPhone in stock?",
        "How much to ship a 2kg package to Hanoi?",
        "Is the coupon 'WINNER' still valid and how much is the discount?",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n[TEST {i}] {query}")
        print("-" * 50)
        try:
            answer = agent.run(query)
            print(f"\n[SUCCESS] FINAL ANSWER: {answer}")
        except Exception as e:
            print(f"[ERROR] {e}")
        print("=" * 60)


if __name__ == "__main__":
    test_agent_run()
