from typing import Any, Dict

from src.telemetry.logger import logger


def check_stock(item_name: str) -> Dict[str, Any]:
    """Check available stock for an item."""
    inventory = {
        "iPhone": 5,
        "MacBook": 2,
        "AirPods": 15,
    }
    quantity = inventory.get(item_name, 0)
    result = {"item": item_name, "quantity": quantity, "available": quantity > 0}
    logger.log_event("TOOL_EXECUTED", {"tool": "check_stock", "result": result})
    return result
