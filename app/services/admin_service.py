"""
Admin service for discount code generation and statistics.
"""

from typing import Tuple, Optional
from datetime import datetime
from app.stores.data import (
    get_order_count,
    get_all_orders,
    get_all_discount_codes,
    get_available_discount_code,
    add_discount_code,
    set_available_code,
    system_state
)
from app.config import NTH_ORDER, DISCOUNT_CODE_PREFIX
from app.models.schemas import (
    GenerateDiscountResponse,
    StatisticsResponse,
    DiscountCodeResponse
)


def generate_discount() -> GenerateDiscountResponse:
    """
    Manually generate a discount code if the nth order condition is met.
    
    Returns:
        GenerateDiscountResponse with code or status message
    """
    current_order_count = get_order_count()
    nth_order = system_state["nthOrder"]
    
    # Check if nth order condition is met (orderCount divisible by nthOrder)
    if current_order_count % nth_order != 0:
        # Condition not met
        orders_remaining = nth_order - (current_order_count % nth_order)
        next_discount_at = ((current_order_count // nth_order) + 1) * nth_order
        
        return GenerateDiscountResponse(
            success=False,
            message="Discount code cannot be generated yet",
            code=None,
            currentOrderCount=current_order_count,
            nextDiscountAt=next_discount_at,
            ordersRemaining=orders_remaining
        )
    
    # Prevent duplicate codes - check if unused code already exists
    available_code = get_available_discount_code()
    if available_code and not available_code.get("isUsed", False):
        return GenerateDiscountResponse(
            success=False,
            message=f"Unused discount code '{available_code['code']}' already exists",
            code=available_code["code"],
            currentOrderCount=current_order_count,
            nextDiscountAt=current_order_count + nth_order,
            ordersRemaining=None
        )
    
    # Condition is met and no unused code exists - generate new code
    existing_codes = get_all_discount_codes()
    code_number = len(existing_codes) + 1
    new_code = f"{DISCOUNT_CODE_PREFIX}{code_number}"
    
    # Ensure uniqueness
    while any(dc["code"] == new_code for dc in existing_codes):
        code_number += 1
        new_code = f"{DISCOUNT_CODE_PREFIX}{code_number}"
    
    # Create discount code
    discount_code_obj = {
        "code": new_code,
        "isUsed": False,
        "usedByOrder": None,
        "createdAt": datetime.now(),
        "usedAt": None
    }
    
    add_discount_code(discount_code_obj)
    set_available_code(new_code)
    
    return GenerateDiscountResponse(
        success=True,
        message="Discount code generated successfully",
        code=new_code,
        currentOrderCount=current_order_count,
        nextDiscountAt=current_order_count + nth_order,
        ordersRemaining=None
    )


def get_statistics() -> StatisticsResponse:
    """
    Calculate and return store statistics.
    
    Returns:
        StatisticsResponse with all statistics
    """
    all_orders = get_all_orders()
    all_discount_codes = get_all_discount_codes()
    
    # Calculate total items purchased
    total_items_purchased = 0
    for order in all_orders:
        for item in order.get("items", []):
            total_items_purchased += item.get("quantity", 0)
    
    # Calculate total purchase amount
    total_purchase_amount = sum(order.get("total", 0) for order in all_orders)
    total_purchase_amount = round(total_purchase_amount, 2)
    
    # Calculate total discount amount
    total_discount_amount = sum(order.get("discountAmount", 0) for order in all_orders)
    total_discount_amount = round(total_discount_amount, 2)
    
    # Build discount codes list
    discount_codes_response = []
    for dc in all_discount_codes:
        discount_codes_response.append(DiscountCodeResponse(
            code=dc["code"],
            isUsed=dc.get("isUsed", False),
            usedByOrder=dc.get("usedByOrder"),
            createdAt=dc.get("createdAt", datetime.now()),
            usedAt=dc.get("usedAt")
        ))
    
    return StatisticsResponse(
        totalItemsPurchased=total_items_purchased,
        totalPurchaseAmount=total_purchase_amount,
        discountCodes=discount_codes_response,
        totalDiscountAmount=total_discount_amount
    )
