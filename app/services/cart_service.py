"""
Cart service for managing user carts.
"""

from typing import Optional
from fastapi import HTTPException
from datetime import datetime
from app.stores.data import (
    get_item,
    get_cart,
    create_cart,
    carts
)
from app.models.schemas import CartResponse, CartItemResponse


def add_item_to_cart(user_id: str, item_id: str, quantity: int) -> CartResponse:
    """
    Add an item to the user's cart.
    
    Args:
        user_id: User identifier
        item_id: Item identifier
        quantity: Quantity to add (must be > 0)
    
    Returns:
        CartResponse with updated cart
    
    Raises:
        HTTPException: If item not found or invalid input
    """
    # Validate item exists
    item = get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item '{item_id}' not found")
    
    # Get or create cart
    cart = get_cart(user_id)
    if not cart:
        cart = create_cart(user_id)
    
    # Check if item already exists in cart
    item_exists = False
    for cart_item in cart["items"]:
        if cart_item["itemId"] == item_id:
            # Update quantity
            cart_item["quantity"] += quantity
            item_exists = True
            break
    
    # Add new item if it doesn't exist
    if not item_exists:
        cart["items"].append({
            "itemId": item_id,
            "quantity": quantity
        })
    
    # Update cart timestamp
    cart["updatedAt"] = datetime.now()
    
    # Build response with full item details
    cart_items_response = []
    subtotal = 0.0
    
    for cart_item in cart["items"]:
        item_data = get_item(cart_item["itemId"])
        if item_data:
            item_subtotal = item_data["price"] * cart_item["quantity"]
            subtotal += item_subtotal
            
            cart_items_response.append(CartItemResponse(
                itemId=item_data["itemId"],
                name=item_data["name"],
                price=item_data["price"],
                quantity=cart_item["quantity"],
                subtotal=item_subtotal
            ))
    
    # Build cart response
    cart_response = CartResponse(
        userId=user_id,
        items=cart_items_response,
        subtotal=round(subtotal, 2),
        discountCode=None,
        discountAmount=0.0,
        total=round(subtotal, 2)
    )
    
    return cart_response


def get_cart_for_user(user_id: str) -> Optional[CartResponse]:
    """
    Get cart for a user with full item details.
    
    Args:
        user_id: User identifier
    
    Returns:
        CartResponse or None if cart doesn't exist
    """
    cart = get_cart(user_id)
    if not cart or not cart.get("items"):
        return None
    
    # Build response with full item details
    cart_items_response = []
    subtotal = 0.0
    
    for cart_item in cart["items"]:
        item_data = get_item(cart_item["itemId"])
        if item_data:
            item_subtotal = item_data["price"] * cart_item["quantity"]
            subtotal += item_subtotal
            
            cart_items_response.append(CartItemResponse(
                itemId=item_data["itemId"],
                name=item_data["name"],
                price=item_data["price"],
                quantity=cart_item["quantity"],
                subtotal=item_subtotal
            ))
    
    # Get discount info if any (for future use)
    discount_code = cart.get("discountCode")
    discount_amount = cart.get("discountAmount", 0.0)
    total = subtotal - discount_amount
    
    cart_response = CartResponse(
        userId=user_id,
        items=cart_items_response,
        subtotal=round(subtotal, 2),
        discountCode=discount_code,
        discountAmount=round(discount_amount, 2),
        total=round(total, 2)
    )
    
    return cart_response
