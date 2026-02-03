"""
Pydantic schemas for request/response validation.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


# ==================== Request Schemas ====================

class AddToCartRequest(BaseModel):
    """Request schema for adding item to cart."""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    userId: str = Field(..., min_length=1, max_length=100, description="User identifier")
    itemId: str = Field(..., min_length=1, max_length=50, description="Item identifier")
    quantity: int = Field(..., gt=0, le=1000, description="Quantity of items to add (max 1000)")


class CheckoutRequest(BaseModel):
    """Request schema for checkout."""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    userId: str = Field(..., min_length=1, max_length=100, description="User identifier")
    discountCode: Optional[str] = Field(None, max_length=50, description="Optional discount code")


# ==================== Response Schemas ====================

class CartItemResponse(BaseModel):
    """Cart item in response."""
    itemId: str
    name: str
    price: float
    quantity: int
    subtotal: float


class CartResponse(BaseModel):
    """Cart response schema."""
    userId: str
    items: List[CartItemResponse]
    subtotal: float
    discountCode: Optional[str] = None
    discountAmount: float = 0.0
    total: float


class AddToCartResponse(BaseModel):
    """Response schema for add to cart."""
    success: bool
    message: str
    cart: CartResponse


class OrderItemResponse(BaseModel):
    """Order item in response."""
    itemId: str
    name: str
    price: float
    quantity: int
    subtotal: float


class OrderResponse(BaseModel):
    """Order response schema."""
    orderId: str
    userId: str
    items: List[OrderItemResponse]
    subtotal: float
    discountCode: Optional[str] = None
    discountAmount: float = 0.0
    total: float
    createdAt: datetime


class CheckoutResponse(BaseModel):
    """Response schema for checkout."""
    success: bool
    message: str
    order: OrderResponse
    newDiscountCode: Optional[str] = Field(None, description="New discount code if generated")


class DiscountCodeResponse(BaseModel):
    """Discount code response schema."""
    code: str
    isUsed: bool
    usedByOrder: Optional[str] = None
    createdAt: datetime
    usedAt: Optional[datetime] = None


class GenerateDiscountResponse(BaseModel):
    """Response schema for generate discount."""
    success: bool
    message: str
    code: Optional[str] = None
    currentOrderCount: Optional[int] = None
    nextDiscountAt: Optional[int] = None
    ordersRemaining: Optional[int] = None


class StatisticsResponse(BaseModel):
    """Statistics response schema."""
    totalItemsPurchased: int
    totalPurchaseAmount: float
    discountCodes: List[DiscountCodeResponse]
    totalDiscountAmount: float


class StatsResponse(BaseModel):
    """Response schema for admin stats."""
    success: bool
    statistics: StatisticsResponse


class ErrorResponse(BaseModel):
    """Error response schema."""
    success: bool = False
    error: dict = Field(..., description="Error details with code and message")
