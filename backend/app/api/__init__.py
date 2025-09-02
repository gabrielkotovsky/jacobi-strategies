"""
Portfolio Analysis API Module

This module contains the FastAPI routes, schemas, and logic for portfolio analysis endpoints.
"""

from .routes import router
from .schemas import (
    ForecastStatisticRequest,
    RiskFreeRateRequest,
    MinimumAcceptableReturnRequest,
    ConfidenceRequest,
    TrackingErrorRequest,
    ForecastStatisticResponse
)
from .logic import (
    build_portfolio_returns,
    build_benchmark_returns,
    get_calculation_params
)

__all__ = [
    # Router
    "router",
    
    # Request schemas
    "ForecastStatisticRequest",
    "RiskFreeRateRequest", 
    "MinimumAcceptableReturnRequest",
    "ConfidenceRequest",
    "TrackingErrorRequest",
    
    # Response schemas
    "ForecastStatisticResponse",
    
    # Logic functions
    "build_portfolio_returns",
    "build_benchmark_returns",
    "get_calculation_params"
]
