import os
import sys

from dotenv import load_dotenv

from src.chatbot import ChatBot

load_dotenv()


def get_provider():
    """Tự động chọn Provider dựa trên API Key có sẵn trong .env"""
    # 1. Thử OpenAI
    if api_key := os.getenv("OPENAI_API_KEY"):
        from src.core.openai_provider import OpenAIProvider

        print("✅ Using OpenAI (OpenRouter)")
        return OpenAIProvider(
            model_name="gpt-4o-mini",
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )

    # 2. Thử Gemini
    if api_key := os.getenv("GEMINI_API_KEY"):
        from src.core.gemini_provider import GeminiProvider

        print("✅ Using Gemini Provider")
        return GeminiProvider(model_name="gemini-2.0-flash", api_key=api_key)

    # 3. Thử Local
    if model_path := os.getenv("LOCAL_MODEL_PATH"):
        if os.path.exists(model_path):
            from src.core.local_provider import LocalProvider

            print(f"✅ Using Local: {model_path}")
            return LocalProvider(model_path=model_path)

    print("❌ No provider found! Check your .env file.")
    return None


def test_chatbot_basic():
    print(f"\n{'=' * 30}\n🤖 ChatBot Base Test\n{'=' * 30}")

    provider = get_provider()
    if not provider:
        sys.exit(1)

    chatbot = ChatBot(
        llm_provider=provider,
        system_prompt="You are a helpful ecommerce assistant. Be concise.",
        max_history=5,
    )

    test_messages = [
        "Hello! Do you have iPhone in stock?",
        "Shipping cost to Ha Noi for 2kg?",
        "Any discount codes?",
    ]

    for i, msg in enumerate(test_messages, 1):
        print(f"\n[Message {i}] 📨 User: {msg}")
        res = chatbot.chat(msg)

        if res["status"] == "success":
            print(f"🤖 Assistant: {res['response']}")
            print(f"⏱️  {res['latency_ms']:.0f}ms | 📊 {res['tokens_used']} tokens")
        else:
            print(f"❌ Error: {res.get('error')}")

    # Tổng kết nhanh
    metrics = chatbot.get_metrics_summary()
    print(
        f"\n{'=' * 30}\n📊 Summary: {metrics['total_requests']} reqs | {metrics['total_tokens_used']} tokens\n{'=' * 30}"
    )


if __name__ == "__main__":
    test_chatbot_basic()
