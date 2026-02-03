# Discount Cart API

An ecommerce store backend with discount code functionality built with FastAPI.

## Features

- Add items to cart
- Checkout with discount code validation
- Automatic discount code generation (every nth order)
- Admin APIs for discount code management and statistics

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
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Customer APIs
- `POST /api/cart` - Add item to cart
- `POST /api/checkout` - Place order with optional discount code

### Admin APIs
- `POST /api/admin/generate-discount` - Generate discount code (if condition met)
- `GET /api/admin/stats` - Get store statistics

## Testing

Run tests with pytest:

```bash
pytest
```

## Project Structure

```
/discount-cart
  /app
    main.py           # FastAPI entry point
    config.py         # Configuration
    /models           # Pydantic schemas
    /stores           # In-memory data stores
    /services         # Business logic
    /routes           # API routes
  /tests              # Test files
  requirements.txt
  README.md
```

## Configuration

Edit `app/config.py` to change:
- `NTH_ORDER`: Every nth order generates a discount code (default: 5)
- `DISCOUNT_PERCENT`: Discount percentage (default: 10)

## License

MIT
