"""
API logic helpers for portfolio construction and asset filtering.
"""

import numpy as np
from typing import List, Tuple, Optional
from app.data.loader import get_cached_data
from app.logic.stats import (
    annualised_return,
    annualised_volatility,
    sharpe_ratio,
    tracking_error,
    downside_deviation,
    value_at_risk,
    conditional_value_at_risk,
    maximum_drawdown
)



def build_portfolio_returns(weights: List[float], 
                           rebalance: str = "periodic",
                           include_categories: Optional[List[str]] = None,
                           exclude_categories: Optional[List[str]] = None) -> Tuple[np.ndarray, int]:
    """
    Build portfolio returns using the specified weights.
    
    Args:
        weights: Portfolio weights
        rebalance: Rebalancing strategy ('periodic' or 'none')
    
    Returns:
        Tuple of (portfolio_returns, n_assets_used)
    """
    # Get returns data
    returns, asset_names, asset_categories, asset_index_to_category = get_cached_data()
    
    # Validate weights length
    if len(weights) != len(asset_names):
        raise ValueError(f"Expected {len(asset_names)} weights, got {len(weights)}")
    
    # Convert weights to numpy array and validate
    weights_array = np.array(weights)
    if not np.allclose(np.sum(weights_array), 1.0, atol=1e-6):
        raise ValueError(f"Weights must sum to 1.0, got {np.sum(weights_array):.6f}")
    
    # Apply category filtering by masking assets
    if include_categories or exclude_categories:
        include_set = set(include_categories) if include_categories else None
        exclude_set = set(exclude_categories) if exclude_categories else None
        asset_mask = np.ones(len(asset_names), dtype=bool)
        if include_set is not None:
            asset_mask &= np.array([cat in include_set for cat in asset_categories])
        if exclude_set is not None:
            asset_mask &= np.array([cat not in exclude_set for cat in asset_categories])

        if not np.any(asset_mask):
            raise ValueError("No assets match the specified category filters")

        # Slice weights to included assets only and renormalize
        filtered_weights = weights_array[asset_mask]
        total = filtered_weights.sum()
        if total <= 0:
            raise ValueError("Filtered weights sum to zero after category filtering")
        filtered_weights = filtered_weights / total

        # Filter returns to included assets only for performance
        filtered_returns = returns[asset_mask, :, :]

        from app.services.portfolio import portfolio_period_returns
        portfolio_returns = portfolio_period_returns(filtered_weights, filtered_returns, rebalance)
        n_assets_used = int(asset_mask.sum())
        return portfolio_returns, n_assets_used

    # Calculate portfolio returns using portfolio service with rebalancing (no filtering)
    from app.services.portfolio import portfolio_period_returns
    portfolio_returns = portfolio_period_returns(weights_array, returns, rebalance)
    
    return portfolio_returns, len(asset_names)

def build_benchmark_returns(benchmark_weights: List[float]) -> np.ndarray:
    """
    Build benchmark returns using the specified weights.
    
    Args:
        benchmark_weights: Benchmark portfolio weights
    
    Returns:
        Benchmark portfolio returns
    """
    # Get returns data
    returns, asset_names, asset_categories, asset_index_to_category = get_cached_data()
    
    # Validate weights length
    if len(benchmark_weights) != len(asset_names):
        raise ValueError(f"Expected {len(asset_names)} benchmark weights, got {len(benchmark_weights)}")
    
    # Convert weights to numpy array and validate
    weights_array = np.array(benchmark_weights)
    if not np.allclose(np.sum(weights_array), 1.0, atol=1e-6):
        raise ValueError(f"Benchmark weights must sum to 1.0, got {np.sum(weights_array):.6f}")
    
    # Calculate benchmark returns using einsum
    benchmark_returns = np.einsum('a,ats->ts', weights_array, returns)
    
    return benchmark_returns

def get_calculation_params(weights: List[float],
                          periods_per_year: float = 1.0,
                          aggregation: str = "mean",
                          var_type: str = "pooled",
                          rebalance: str = "periodic",
                          include_categories: Optional[List[str]] = None,
                          exclude_categories: Optional[List[str]] = None,
                          **kwargs) -> dict:
    """
    Get parameters used in calculation for response.
    
    Args:
        weights: Portfolio weights
        periods_per_year: Periods per year
        aggregation: Aggregation method
        var_type: VaR calculation type
        rebalance: Rebalancing strategy
        **kwargs: Additional parameters
    
    Returns:
        Dictionary of calculation parameters
    """
    params = {
        "weights": weights,
        "periods_per_year": periods_per_year,
        "aggregation": aggregation,
        "rebalance": rebalance,
        "var_type": var_type,
        "include_categories": include_categories,
        "exclude_categories": exclude_categories
    }
    
    # Add additional parameters
    for key, value in kwargs.items():
        if value is not None:
            params[key] = value
    
    return params
