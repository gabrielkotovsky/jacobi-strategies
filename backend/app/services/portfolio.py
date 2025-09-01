import numpy as np
from typing import Tuple, Optional
import logging
import warnings

logger = logging.getLogger(__name__)

def portfolio_period_returns(weights: np.ndarray, returns: np.ndarray, 
                           rebalance: str = "periodic") -> np.ndarray:
    """
    Calculate portfolio period returns using vectorized operations.
    
    Args:
        weights: Portfolio weights array of shape (A,) where A = number of assets
        returns: Asset returns array of shape (A, T, S) where:
                A = number of assets, T = time periods, S = simulations
        rebalance: Rebalancing strategy - "periodic" or "none"
    
    Returns:
        Portfolio returns array of shape (T, S)
    
    Notes:
        - Uses einsum for efficient matrix multiplication: p = einsum('a,ats->ts', w, R)
        - For rebalance="none": applies weights only at t=0 and allows drift
        - For rebalance="periodic": applies weights each period (standard approach)
    """
    if weights.shape[0] != returns.shape[0]:
        raise ValueError(f"Weights shape {weights.shape} doesn't match returns assets dimension {returns.shape[0]}")
    
    if rebalance == "periodic":
        # Standard periodic rebalancing: apply weights each period
        # einsum('a,ats->ts', weights, returns) -> (T, S)
        portfolio_returns = np.einsum('a,ats->ts', weights, returns)
        
    elif rebalance == "none":
        # Buy-and-hold: apply weights only at t=0, allow drift
        portfolio_returns = _calculate_buy_and_hold_returns(weights, returns)
        
    else:
        raise ValueError(f"Invalid rebalancing strategy: {rebalance}. Must be 'periodic' or 'none'")
    
    return portfolio_returns


def _calculate_buy_and_hold_returns(weights: np.ndarray, returns: np.ndarray) -> np.ndarray:
    """
    Calculate buy-and-hold portfolio returns where weights drift based on performance.
    
    Args:
        weights: Initial portfolio weights array of shape (A,)
        returns: Asset returns array of shape (A, T, S)
    
    Returns:
        Portfolio returns array of shape (T, S)
    
    Algorithm:
        1. Start with initial weights at t=0
        2. For each period, calculate portfolio return using current weights
        3. Update weights based on relative asset performance
        4. Repeat for all periods
    """
    A, T, S = returns.shape  # Assets, Time periods, Simulations
    
    # Initialize portfolio returns array
    portfolio_returns = np.zeros((T, S))
    
    # Start with initial weights
    current_weights = weights.copy()  # Shape: (A,)
    
    # Calculate portfolio return for each period
    for t in range(T):
        # Get asset returns for this period
        period_returns = returns[:, t, :]  # Shape: (A, S)
        
        # Calculate portfolio return using current weights
        # einsum('a,as->s', current_weights, period_returns)
        portfolio_returns[t, :] = np.einsum('a,as->s', current_weights, period_returns)
        
        # Update weights for next period (if not the last period)
        if t < T - 1:
            # Calculate cumulative returns up to this point for weight updating
            # We need to track the cumulative performance of each asset
            cumulative_asset_returns = (1 + returns[:, :t+1, :]).prod(axis=1)  # Shape: (A, S)
            
            # Update weights based on relative performance
            # New weight = (old_weight * cumulative_return) / sum(all_weights * cumulative_returns)
            weighted_cumulative = current_weights[:, np.newaxis] * cumulative_asset_returns  # Shape: (A, S)
            weight_sums = weighted_cumulative.sum(axis=0)  # Shape: (S,)
            
            # Avoid division by zero
            weight_sums = np.where(weight_sums == 0, 1.0, weight_sums)
            
            # Update weights for next period
            current_weights = (weighted_cumulative / weight_sums).mean(axis=1)  # Shape: (A,)
            
            # Normalize weights to sum to 1.0
            current_weights = current_weights / current_weights.sum()
    
    return portfolio_returns


def to_cumulative_returns(period_returns: np.ndarray) -> np.ndarray:
    """
    Convert period returns to cumulative returns.
    
    Args:
        period_returns: Period returns array of shape (T, S)
    
    Returns:
        Cumulative returns array of shape (T, S)
    
    Formula: (1 + r1) * (1 + r2) * ... * (1 + rT)
    """
    # Add 1 to period returns and take cumulative product along time axis
    # (1 + r).cumprod(axis=0) where axis=0 is the time dimension
    cumulative_returns = (1 + period_returns).cumprod(axis=0)
    return cumulative_returns


def calculate_annualized_metrics(portfolio_returns: np.ndarray, 
                               periods_per_year: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate annualized mean return and volatility.
    
    Args:
        portfolio_returns: Portfolio returns array of shape (T, S)
        periods_per_year: Number of periods per year (default: 1.0 for annual data)
    
    Returns:
        Tuple of (annualized_mean, annualized_volatility) each of shape (S,)
    
    Notes:
        - Data are already annual steps, so ann_factor = T (periods_per_year)
        - mean_ann = p.mean(axis=0) across time periods
        - vol_ann = p.std(axis=0, ddof=1) across time periods
    """
    # Calculate mean and volatility across time dimension (axis=0)
    # This gives us one value per simulation
    mean_period = portfolio_returns.mean(axis=0)  # Shape: (S,)
    vol_period = portfolio_returns.std(axis=0, ddof=1)  # Shape: (S,)
    
    # Annualize if needed (for non-annual data)
    if periods_per_year != 1.0:
        # For mean: multiply by periods per year
        annualized_mean = mean_period * periods_per_year
        # For volatility: multiply by square root of periods per year
        annualized_volatility = vol_period * np.sqrt(periods_per_year)
    else:
        # Data already annual, no adjustment needed
        annualized_mean = mean_period
        annualized_volatility = vol_period
    
    return annualized_mean, annualized_volatility


def portfolio_analysis_pipeline(weights: np.ndarray, returns: np.ndarray,
                              rebalance: str = "periodic",
                              periods_per_year: float = 1.0) -> dict:
    """
    Complete portfolio analysis pipeline.
    
    Args:
        weights: Portfolio weights array of shape (A,)
        returns: Asset returns array of shape (A, T, S)
        rebalance: Rebalancing strategy
        periods_per_year: Number of periods per year
    
    Returns:
        Dictionary containing all portfolio metrics
    """
    # Step 1: Calculate period returns
    period_returns = portfolio_period_returns(weights, returns, rebalance)
    
    # Step 2: Calculate cumulative returns
    cumulative_returns = to_cumulative_returns(period_returns)
    
    # Step 3: Calculate annualized metrics
    annualized_mean, annualized_volatility = calculate_annualized_metrics(
        period_returns, periods_per_year
    )
    
    # Step 4: Calculate additional metrics
    total_return = cumulative_returns[-1, :] - 1  # Final cumulative return - 1
    
    # Maximum drawdown calculation
    peak_values = np.maximum.accumulate(cumulative_returns, axis=0)
    drawdowns = (cumulative_returns - peak_values) / peak_values
    max_drawdown = drawdowns.min(axis=0)
    
    return {
        'period_returns': period_returns,           # Shape: (T, S)
        'cumulative_returns': cumulative_returns,   # Shape: (T, S)
        'annualized_mean': annualized_mean,         # Shape: (S,)
        'annualized_volatility': annualized_volatility,  # Shape: (S,)
        'total_return': total_return,               # Shape: (S,)
        'max_drawdown': max_drawdown,               # Shape: (S,)
        'shapes': {
            'period_returns': period_returns.shape,
            'cumulative_returns': cumulative_returns.shape,
            'annualized_mean': annualized_mean.shape,
            'annualized_volatility': annualized_volatility.shape,
            'total_return': total_return.shape,
            'max_drawdown': max_drawdown.shape
        }
    }


def validate_portfolio_inputs(weights: np.ndarray, returns: np.ndarray) -> None:
    """
    Validate portfolio calculation inputs.
    
    Args:
        weights: Portfolio weights array
        returns: Asset returns array
    
    Raises:
        ValueError: If inputs are invalid
    """
    # Check weights
    if weights.ndim != 1:
        raise ValueError(f"Weights must be 1D array, got {weights.ndim}D")
    
    if not np.allclose(weights.sum(), 1.0, atol=1e-6):
        raise ValueError(f"Weights must sum to 1.0, got {weights.sum():.6f}")
    
    if np.any(weights < 0):
        raise ValueError("Weights cannot be negative")
    
    # Check returns
    if returns.ndim != 3:
        raise ValueError(f"Returns must be 3D array (A, T, S), got {returns.ndim}D")
    
    # Check compatibility
    if weights.shape[0] != returns.shape[0]:
        raise ValueError(f"Weights length {weights.shape[0]} doesn't match returns assets {returns.shape[0]}")
    
    # Check for NaN or inf values
    if not np.all(np.isfinite(returns)):
        raise ValueError("Returns contain NaN or infinite values")
    
    logger.info(f"Portfolio inputs validated: {weights.shape[0]} assets, {returns.shape[1]} periods, {returns.shape[2]} simulations")
