"""
Checkout service for processing orders.
"""

from typing import Optional, Tuple
from fastapi import HTTPException
from datetime import datetime
from app.stores.data import (
    get_cart,
    get_item,
    clear_cart,
    add_order,
    increment_order_count,
    get_order_count,
    get_available_discount_code,
    add_discount_code,
    set_available_code,
    get_all_discount_codes,
    system_state
)
from app.config import NTH_ORDER, DISCOUNT_PERCENT, DISCOUNT_CODE_PREFIX
from app.models.schemas import OrderResponse, OrderItemResponse


def validate_discount_code(code: str) -> Tuple[bool, Optional[dict], str]:
    """
    Validate if a discount code is valid and available.
    
    Args:
        code: Discount code to validate
    
    Returns:
        Tuple of (is_valid, discount_code_dict, message)
    """
    # Find the discount code
    discount_code_obj = None
    for dc in get_all_discount_codes():
        if dc["code"] == code:
            discount_code_obj = dc
            break
    
    if not discount_code_obj:
        return False, None, f"Discount code '{code}' not found"
    
    if discount_code_obj.get("isUsed", False):
        return False, discount_code_obj, f"Discount code '{code}' has already been used"
    
    # Code is valid and available
    return True, discount_code_obj, "Discount code is valid"


def calculate_discount(subtotal: float) -> float:
    """
    Calculate discount amount (10% of subtotal).
    
    Args:
        subtotal: Order subtotal
    
    Returns:
        Discount amount rounded to 2 decimal places
    """
    discount = subtotal * (DISCOUNT_PERCENT / 100)
    return round(discount, 2)


def generate_discount_code() -> str:
    """
    Generate a new unique discount code.
    
    Returns:
        New discount code string
    """
    # Get count of existing codes to make unique
    existing_codes = get_all_discount_codes()
    code_number = len(existing_codes) + 1
    
    # Generate code: DISCOUNT1, DISCOUNT2, etc.
    new_code = f"{DISCOUNT_CODE_PREFIX}{code_number}"
    
    # Ensure uniqueness (in case of manual generation)
    while any(dc["code"] == new_code for dc in existing_codes):
        code_number += 1
        new_code = f"{DISCOUNT_CODE_PREFIX}{code_number}"
    
    return new_code


def create_new_discount_code() -> Optional[str]:
    """
    Create a new discount code and add it to the system.
    
    Returns:
        New discount code string or None if not needed
    """
    new_code = generate_discount_code()
    
    discount_code_obj = {
        "code": new_code,
        "isUsed": False,
        "usedByOrder": None,
        "createdAt": datetime.now(),
        "usedAt": None
    }
    
    add_discount_code(discount_code_obj)
    set_available_code(new_code)
    
    return new_code


def checkout(user_id: str, discount_code: Optional[str] = None) -> Tuple[OrderResponse, Optional[str]]:
    """
    Process checkout for a user's cart.
    
    Args:
        user_id: User identifier
        discount_code: Optional discount code to apply
    
    Returns:
        Tuple of (OrderResponse, new_discount_code_if_generated)
    
    Raises:
        HTTPException: If cart is empty or invalid
    """
    # Get user's cart
    cart = get_cart(user_id)
    if not cart or not cart.get("items"):
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Build order items with price snapshots
    order_items = []
    subtotal = 0.0
    
    for cart_item in cart["items"]:
        item_data = get_item(cart_item["itemId"])
        if not item_data:
            # Item was removed from catalog, skip it
            continue
        
        item_subtotal = item_data["price"] * cart_item["quantity"]
        subtotal += item_subtotal
        
        order_items.append(OrderItemResponse(
            itemId=item_data["itemId"],
            name=item_data["name"],
            price=item_data["price"],
            quantity=cart_item["quantity"],
            subtotal=round(item_subtotal, 2)
        ))
    
    if not order_items:
        raise HTTPException(status_code=400, detail="Cart contains no valid items")
    
    subtotal = round(subtotal, 2)
    
    # Validate and apply discount code (if provided)
    discount_amount = 0.0
    discount_code_used = None
    
    if discount_code:
        is_valid, discount_code_obj, message = validate_discount_code(discount_code)
        
        if is_valid:
            # Apply 10% discount
            discount_amount = calculate_discount(subtotal)
            discount_code_used = discount_code
            
            # Mark discount code as used
            discount_code_obj["isUsed"] = True
            discount_code_obj["usedAt"] = datetime.now()
        # If invalid, proceed without discount (no error)
    
    # Calculate total
    total = round(subtotal - discount_amount, 2)
    
    # Generate order ID
    order_id = f"order{get_order_count() + 1:03d}"
    
    # Create order
    order = {
        "orderId": order_id,
        "userId": user_id,
        "items": [item.model_dump() for item in order_items],
        "subtotal": subtotal,
        "discountCode": discount_code_used,
        "discountAmount": discount_amount,
        "total": total,
        "createdAt": datetime.now()
    }
    
    # If discount code was used, update it with order ID
    if discount_code_used:
        for dc in get_all_discount_codes():
            if dc["code"] == discount_code_used:
                dc["usedByOrder"] = order_id
                break
        # Clear available code since it's now used
        set_available_code(None)
    
    # Add order to system
    add_order(order)
    
    # Increment order count and check if new discount code should be generated
    new_order_count = increment_order_count()
    new_discount_code = None
    if new_order_count % NTH_ORDER == 0:  # Every 5th order generates a code
        new_discount_code = create_new_discount_code()
    
    # Clear user's cart
    clear_cart(user_id)
    
    # Build order response
    order_response = OrderResponse(
        orderId=order_id,
        userId=user_id,
        items=order_items,
        subtotal=subtotal,
        discountCode=discount_code_used,
        discountAmount=discount_amount,
        total=total,
        createdAt=order["createdAt"]
    )
    
    return order_response, new_discount_code
