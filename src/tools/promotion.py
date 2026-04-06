from typing import Any, Dict

from src.telemetry.logger import logger


def get_discount(coupon_code: str) -> Dict[str, Any]:
    """Get discount percentage for a coupon code."""
    coupons = {
        "WINNER": 20,
        "SUMMER2024": 15,
        "VIP": 30,
    }
    discount = coupons.get(coupon_code, 0)
    result = {
        "coupon_code": coupon_code,
        "discount": discount,
        "valid": discount > 0,
    }
    logger.log_event("TOOL_EXECUTED", {"tool": "get_discount", "result": result})
    return result
