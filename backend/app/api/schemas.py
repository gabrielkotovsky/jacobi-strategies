"""
API schemas for forecast statistics endpoints.
"""

from pydantic import BaseModel, Field, validator, ConfigDict
from typing import List, Optional, Dict, Any, Union
import numpy as np

class ForecastStatisticRequest(BaseModel):
    """Base request model for forecast statistics."""
    
    weights: List[float] = Field(
        ..., description="Portfolio weights (must sum to 1.0)", min_length=25, max_length=25
    )
    periods_per_year: float = Field(1.0, description="Number of periods per year for annualization")
    aggregation: str = Field("mean", description="Aggregation method across simulations: 'mean' or 'median'")
    rebalance: str = Field("periodic", description="Rebalancing strategy: 'periodic' or 'none'")
    initial_value: Optional[float] = Field(100000.0, description="Initial portfolio value for projections")
    include_categories: Optional[List[str]] = Field(None, description="Asset categories to include")
    exclude_categories: Optional[List[str]] = Field(None, description="Asset categories to exclude")

    # Improve OpenAPI example
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "weights": [0.04] * 25,
                    "periods_per_year": 1.0,
                    "aggregation": "mean",
                    "rebalance": "periodic",
                    "initial_value": 100000.0,
                    "include_categories": ["Equity"],
                    "exclude_categories": None
                }
            ]
        }
    )
    
    @validator('weights')
    def validate_weights(cls, v):
        """Validate portfolio weights."""
        if not v:
            raise ValueError("Weights cannot be empty")
        
        # Check if weights are numeric and finite
        if not all(isinstance(w, (int, float)) for w in v):
            raise ValueError("All weights must be numeric")
        
        if not all(np.isfinite(w) for w in v):
            raise ValueError("All weights must be finite")
        
        # Check if weights are non-negative
        if any(w < 0 for w in v):
            raise ValueError("All weights must be non-negative")
        
        # Check if weights sum to 1.0 (with tolerance)
        weight_sum = sum(v)
        if not np.isclose(weight_sum, 1.0, atol=1e-6):
            raise ValueError(f"Weights must sum to 1.0, got {weight_sum:.6f}")
        
        return v
    
    @validator('periods_per_year')
    def validate_periods_per_year(cls, v):
        """Validate periods per year."""
        if v <= 0:
            raise ValueError("periods_per_year must be positive")
        if not np.isfinite(v):
            raise ValueError("periods_per_year must be finite")
        return v
    
    @validator('aggregation')
    def validate_aggregation(cls, v):
        """Validate aggregation method."""
        if v not in ["mean", "median"]:
            raise ValueError("aggregation must be 'mean' or 'median'")
        return v
    
    @validator('rebalance')
    def validate_rebalance(cls, v):
        """Validate rebalancing strategy."""
        if v not in ["periodic", "none"]:
            raise ValueError("rebalance must be 'periodic' or 'none'")
        return v

    @validator('include_categories', 'exclude_categories')
    def validate_category_lists(cls, v):
        if v is None:
            return v
        if not isinstance(v, list):
            raise ValueError("category filters must be lists")
        if len(v) == 0:
            raise ValueError("category filter lists cannot be empty")
        if not all(isinstance(x, str) for x in v):
            raise ValueError("all category names must be strings")
        return v

    @validator('exclude_categories')
    def validate_category_conflicts(cls, v, values):
        if v is None:
            return v
        include = values.get('include_categories')
        if include is not None and set(include) & set(v):
            raise ValueError("Cannot have overlapping categories in include_categories and exclude_categories")
        return v

class RiskFreeRateRequest(ForecastStatisticRequest):
    """Request model for statistics requiring risk-free rate."""
    
    risk_free_rate: float = Field(0.0, description="Annual risk-free rate")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "weights": [0.04] * 25,
                    "periods_per_year": 1.0,
                    "aggregation": "mean",
                    "rebalance": "periodic",
                    "risk_free_rate": 0.02,
                    "include_categories": None,
                    "exclude_categories": None
                }
            ]
        }
    )
    
    @validator('risk_free_rate')
    def validate_risk_free_rate(cls, v):
        """Validate risk-free rate."""
        if not np.isfinite(v):
            raise ValueError("risk_free_rate must be finite")
        return v

class MinimumAcceptableReturnRequest(ForecastStatisticRequest):
    """Request model for statistics requiring minimum acceptable return."""
    
    minimum_acceptable_return: float = Field(0.0, description="Minimum acceptable return threshold")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "weights": [0.04] * 25,
                    "periods_per_year": 1.0,
                    "aggregation": "mean",
                    "rebalance": "periodic",
                    "minimum_acceptable_return": 0.0,
                    "include_categories": None,
                    "exclude_categories": None
                }
            ]
        }
    )
    
    @validator('minimum_acceptable_return')
    def validate_minimum_acceptable_return(cls, v):
        """Validate minimum acceptable return."""
        if not np.isfinite(v):
            raise ValueError("minimum_acceptable_return must be finite")
        return v

class ConfidenceRequest(ForecastStatisticRequest):
    """Request model for statistics requiring confidence level."""
    
    confidence: float = Field(0.95, description="Confidence level (0 < confidence < 1)")
    var_type: str = Field("pooled", description="VaR calculation method: 'pooled', 'year_by_year', or 'cumulative'")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "weights": [0.04] * 25,
                    "periods_per_year": 1.0,
                    "aggregation": "mean",
                    "rebalance": "periodic",
                    "confidence": 0.95,
                    "var_type": "pooled",
                    "include_categories": None,
                    "exclude_categories": None
                }
            ]
        }
    )
    
    @validator('confidence')
    def validate_confidence(cls, v):
        """Validate confidence level."""
        if not 0 < v < 1:
            raise ValueError("confidence must be between 0 and 1")
        return v

class AssetMetricsRequest(BaseModel):
    """Request model for asset-level metrics calculation."""
    
    weights: List[float] = Field(
        ..., description="Portfolio weights (must sum to 1.0)", min_length=25, max_length=25
    )
    periods_per_year: float = Field(1.0, description="Number of periods per year for annualization")
    is_log: bool = Field(False, description="Whether returns are log returns (True) or simple returns (False)")
    aggregation: str = Field("pooled", description="Aggregation method: 'pooled', 'year_by_year', or 'simulation_by_simulation'")
    corr_method: str = Field("pooled", description="Correlation method: 'pooled', 'year_by_year', or 'simulation_by_simulation'")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "weights": [0.04] * 25,
                    "periods_per_year": 1.0,
                    "is_log": False,
                    "aggregation": "pooled",
                    "corr_method": "pooled"
                }
            ]
        }
    )
    
    @validator('periods_per_year')
    def validate_periods_per_year(cls, v):
        """Validate periods per year."""
        if v <= 0:
            raise ValueError("periods_per_year must be positive")
        if not np.isfinite(v):
            raise ValueError("periods_per_year must be finite")
        return v
    
    @validator('aggregation')
    def validate_aggregation(cls, v):
        """Validate aggregation method."""
        if v not in ["pooled", "year_by_year", "simulation_by_simulation"]:
            raise ValueError("aggregation must be 'pooled', 'year_by_year', or 'simulation_by_simulation'")
        return v
    
    @validator('corr_method')
    def validate_corr_method(cls, v):
        """Validate correlation method."""
        if v not in ["pooled", "year_by_year", "simulation_by_simulation"]:
            raise ValueError("corr_method must be 'pooled', 'year_by_year', or 'simulation_by_simulation'")
        return v

class TrackingErrorRequest(ForecastStatisticRequest):
    """Request model for tracking error calculation."""
    
    benchmark_weights: List[float] = Field(
        ..., description="Benchmark portfolio weights", min_length=25, max_length=25
    )
    
    @validator('benchmark_weights')
    def validate_benchmark_weights(cls, v):
        """Validate benchmark weights."""
        if not v:
            raise ValueError("Benchmark weights cannot be empty")
        
        # Check if weights are numeric and finite
        if not all(isinstance(w, (int, float)) for w in v):
            raise ValueError("All benchmark weights must be numeric")
        
        if not all(np.isfinite(w) for w in v):
            raise ValueError("All benchmark weights must be finite")
        
        # Check if weights are non-negative
        if any(w < 0 for w in v):
            raise ValueError("All benchmark weights must be non-negative")
        
        # Check if weights sum to 1.0 (with tolerance)
        weight_sum = sum(v)
        if not np.isclose(weight_sum, 1.0, atol=1e-6):
            raise ValueError(f"Benchmark weights must sum to 1.0, got {weight_sum:.6f}")
        
        return v

class ForecastStatisticResponse(BaseModel):
    """Response model for forecast statistics."""
    
    value: Union[float, List[float]] = Field(..., description="Calculated statistic value (float for single value, list for time series)")
    method: str = Field(..., description="Method used for calculation")
    params: Dict[str, Any] = Field(..., description="Parameters used in calculation")
    n_assets_used: int = Field(..., description="Number of assets used in calculation")
    timesteps: int = Field(20, description="Number of time periods")
    simulations: int = Field(10000, description="Number of Monte Carlo simulations")
    aggregation: str = Field("mean_across_simulations", description="Aggregation method used")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "value": 0.0685,
                "method": "Compound Annual Growth Rate (CAGR)",
                "params": {
                    "weights": [0.04, 0.04, 0.04, 0.04, 0.04],
                    "periods_per_year": 1.0,
                    "include_categories": None,
                    "exclude_categories": None
                },
                "n_assets_used": 25,
                "timesteps": 20,
                "simulations": 10000
            }
        }
    )
