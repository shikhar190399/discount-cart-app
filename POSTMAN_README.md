# API Testing Guide

This directory contains API testing files for the Discount Cart API.

## Files Included

1. **postman_collection.json** - Postman collection file
2. **api_requests.http** - REST Client file (for VS Code REST Client extension)

## Using Postman Collection

### Import into Postman

1. Open Postman
2. Click **Import** button (top left)
3. Select `postman_collection.json`
4. Collection will be imported with all endpoints

### Setting Up Environment Variable

1. In Postman, click on the collection
2. Go to **Variables** tab
3. Set `base_url` to `http://localhost:8000` (or your server URL)
4. Save the collection

### Available Endpoints

**Customer APIs:**
- Add Item to Cart
- Checkout Without Discount
- Checkout With Discount

**Admin APIs:**
- Generate Discount Code
- Get Statistics

**Utility Endpoints:**
- Health Check
- Root Endpoint

## Using REST Client (VS Code)

### Installation

1. Install VS Code REST Client extension
2. Open `api_requests.http` file
3. Click "Send Request" above each request

### Features

- Pre-configured base URL
- Example requests for all endpoints
- Complete workflow examples
- Edge case testing examples

## Quick Start

### 1. Start the Server

```bash
uvicorn app.main:app --reload
```

### 2. Test Health Endpoint

```bash
curl http://localhost:8000/health
```

### 3. Add Item to Cart

```bash
curl -X POST http://localhost:8000/api/cart \
  -H "Content-Type: application/json" \
  -d '{"userId": "user123", "itemId": "item001", "quantity": 2}'
```

### 4. Checkout

```bash
curl -X POST http://localhost:8000/api/checkout \
  -H "Content-Type: application/json" \
  -d '{"userId": "user123"}'
```

## Example Workflow

1. **Add items to cart** - Use "Add Item to Cart" endpoint multiple times
2. **Checkout** - Use "Checkout" endpoint (with or without discount code)
3. **View statistics** - Use "Get Statistics" endpoint to see results
4. **Generate discount** - After 5 orders, use "Generate Discount Code" or it auto-generates

## Available Items

The API comes with 6 dummy items:
- `item001` - Laptop ($999.99)
- `item002` - Mouse ($29.99)
- `item003` - Keyboard ($79.99)
- `item004` - Monitor ($299.99)
- `item005` - Headphones ($149.99)
- `item006` - Webcam ($89.99)

## Notes

- All data is in-memory (lost on server restart)
- Discount codes are generated every 5th order
- Invalid discount codes don't prevent checkout
- Cart is cleared after successful checkout
