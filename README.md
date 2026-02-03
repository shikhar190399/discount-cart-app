# Discount Cart API

An ecommerce store backend with discount code functionality built with FastAPI.

## Features

- ✅ Add items to cart
- ✅ Checkout with discount code validation
- ✅ Automatic discount code generation (every nth order)
- ✅ Admin APIs for discount code management and statistics
- ✅ Comprehensive test coverage

## Setup

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, you can access:
- **Swagger UI**: `http://localhost:8000/docs` (Interactive API documentation)
- **ReDoc**: `http://localhost:8000/redoc` (Alternative documentation)

## API Endpoints

### Customer APIs

#### 1. Add Item to Cart

**POST** `/api/cart`

Add an item to the user's cart. If the item already exists, the quantity is increased.

**Request:**
```json
{
  "userId": "user123",
  "itemId": "item001",
  "quantity": 2
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Item added to cart successfully",
  "cart": {
    "userId": "user123",
    "items": [
      {
        "itemId": "item001",
        "name": "Laptop",
        "price": 999.99,
        "quantity": 2,
        "subtotal": 1999.98
      }
    ],
    "subtotal": 1999.98,
    "discountCode": null,
    "discountAmount": 0.0,
    "total": 1999.98
  }
}
```

**Error Responses:**
- `404`: Item not found
- `422`: Validation error (invalid quantity, missing fields)

#### 2. Checkout

**POST** `/api/checkout`

Place an order from the user's cart. Validates and applies discount code if provided. If discount code is invalid, order proceeds without discount.

**Request:**
```json
{
  "userId": "user123",
  "discountCode": "DISCOUNT1"  // optional
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Order placed successfully. New discount code 'DISCOUNT1' generated!",
  "order": {
    "orderId": "order001",
    "userId": "user123",
    "items": [
      {
        "itemId": "item001",
        "name": "Laptop",
        "price": 999.99,
        "quantity": 2,
        "subtotal": 1999.98
      }
    ],
    "subtotal": 1999.98,
    "discountCode": "DISCOUNT1",
    "discountAmount": 199.98,
    "total": 1800.00,
    "createdAt": "2026-02-03T17:47:04.961952"
  },
  "newDiscountCode": "DISCOUNT1"  // null if not nth order
}
```

**Error Responses:**
- `400`: Cart is empty

**Business Logic:**
- Discount code is validated before applying
- If invalid, order proceeds without discount (no error)
- Every 5th order automatically generates a new discount code
- Cart is cleared after successful checkout

### Admin APIs

#### 3. Generate Discount Code

**POST** `/api/admin/generate-discount`

Manually generate a discount code if the nth order condition is met (order count divisible by 5).

**Request:** None (empty body)

**Response - Success (200 OK):**
```json
{
  "success": true,
  "message": "Discount code generated successfully",
  "code": "DISCOUNT1",
  "currentOrderCount": 5,
  "nextDiscountAt": 10,
  "ordersRemaining": null
}
```

**Response - Condition Not Met (200 OK):**
```json
{
  "success": false,
  "message": "Discount code cannot be generated yet",
  "code": null,
  "currentOrderCount": 3,
  "nextDiscountAt": 5,
  "ordersRemaining": 2
}
```

**Response - Code Already Exists (200 OK):**
```json
{
  "success": false,
  "message": "Unused discount code 'DISCOUNT1' already exists",
  "code": "DISCOUNT1",
  "currentOrderCount": 5,
  "nextDiscountAt": 10,
  "ordersRemaining": null
}
```

#### 4. Get Statistics

**GET** `/api/admin/stats`

Get comprehensive store statistics including total items purchased, revenue, discount codes, and discount amounts.

**Request:** None

**Response (200 OK):**
```json
{
  "success": true,
  "statistics": {
    "totalItemsPurchased": 45,
    "totalPurchaseAmount": 1250.50,
    "discountCodes": [
      {
        "code": "DISCOUNT1",
        "isUsed": true,
        "usedByOrder": "order006",
        "createdAt": "2026-02-03T10:00:00",
        "usedAt": "2026-02-03T14:30:00"
      },
      {
        "code": "DISCOUNT2",
        "isUsed": false,
        "usedByOrder": null,
        "createdAt": "2026-02-03T15:00:00",
        "usedAt": null
      }
    ],
    "totalDiscountAmount": 125.05
  }
}
```

## Testing

Run all tests:
```bash
pytest
```

Run tests with verbose output:
```bash
pytest -v
```

Run specific test file:
```bash
pytest tests/test_cart.py
```

**Test Coverage:**
- ✅ Cart API tests (7 tests)
- ✅ Checkout API tests (9 tests)
- ✅ Admin API tests (8 tests)
- **Total: 24 tests, all passing**

## Project Structure

```
/discount-cart
  /app
    main.py              # FastAPI entry point
    config.py            # Configuration constants
    /models
      schemas.py         # Pydantic request/response models
    /stores
      data.py            # In-memory data stores
    /services
      cart_service.py    # Cart business logic
      checkout_service.py # Checkout business logic
      admin_service.py   # Admin business logic
    /routes
      cart.py            # Cart API routes
      checkout.py        # Checkout API routes
      admin.py           # Admin API routes
  /tests
    test_cart.py         # Cart API tests
    test_checkout.py     # Checkout API tests
    test_admin.py        # Admin API tests
  requirements.txt       # Python dependencies
  README.md             # This file
```

## Configuration

Edit `app/config.py` to customize:

- **NTH_ORDER** (default: 5): Every nth order generates a discount code
- **DISCOUNT_PERCENT** (default: 10): Discount percentage applied
- **DISCOUNT_CODE_PREFIX** (default: "DISCOUNT"): Prefix for discount codes

## Business Rules

### Discount Code System

1. **Generation**: Discount codes are automatically generated on every 5th order (configurable via `NTH_ORDER`)
2. **Availability**: Only one discount code is available at a time
3. **Usage**: Each discount code can be used only once
4. **Application**: Discount applies to the entire order (10% off total)
5. **Validation**: Invalid discount codes don't prevent checkout - order proceeds without discount

### Cart Management

- Carts are stored per user (identified by `userId`)
- Adding the same item increases quantity
- Cart persists until checkout
- Cart is automatically cleared after successful checkout

### Order Processing

- Orders contain price snapshots (prices fixed at checkout time)
- Order count increments globally (not per user)
- Discount codes are global (any user can use available code)

## Example Usage Flow

1. **Add items to cart:**
   ```bash
   curl -X POST http://localhost:8000/api/cart \
     -H "Content-Type: application/json" \
     -d '{"userId": "user123", "itemId": "item001", "quantity": 2}'
   ```

2. **Checkout with discount:**
   ```bash
   curl -X POST http://localhost:8000/api/checkout \
     -H "Content-Type: application/json" \
     -d '{"userId": "user123", "discountCode": "DISCOUNT1"}'
   ```

3. **View statistics (admin):**
   ```bash
   curl http://localhost:8000/api/admin/stats
   ```

## Dummy Data

The application initializes with 6 dummy products:
- item001: Laptop ($999.99)
- item002: Mouse ($29.99)
- item003: Keyboard ($79.99)
- item004: Monitor ($299.99)
- item005: Headphones ($149.99)
- item006: Webcam ($89.99)

## Notes

- **In-memory storage**: All data is stored in memory and lost on server restart
- **No authentication**: User identification via `userId` string (no auth required)
- **No database**: Designed for demonstration purposes with in-memory storage