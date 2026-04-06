import os
from typing import Callable

# Format the output nicely (e.g., convert 15296.0 to 15296)
from src.agent.agent import ReActAgent
from src.core.gemini_provider import GeminiProvider
from src.core.llm_provider import LLMProvider
from src.core.local_provider import LocalProvider
from src.core.openai_provider import OpenAIProvider
from src.tools.calculator import calculator
from src.tools.wikipedia_search import wikipedia_search
from src.tools.websearch import web_search, get_system_time

from dotenv import load_dotenv

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


def get_tool_descriptions() -> list[dict[str, str | Callable[[str], str]]]:
    return [
        {
            "name": "wikipedia_search",
            "description": "A wrapper around Wikipedia. Useful for when you need to answer general questions about people, places, companies, facts, historical events, or other subjects. Input should be a search query.",
            "func": wikipedia_search,
        },
        {
            "name": "web_search",
            "description": (
                "Search the web for real-time information using Brave Search API. "
                "Use this for weather forecasts, ticket prices, hotel prices, travel blogs, "
                "restaurant recommendations, and any current data. "
                "Input: a search query string. Output: top 3 result snippets."
            ),
            "func": web_search,
        },
        {
            "name": "calculator",
            "description": (
                "Evaluate a mathematical expression to get an exact numeric result. "
                "Use this for budget calculations, total cost estimates, unit conversions. "
                "Input: a math expression (e.g., '150000 * 2 + 50000'). Output: the result."
            ),
            "func": calculator,
        },
        {
            "name": "get_system_time",
            "description": (
                "Get today's date and day of the week. "
                "Use this to determine the current date for planning trips, "
                "calculating 'next weekend', or checking seasonal weather. "
                "Input: none. Output: current date string."
            ),
            "func": get_system_time,
        },
    ]


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
