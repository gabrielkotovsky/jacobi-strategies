# Investment Engineer Technical Test

This two-part technical assessment is designed to evaluate your Python programming and problem-solving skills. In this test, you will:

1. Build a local API that computes portfolio statistics using simulated asset-class projections.
2. Build a lightweight dashboard that allows a user to construct a portfolio and view its performance and risk metrics.

Use Python for the backend (Flask or FastAPI) and React or Plotly Dash for the frontend. Submit your project as a zipped folder. 

We value clean design and well-considered implementation choices. Rather than aiming for a perfect solution, we’re more interested in how you approach problems, make decisions, and balance trade-offs. Practical, thoughtful solutions are encouraged. While the core requirements are clearly defined, we encourage you to go above and beyond where you see opportunities to improve usability, robustness, or clarity. Thoughtful enhancements in design, documentation, testing, user experience, and the depth and presentation of calculated metrics will be recognised and appreciated.

## Data
You will use two simple inputs located in `Data/`:
- `base_simulation.hdf5` — a simulation file in HDF5 format containing
  - `asset_names`: a list of asset names. The order of entries in this list corresponds directly to the order of the assets dimension in the simulation array.
  - `asset_class_projections/simulated_return` array of shape `(assets, years, paths)`.
- `asset_categories.csv` — the asset groupings
  - Columns: `asset_name,category`. Use this to build grouped allocation charts.

## Part 1 — Forecast Statistics API 
Implement API endpoints to calculate forecast portfolio statistics. Each endpoint should support user-defined portfolio allocations, and any additional parameters relevant to that specific endpoint. While batch handling of portfolios is encouraged for flexibility, it is not a strict requirement. You are free to design the input and output schema as you see fit.

Endpoints
- POST `/forecast_statistic/annualised_return`
- POST `/forecast_statistic/annualised_volatility`
- POST `/forecast_statistic/sharpe_ratio`
- POST `/forecast_statistic/tracking_error`
- POST `/forecast_statistic/downside_deviation`
- POST `/forecast_statistic/value_at_risk`
- POST `/forecast_statistic/conditional_value_at_risk`
- POST `/forecast_statistic/maximum_drawdown`


Error handling
- Validate inputs and provide clear, actionable messages.

## Part 2 — Dashboard
Build a lightweight dashboard (React or Plotly Dash) that integrates with your API.

Must include
- Portfolio inputs:
  - Grid/table to input allocations (one row per asset with weight input), with functionality to add or remove assets, and display real-time total allocation.
  - Text box to input the starting portfolio value.

- Allocation charts:
  - Pie chart showing allocations by individual asset.
  - Bar chart showing allocations grouped by asset category (from asset_categories.csv).

- Projected portfolio value chart that displays projected portfolio values across years at key percentiles (e.g., 1st, 5th, 25th, 50th, 75th, 95th, 99th).

- Portfolio metrics table that displays the following performance and risk measures:
  - Annualised volatility
  - Annualised downside deviation
  - 5% Value at Risk (VaR) 
  - 5% Conditional Value at Risk (CVaR)
  - Maximum drawdown

- Asset metrics tables to support additional analysis:
  - Annualised return and volatility per asset 
  - Asset return correlation matrix

## Deliverable
- A zip file containing both backend and frontend source code, along with clear local setup and run instructions. Your submission must include unit tests for key components. This helps us assess how you approach reliability and maintainability. Tests should be easy to run and demonstrate coverage of core functionality and edge cases.

## Assumptions
- You are encouraged to make any reasonable assumptions necessary to complete the task. Please document them clearly where relevant.

## Use of AI tools 
- The use of AI tools is permitted during this assessment. However, please ensure that all submitted work reflects your own understanding and decision-making.

