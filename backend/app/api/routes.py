"""
FastAPI routes for forecast statistics endpoints.
"""

from fastapi import APIRouter, HTTPException
from app.api.schemas import (
    ForecastStatisticRequest,
    RiskFreeRateRequest,
    MinimumAcceptableReturnRequest,
    ConfidenceRequest,
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
            request.include_categories,
            request.exclude_categories
        )
        
        # Calculate annualized return
        value = annualised_return(portfolio_returns, request.periods_per_year)
        
        # Prepare response
        params = get_calculation_params(
            weights=request.weights,
            include_categories=request.include_categories,
            exclude_categories=request.exclude_categories,
            periods_per_year=request.periods_per_year
        )
        
        return ForecastStatisticResponse(
            value=value,
            method="Compound Annual Growth Rate (CAGR)",
            params=params,
            n_assets_used=n_assets_used,
            timesteps=20,
            simulations=10000
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
            request.include_categories,
            request.exclude_categories
        )
        
        # Calculate annualized volatility
        value = annualised_volatility(portfolio_returns, request.periods_per_year)
        
        # Prepare response
        params = get_calculation_params(
            weights=request.weights,
            include_categories=request.include_categories,
            exclude_categories=request.exclude_categories,
            periods_per_year=request.periods_per_year
        )
        
        return ForecastStatisticResponse(
            value=value,
            method="Sample Standard Deviation Annualized",
            params=params,
            n_assets_used=n_assets_used,
            timesteps=20,
            simulations=10000
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
            request.include_categories,
            request.exclude_categories
        )
        
        # Calculate Sharpe ratio
        value = sharpe_ratio(
            portfolio_returns, 
            request.risk_free_rate, 
            request.periods_per_year
        )
        
        # Prepare response
        params = get_calculation_params(
            weights=request.weights,
            include_categories=request.include_categories,
            exclude_categories=request.exclude_categories,
            periods_per_year=request.periods_per_year,
            risk_free_rate=request.risk_free_rate
        )
        
        return ForecastStatisticResponse(
            value=value,
            method="Sharpe Ratio: (Return - RFR) / Volatility",
            params=params,
            n_assets_used=n_assets_used,
            timesteps=20,
            simulations=10000
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
            request.include_categories,
            request.exclude_categories
        )
        
        # Build benchmark returns
        benchmark_returns = build_benchmark_returns(
            request.benchmark_weights,
            request.include_categories,
            request.exclude_categories
        )
        
        # Calculate tracking error
        value = tracking_error(
            portfolio_returns, 
            benchmark_returns, 
            request.periods_per_year
        )
        
        # Prepare response
        params = get_calculation_params(
            weights=request.weights,
            include_categories=request.include_categories,
            exclude_categories=request.exclude_categories,
            periods_per_year=request.periods_per_year,
            benchmark_weights=request.benchmark_weights
        )
        
        return ForecastStatisticResponse(
            value=value,
            method="Standard Deviation of Excess Returns",
            params=params,
            n_assets_used=n_assets_used,
            timesteps=20,
            simulations=10000
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
            request.include_categories,
            request.exclude_categories
        )
        
        # Calculate downside deviation
        value = downside_deviation(
            portfolio_returns, 
            request.minimum_acceptable_return, 
            request.periods_per_year
        )
        
        # Prepare response
        params = get_calculation_params(
            weights=request.weights,
            include_categories=request.include_categories,
            exclude_categories=request.exclude_categories,
            periods_per_year=request.periods_per_year,
            minimum_acceptable_return=request.minimum_acceptable_return
        )
        
        return ForecastStatisticResponse(
            value=value,
            method="Root Mean Square of Downside Returns",
            params=params,
            n_assets_used=n_assets_used,
            timesteps=20,
            simulations=10000
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/value_at_risk", response_model=ForecastStatisticResponse)
async def forecast_value_at_risk(request: ConfidenceRequest):
    """
    Calculate Value at Risk (VaR) for a portfolio.
    
    VaR = Quantile of return distribution at specified confidence level
    """
    try:
        # Build portfolio returns
        portfolio_returns, n_assets_used = build_portfolio_returns(
            request.weights,
            request.include_categories,
            request.exclude_categories
        )
        
        # Calculate VaR
        value = value_at_risk(portfolio_returns, request.confidence)
        
        # Prepare response
        params = get_calculation_params(
            weights=request.weights,
            include_categories=request.include_categories,
            exclude_categories=request.exclude_categories,
            periods_per_year=request.periods_per_year,
            confidence=request.confidence
        )
        
        return ForecastStatisticResponse(
            value=value,
            method=f"Value at Risk ({request.confidence*100:.0f}% confidence)",
            params=params,
            n_assets_used=n_assets_used,
            timesteps=20,
            simulations=10000
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/conditional_value_at_risk", response_model=ForecastStatisticResponse)
async def forecast_conditional_value_at_risk(request: ConfidenceRequest):
    """
    Calculate Conditional Value at Risk (CVaR) for a portfolio.
    
    CVaR = Expected loss when exceeding VaR threshold
    """
    try:
        # Build portfolio returns
        portfolio_returns, n_assets_used = build_portfolio_returns(
            request.weights,
            request.include_categories,
            request.exclude_categories
        )
        
        # Calculate CVaR
        value = conditional_value_at_risk(portfolio_returns, request.confidence)
        
        # Prepare response
        params = get_calculation_params(
            weights=request.weights,
            include_categories=request.include_categories,
            exclude_categories=request.exclude_categories,
            periods_per_year=request.periods_per_year,
            confidence=request.confidence
        )
        
        return ForecastStatisticResponse(
            value=value,
            method=f"Conditional Value at Risk ({request.confidence*100:.0f}% confidence)",
            params=params,
            n_assets_used=n_assets_used,
            timesteps=20,
            simulations=10000
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
            request.include_categories,
            request.exclude_categories
        )
        
        # Calculate maximum drawdown
        value = maximum_drawdown(portfolio_returns)
        
        # Prepare response
        params = get_calculation_params(
            weights=request.weights,
            include_categories=request.include_categories,
            exclude_categories=request.exclude_categories,
            periods_per_year=request.periods_per_year
        )
        
        return ForecastStatisticResponse(
            value=value,
            method="Peak-to-Trough Maximum Decline",
            params=params,
            n_assets_used=n_assets_used,
            timesteps=20,
            simulations=10000
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))