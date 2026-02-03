"""
Admin API routes.
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import GenerateDiscountResponse, StatsResponse
from app.services.admin_service import generate_discount, get_statistics

router = APIRouter()


@router.post("/generate-discount", response_model=GenerateDiscountResponse, status_code=200)
def generate_discount_code():
    """
    Manually generate a discount code if the nth order condition is met.
    
    - Checks if current order count is divisible by nth order (default: 5)
    - If condition is met and no unused code exists, generates new code
    - Returns status with code or information about when next code will be available
    """
    try:
        response = generate_discount()
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/stats", response_model=StatsResponse, status_code=200)
def get_store_statistics():
    """
    Get store statistics.
    
    Returns:
        - Total items purchased (sum of all item quantities)
        - Total purchase amount (sum of all order totals)
        - List of all discount codes with their status
        - Total discount amount (sum of all discounts given)
    """
    try:
        statistics = get_statistics()
        return StatsResponse(
            success=True,
            statistics=statistics
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
