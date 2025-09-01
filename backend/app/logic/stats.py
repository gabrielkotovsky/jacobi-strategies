"""
Statistical functions for portfolio analysis using pure NumPy.

All functions are stateless and vectorized for performance.
Avoids pandas in hot path for maximum efficiency.
"""

import numpy as np
from typing import Tuple, Optional


def annualised_return(period_returns: np.ndarray, periods_per_year: float = 1.0) -> float:
    """
    Calculate annualized return using Compound Annual Growth Rate (CAGR).
    
    Args:
        period_returns: Period returns array of shape (T, S) where T=time periods, S=simulations
        periods_per_year: Number of periods per year (default: 1.0 for annual data)
    
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
    
    # Average across simulations
    return float(np.mean(cagr_per_sim))


def annualised_volatility(period_returns: np.ndarray, periods_per_year: float = 1.0) -> float:
    """
    Calculate annualized volatility.
    
    Args:
        period_returns: Period returns array of shape (T, S) where T=time periods, S=simulations
        periods_per_year: Number of periods per year (default: 1.0 for annual data)
    
    Returns:
        Annualized volatility as a float
        
    Method: Calculate std across periods per simulation, then average across simulations
    """
    # Calculate standard deviation across time periods for each simulation
    # This gives us volatility per simulation
    vol_per_sim = np.std(period_returns, axis=0, ddof=1)  # Shape: (S,)
    
    # Annualize by multiplying by sqrt(periods_per_year)
    annualized_vol_per_sim = vol_per_sim * np.sqrt(periods_per_year)  # Shape: (S,)
    
    # Average across simulations
    return float(np.mean(annualized_vol_per_sim))


def sharpe_ratio(period_returns: np.ndarray, risk_free_rate: float = 0.0, 
                 periods_per_year: float = 1.0) -> float:
    """
    Calculate Sharpe ratio: (CAGR - RFR) / volatility.
    
    Args:
        period_returns: Period returns array of shape (T, S) where T=time periods, S=simulations
        risk_free_rate: Annual risk-free rate (default: 0.0)
        periods_per_year: Number of periods per year (default: 1.0 for annual data)
    
    Returns:
        Sharpe ratio as a float
    """
    # Get annualized return and volatility
    annual_return = annualised_return(period_returns, periods_per_year)
    annual_vol = annualised_volatility(period_returns, periods_per_year)
    
    # Avoid division by zero
    if annual_vol == 0:
        return 0.0 if annual_return == risk_free_rate else np.inf
    
    # Sharpe ratio = (return - risk_free_rate) / volatility
    return (annual_return - risk_free_rate) / annual_vol


def tracking_error(portfolio_returns: np.ndarray, benchmark_returns: np.ndarray, 
                  periods_per_year: float = 1.0) -> float:
    """
    Calculate tracking error: standard deviation of excess returns.
    
    Args:
        portfolio_returns: Portfolio period returns array of shape (T, S)
        benchmark_returns: Benchmark period returns array of shape (T, S)
        periods_per_year: Number of periods per year (default: 1.0 for annual data)
    
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
    
    # Average across simulations
    return float(np.mean(annualized_te_per_sim))


def downside_deviation(period_returns: np.ndarray, minimum_acceptable_return: float = 0.0,
                       periods_per_year: float = 1.0) -> float:
    """
    Calculate downside deviation: sqrt(mean(min(return - MAR, 0)^2)).
    
    Args:
        period_returns: Period returns array of shape (T, S) where T=time periods, S=simulations
        minimum_acceptable_return: Minimum acceptable return threshold (default: 0.0)
        periods_per_year: Number of periods per year (default: 1.0 for annual data)
    
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
    
    # Average across simulations
    return float(np.mean(annualized_dd_per_sim))


def value_at_risk(period_returns: np.ndarray, confidence: float = 0.95) -> float:
    """
    Calculate Value at Risk (VaR) at specified confidence level.
    
    Args:
        period_returns: Period returns array of shape (T, S) where T=time periods, S=simulations
        confidence: Confidence level (default: 0.95 for 95% VaR)
    
    Returns:
        VaR as a float (negative value represents loss)
        
    Method: Pool all period returns across time and simulations, then take quantile
    """
    if not 0 < confidence < 1:
        raise ValueError("Confidence must be between 0 and 1")
    
    # Flatten the array to pool all period returns across time and simulations
    # This gives us the full distribution of 1-period returns
    all_returns = period_returns.flatten()  # Shape: (T * S,)
    
    # Calculate VaR as the (1 - confidence) quantile
    # For 95% confidence, we want the 5th percentile (worst 5% of returns)
    var_quantile = 1 - confidence
    var = np.quantile(all_returns, var_quantile)
    
    return float(var)


def conditional_value_at_risk(period_returns: np.ndarray, confidence: float = 0.95) -> float:
    """
    Calculate Conditional Value at Risk (CVaR) at specified confidence level.
    
    Args:
        period_returns: Period returns array of shape (T, S) where T=time periods, S=simulations
        confidence: Confidence level (default: 0.95 for 95% CVaR)
    
    Returns:
        CVaR as a float (negative value represents expected loss)
        
    Method: Average of all returns below the VaR threshold
    """
    if not 0 < confidence < 1:
        raise ValueError("Confidence must be between 0 and 1")
    
    # Flatten the array to pool all period returns
    all_returns = period_returns.flatten()  # Shape: (T * S,)
    
    # Calculate VaR threshold
    var_quantile = 1 - confidence
    var_threshold = np.quantile(all_returns, var_quantile)
    
    # Find all returns below the VaR threshold
    tail_returns = all_returns[all_returns <= var_threshold]
    
    # If no returns below threshold, return VaR
    if len(tail_returns) == 0:
        return float(var_threshold)
    
    # CVaR is the mean of returns below VaR
    cvar = np.mean(tail_returns)
    
    return float(cvar)


def maximum_drawdown(period_returns: np.ndarray) -> float:
    """
    Calculate maximum drawdown: largest peak-to-trough decline.
    
    Args:
        period_returns: Period returns array of shape (T, S) where T=time periods, S=simulations
    
    Returns:
        Maximum drawdown as a float (negative value represents decline)
        
    Method: Calculate cumulative returns, find rolling maximum, compute drawdowns, take minimum per sim
    """
    T, S = period_returns.shape
    
    # Calculate cumulative returns for each simulation
    # (1 + r1) * (1 + r2) * ... * (1 + rT)
    cumulative_returns = (1 + period_returns).cumprod(axis=0)  # Shape: (T, S)
    
    # Calculate rolling maximum (peak) for each simulation
    # np.maximum.accumulate gives us the running maximum
    rolling_max = np.maximum.accumulate(cumulative_returns, axis=0)  # Shape: (T, S)
    
    # Calculate drawdowns: (current_value / peak_value) - 1
    # This gives us negative values for declines, 0 at peaks
    drawdowns = (cumulative_returns / rolling_max) - 1  # Shape: (T, S)
    
    # Find the minimum drawdown for each simulation (worst decline)
    max_dd_per_sim = np.min(drawdowns, axis=0)  # Shape: (S,)
    
    # Average across simulations
    return float(np.mean(max_dd_per_sim))


def sortino_ratio(period_returns: np.ndarray, risk_free_rate: float = 0.0,
                  minimum_acceptable_return: float = 0.0, periods_per_year: float = 1.0) -> float:
    """
    Calculate Sortino ratio: (CAGR - RFR) / downside_deviation.
    
    Args:
        period_returns: Period returns array of shape (T, S) where T=time periods, S=simulations
        risk_free_rate: Annual risk-free rate (default: 0.0)
        minimum_acceptable_return: Minimum acceptable return for downside deviation (default: 0.0)
        periods_per_year: Number of periods per year (default: 1.0 for annual data)
    
    Returns:
        Sortino ratio as a float
    """
    # Get annualized return and downside deviation
    annual_return = annualised_return(period_returns, periods_per_year)
    downside_dev = downside_deviation(period_returns, minimum_acceptable_return, periods_per_year)
    
    # Avoid division by zero
    if downside_dev == 0:
        return 0.0 if annual_return == risk_free_rate else np.inf
    
    # Sortino ratio = (return - risk_free_rate) / downside_deviation
    return (annual_return - risk_free_rate) / downside_dev


def information_ratio(portfolio_returns: np.ndarray, benchmark_returns: np.ndarray,
                     periods_per_year: float = 1.0) -> float:
    """
    Calculate information ratio: excess return / tracking error.
    
    Args:
        portfolio_returns: Portfolio period returns array of shape (T, S)
        benchmark_returns: Benchmark period returns array of shape (T, S)
        periods_per_year: Number of periods per year (default: 1.0 for annual data)
    
    Returns:
        Information ratio as a float
    """
    # Calculate excess return (portfolio - benchmark)
    portfolio_cagr = annualised_return(portfolio_returns, periods_per_year)
    benchmark_cagr = annualised_return(benchmark_returns, periods_per_year)
    excess_return = portfolio_cagr - benchmark_cagr
    
    # Calculate tracking error
    tracking_err = tracking_error(portfolio_returns, benchmark_returns, periods_per_year)
    
    # Avoid division by zero
    if tracking_err == 0:
        return 0.0 if excess_return == 0 else np.inf
    
    # Information ratio = excess_return / tracking_error
    return excess_return / tracking_err


def calmar_ratio(period_returns: np.ndarray, risk_free_rate: float = 0.0,
                 periods_per_year: float = 1.0) -> float:
    """
    Calculate Calmar ratio: (CAGR - RFR) / |maximum_drawdown|.
    
    Args:
        period_returns: Period returns array of shape (T, S) where T=time periods, S=simulations
        risk_free_rate: Annual risk-free rate (default: 0.0)
        periods_per_year: Number of periods per year (default: 1.0 for annual data)
    
    Returns:
        Calmar ratio as a float
    """
    # Get annualized return and maximum drawdown
    annual_return = annualised_return(period_returns, periods_per_year)
    max_dd = maximum_drawdown(period_returns)
    
    # Avoid division by zero
    if max_dd == 0:
        return 0.0 if annual_return == risk_free_rate else np.inf
    
    # Calmar ratio = (return - risk_free_rate) / |maximum_drawdown|
    return (annual_return - risk_free_rate) / abs(max_dd)
