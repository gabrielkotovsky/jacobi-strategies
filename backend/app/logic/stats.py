"""
Statistical functions for portfolio analysis using pure NumPy.

All functions are stateless and vectorized for performance.
Avoids pandas in hot path for maximum efficiency.
"""

import numpy as np
from typing import Tuple, Optional, Union, List


def annualised_return(period_returns: np.ndarray, periods_per_year: float = 1.0, 
                      aggregation: str = "mean") -> float:
    """
    Calculate annualized return using Compound Annual Growth Rate (CAGR).
    
    Args:
        period_returns: Period returns array of shape (T, S) where T=time periods, S=simulations
        periods_per_year: Number of periods per year (default: 1.0 for annual data)
        aggregation: Aggregation method across simulations - "mean" or "median" (default: "mean")
    
    Returns:
        Annualized return as a float
        
    Formula: CAGR = (final_value / initial_value)^(1/years) - 1
    """
    T, S = period_returns.shape
    
    # Calculate cumulative returns for each simulation
    # (1 + r1) * (1 + r2) * ... * (1 + rT)
    cumulative_returns = (1 + period_returns).prod(axis=0)  # Shape: (S,)
    
    # Calculate years elapsed
    years = T / periods_per_year
    
    # CAGR = (final_value)^(1/years) - 1
    # Since we start with 1.0, final_value = cumulative_returns
    cagr_per_sim = cumulative_returns ** (1 / years) - 1  # Shape: (S,)
    
    # Aggregate across simulations
    if aggregation == "median":
        return float(np.median(cagr_per_sim))
    else:  # default to mean
        return float(np.mean(cagr_per_sim))


def annualised_volatility(period_returns: np.ndarray, periods_per_year: float = 1.0,
                          aggregation: str = "mean") -> float:
    """
    Calculate annualized volatility.
    
    Args:
        period_returns: Period returns array of shape (T, S) where T=time periods, S=simulations
        periods_per_year: Number of periods per year (default: 1.0 for annual data)
        aggregation: Aggregation method across simulations - "mean" or "median" (default: "mean")
    
    Returns:
        Annualized volatility as a float
        
    Method: Calculate std across periods per simulation, then aggregate across simulations
    """
    # Calculate standard deviation across time periods for each simulation
    # This gives us volatility per simulation
    vol_per_sim = np.std(period_returns, axis=0, ddof=1)  # Shape: (S,)
    
    # Annualize by multiplying by sqrt(periods_per_year)
    annualized_vol_per_sim = vol_per_sim * np.sqrt(periods_per_year)  # Shape: (S,)
    
    # Aggregate across simulations
    if aggregation == "median":
        return float(np.median(annualized_vol_per_sim))
    else:  # default to mean
        return float(np.mean(annualized_vol_per_sim))


def sharpe_ratio(period_returns: np.ndarray, risk_free_rate: float = 0.0, 
                 periods_per_year: float = 1.0, aggregation: str = "mean") -> float:
    """
    Calculate Sharpe ratio: per-simulation (CAGR - RFR) / volatility, then aggregate.
    
    Args:
        period_returns: Period returns array of shape (T, S) where T=time periods, S=simulations
        risk_free_rate: Risk-free rate (default: 0.0)
        periods_per_year: Number of periods per year (default: 1.0 for annual data)
        aggregation: Aggregation method across simulations - "mean" or "median" (default: "mean")
    
    Returns:
        Sharpe ratio as a float
    """
    T, S = period_returns.shape
    
    # Step 1: Calculate CAGR per simulation
    cumulative_returns = (1 + period_returns).prod(axis=0)  # Shape: (S,)
    years = T / periods_per_year
    cagr_per_sim = cumulative_returns ** (1 / years) - 1  # Shape: (S,)
    
    # Step 2: Calculate volatility per simulation
    vol_per_sim = np.std(period_returns, axis=0, ddof=1)  # Shape: (S,)
    annualized_vol_per_sim = vol_per_sim * np.sqrt(periods_per_year)  # Shape: (S,)
    
    # Step 3: Calculate Sharpe ratio per simulation
    sharpe_per_sim = (cagr_per_sim - risk_free_rate) / annualized_vol_per_sim  # Shape: (S,)
    
    # Step 4: Aggregate across simulations
    if aggregation == "median":
        return float(np.median(sharpe_per_sim))
    else:  # default to mean
        return float(np.mean(sharpe_per_sim))


def tracking_error(portfolio_returns: np.ndarray, benchmark_returns: np.ndarray, 
                  periods_per_year: float = 1.0, aggregation: str = "mean") -> float:
    """
    Calculate tracking error: standard deviation of excess returns.
    
    Args:
        portfolio_returns: Portfolio period returns array of shape (T, S)
        benchmark_returns: Benchmark period returns array of shape (T, S)
        periods_per_year: Number of periods per year (default: 1.0 for annual data)
        aggregation: Aggregation method across simulations - "mean" or "median" (default: "mean")
    
    Returns:
        Annualized tracking error as a float
        
    Formula: std(portfolio_return - benchmark_return) * sqrt(periods_per_year)
    """
    if portfolio_returns.shape != benchmark_returns.shape:
        raise ValueError("Portfolio and benchmark returns must have the same shape")
    
    # Calculate excess returns (portfolio - benchmark)
    excess_returns = portfolio_returns - benchmark_returns  # Shape: (T, S)
    
    # Calculate standard deviation across time periods for each simulation
    tracking_error_per_sim = np.std(excess_returns, axis=0, ddof=1)  # Shape: (S,)
    
    # Annualize by multiplying by sqrt(periods_per_year)
    annualized_te_per_sim = tracking_error_per_sim * np.sqrt(periods_per_year)  # Shape: (S,)
    
    # Aggregate across simulations
    if aggregation == "median":
        return float(np.median(annualized_te_per_sim))
    else:  # default to mean
        return float(np.mean(annualized_te_per_sim))


def downside_deviation(period_returns: np.ndarray, minimum_acceptable_return: float = 0.0,
                       periods_per_year: float = 1.0, aggregation: str = "mean") -> float:
    """
    Calculate downside deviation: sqrt(mean(min(return - MAR, 0)^2)).
    
    Args:
        period_returns: Period returns array of shape (T, S) where T=time periods, S=simulations
        minimum_acceptable_return: Minimum acceptable return threshold (default: 0.0)
        periods_per_year: Number of periods per year (default: 1.0 for annual data)
        aggregation: Aggregation method across simulations - "mean" or "median" (default: "mean")
    
    Returns:
        Annualized downside deviation as a float
        
    Formula: sqrt(mean(min(return - MAR, 0)^2)) * sqrt(periods_per_year)
    """
    # Calculate excess returns below MAR
    excess_returns = period_returns - minimum_acceptable_return  # Shape: (T, S)
    
    # Take minimum of excess returns and 0 (only negative deviations)
    downside_returns = np.minimum(excess_returns, 0)  # Shape: (T, S)
    
    # Square the downside returns
    squared_downside = downside_returns ** 2  # Shape: (T, S)
    
    # Calculate mean across time periods for each simulation
    mean_squared_downside_per_sim = np.mean(squared_downside, axis=0)  # Shape: (S,)
    
    # Take square root to get downside deviation per simulation
    downside_dev_per_sim = np.sqrt(mean_squared_downside_per_sim)  # Shape: (S,)
    
    # Annualize by multiplying by sqrt(periods_per_year)
    annualized_dd_per_sim = downside_dev_per_sim * np.sqrt(periods_per_year)  # Shape: (S,)
    
    # Aggregate across simulations
    if aggregation == "median":
        return float(np.median(annualized_dd_per_sim))
    else:  # default to mean
        return float(np.mean(annualized_dd_per_sim))


def value_at_risk_1period(period_returns: np.ndarray, confidence: float = 0.95, 
                          var_type: str = "pooled") -> Union[float, List[float]]:
    """
    Calculate 1-period VaR with different calculation methods.
    
    Args:
        period_returns: Period returns array of shape (T, S) where T=time periods, S=simulations
        confidence: Confidence level (default: 0.95 for 95% VaR)
        var_type: Calculation method - "pooled", "year_by_year", or "cumulative" (default: "pooled")
    
    Returns:
        VaR as a float (negative value represents loss) for "pooled" and "cumulative"
        List of VaR values (one per year) for "year_by_year"
    """
    if not 0 < confidence < 1:
        raise ValueError("Confidence must be between 0 and 1")
    
    if var_type not in ["pooled", "year_by_year", "cumulative"]:
        raise ValueError("var_type must be 'pooled', 'year_by_year', or 'cumulative'")
    
    T, S = period_returns.shape
    var_quantile = 1 - confidence
    
    if var_type == "pooled":
        # Option 2: Pooled Distribution (All Years Together)
        # Flatten all 20 × 10,000 returns = 200,000 simulated annual returns
        all_period_returns = period_returns.flatten()  # Shape: (T*S,)
        var = np.quantile(all_period_returns, var_quantile)
        return float(var)
    
    elif var_type == "year_by_year":
        # Option 1: Year-by-Year VaR
        # For each year, take all 10,000 simulated returns and compute VaR separately
        var_per_year = []
        for year in range(T):
            year_returns = period_returns[year, :]  # Shape: (S,)
            year_var = np.quantile(year_returns, var_quantile)
            var_per_year.append(float(year_var))
        
        # Return list of VaR values (one per year)
        return var_per_year
    
    elif var_type == "cumulative":
        # Option 3: Investment Horizon VaR (Cumulative)
        # Compound returns within each simulation to the T-year terminal value
        cumulative_returns = (1 + period_returns).prod(axis=0) - 1  # Shape: (S,)
        var = np.quantile(cumulative_returns, var_quantile)
        return float(var)
    
    else:
        raise ValueError("Invalid var_type")


def value_at_risk(period_returns: np.ndarray, confidence: float = 0.95, 
                  var_type: str = "pooled") -> Union[float, List[float]]:
    """
    Calculate Value at Risk (VaR) at specified confidence level and calculation method.
    
    Args:
        period_returns: Period returns array of shape (T, S)
        confidence: Confidence level (default: 0.95 for 95% VaR)
        var_type: Calculation method - "pooled", "year_by_year", or "cumulative" (default: "pooled")
    
    Returns:
        VaR as a float (negative value represents loss) for "pooled" and "cumulative"
        List of VaR values (one per year) for "year_by_year"
    """
    return value_at_risk_1period(period_returns, confidence, var_type)


def conditional_value_at_risk_1period(period_returns: np.ndarray, confidence: float = 0.95,
                                     var_type: str = "pooled") -> Union[float, List[float]]:
    """
    Calculate 1-period CVaR with different calculation methods.
    
    Args:
        period_returns: Period returns array of shape (T, S) where T=time periods, S=simulations
        confidence: Confidence level (default: 0.95 for 95% CVaR)
        var_type: Calculation method - "pooled", "year_by_year", or "cumulative" (default: "pooled")
    
    Returns:
        CVaR as a float (negative value represents expected loss) for "pooled" and "cumulative"
        List of CVaR values (one per year) for "year_by_year"
    """
    if not 0 < confidence < 1:
        raise ValueError("Confidence must be between 0 and 1")
    
    if var_type not in ["pooled", "year_by_year", "cumulative"]:
        raise ValueError("var_type must be 'pooled', 'year_by_year', or 'cumulative'")
    
    T, S = period_returns.shape
    var_quantile = 1 - confidence
    
    if var_type == "pooled":
        # Option 2: Pooled Distribution (All Years Together)
        all_period_returns = period_returns.flatten()  # Shape: (T*S,)
        var_threshold = np.quantile(all_period_returns, var_quantile)
        tail_returns = all_period_returns[all_period_returns <= var_threshold]
        
        if len(tail_returns) == 0:
            return float(var_threshold)
        
        cvar = np.mean(tail_returns)
        return float(cvar)
    
    elif var_type == "year_by_year":
        # Option 1: Year-by-Year CVaR
        cvar_per_year = []
        for year in range(T):
            year_returns = period_returns[year, :]  # Shape: (S,)
            var_threshold = np.quantile(year_returns, var_quantile)
            tail_returns = year_returns[year_returns <= var_threshold]
            
            if len(tail_returns) == 0:
                year_cvar = var_threshold
            else:
                year_cvar = np.mean(tail_returns)
            
            cvar_per_year.append(float(year_cvar))
        
        # Return list of CVaR values (one per year)
        return cvar_per_year
    
    elif var_type == "cumulative":
        # Option 3: Investment Horizon CVaR (Cumulative)
        cumulative_returns = (1 + period_returns).prod(axis=0) - 1  # Shape: (S,)
        var_threshold = np.quantile(cumulative_returns, var_quantile)
        tail_returns = cumulative_returns[cumulative_returns <= var_threshold]
        
        if len(tail_returns) == 0:
            return float(var_threshold)
        
        cvar = np.mean(tail_returns)
        return float(cvar)
    
    else:
        raise ValueError("Invalid var_type")


def conditional_value_at_risk(period_returns: np.ndarray, confidence: float = 0.95,
                             var_type: str = "pooled") -> Union[float, List[float]]:
    """
    Calculate Conditional Value at Risk (CVaR) at specified confidence level and calculation method.
    
    Args:
        period_returns: Period returns array of shape (T, S)
        confidence: Confidence level (default: 0.95 for 95% CVaR)
        var_type: Calculation method - "pooled", "year_by_year", or "cumulative" (default: "pooled")
    
    Returns:
        CVaR as a float (negative value represents expected loss) for "pooled" and "cumulative"
        List of CVaR values (one per year) for "year_by_year"
    """
    return conditional_value_at_risk_1period(period_returns, confidence, var_type)


def maximum_drawdown(period_returns: np.ndarray, aggregation: str = "mean") -> float:
    """
    Calculate maximum drawdown: largest peak-to-trough decline (positive magnitude).
    
    Args:
        period_returns: Period returns array of shape (T, S) where T=time periods, S=simulations
        aggregation: Aggregation method across simulations - "mean" or "median" (default: "mean")
    
    Returns:
        Maximum drawdown as a float (positive magnitude)
    """
    T, S = period_returns.shape
    
    # Step 1: Calculate cumulative returns for each simulation
    cumulative_returns = (1 + period_returns).cumprod(axis=0)  # Shape: (T, S)
    
    # Step 2: Calculate rolling maximum (peak) for each simulation
    rolling_max = np.maximum.accumulate(cumulative_returns, axis=0)  # Shape: (T, S)
    
    # Step 3: Calculate drawdowns: 1 - (current_value / peak_value)
    # This gives us positive values for declines, 0 at peaks
    drawdowns = 1 - (cumulative_returns / rolling_max)  # Shape: (T, S)
    
    # Step 4: Find the maximum drawdown for each simulation (worst decline)
    max_dd_per_sim = np.max(drawdowns, axis=0)  # Shape: (S,) - now positive values
    
    # Step 5: Aggregate across simulations
    if aggregation == "median":
        return float(np.median(max_dd_per_sim))
    else:  # default to mean
        return float(np.mean(max_dd_per_sim))