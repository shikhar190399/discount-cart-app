"""
In-memory data stores for the application.
"""

from typing import Dict, List, Optional
from datetime import datetime
from app.config import NTH_ORDER, DISCOUNT_CODE_PREFIX


# ==================== Data Stores ====================

# Items catalog - static reference data
items_catalog: Dict[str, dict] = {}

# User carts - key: userId, value: cart dict
carts: Dict[str, dict] = {}

# Orders - list of all orders
orders: List[dict] = []

# Discount codes - list of all discount codes
discount_codes: List[dict] = []

# System state
system_state: dict = {
    "orderCount": 0,
    "nthOrder": NTH_ORDER,
    "currentAvailableCode": None
}


# ==================== Dummy Data ====================

def initialize_dummy_data():
    """
    Initialize the application with dummy data.
    Called on server startup.
    """
    global items_catalog, carts, orders, discount_codes, system_state
    
    # Clear existing data
    items_catalog.clear()
    carts.clear()
    orders.clear()
    discount_codes.clear()
    
    # Initialize items catalog with dummy products
    items_catalog.update({
        "item001": {
            "itemId": "item001",
            "name": "Laptop",
            "price": 999.99,
            "description": "High-performance laptop"
        },
        "item002": {
            "itemId": "item002",
            "name": "Mouse",
            "price": 29.99,
            "description": "Wireless mouse"
        },
        "item003": {
            "itemId": "item003",
            "name": "Keyboard",
            "price": 79.99,
            "description": "Mechanical keyboard"
        },
        "item004": {
            "itemId": "item004",
            "name": "Monitor",
            "price": 299.99,
            "description": "27-inch 4K monitor"
        },
        "item005": {
            "itemId": "item005",
            "name": "Headphones",
            "price": 149.99,
            "description": "Noise-cancelling headphones"
        },
        "item006": {
            "itemId": "item006",
            "name": "Webcam",
            "price": 89.99,
            "description": "HD webcam"
        }
    })
    
    # Initialize system state
    system_state = {
        "orderCount": 0,
        "nthOrder": NTH_ORDER,
        "currentAvailableCode": None
    }
    
    print(f"✅ Dummy data initialized:")
    print(f"   - {len(items_catalog)} items in catalog")
    print(f"   - System ready with nthOrder = {NTH_ORDER}")


def get_item(item_id: str) -> Optional[dict]:
    """Get item from catalog by itemId."""
    return items_catalog.get(item_id)


def get_cart(user_id: str) -> Optional[dict]:
    """Get cart for a user."""
    return carts.get(user_id)


def create_cart(user_id: str) -> dict:
    """Create a new empty cart for a user."""
    cart = {
        "userId": user_id,
        "items": [],
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    }
    carts[user_id] = cart
    return cart


def clear_cart(user_id: str):
    """Clear cart for a user."""
    if user_id in carts:
        del carts[user_id]


def add_order(order: dict):
    """Add an order to the orders list."""
    orders.append(order)


def get_all_orders() -> List[dict]:
    """Get all orders."""
    return orders


def add_discount_code(code: dict):
    """Add a discount code."""
    discount_codes.append(code)


def get_all_discount_codes() -> List[dict]:
    """Get all discount codes."""
    return discount_codes


def get_available_discount_code() -> Optional[dict]:
    """Get the currently available (unused) discount code."""
    for code in discount_codes:
        if not code.get("isUsed", False):
            return code
    return None


def increment_order_count():
    """Increment the global order count."""
    system_state["orderCount"] += 1
    return system_state["orderCount"]


def get_order_count() -> int:
    """Get current order count."""
    return system_state["orderCount"]


def set_available_code(code: str):
    """Set the current available discount code."""
    system_state["currentAvailableCode"] = code


def get_available_code() -> Optional[str]:
    """Get the current available discount code string."""
    return system_state["currentAvailableCode"]
