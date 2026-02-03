"""
Tests for cart API.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.stores.data import initialize_dummy_data, carts, clear_cart

# Initialize test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Setup: Initialize dummy data before each test. Teardown: Clear carts after each test."""
    initialize_dummy_data()
    yield
    # Teardown: Clear all carts after each test
    carts.clear()


def test_add_item_to_cart_success():
    """Test adding a valid item to cart."""
    response = client.post(
        "/api/cart",
        json={
            "userId": "user123",
            "itemId": "item001",
            "quantity": 2
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Item added to cart successfully"
    assert data["cart"]["userId"] == "user123"
    assert len(data["cart"]["items"]) == 1
    assert data["cart"]["items"][0]["itemId"] == "item001"
    assert data["cart"]["items"][0]["quantity"] == 2
    assert data["cart"]["items"][0]["name"] == "Laptop"
    assert data["cart"]["items"][0]["price"] == 999.99
    assert data["cart"]["subtotal"] == 1999.98  # 2 * 999.99
    assert data["cart"]["total"] == 1999.98


def test_add_item_to_cart_invalid_item():
    """Test adding a non-existent item to cart."""
    response = client.post(
        "/api/cart",
        json={
            "userId": "user123",
            "itemId": "invalid_item",
            "quantity": 1
        }
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_add_item_to_cart_multiple_items():
    """Test adding multiple different items to cart."""
    # Add first item
    response1 = client.post(
        "/api/cart",
        json={
            "userId": "user123",
            "itemId": "item001",
            "quantity": 1
        }
    )
    assert response1.status_code == 200
    
    # Add second item
    response2 = client.post(
        "/api/cart",
        json={
            "userId": "user123",
            "itemId": "item002",
            "quantity": 2
        }
    )
    
    assert response2.status_code == 200
    data = response2.json()
    assert len(data["cart"]["items"]) == 2
    assert data["cart"]["subtotal"] == pytest.approx(1059.97)  # 999.99 + (29.99 * 2)


def test_add_same_item_increases_quantity():
    """Test that adding the same item increases quantity."""
    # Add item first time
    response1 = client.post(
        "/api/cart",
        json={
            "userId": "user123",
            "itemId": "item001",
            "quantity": 2
        }
    )
    assert response1.status_code == 200
    
    # Add same item again
    response2 = client.post(
        "/api/cart",
        json={
            "userId": "user123",
            "itemId": "item001",
            "quantity": 3
        }
    )
    
    assert response2.status_code == 200
    data = response2.json()
    assert len(data["cart"]["items"]) == 1  # Still one item
    assert data["cart"]["items"][0]["quantity"] == 5  # 2 + 3
    assert data["cart"]["subtotal"] == pytest.approx(4999.95)  # 5 * 999.99


def test_add_item_invalid_quantity():
    """Test adding item with invalid quantity (0 or negative)."""
    response = client.post(
        "/api/cart",
        json={
            "userId": "user123",
            "itemId": "item001",
            "quantity": 0
        }
    )
    
    assert response.status_code == 422  # Validation error


def test_add_item_missing_fields():
    """Test adding item with missing required fields."""
    response = client.post(
        "/api/cart",
        json={
            "userId": "user123"
            # Missing itemId and quantity
        }
    )
    
    assert response.status_code == 422  # Validation error


def test_add_item_different_users():
    """Test that different users have separate carts."""
    # User 1 adds item
    response1 = client.post(
        "/api/cart",
        json={
            "userId": "user1",
            "itemId": "item001",
            "quantity": 1
        }
    )
    assert response1.status_code == 200
    
    # User 2 adds item
    response2 = client.post(
        "/api/cart",
        json={
            "userId": "user2",
            "itemId": "item002",
            "quantity": 1
        }
    )
    assert response2.status_code == 200
    
    # Verify carts are separate
    assert response1.json()["cart"]["userId"] == "user1"
    assert response2.json()["cart"]["userId"] == "user2"
    assert response1.json()["cart"]["items"][0]["itemId"] == "item001"
    assert response2.json()["cart"]["items"][0]["itemId"] == "item002"
