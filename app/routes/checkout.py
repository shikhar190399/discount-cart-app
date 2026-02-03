"""
Checkout API routes.
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import CheckoutRequest, CheckoutResponse
from app.services.checkout_service import checkout

router = APIRouter()


@router.post("/checkout", response_model=CheckoutResponse, status_code=200)
def process_checkout(request: CheckoutRequest):
    """
    Process checkout for a user's cart.
    
    - **userId**: User identifier
    - **discountCode**: Optional discount code to apply
    
    Validates the discount code if provided. If invalid, proceeds without discount.
    Creates order, clears cart, and generates new discount code if nth order condition is met.
    """
    try:
        order, new_discount_code = checkout(
            user_id=request.userId,
            discount_code=request.discountCode
        )
        
        message = "Order placed successfully"
        if new_discount_code:
            message += f". New discount code '{new_discount_code}' generated!"
        
        return CheckoutResponse(
            success=True,
            message=message,
            order=order,
            newDiscountCode=new_discount_code
        )
    except HTTPException:
        raise
    except Exception as e:
        # Log error in production (logging would be added here)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request"
        )
