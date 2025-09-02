"""
FastAPI routes for forecast statistics endpoints.
"""

from fastapi import APIRouter, HTTPException
import numpy as np
from app.api.schemas import (
    ForecastStatisticRequest,
    RiskFreeRateRequest,
    MinimumAcceptableReturnRequest,
    ConfidenceRequest,
    AssetMetricsRequest,
    TrackingErrorRequest,
    ForecastStatisticResponse
)
from app.api.logic import (
    build_portfolio_returns,
    build_benchmark_returns,
    get_calculation_params
)
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
from app.data.loader import get_cached_data

router = APIRouter()

@router.get("/assets")
async def get_assets():
    """
    Get list of available assets with their names and categories from the HDF5 file.
    """
    try:
        # Get cached data
        returns, asset_names, asset_categories, asset_index_to_category = get_cached_data()
        
        # Create asset list with id, name, and category
        assets = []
        for i, (name, category) in enumerate(zip(asset_names, asset_categories)):
            assets.append({
                "id": i,
                "name": name,
                "category": category
            })
        
        # Sort assets alphabetically by name
        assets.sort(key=lambda x: x["name"])
        
        return {
            "assets": assets,
            "total_count": len(assets),
            "categories": list(set(asset_categories))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving asset data: {str(e)}")

@router.post("/annualised_return", response_model=ForecastStatisticResponse)
async def forecast_annualised_return(request: ForecastStatisticRequest):
    """
    Calculate annualized return for a portfolio.
    
    Uses Compound Annual Growth Rate (CAGR) method.
    """
    try:
        # Build portfolio returns
        portfolio_returns, n_assets_used = build_portfolio_returns(
            request.weights,
            request.rebalance
        )
        
        # Calculate annualized return
        value = annualised_return(portfolio_returns, request.periods_per_year, request.aggregation)
        
        # Prepare response
        params = get_calculation_params(
            weights=request.weights,
            periods_per_year=request.periods_per_year,
            aggregation=request.aggregation,
            rebalance=request.rebalance
        )
        
        return ForecastStatisticResponse(
            value=value,
            method="Compound Annual Growth Rate (CAGR)",
            params=params,
            n_assets_used=n_assets_used,
            timesteps=20,
            simulations=10000,
            aggregation=f"{request.aggregation}_across_simulations"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/annualised_volatility", response_model=ForecastStatisticResponse)
async def forecast_annualised_volatility(request: ForecastStatisticRequest):
    """
    Calculate annualized volatility for a portfolio.
    
    Uses sample standard deviation across time periods, then annualized.
    """
    try:
        # Build portfolio returns
        portfolio_returns, n_assets_used = build_portfolio_returns(
            request.weights,
            request.rebalance
        )
        
        # Calculate annualized volatility
        value = annualised_volatility(portfolio_returns, request.periods_per_year, request.aggregation)
        
        # Prepare response
        params = get_calculation_params(
            weights=request.weights,
            periods_per_year=request.periods_per_year,
            aggregation=request.aggregation,
            rebalance=request.rebalance
        )
        
        return ForecastStatisticResponse(
            value=value,
            method="Sample Standard Deviation Annualized",
            params=params,
            n_assets_used=n_assets_used,
            timesteps=20,
            simulations=10000,
            aggregation=f"{request.aggregation}_across_simulations"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sharpe_ratio", response_model=ForecastStatisticResponse)
async def forecast_sharpe_ratio(request: RiskFreeRateRequest):
    """
    Calculate Sharpe ratio for a portfolio.
    
    Sharpe ratio = (CAGR - Risk Free Rate) / Volatility
    """
    try:
        # Build portfolio returns
        portfolio_returns, n_assets_used = build_portfolio_returns(
            request.weights,
            request.rebalance
        )
        
        # Calculate Sharpe ratio
        value = sharpe_ratio(
            portfolio_returns, 
            request.risk_free_rate, 
            request.periods_per_year,
            request.aggregation
        )
        
        # Prepare response
        params = get_calculation_params(
            weights=request.weights,
            periods_per_year=request.periods_per_year,
            aggregation=request.aggregation,
            rebalance=request.rebalance,
            risk_free_rate=request.risk_free_rate
        )
        
        return ForecastStatisticResponse(
            value=value,
            method="Sharpe Ratio: (Return - RFR) / Volatility",
            params=params,
            n_assets_used=n_assets_used,
            timesteps=20,
            simulations=10000,
            aggregation=f"{request.aggregation}_across_simulations"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/tracking_error", response_model=ForecastStatisticResponse)
async def forecast_tracking_error(request: TrackingErrorRequest):
    """
    Calculate tracking error between portfolio and benchmark.
    
    Tracking error = Standard deviation of excess returns
    """
    try:
        # Build portfolio returns
        portfolio_returns, n_assets_used = build_portfolio_returns(
            request.weights,
            request.rebalance
        )
        
        # Build benchmark returns
        benchmark_returns = build_benchmark_returns(
            request.benchmark_weights
        )
        
        # Calculate tracking error
        value = tracking_error(
            portfolio_returns, 
            benchmark_returns, 
            request.periods_per_year,
            request.aggregation
        )
        
        # Prepare response
        params = get_calculation_params(
            weights=request.weights,
            periods_per_year=request.periods_per_year,
            aggregation=request.aggregation,
            rebalance=request.rebalance,
            benchmark_weights=request.benchmark_weights
        )
        
        return ForecastStatisticResponse(
            value=value,
            method="Standard Deviation of Excess Returns",
            params=params,
            n_assets_used=n_assets_used,
            timesteps=20,
            simulations=10000,
            aggregation=f"{request.aggregation}_across_simulations"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/downside_deviation", response_model=ForecastStatisticResponse)
async def forecast_downside_deviation(request: MinimumAcceptableReturnRequest):
    """
    Calculate downside deviation for a portfolio.
    
    Downside deviation = sqrt(mean(min(return - MAR, 0)^2))
    """
    try:
        # Build portfolio returns
        portfolio_returns, n_assets_used = build_portfolio_returns(
            request.weights,
            request.rebalance
        )
        
        # Calculate downside deviation
        value = downside_deviation(
            portfolio_returns, 
            request.minimum_acceptable_return, 
            request.periods_per_year,
            request.aggregation
        )
        
        # Prepare response
        params = get_calculation_params(
            weights=request.weights,
            periods_per_year=request.periods_per_year,
            aggregation=request.aggregation,
            rebalance=request.rebalance,
            minimum_acceptable_return=request.minimum_acceptable_return
        )
        
        return ForecastStatisticResponse(
            value=value,
            method="Root Mean Square of Downside Returns",
            params=params,
            n_assets_used=n_assets_used,
            timesteps=20,
            simulations=10000,
            aggregation=f"{request.aggregation}_across_simulations"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/value_at_risk", response_model=ForecastStatisticResponse)
async def forecast_value_at_risk(request: ConfidenceRequest):
    """
    Calculate Value at Risk (VaR) for a portfolio.
    
    VaR = Quantile of 1-period return distribution at specified confidence level
    """
    try:
        # Build portfolio returns
        portfolio_returns, n_assets_used = build_portfolio_returns(
            request.weights,
            request.rebalance
        )
        
        # Calculate VaR with specified method
        value = value_at_risk(portfolio_returns, request.confidence, request.var_type)
        
        # Prepare response
        params = get_calculation_params(
            weights=request.weights,
            periods_per_year=request.periods_per_year,
            rebalance=request.rebalance,
            var_type=request.var_type,
            confidence=request.confidence
        )
        
        return ForecastStatisticResponse(
            value=value,
            method=f"Value at Risk ({request.confidence*100:.0f}% confidence, {request.var_type})",
            params=params,
            n_assets_used=n_assets_used,
            timesteps=20,
            simulations=10000,
            aggregation="quantile_across_all_data"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/conditional_value_at_risk", response_model=ForecastStatisticResponse)
async def forecast_conditional_value_at_risk(request: ConfidenceRequest):
    """
    Calculate Conditional Value at Risk (CVaR) for a portfolio.
    
    CVaR = Expected loss when exceeding VaR threshold at specified confidence level
    """
    try:
        # Build portfolio returns
        portfolio_returns, n_assets_used = build_portfolio_returns(
            request.weights,
            request.rebalance
        )
        
        # Calculate CVaR with specified method
        value = conditional_value_at_risk(portfolio_returns, request.confidence, request.var_type)
        
        # Prepare response
        params = get_calculation_params(
            weights=request.weights,
            periods_per_year=request.periods_per_year,
            rebalance=request.rebalance,
            var_type=request.var_type,
            confidence=request.confidence
        )
        
        return ForecastStatisticResponse(
            value=value,
            method=f"Conditional Value at Risk ({request.confidence*100:.0f}% confidence, {request.var_type})",
            params=params,
            n_assets_used=n_assets_used,
            timesteps=20,
            simulations=10000,
            aggregation="mean_of_tail_distribution"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/maximum_drawdown", response_model=ForecastStatisticResponse)
async def forecast_maximum_drawdown(request: ForecastStatisticRequest):
    """
    Calculate maximum drawdown for a portfolio.
    
    Maximum drawdown = Largest peak-to-trough decline
    """
    try:
        # Build portfolio returns
        portfolio_returns, n_assets_used = build_portfolio_returns(
            request.weights,
            request.rebalance
        )
        
        # Calculate maximum drawdown
        value = maximum_drawdown(portfolio_returns, request.aggregation)
        
        # Prepare response
        params = get_calculation_params(
            weights=request.weights,
            periods_per_year=request.periods_per_year,
            aggregation=request.aggregation,
            rebalance=request.rebalance
        )
        
        return ForecastStatisticResponse(
            value=value,
            method="Peak-to-Trough Maximum Decline (Positive Magnitude)",
            params=params,
            n_assets_used=n_assets_used,
            timesteps=20,
            simulations=10000,
            aggregation=f"{request.aggregation}_across_simulations"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/projected_values")
async def projected_values_endpoint(request: ForecastStatisticRequest):
    """Calculate projected portfolio values over time with percentiles."""
    try:
        # Build portfolio returns
        portfolio_returns, n_assets_used = build_portfolio_returns(
            request.weights,
            request.rebalance
        )
        
        # Calculate projected values using the portfolio service
        from app.services.portfolio import calculate_projected_values
        
        # Get initial portfolio value from request (default to 100000 if not provided)
        initial_value = getattr(request, 'initial_value', 100000.0)
        
        projected_values = calculate_projected_values(
            portfolio_returns, 
            initial_value, 
            request.rebalance
        )
        
        # Prepare response
        params = get_calculation_params(
            weights=request.weights,
            periods_per_year=request.periods_per_year,
            aggregation=request.aggregation,
            rebalance=request.rebalance,
            initial_value=initial_value
        )
        
        return {
            "projected_values": projected_values,
            "method": "Projected Portfolio Values with Percentiles",
            "params": params,
            "n_assets_used": n_assets_used,
            "timesteps": portfolio_returns.shape[0],
            "simulations": portfolio_returns.shape[1],
            "rebalance": request.rebalance
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/asset_metrics")
async def asset_metrics_endpoint(request: AssetMetricsRequest):
    """Calculate per-asset annualised returns, volatilities, and correlation matrix."""
    try:
        # Get returns data
        returns, asset_names, asset_categories, asset_index_to_category = get_cached_data()
        
        # Calculate asset metrics using the portfolio service
        from app.services.portfolio import calculate_asset_metrics
        
        # Convert weights to numpy array
        weights_array = np.array(request.weights)
        
        asset_metrics = calculate_asset_metrics(
            returns=returns, weights=weights_array,
            periods_per_year=request.periods_per_year,
            is_log=request.is_log,
            aggregation=request.aggregation,
            corr_method=request.corr_method
        )
        
        # Prepare response
        params = get_calculation_params(
            weights=[],  # Not applicable for asset metrics
            periods_per_year=request.periods_per_year,
            aggregation=request.aggregation,
            is_log=request.is_log,
            corr_method=request.corr_method
        )
        
        return {
            "asset_metrics": asset_metrics["asset_metrics"],
            "correlation_matrix": asset_metrics["correlation_matrix"],
            "method": "Asset-Level Annualised Returns, Volatilities, and Correlations",
            "params": params,
            "n_assets": len(asset_names),
            "timesteps": returns.shape[1],
            "simulations": returns.shape[2]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))