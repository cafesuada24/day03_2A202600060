from typing import Any, Dict

from src.telemetry.logger import logger

from .inventory import CHECK_STOCK_SCHEMA, check_stock
from .logistics import CALC_SHIPPING_SCHEMA, calc_shipping
from .promotion import GET_DISCOUNT_SCHEMA, get_discount

# Danh sách Schema cho AI model (LLM)
TOOLS_REGISTRY = [
    CHECK_STOCK_SCHEMA,
    GET_DISCOUNT_SCHEMA,
    CALC_SHIPPING_SCHEMA,
]

# Mapping tên hàm với đối tượng hàm thực tế
TOOL_FUNCTIONS = {
    "check_stock": check_stock,
    "get_discount": get_discount,
    "calc_shipping": calc_shipping,
}


def execute_tool(tool_name: str, **kwargs) -> Dict[str, Any]:
    """Hàm điều phối chung để thực thi tool."""
    if tool_name not in TOOL_FUNCTIONS:
        logger.error(f"Tool {tool_name} not found")
        return {"error": f"Tool '{tool_name}' does not exist"}

    try:
        func = TOOL_FUNCTIONS[tool_name]
        return func(**kwargs)
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {str(e)}")
        return {"error": str(e)}
