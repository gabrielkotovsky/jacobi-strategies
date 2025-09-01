from pydantic import BaseModel, Field, validator
from typing import List, Literal, Optional
import numpy as np

class BaseInputs(BaseModel):
    """
    Global schema for portfolio analysis inputs.
    
    Attributes:
        weights: Portfolio weights for assets (default: equal-weight)
        rfr: Risk-free rate for Sharpe ratio calculations (unconstrained)
        mar: Minimum acceptable return for downside deviation (unconstrained)
        confidence: Confidence level for VaR/CVaR calculations (0.0 to 1.0, exclusive)
        var_tail: Tail for VaR/CVaR calculations (left/right, optional)
        benchmark_weights: Benchmark weights for tracking error (required if needed)
        rebalance: Rebalancing strategy for multi-period analysis
        include_categories: Asset categories to include (optional)
        exclude_categories: Asset categories to exclude (optional)
        periods_per_year: Number of periods per year for annualization
    """
    
    weights: Optional[List[float]] = Field(
        default=None,
        description="Portfolio weights for assets. If omitted, equal-weight portfolio is used."
    )
    
    rfr: float = Field(
        default=0.0,
        description="Risk-free rate for Sharpe ratio calculations (unconstrained finite float)"
    )
    
    mar: float = Field(
        default=0.0,
        description="Minimum acceptable return for downside deviation calculations (unconstrained finite float)"
    )
    
    confidence: float = Field(
        default=0.95,
        description="Confidence level for VaR/CVaR calculations (0.0 to 1.0, exclusive)",
        gt=0.0,
        lt=1.0
    )
    
    var_tail: Optional[Literal["left", "right"]] = Field(
        default="left",
        description="Tail for VaR/CVaR calculations: 'left' for loss tail (default), 'right' for gain tail"
    )
    
    benchmark_weights: Optional[List[float]] = Field(
        default=None,
        description="Benchmark weights for tracking error calculations (required if tracking error needed)"
    )
    
    rebalance: Literal["none", "periodic"] = Field(
        default="periodic",
        description="Rebalancing strategy: 'none' for buy-and-hold, 'periodic' for rebalancing each period"
    )
    
    # Category filtering for convenience
    include_categories: Optional[List[str]] = Field(
        default=None,
        description="Asset categories to include in analysis (if None, all categories included)"
    )
    
    exclude_categories: Optional[List[str]] = Field(
        default=None,
        description="Asset categories to exclude from analysis (if None, no categories excluded)"
    )
    
    # Time period configuration
    periods_per_year: float = Field(
        default=1.0,
        description="Number of periods per year for annualization (default: 1 for annual data)",
        gt=0.0
    )
    
    # Class variable to store the expected asset count
    _expected_asset_count: Optional[int] = None
    
    @classmethod
    def set_asset_count(cls, asset_count: int) -> None:
        """
        Set the expected number of assets for validation.
        This should be called after loading the data files.
        
        Args:
            asset_count: Number of assets in the portfolio
        """
        if asset_count <= 0:
            raise ValueError(f"Asset count must be positive, got {asset_count}")
        cls._expected_asset_count = asset_count
    
    @classmethod
    def get_asset_count(cls) -> Optional[int]:
        """
        Get the expected number of assets.
        
        Returns:
            Expected asset count or None if not set
        """
        return cls._expected_asset_count
    
    @validator('weights')
    def validate_weights(cls, v):
        """Validate portfolio weights if provided."""
        if v is not None:
            if cls._expected_asset_count is None:
                raise ValueError("Asset count not set. Call BaseInputs.set_asset_count() after loading data.")
            
            # Check length
            if len(v) != cls._expected_asset_count:
                raise ValueError(f"Portfolio weights must have exactly {cls._expected_asset_count} elements, got {len(v)}")
            
            # Check for numeric, finite, no NaNs
            if not all(isinstance(w, (int, float)) for w in v):
                raise ValueError("All portfolio weights must be numeric")
            
            if not all(np.isfinite(w) for w in v):
                raise ValueError("All portfolio weights must be finite (no inf, -inf, or NaN)")
            
            # Check for negative weights
            if any(w < 0 for w in v):
                raise ValueError("Portfolio weights cannot be negative")
            
            # Check if weights sum to approximately 1.0 (allowing for floating point precision)
            weight_sum = sum(v)
            if not np.isclose(weight_sum, 1.0, atol=1e-6):
                # Option 1: Strict validation (current behavior)
                raise ValueError(f"Portfolio weights must sum to 1.0, got {weight_sum:.6f}")
                
                # Option 2: Auto-normalization (uncomment to enable)
                # logger.warning(f"Weights sum to {weight_sum:.6f}, normalizing to 1.0")
                # v = [w / weight_sum for w in v]
        
        return v
    
    @validator('benchmark_weights')
    def validate_benchmark_weights(cls, v):
        """Validate benchmark weights if provided."""
        if v is not None:
            if cls._expected_asset_count is None:
                raise ValueError("Asset count not set. Call BaseInputs.set_asset_count() after loading data.")
            
            # Check length
            if len(v) != cls._expected_asset_count:
                raise ValueError(f"Benchmark weights must have exactly {cls._expected_asset_count} elements, got {len(v)}")
            
            # Check for numeric, finite, no NaNs
            if not all(isinstance(w, (int, float)) for w in v):
                raise ValueError("All benchmark weights must be numeric")
            
            if not all(np.isfinite(w) for w in v):
                raise ValueError("All benchmark weights must be finite (no inf, -inf, or NaN)")
            
            # Check for negative weights
            if any(w < 0 for w in v):
                raise ValueError("Benchmark weights cannot be negative")
            
            # Check if weights sum to approximately 1.0
            weight_sum = sum(v)
            if not np.isclose(weight_sum, 1.0, atol=1e-6):
                raise ValueError(f"Benchmark weights must sum to 1.0, got {weight_sum:.6f}")
        
        return v
    
    def get_weights(self) -> List[float]:
        """
        Get portfolio weights, returning equal-weight if not specified.
        
        Returns:
            List of portfolio weights that sum to 1.0
        """
        if self.weights is not None:
            return self.weights
        
        # Return equal-weight portfolio based on actual asset count
        if self._expected_asset_count is None:
            raise ValueError("Asset count not set. Call BaseInputs.set_asset_count() after loading data.")
        
        return [1.0 / self._expected_asset_count] * self._expected_asset_count
    
    def get_benchmark_weights(self) -> Optional[List[float]]:
        """
        Get benchmark weights if provided.
        
        Returns:
            Benchmark weights or None if not provided
        """
        return self.benchmark_weights
    
    @validator('include_categories', 'exclude_categories')
    def validate_category_filters(cls, v):
        """Validate category filter lists."""
        if v is not None:
            if not isinstance(v, list):
                raise ValueError("Category filters must be lists")
            if not all(isinstance(cat, str) for cat in v):
                raise ValueError("All category names must be strings")
            if len(v) == 0:
                raise ValueError("Category filter lists cannot be empty")
        return v
    
    @validator('exclude_categories')
    def validate_category_conflicts(cls, v, values):
        """Validate that include and exclude categories don't conflict."""
        if v is not None and 'include_categories' in values and values['include_categories'] is not None:
            include_set = set(values['include_categories'])
            exclude_set = set(v)
            if include_set & exclude_set:  # Check for intersection
                raise ValueError("Cannot have overlapping categories in include_categories and exclude_categories")
        return v
    

    
    class Config:
        """Pydantic configuration."""
        # Allow numpy arrays and other numeric types
        arbitrary_types_allowed = True
        # Validate assignment
        validate_assignment = True
        # Extra fields not allowed
        extra = "forbid"
        # Use enum values for validation
        use_enum_values = True

class PortfolioRequest(BaseInputs):
    """
    Extended schema for portfolio analysis requests.
    Inherits from BaseInputs and can be extended with additional fields.
    """
    
    portfolio_name: Optional[str] = Field(
        default=None,
        description="Optional name for the portfolio analysis"
    )
    
    description: Optional[str] = Field(
        default=None,
        description="Optional description of the portfolio strategy"
    )

class BatchPortfolioRequest(BaseModel):
    """
    Schema for batch portfolio analysis requests.
    """
    
    portfolios: List[PortfolioRequest] = Field(
        description="List of portfolio requests to analyze"
    )
    
    @validator('portfolios')
    def validate_portfolios(cls, v):
        """Validate that at least one portfolio is provided."""
        if not v:
            raise ValueError("At least one portfolio must be provided")
        if len(v) > 100:  # Reasonable limit for batch processing
            raise ValueError("Maximum of 100 portfolios allowed in batch request")
        return v



