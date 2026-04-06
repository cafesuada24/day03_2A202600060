from typing import Callable

from src.tools.calculator import calculator
from src.tools.inventory import check_stock
from src.tools.logistics import calc_shipping
from src.tools.promotion import get_discount
from src.tools.websearch import get_system_time, web_search
from src.tools.wikipedia_search import wikipedia_search


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
                "Input: a search query string. Output: top 2 result snippets."
            ),
            "func": web_search,
        },
        {
            "name": "calculator",
            "description": (
                "Evaluate a mathematical expression to get an exact numeric result. "
                "Use this for budget calculations, total cost estimates, unit conversions. "
                "Input: a math expression (e.g., '149999 * 2 + 50000'). Output: the result."
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
        {
            "name": "check_stock",
            "description": (
                "Check the available quantity of a specific item in the inventory. "
                "Use this to verify if an item is in stock and get its current quantity. "
                "Input: the name of the item (e.g., 'iPhone'). Output: item, quantity, and availability."
            ),
            "func": check_stock,
        },
        {
            "name": "calc_shipping",
            "description": (
                "Calculate shipping cost. Input MUST be two values separated by a comma: "
                "'weight, destination' (e.g., '2, Hanoi')."
            ),
            "func": calc_shipping,
        },
        {
            "name": "get_discount",
            "description": (
                "Get the discount percentage for a specific coupon code. "
                "Use this to validate promotions like 'WINNER' or 'VIP'. "
                "Input: coupon code string. Output: discount amount and validity status."
            ),
            "func": get_discount,
        },
    ]
