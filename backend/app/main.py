"""
FastAPI application for portfolio analysis API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.routes import router as forecast_router
from app.data.loader import initialize_cache

# Create FastAPI app
app = FastAPI(
    title="Portfolio Analysis API",
    description="API for portfolio statistics and risk metrics using Monte Carlo simulations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize data cache on startup."""
    try:
        print("🚀 Initializing portfolio analysis API...")
        print("📊 Loading Monte Carlo simulation data...")
        
        # Initialize data cache
        initialize_cache("../data/base_simulation.hdf5", "../data/asset_categories.csv")
        
        print("✅ Data loaded successfully!")
        print("🎯 API ready for portfolio analysis requests!")
        
    except Exception as e:
        print(f"❌ Error during startup: {e}")
        raise

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Portfolio Analysis API",
        "version": "1.0.0",
        "description": "API for portfolio statistics and risk metrics",
        "endpoints": {
            "assets": "/forecast_statistic/assets",
            "forecast_statistics": "/forecast_statistic/*",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Portfolio Analysis API is running"}

# Include the forecast statistics router
app.include_router(
    forecast_router,
    prefix="/forecast_statistic",
    tags=["forecast_statistics"]
)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )



 