# Portfolio Analysis API & Dashboard

## Quick Start

1) Prerequisites
- Python 3.10+ with venv
- Node 18+

2) Using Makefile (recommended)
```bash
# From the project root
make install-backend
make install-frontend
make preflight
make backend    # starts FastAPI on 127.0.0.1:8000
make frontend   # starts CRA dev server on :3000
make test       # runs backend tests
```
Backend: http://localhost:8000 (Swagger at /docs)
Frontend: http://localhost:3000
Preflight checks data files under `data/`, venv presence, and port 8000 availability.

3) Backend (FastAPI)
```bash
# From the project root directory
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
API runs on http://localhost:8000 (Swagger UI at /docs)

**Note**: Use `python3 -m uvicorn app.main:app --reload` instead of `python -m app.main` for proper FastAPI server startup.

4) Frontend (React)
```bash
# From the project root directory (jacobi-strategies/frontend)
cd frontend
npm install
npm start
```
App runs on http://localhost:3000 with proxy to the API.

5) Tests
```bash
# From the project root directory (jacobi-strategies/backend)
cd backend
pytest -q
```

## Project Structure
```
backend/         FastAPI app, data loader, stats logic, tests
frontend/        React dashboard (CRA) with Recharts
data/            base_simulation.hdf5, asset_categories.csv
```

## Data
- base_simulation.hdf5: contains `asset_names` and `asset_class_projections/simulated_return` with shape (25 assets, 20 years, 10,000 simulations)
- asset_categories.csv: columns `asset_name,category`

Place both files under the repository `data/` directory.

## API Overview
Base: http://localhost:8000
- GET `/`               API info
- GET `/health`         Health check
- GET `/docs`           Swagger UI

Forecast statistics (POST `/forecast_statistic/...`):
- `annualised_return`
- `annualised_volatility`
- `sharpe_ratio`
- `tracking_error`
- `downside_deviation`
- `value_at_risk`
- `conditional_value_at_risk`
- `maximum_drawdown`

Additional endpoints:
- GET `/forecast_statistic/assets`
- POST `/forecast_statistic/projected_values`
- POST `/forecast_statistic/asset_metrics`

Request (example):
```json
{
  "weights": [0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04],
  "periods_per_year": 1.0,
  "aggregation": "mean",
  "rebalance": "periodic",
  "initial_value": 100000.0,
  "include_categories": ["Equity"],
  "exclude_categories": null
}
```

Notes:
- `weights` must have 25 items and sum to 1.0
- `include_categories`/`exclude_categories` are optional and cannot overlap
- `maximum_drawdown` returns a positive magnitude (e.g., 0.23 for 23%)

## Financial Assumptions
- Returns in the HDF5 are annual simple returns; annualisation uses standard factors (mean unchanged, volatility × √periods_per_year).
- Sharpe ratio uses CAGR per simulation minus an annual risk-free rate, divided by annualised volatility; aggregation across simulations uses mean or median.
- VaR/CVaR are computed on simulated return distributions:
  - pooled: quantile of all T×S 1-period returns; CVaR is mean of the loss tail.
  - cumulative: quantile of terminal multi-period cumulative return; CVaR is mean of the loss tail.
- Maximum drawdown is reported as positive magnitude of peak-to-trough decline per simulation, then aggregated.
- Weights are long-only, non-negative, and must sum to 1.0; when category filters are applied, excluded assets are dropped and the remaining weights are renormalised.
- Rebalancing:
  - periodic: apply weights each period
  - none: buy-and-hold with drifting weights
- Risk-free rate is an annual rate and applied consistently with annualisation.
- Correlations can be computed pooled (all observations), year-by-year, or simulation-by-simulation with Fisher z-averaging for stability.

Notes and conventions:
- Dataset periodicity is annual; using periods_per_year ≠ 1 is a modeling assumption for scaling, not a change in data frequency.
- VaR and CVaR are reported as negative returns (loss thresholds). The API may present magnitudes for certain metrics (e.g., maximum drawdown) for readability; the underlying functions use conventional signs.

## Frontend Overview
Features:
- Allocation editor with selection and total validation
- Charts: individual asset pie, projected values with percentiles
- Metrics: volatility, downside deviation, VaR, CVaR, maximum drawdown
- Asset metrics and correlation matrix

Configuration:
- API calls use relative URLs and CRA proxy (`frontend/package.json`)

## Development Notes
- Backend resolves data paths at startup; ensure `data/` exists and contains the files listed above.
- CORS is permissive for development; restrict appropriately for production.

## Troubleshooting

### Backend Issues
- **Port already in use**: If you get "Address already in use" error, the backend might already be running. Check if port 8000 is occupied.
- **Virtual environment**: Ensure you're in the correct directory and have activated the virtual environment: `source .venv/bin/activate`
- **Python version**: Use `python3` explicitly if you have multiple Python versions installed

### Frontend Issues
- **API connection**: Ensure the backend is running on port 8000 before starting the frontend
- **Proxy errors**: The frontend uses a proxy to the backend API. Check that both services are running on their respective ports.

### Common Commands
```bash
# Check if backend is running
curl http://localhost:8000/health

# Kill process on port 8000 (if needed)
lsof -ti:8000 | xargs kill -9

# Restart backend (from project root)
cd backend && python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Check frontend status (from project root)
cd frontend && npm run build
```

## Packaging
- When zipping for submission, exclude `node_modules` and build artifacts. Include: this README, `backend/`, `frontend/`, and `data/`.

## License
For assessment use only.

