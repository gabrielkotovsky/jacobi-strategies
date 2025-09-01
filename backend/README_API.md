# Portfolio Analysis API

A FastAPI-based REST API for portfolio statistics and risk metrics using Monte Carlo simulations.

## 🚀 Features

- **8 Portfolio Statistics Endpoints**: Annualized return, volatility, Sharpe ratio, tracking error, downside deviation, VaR, CVaR, and maximum drawdown
- **Asset Category Filtering**: Include/exclude assets by category
- **Flexible Period Handling**: Support for annual, quarterly, monthly, and daily data
- **Real Monte Carlo Data**: Uses actual simulation data (25 assets × 20 periods × 10,000 simulations)
- **Input Validation**: Comprehensive Pydantic validation for all inputs
- **Auto-generated Documentation**: Swagger UI and ReDoc interfaces

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── api/
│   │   ├── routes.py        # API endpoint definitions
│   │   ├── schemas.py       # Request/response models
│   │   └── logic.py         # Portfolio construction helpers
│   ├── logic/
│   │   └── stats.py         # Statistical functions
│   ├── data/
│   │   └── loader.py        # Data loading and caching
│   └── schemas/
│       └── inputs.py        # Input validation schemas
├── requirements.txt          # Python dependencies
├── test_api.py              # API testing script
└── README_API.md            # This file
```

## 🛠️ Installation

1. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Ensure data files exist**:
   - `../data/base_simulation.hdf5` - Monte Carlo simulation data
   - `../data/asset_categories.csv` - Asset category mappings

## 🚀 Running the API

### Development Mode
```bash
cd backend
python -m app.main
```

The API will start on `http://localhost:8000`

### Production Mode
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📚 API Endpoints

### Base Endpoints
- `GET /` - API information and available endpoints
- `GET /health` - Health check
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

### Forecast Statistics Endpoints

All endpoints are available under `/forecast_statistic/`:

#### 1. Annualized Return
```http
POST /forecast_statistic/annualised_return
```
**Request Body**:
```json
{
  "weights": [0.04, 0.04, 0.04, ...],  // 25 weights summing to 1.0
  "include_categories": ["Equity"],      // Optional: include only these categories
  "exclude_categories": ["Bond"],        // Optional: exclude these categories
  "periods_per_year": 1.0               // Annualization factor
}
```

#### 2. Annualized Volatility
```http
POST /forecast_statistic/annualised_volatility
```
Same request format as annualized return.

#### 3. Sharpe Ratio
```http
POST /forecast_statistic/sharpe_ratio
```
**Request Body**:
```json
{
  "weights": [0.04, 0.04, 0.04, ...],
  "include_categories": null,
  "exclude_categories": null,
  "periods_per_year": 1.0,
  "risk_free_rate": 0.02                // Annual risk-free rate
}
```

#### 4. Tracking Error
```http
POST /forecast_statistic/tracking_error
```
**Request Body**:
```json
{
  "weights": [0.04, 0.04, 0.04, ...],
  "include_categories": null,
  "exclude_categories": null,
  "periods_per_year": 1.0,
  "benchmark_weights": [0.04, 0.04, 0.04, ...]  // Benchmark portfolio weights
}
```

#### 5. Downside Deviation
```http
POST /forecast_statistic/downside_deviation
```
**Request Body**:
```json
{
  "weights": [0.04, 0.04, 0.04, ...],
  "include_categories": null,
  "exclude_categories": null,
  "periods_per_year": 1.0,
  "minimum_acceptable_return": 0.0      // MAR threshold
}
```

#### 6. Value at Risk (VaR)
```http
POST /forecast_statistic/value_at_risk
```
**Request Body**:
```json
{
  "weights": [0.04, 0.04, 0.04, ...],
  "include_categories": null,
  "exclude_categories": null,
  "periods_per_year": 1.0,
  "confidence": 0.95                    // Confidence level (0 < conf < 1)
}
```

#### 7. Conditional Value at Risk (CVaR)
```http
POST /forecast_statistic/conditional_value_at_risk
```
Same request format as VaR.

#### 8. Maximum Drawdown
```http
POST /forecast_statistic/maximum_drawdown
```
Same request format as annualized return.

## 📊 Response Format

All endpoints return the same response structure:

```json
{
  "value": 0.0685,                      // Calculated statistic value
  "method": "Compound Annual Growth Rate (CAGR)",
  "params": {                            // Parameters used in calculation
    "weights": [0.04, 0.04, 0.04, ...],
    "periods_per_year": 1.0,
    "include_categories": null,
    "exclude_categories": null
  },
  "n_assets_used": 25,                   // Number of assets used
  "timesteps": 20,                       // Number of time periods
  "simulations": 10000                   // Number of Monte Carlo simulations
}
```

## 🔧 Configuration

### Asset Categories
The API supports filtering assets by category. Available categories depend on your `asset_categories.csv` file.

### Period Annualization
- `periods_per_year = 1.0` - Annual data (default)
- `periods_per_year = 4.0` - Quarterly data
- `periods_per_year = 12.0` - Monthly data
- `periods_per_year = 252.0` - Daily data

## 🧪 Testing

Run the test script to verify all endpoints:

```bash
cd backend
python test_api.py
```

This will test:
- Health check and root endpoints
- Annualized return calculation
- Sharpe ratio calculation
- Value at Risk calculation
- Category filtering functionality

## 📖 API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs` - Interactive API documentation
- **ReDoc**: `http://localhost:8000/redoc` - Alternative documentation view

## 🚨 Error Handling

The API provides comprehensive error handling:
- **400 Bad Request**: Invalid input parameters
- **500 Internal Server Error**: Server-side errors

All errors include descriptive messages to help debug issues.

## 🔒 Security Notes

- CORS is enabled for all origins (configure appropriately for production)
- Input validation prevents malicious data injection
- No authentication is implemented (add as needed for production)

## 🚀 Production Deployment

For production deployment:

1. **Configure CORS** appropriately for your domain
2. **Add authentication** if required
3. **Use a production WSGI server** like Gunicorn
4. **Set environment variables** for configuration
5. **Add logging** and monitoring
6. **Use HTTPS** for secure communication

## 📞 Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review the error messages in the response
3. Check the server logs for detailed error information
4. Verify your input data format matches the schemas
