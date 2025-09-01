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

def get_asset_mask(include_categories: Optional[List[str]] = None, 
                   exclude_categories: Optional[List[str]] = None) -> np.ndarray:
    """
    Get asset mask based on category filters.
    
    Args:
        include_categories: List of categories to include (None = all)
        exclude_categories: List of categories to exclude (None = none)
    
    Returns:
        Boolean mask array indicating which assets to use
    """
    try:
        returns, asset_names, asset_categories, asset_index_to_category = get_cached_data()
    except RuntimeError:
        raise RuntimeError("Data cache not initialized. Please restart the API.")
    
    n_assets = len(asset_names)
    asset_mask = np.ones(n_assets, dtype=bool)
    
    # Apply include filter
    if include_categories:
        include_mask = np.zeros(n_assets, dtype=bool)
        for i, category in enumerate(asset_categories):
            if category in include_categories:
                include_mask[i] = True
        asset_mask &= include_mask
    
    # Apply exclude filter
    if exclude_categories:
        exclude_mask = np.ones(n_assets, dtype=bool)
        for i, category in enumerate(asset_categories):
            if category in exclude_categories:
                exclude_mask[i] = False
        asset_mask &= exclude_mask
    
    # Ensure at least one asset is selected
    if not np.any(asset_mask):
        raise ValueError("No assets match the specified category filters")
    
    return asset_mask

def normalize_weights(weights: List[float], asset_mask: np.ndarray) -> Tuple[np.ndarray, int]:
    """
    Normalize weights to match the asset mask and ensure they sum to 1.0.
    
    Args:
        weights: Original portfolio weights
        asset_mask: Boolean mask indicating which assets to use
    
    Returns:
        Tuple of (normalized_weights, n_assets_used)
    """
    n_total_assets = len(asset_mask)
    n_selected_assets = np.sum(asset_mask)
    
    # Validate weights length
    if len(weights) != n_total_assets:
        raise ValueError(f"Expected {n_total_assets} weights, got {len(weights)}")
    
    # Apply asset mask to weights
    masked_weights = np.array(weights)[asset_mask]
    
    # Normalize to sum to 1.0
    weight_sum = np.sum(masked_weights)
    if weight_sum == 0:
        # If all weights are zero, use equal weights
        normalized_weights = np.ones(n_selected_assets) / n_selected_assets
    else:
        normalized_weights = masked_weights / weight_sum
    
    return normalized_weights, n_selected_assets

def build_portfolio_returns(weights: List[float], 
                           include_categories: Optional[List[str]] = None,
                           exclude_categories: Optional[List[str]] = None) -> Tuple[np.ndarray, int]:
    """
    Build portfolio returns using the specified weights and category filters.
    
    Args:
        weights: Portfolio weights
        include_categories: Categories to include
        exclude_categories: Categories to exclude
    
    Returns:
        Tuple of (portfolio_returns, n_assets_used)
    """
    # Get asset mask based on category filters
    asset_mask = get_asset_mask(include_categories, exclude_categories)
    
    # Normalize weights
    normalized_weights, n_assets_used = normalize_weights(weights, asset_mask)
    
    # Get returns data
    returns, asset_names, asset_categories, asset_index_to_category = get_cached_data()
    
    # Apply asset mask to returns
    masked_returns = returns[asset_mask, :, :]  # Shape: (n_selected_assets, 20, 10000)
    
    # Calculate portfolio returns using einsum
    portfolio_returns = np.einsum('a,ats->ts', normalized_weights, masked_returns)
    
    return portfolio_returns, n_assets_used

def build_benchmark_returns(benchmark_weights: List[float],
                           include_categories: Optional[List[str]] = None,
                           exclude_categories: Optional[List[str]] = None) -> np.ndarray:
    """
    Build benchmark returns using the specified weights and category filters.
    
    Args:
        benchmark_weights: Benchmark portfolio weights
        include_categories: Categories to include
        exclude_categories: Categories to exclude
    
    Returns:
        Benchmark portfolio returns
    """
    # Get asset mask based on category filters
    asset_mask = get_asset_mask(include_categories, exclude_categories)
    
    # Normalize weights
    normalized_weights, _ = normalize_weights(benchmark_weights, asset_mask)
    
    # Get returns data
    returns, asset_names, asset_categories, asset_index_to_category = get_cached_data()
    
    # Apply asset mask to returns
    masked_returns = returns[asset_mask, :, :]
    
    # Calculate benchmark returns using einsum
    benchmark_returns = np.einsum('a,ats->ts', normalized_weights, masked_returns)
    
    return benchmark_returns

def get_calculation_params(weights: List[float],
                          include_categories: Optional[List[str]] = None,
                          exclude_categories: Optional[List[str]] = None,
                          periods_per_year: float = 1.0,
                          **kwargs) -> dict:
    """
    Get parameters used in calculation for response.
    
    Args:
        weights: Portfolio weights
        include_categories: Categories to include
        exclude_categories: Categories to exclude
        periods_per_year: Periods per year
        **kwargs: Additional parameters
    
    Returns:
        Dictionary of calculation parameters
    """
    params = {
        "weights": weights,
        "periods_per_year": periods_per_year,
        "include_categories": include_categories,
        "exclude_categories": exclude_categories
    }
    
    # Add additional parameters
    for key, value in kwargs.items():
        if value is not None:
            params[key] = value
    
    return params
