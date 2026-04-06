import os
from typing import Callable

from dotenv import load_dotenv

# Format the output nicely (e.g., convert 15296.0 to 15296)
from src.agent.agent import ReActAgent
from src.core.gemini_provider import GeminiProvider
from src.core.llm_provider import LLMProvider
from src.core.local_provider import LocalProvider
from src.core.openai_provider import OpenAIProvider
from src.tools.tools import get_tool_descriptions

load_dotenv()


def get_llm(provider: str | None = None, model_name: str | None = None) -> LLMProvider:
    if provider is None:
        provider = os.getenv("DEFAULT_PROVIDER")

    if model_name is None:
        model_name = os.getenv("DEFAULT_MODEL", "gpt-4o")

    match provider:
        case "openai":
            return OpenAIProvider(
                model_name=model_name,
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL"),
                # extra_body={'reasoning': {'enabled': False}},
            )
        case "google":
            return GeminiProvider(
                model_name=model_name,
                api_key=os.getenv("GEMINI_API_KEY"),
            )
        case "local":
            return LocalProvider(model_name)
        case _:
            raise ValueError(f"Unsupported llm provider: {provider}")


def main() -> None:
    llm = get_llm()
    agent = ReActAgent(
        llm=llm,
        tools=get_tool_descriptions(),
    )

    while True:
        user_input = input("User > ")
        if user_input.strip().lower() == "/q":
            print("Goodbye!")
            break
        agent.run(user_input)


if __name__ == "__main__":
    main()
