"""
Cart API routes.
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import AddToCartRequest, AddToCartResponse
from app.services.cart_service import add_item_to_cart

router = APIRouter()


@router.post("/cart", response_model=AddToCartResponse, status_code=200)
def add_to_cart(request: AddToCartRequest):
    """
    Add an item to the user's cart.
    
    - **userId**: User identifier
    - **itemId**: Item identifier (must exist in catalog)
    - **quantity**: Quantity to add (must be > 0)
    
    Returns the updated cart with all items and calculated totals.
    """
    try:
        cart = add_item_to_cart(
            user_id=request.userId,
            item_id=request.itemId,
            quantity=request.quantity
        )
        
        return AddToCartResponse(
            success=True,
            message="Item added to cart successfully",
            cart=cart
        )
    except HTTPException:
        raise
    except Exception as e:
        # Log error in production (logging would be added here)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request"
        )
