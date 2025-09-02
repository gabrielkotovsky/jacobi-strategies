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


def calculate_projected_values(portfolio_returns: np.ndarray, 
                             initial_value: float = 100000.0,
                             rebalance: str = "periodic") -> list:
    """
    Calculate projected portfolio values over time with percentiles.
    
    Args:
        portfolio_returns: Portfolio returns array of shape (T, S) where:
                          T = time periods, S = simulations
        initial_value: Initial portfolio value (default: 100000.0)
        rebalance: Rebalancing strategy used (for reference only)
    
    Returns:
        List of dictionaries with year and percentile values:
        [
            {"year": 1, "p1": value, "p5": value, "p25": value, "p50": value, 
             "p75": value, "p95": value, "p99": value},
            {"year": 2, "p1": value, "p5": value, ...},
            ...
        ]
    
    Algorithm:
        1. Convert period returns to cumulative portfolio values
        2. For each year, calculate percentiles across simulations
        3. Return time series of percentile values
    """
    T, S = portfolio_returns.shape  # Time periods, Simulations
    
    # Step 1: Convert period returns to cumulative portfolio values
    # V_{t,s} = V_0 * prod_{u=1}^t (1 + r^{(p)}_{u,s})
    cumulative_values = np.zeros((T, S))
    
    # First period: V_1 = V_0 * (1 + r_1)
    cumulative_values[0, :] = initial_value * (1 + portfolio_returns[0, :])
    
    # Subsequent periods: V_t = V_{t-1} * (1 + r_t)
    for t in range(1, T):
        cumulative_values[t, :] = cumulative_values[t-1, :] * (1 + portfolio_returns[t, :])
    
    # Step 2: Calculate percentiles for each year
    percentiles = [1, 5, 25, 50, 75, 95, 99]
    projected_values = []
    
    # Add initial value at year 0
    initial_year_data = {"year": 0}
    for p in percentiles:
        initial_year_data[f"p{p}"] = initial_value  # All percentiles start at initial value
    
    projected_values.append(initial_year_data)
    
    # Add projected values for years 1 to T
    for t in range(T):
        year_data = {"year": t + 1}  # Convert to 1-based indexing
        
        # Calculate percentiles for this year across all simulations
        for p in percentiles:
            percentile_value = np.percentile(cumulative_values[t, :], p)
            year_data[f"p{p}"] = float(percentile_value)  # Convert numpy type to Python float
        
        projected_values.append(year_data)
    
    return projected_values


def calculate_asset_metrics(returns: np.ndarray, weights: np.ndarray,
                           periods_per_year: float = 1.0,
                           is_log: bool = False,
                           aggregation: str = "pooled",
                           corr_method: str = "pooled") -> dict:
    """
    Calculate per-asset annualised returns, volatilities, and correlation matrix.
    
    Args:
        returns: Asset returns array of shape (A, T, S) where:
                A = assets, T = time periods, S = simulations
        weights: Portfolio weights array of shape (A,) - only assets with non-zero weights are included
        periods_per_year: Number of periods per year for annualization
        is_log: Whether returns are log returns (True) or simple returns (False)
        aggregation: Aggregation method: 'pooled', 'year_by_year', or 'simulation_by_simulation'
        corr_method: Correlation method: 'pooled', 'year_by_year', or 'simulation_by_simulation'
    
    Returns:
        Dictionary containing:
        - asset_metrics: List of dicts with asset name, annualised_return, annualised_volatility
        - correlation_matrix: List of dicts with asset1, asset2, correlation
    """
    A, T, S = returns.shape  # Assets, Time periods, Simulations
    
    # Filter to only include assets with non-zero weights
    selected_indices = np.where(weights > 0)[0]
    if len(selected_indices) == 0:
        return {"asset_metrics": [], "correlation_matrix": []}
    
    # Get actual asset names from the data loader
    from app.data.loader import get_cached_data
    _, asset_names, _, _ = get_cached_data()
    
    # Step 1: Calculate per-asset annualised returns
    asset_returns = []
    
    for a in selected_indices:
        asset_name = asset_names[a] if a < len(asset_names) else f"Asset_{a+1}"
        
        if aggregation == "pooled":
            # Concatenate all T×S observations into one series per asset
            asset_data = returns[a, :, :].flatten()  # Shape: (T*S,)
            
        elif aggregation == "year_by_year":
            # Compute per-year means across simulations, then average the T yearly means
            yearly_means = np.mean(returns[a, :, :], axis=1)  # Shape: (T,)
            asset_data = yearly_means
            
        elif aggregation == "simulation_by_simulation":
            # Compute per-simulation means across time, then average the S simulation means
            simulation_means = np.mean(returns[a, :, :], axis=0)  # Shape: (S,)
            asset_data = simulation_means
        
        # Calculate annualised return
        if is_log:
            # For log returns: average directly on log scale, exponentiate, subtract 1
            log_mean = np.mean(asset_data)
            annualised_return = np.exp(log_mean * periods_per_year) - 1
        else:
            # For simple returns: take log(1+r), average on log scale, exponentiate, subtract 1
            log_returns = np.log(1 + asset_data)
            log_mean = np.mean(log_returns)
            annualised_return = np.exp(log_mean * periods_per_year) - 1
        
        # Calculate annualised volatility
        if is_log:
            # Standard deviation of log returns
            vol_period = np.std(asset_data)
        else:
            # Standard deviation of simple returns
            vol_period = np.std(asset_data)
        
        # Annualise volatility
        annualised_volatility = vol_period * np.sqrt(periods_per_year)
        
        asset_returns.append({
            "asset": asset_name,
            "annualised_return": float(annualised_return),
            "annualised_volatility": float(annualised_volatility)
        })
    
    # Step 2: Calculate asset correlation matrix
    correlation_matrix = []
    
    if corr_method == "pooled":
        # Build A×N matrix where N = T×S (concatenate all periods and simulations)
        # Only include selected assets
        selected_returns = returns[selected_indices, :, :]  # Shape: (selected_A, T, S)
        pooled_returns = selected_returns.reshape(len(selected_indices), T * S)  # Shape: (selected_A, T*S)
        corr_matrix = np.corrcoef(pooled_returns)
        
    elif corr_method == "year_by_year":
        # Compute one correlation matrix per year using S sims, then Fisher-average
        # Only include selected assets
        selected_returns = returns[selected_indices, :, :]  # Shape: (selected_A, T, S)
        yearly_corr_matrices = []
        for t in range(T):
            year_returns = selected_returns[:, t, :]  # Shape: (selected_A, S)
            corr_matrix = np.corrcoef(year_returns)
            yearly_corr_matrices.append(corr_matrix)
        
        # Fisher z-transform average
        corr_matrix = _fisher_average_correlations(yearly_corr_matrices)
        
    elif corr_method == "simulation_by_simulation":
        # Compute one matrix per simulation over T periods, then Fisher-average
        # Only include selected assets
        selected_returns = returns[selected_indices, :, :]  # Shape: (selected_A, T, S)
        simulation_corr_matrices = []
        for s in range(S):
            sim_returns = selected_returns[:, :, s]  # Shape: (selected_A, T)
            corr_matrix = np.corrcoef(sim_returns)
            simulation_corr_matrices.append(corr_matrix)
        
        # Fisher z-transform average
        corr_matrix = _fisher_average_correlations(simulation_corr_matrices)
    
    # Handle zero-variance assets and convert to list format
    for i in range(len(selected_indices)):
        for j in range(len(selected_indices)):
            if i == j:
                correlation = 1.0  # Diagonal elements
            elif np.isnan(corr_matrix[i, j]) or not np.isfinite(corr_matrix[i, j]):
                correlation = 0.0  # Handle zero-variance assets
            else:
                correlation = float(corr_matrix[i, j])
            
            asset_i_idx = selected_indices[i]
            asset_j_idx = selected_indices[j]
            correlation_matrix.append({
                "asset1": asset_names[asset_i_idx] if asset_i_idx < len(asset_names) else f"Asset_{asset_i_idx+1}",
                "asset2": asset_names[asset_j_idx] if asset_j_idx < len(asset_names) else f"Asset_{asset_j_idx+1}",
                "correlation": correlation
            })
    
    return {
        "asset_metrics": asset_returns,
        "correlation_matrix": correlation_matrix
    }


def _fisher_average_correlations(corr_matrices: list) -> np.ndarray:
    """
    Average correlation matrices using Fisher z-transform.
    
    Args:
        corr_matrices: List of correlation matrices
    
    Returns:
        Averaged correlation matrix
    """
    if not corr_matrices:
        return np.array([])
    
    # Convert correlations to Fisher z-scores
    z_matrices = []
    for corr_matrix in corr_matrices:
        # Handle edge cases: correlations of ±1 or NaN
        safe_corr = np.clip(corr_matrix, -0.9999, 0.9999)
        z_matrix = np.arctanh(safe_corr)
        z_matrices.append(z_matrix)
    
    # Average z-scores
    avg_z = np.mean(z_matrices, axis=0)
    
    # Convert back to correlations
    avg_corr = np.tanh(avg_z)
    
    # Restore diagonal elements to 1.0
    np.fill_diagonal(avg_corr, 1.0)
    
    return avg_corr
