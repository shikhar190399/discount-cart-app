"""
Tests for admin API.
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
    get_order_count,
    increment_order_count
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


def test_generate_discount_condition_met():
    """Test generating discount code when nth order condition is met."""
    # Set order count to 5 (divisible by 5)
    for _ in range(5):
        increment_order_count()
    
    response = client.post("/api/admin/generate-discount")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["code"] is not None
    assert data["code"].startswith("DISCOUNT")
    assert data["currentOrderCount"] == 5
    assert data["nextDiscountAt"] == 10


def test_generate_discount_condition_not_met():
    """Test generating discount code when condition is not met."""
    # Set order count to 3 (not divisible by 5)
    for _ in range(3):
        increment_order_count()
    
    response = client.post("/api/admin/generate-discount")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["code"] is None
    assert data["currentOrderCount"] == 3
    assert data["nextDiscountAt"] == 5
    assert data["ordersRemaining"] == 2


def test_generate_discount_code_already_exists():
    """Test generating discount code when unused code already exists."""
    # Set order count to 5
    for _ in range(5):
        increment_order_count()
    
    # Manually create an unused discount code
    from app.stores.data import add_discount_code, set_available_code
    from datetime import datetime
    
    existing_code = {
        "code": "DISCOUNT1",
        "isUsed": False,
        "usedByOrder": None,
        "createdAt": datetime.now(),
        "usedAt": None
    }
    add_discount_code(existing_code)
    set_available_code("DISCOUNT1")
    
    response = client.post("/api/admin/generate-discount")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "already exists" in data["message"].lower()
    assert data["code"] == "DISCOUNT1"


def test_get_statistics_no_orders():
    """Test getting statistics with no orders."""
    response = client.get("/api/admin/stats")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["statistics"]["totalItemsPurchased"] == 0
    assert data["statistics"]["totalPurchaseAmount"] == 0.0
    assert data["statistics"]["totalDiscountAmount"] == 0.0
    assert len(data["statistics"]["discountCodes"]) == 0


def test_get_statistics_with_orders():
    """Test getting statistics with multiple orders."""
    # Create some orders manually
    from app.stores.data import add_order
    from datetime import datetime
    
    order1 = {
        "orderId": "order001",
        "userId": "user1",
        "items": [
            {"itemId": "item001", "name": "Laptop", "price": 999.99, "quantity": 2, "subtotal": 1999.98}
        ],
        "subtotal": 1999.98,
        "discountCode": None,
        "discountAmount": 0.0,
        "total": 1999.98,
        "createdAt": datetime.now()
    }
    
    order2 = {
        "orderId": "order002",
        "userId": "user2",
        "items": [
            {"itemId": "item002", "name": "Mouse", "price": 29.99, "quantity": 3, "subtotal": 89.97}
        ],
        "subtotal": 89.97,
        "discountCode": "DISCOUNT1",
        "discountAmount": 8.99,
        "total": 80.98,
        "createdAt": datetime.now()
    }
    
    add_order(order1)
    add_order(order2)
    
    response = client.get("/api/admin/stats")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["statistics"]["totalItemsPurchased"] == 5  # 2 + 3
    assert data["statistics"]["totalPurchaseAmount"] == pytest.approx(2080.96)  # 1999.98 + 80.98
    assert data["statistics"]["totalDiscountAmount"] == pytest.approx(8.99)


def test_get_statistics_with_discount_codes():
    """Test getting statistics includes discount codes."""
    # Create discount codes
    from app.stores.data import add_discount_code
    from datetime import datetime
    
    code1 = {
        "code": "DISCOUNT1",
        "isUsed": True,
        "usedByOrder": "order001",
        "createdAt": datetime.now(),
        "usedAt": datetime.now()
    }
    
    code2 = {
        "code": "DISCOUNT2",
        "isUsed": False,
        "usedByOrder": None,
        "createdAt": datetime.now(),
        "usedAt": None
    }
    
    add_discount_code(code1)
    add_discount_code(code2)
    
    response = client.get("/api/admin/stats")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["statistics"]["discountCodes"]) == 2
    assert data["statistics"]["discountCodes"][0]["code"] == "DISCOUNT1"
    assert data["statistics"]["discountCodes"][0]["isUsed"] is True
    assert data["statistics"]["discountCodes"][1]["code"] == "DISCOUNT2"
    assert data["statistics"]["discountCodes"][1]["isUsed"] is False


def test_get_statistics_calculates_correctly():
    """Test that statistics calculations are correct."""
    # Create orders with known values
    from app.stores.data import add_order
    from datetime import datetime
    
    # Order with discount
    order1 = {
        "orderId": "order001",
        "userId": "user1",
        "items": [
            {"itemId": "item001", "name": "Laptop", "price": 100.00, "quantity": 1, "subtotal": 100.00}
        ],
        "subtotal": 100.00,
        "discountCode": "DISCOUNT1",
        "discountAmount": 10.00,  # 10% of 100
        "total": 90.00,
        "createdAt": datetime.now()
    }
    
    # Order without discount
    order2 = {
        "orderId": "order002",
        "userId": "user2",
        "items": [
            {"itemId": "item002", "name": "Mouse", "price": 20.00, "quantity": 2, "subtotal": 40.00}
        ],
        "subtotal": 40.00,
        "discountCode": None,
        "discountAmount": 0.00,
        "total": 40.00,
        "createdAt": datetime.now()
    }
    
    add_order(order1)
    add_order(order2)
    
    response = client.get("/api/admin/stats")
    
    assert response.status_code == 200
    data = response.json()
    # Total items: 1 + 2 = 3
    assert data["statistics"]["totalItemsPurchased"] == 3
    # Total purchase: 90 + 40 = 130
    assert data["statistics"]["totalPurchaseAmount"] == pytest.approx(130.00)
    # Total discount: 10
    assert data["statistics"]["totalDiscountAmount"] == pytest.approx(10.00)


def test_generate_discount_at_10th_order():
    """Test generating discount code at 10th order."""
    # Set order count to 10
    for _ in range(10):
        increment_order_count()
    
    response = client.post("/api/admin/generate-discount")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["code"] is not None
    assert data["currentOrderCount"] == 10
    assert data["nextDiscountAt"] == 15
