"""
Main FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    from app.stores.data import initialize_dummy_data
    initialize_dummy_data()
    yield
    # Shutdown (if needed in future)

# Initialize FastAPI app
app = FastAPI(
    title="Discount Cart API",
    description="Ecommerce store with discount code functionality",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
def root():
    """Root endpoint to verify API is running."""
    return {
        "message": "Discount Cart API is running",
        "version": "1.0.0"
    }

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Include routers
from app.routes import cart, checkout, admin
app.include_router(cart.router, prefix="/api", tags=["Cart"])
app.include_router(checkout.router, prefix="/api", tags=["Checkout"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
