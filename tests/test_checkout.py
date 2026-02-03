"""
Tests for checkout API.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.stores.data import (
    initialize_dummy_data,
    carts,
    orders,
    discount_codes,
    system_state,
    clear_cart
)

# Initialize test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Setup: Initialize dummy data before each test. Teardown: Clear data after each test."""
    initialize_dummy_data()
    yield
    # Teardown: Clear all data after each test
    carts.clear()
    orders.clear()
    discount_codes.clear()


def test_checkout_without_discount():
    """Test checkout without discount code."""
    # Add item to cart first
    client.post(
        "/api/cart",
        json={"userId": "user123", "itemId": "item001", "quantity": 1}
    )
    
    # Checkout
    response = client.post(
        "/api/checkout",
        json={"userId": "user123"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Order placed successfully" in data["message"]
    assert data["order"]["userId"] == "user123"
    assert data["order"]["discountCode"] is None
    assert data["order"]["discountAmount"] == 0.0
    assert data["order"]["total"] == data["order"]["subtotal"]
    assert data["newDiscountCode"] is None  # First order, not 5th


def test_checkout_empty_cart():
    """Test checkout with empty cart."""
    response = client.post(
        "/api/checkout",
        json={"userId": "user123"}
    )
    
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_checkout_with_valid_discount():
    """Test checkout with valid discount code."""
    # First, create a discount code manually
    from app.stores.data import add_discount_code, set_available_code
    from datetime import datetime
    
    discount_code_obj = {
        "code": "DISCOUNT1",
        "isUsed": False,
        "usedByOrder": None,
        "createdAt": datetime.now(),
        "usedAt": None
    }
    add_discount_code(discount_code_obj)
    set_available_code("DISCOUNT1")
    
    # Add item to cart
    client.post(
        "/api/cart",
        json={"userId": "user123", "itemId": "item001", "quantity": 1}
    )
    
    # Checkout with discount
    response = client.post(
        "/api/checkout",
        json={"userId": "user123", "discountCode": "DISCOUNT1"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["order"]["discountCode"] == "DISCOUNT1"
    assert data["order"]["discountAmount"] > 0
    assert data["order"]["total"] < data["order"]["subtotal"]
    # Verify discount is 10%
    expected_discount = data["order"]["subtotal"] * 0.10
    assert abs(data["order"]["discountAmount"] - expected_discount) < 0.01


def test_checkout_with_invalid_discount():
    """Test checkout with invalid discount code - should proceed without discount."""
    # Add item to cart
    client.post(
        "/api/cart",
        json={"userId": "user123", "itemId": "item001", "quantity": 1}
    )
    
    # Checkout with invalid discount
    response = client.post(
        "/api/checkout",
        json={"userId": "user123", "discountCode": "INVALID_CODE"}
    )
    
    assert response.status_code == 200  # Still succeeds
    data = response.json()
    assert data["success"] is True
    assert data["order"]["discountCode"] is None
    assert data["order"]["discountAmount"] == 0.0


def test_checkout_with_used_discount():
    """Test checkout with already used discount code - should proceed without discount."""
    # Create and mark discount as used
    from app.stores.data import add_discount_code
    from datetime import datetime
    
    discount_code_obj = {
        "code": "DISCOUNT1",
        "isUsed": True,
        "usedByOrder": "order001",
        "createdAt": datetime.now(),
        "usedAt": datetime.now()
    }
    add_discount_code(discount_code_obj)
    
    # Add item to cart
    client.post(
        "/api/cart",
        json={"userId": "user123", "itemId": "item001", "quantity": 1}
    )
    
    # Checkout with used discount
    response = client.post(
        "/api/checkout",
        json={"userId": "user123", "discountCode": "DISCOUNT1"}
    )
    
    assert response.status_code == 200  # Still succeeds
    data = response.json()
    assert data["success"] is True
    assert data["order"]["discountCode"] is None  # Not applied
    assert data["order"]["discountAmount"] == 0.0


def test_checkout_clears_cart():
    """Test that checkout clears the user's cart."""
    # Add item to cart
    client.post(
        "/api/cart",
        json={"userId": "user123", "itemId": "item001", "quantity": 1}
    )
    
    # Verify cart exists
    from app.stores.data import get_cart
    assert get_cart("user123") is not None
    
    # Checkout
    response = client.post(
        "/api/checkout",
        json={"userId": "user123"}
    )
    
    assert response.status_code == 200
    
    # Verify cart is cleared
    assert get_cart("user123") is None


def test_checkout_generates_discount_on_nth_order():
    """Test that checkout generates discount code on nth order (5th order)."""
    # Place 4 orders first
    for i in range(4):
        user_id = f"user{i}"
        client.post(
            "/api/cart",
            json={"userId": user_id, "itemId": "item001", "quantity": 1}
        )
        client.post(
            "/api/checkout",
            json={"userId": user_id}
        )
    
    # Verify order count is 4
    from app.stores.data import get_order_count
    assert get_order_count() == 4
    
    # Place 5th order
    client.post(
        "/api/cart",
        json={"userId": "user5", "itemId": "item001", "quantity": 1}
    )
    response = client.post(
        "/api/checkout",
        json={"userId": "user5"}
    )
    
    assert response.status_code == 200
    data = response.json()
    # Should generate new discount code
    assert data["newDiscountCode"] is not None
    assert data["newDiscountCode"].startswith("DISCOUNT")
    assert "generated" in data["message"].lower()


def test_checkout_multiple_items():
    """Test checkout with multiple items in cart."""
    # Add multiple items
    client.post(
        "/api/cart",
        json={"userId": "user123", "itemId": "item001", "quantity": 2}
    )
    client.post(
        "/api/cart",
        json={"userId": "user123", "itemId": "item002", "quantity": 3}
    )
    
    # Checkout
    response = client.post(
        "/api/checkout",
        json={"userId": "user123"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["order"]["items"]) == 2
    # Verify totals
    expected_subtotal = (999.99 * 2) + (29.99 * 3)
    assert abs(data["order"]["subtotal"] - expected_subtotal) < 0.01


def test_checkout_discount_calculation():
    """Test that discount is calculated correctly (10% of subtotal)."""
    # Create discount code
    from app.stores.data import add_discount_code, set_available_code
    from datetime import datetime
    
    discount_code_obj = {
        "code": "DISCOUNT1",
        "isUsed": False,
        "usedByOrder": None,
        "createdAt": datetime.now(),
        "usedAt": None
    }
    add_discount_code(discount_code_obj)
    set_available_code("DISCOUNT1")
    
    # Add item with known price
    client.post(
        "/api/cart",
        json={"userId": "user123", "itemId": "item001", "quantity": 1}
    )
    
    # Checkout with discount
    response = client.post(
        "/api/checkout",
        json={"userId": "user123", "discountCode": "DISCOUNT1"}
    )
    
    assert response.status_code == 200
    data = response.json()
    subtotal = data["order"]["subtotal"]
    discount = data["order"]["discountAmount"]
    total = data["order"]["total"]
    
    # Verify 10% discount
    expected_discount = round(subtotal * 0.10, 2)
    assert abs(discount - expected_discount) < 0.01
    assert abs(total - (subtotal - discount)) < 0.01
