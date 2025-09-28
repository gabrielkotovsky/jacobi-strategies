# Backend Architecture & File Interactions

## Overview
This document shows the interaction patterns and dependencies between backend files in the Portfolio Analysis API.

## File Interaction Chart

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                FastAPI Application                              │
│                                    main.py                                     │
└─────────────────────────┬───────────────────────────────────────────────────────┘
                          │
                          │ includes router
                          ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              API Layer                                          │
│                               routes.py                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ • GET /forecast_statistic/assets                                        │   │
│  │ • POST /forecast_statistic/annualised_return                           │   │
│  │ • POST /forecast_statistic/annualised_volatility                       │   │
│  │ • POST /forecast_statistic/sharpe_ratio                                │   │
│  │ • POST /forecast_statistic/tracking_error                              │   │
│  │ • POST /forecast_statistic/downside_deviation                          │   │
│  │ • POST /forecast_statistic/value_at_risk                               │   │
│  │ • POST /forecast_statistic/conditional_value_at_risk                   │   │
│  │ • POST /forecast_statistic/maximum_drawdown                            │   │
│  │ • POST /forecast_statistic/projected_values                            │   │
│  │ • POST /forecast_statistic/asset_metrics                               │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────────────────────────┘
                          │
                          │ imports & calls
                          ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            Business Logic Layer                                 │
│                              logic.py                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ • build_portfolio_returns()                                            │   │
│  │ • build_benchmark_returns()                                            │   │
│  │ • get_calculation_params()                                             │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────────────────────────┘
                          │
                          │ imports & calls
                          ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            Services Layer                                       │
│                            portfolio.py                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ • portfolio_period_returns()                                           │   │
│  │ • _calculate_buy_and_hold_returns()                                    │   │
│  │ • to_cumulative_returns()                                              │   │
│  │ • calculate_annualized_metrics()                                       │   │
│  │ • portfolio_analysis_pipeline()                                        │   │
│  │ • validate_portfolio_inputs()                                          │   │
│  │ • calculate_projected_values()                                         │   │
│  │ • calculate_asset_metrics()                                            │   │
│  │ • _fisher_average_correlations()                                       │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────────────────────────┘
                          │
                          │ imports & calls
                          ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            Statistics Layer                                     │
│                              stats.py                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ • annualised_return()                                                  │   │
│  │ • annualised_volatility()                                              │   │
│  │ • sharpe_ratio()                                                       │   │
│  │ • tracking_error()                                                     │   │
│  │ • downside_deviation()                                                 │   │
│  │ • value_at_risk()                                                      │   │
│  │ • conditional_value_at_risk()                                          │   │
│  │ • maximum_drawdown()                                                   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────────────────────────┘
                          │
                          │ imports & calls
                          ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            Data Layer                                           │
│                              loader.py                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ • load_data()                                                          │   │
│  │ • load_asset_categories()                                              │   │
│  │ • build_asset_index_to_category()                                      │   │
│  │ • initialize_cache()                                                   │   │
│  │ • get_cached_data()                                                    │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────────────────────────┘
                          │
                          │ reads from
                          ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            External Data                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ • base_simulation.hdf5 (Monte Carlo simulation data)                   │   │
│  │ • asset_categories.csv (Asset categorization)                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                            Schema Layer                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ schemas/inputs.py                                                      │   │
│  │ • BaseInputs                                                           │   │
│  │ • PortfolioRequest                                                     │   │
│  │ • BatchPortfolioRequest                                                │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ api/schemas.py                                                         │   │
│  │ • ForecastStatisticRequest                                             │   │
│  │ • RiskFreeRateRequest                                                  │   │
│  │ • MinimumAcceptableReturnRequest                                       │   │
│  │ • ConfidenceRequest                                                    │   │
│  │ • AssetMetricsRequest                                                  │   │
│  │ • TrackingErrorRequest                                                 │   │
│  │ • ForecastStatisticResponse                                            │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Detailed Interaction Patterns

### 1. Request Flow
```
Client Request → routes.py → logic.py → portfolio.py → stats.py → loader.py → Data Files
```

### 2. Data Flow
```
HDF5/CSV Files → loader.py (cache) → portfolio.py → stats.py → logic.py → routes.py → Client
```

### 3. Validation Flow
```
Client Request → api/schemas.py (Pydantic validation) → routes.py → Business Logic
```

## Key Dependencies

### main.py
- **Imports**: `routes.py`, `loader.py`
- **Responsibilities**: FastAPI app setup, CORS, startup event, data initialization
- **Dependencies**: None (entry point)

### routes.py
- **Imports**: `api/schemas.py`, `logic.py`, `stats.py`, `loader.py`, `services/portfolio.py`
- **Responsibilities**: HTTP endpoints, request/response handling, error management
- **Dependencies**: All other modules (central orchestrator)

### logic.py
- **Imports**: `loader.py`, `stats.py`, `services/portfolio.py`
- **Responsibilities**: Portfolio construction, asset filtering, parameter preparation
- **Dependencies**: Data layer, statistics layer, services layer

### portfolio.py (services)
- **Imports**: `loader.py` (for asset names in asset metrics)
- **Responsibilities**: Portfolio calculations, rebalancing logic, projected values, asset metrics
- **Dependencies**: Data layer (minimal)

### stats.py
- **Imports**: None (pure NumPy functions)
- **Responsibilities**: Statistical calculations (VaR, CVaR, Sharpe ratio, etc.)
- **Dependencies**: None (stateless functions)

### loader.py
- **Imports**: `schemas/inputs.py` (for setting asset count)
- **Responsibilities**: Data loading, caching, file I/O
- **Dependencies**: External data files, schema validation

### api/schemas.py
- **Imports**: None (Pydantic models)
- **Responsibilities**: Request/response validation, API documentation
- **Dependencies**: None (standalone validation layer)

### schemas/inputs.py
- **Imports**: None (Pydantic models)
- **Responsibilities**: Base input validation, portfolio request schemas
- **Dependencies**: None (standalone validation layer)

## Data Flow Examples

### Example 1: Annualised Return Calculation
```
1. Client POST /forecast_statistic/annualised_return
2. routes.py receives request
3. api/schemas.py validates ForecastStatisticRequest
4. routes.py calls logic.py build_portfolio_returns()
5. logic.py calls loader.py get_cached_data()
6. logic.py calls portfolio.py portfolio_period_returns()
7. routes.py calls stats.py annualised_return()
8. routes.py returns ForecastStatisticResponse
```

### Example 2: Asset Metrics Calculation
```
1. Client POST /forecast_statistic/asset_metrics
2. routes.py receives request
3. api/schemas.py validates AssetMetricsRequest
4. routes.py calls portfolio.py calculate_asset_metrics()
5. portfolio.py calls loader.py get_cached_data()
6. portfolio.py performs calculations internally
7. routes.py returns asset metrics and correlation matrix
```

### Example 3: Data Initialization (Startup)
```
1. main.py startup event triggers
2. main.py calls loader.py initialize_cache()
3. loader.py loads HDF5 and CSV files
4. loader.py sets asset count in schemas/inputs.py
5. Cache is ready for API requests
```

## Architecture Benefits

### 1. Separation of Concerns
- **API Layer**: HTTP handling, validation, error responses
- **Business Logic**: Portfolio construction, parameter preparation
- **Services**: Complex calculations, portfolio analysis
- **Statistics**: Pure mathematical functions
- **Data**: File I/O, caching, data management
- **Schemas**: Input/output validation

### 2. Dependency Direction
- Dependencies flow downward (API → Logic → Services → Stats → Data)
- No circular dependencies
- Clear separation between layers

### 3. Testability
- Each layer can be tested independently
- Pure functions in stats.py are easily unit tested
- Mock data can be injected at any layer

### 4. Maintainability
- Changes to statistical formulas only affect stats.py
- API changes only affect routes.py and schemas
- Data format changes only affect loader.py

### 5. Performance
- Data loaded once at startup and cached
- Vectorized NumPy operations in stats.py
- Efficient portfolio calculations in services layer

## Error Handling Flow
```
Data Loading Error → loader.py → main.py (startup failure)
Validation Error → api/schemas.py → routes.py → HTTP 422
Business Logic Error → logic.py → routes.py → HTTP 400
Calculation Error → stats.py → routes.py → HTTP 400
```

This architecture provides a clean, maintainable, and scalable foundation for the portfolio analysis API.
