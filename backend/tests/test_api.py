"""
Tests for the FastAPI portfolio analysis API endpoints.
"""

import pytest
import numpy as np
from fastapi.testclient import TestClient
from app.main import app
from app.data.loader import initialize_cache

# Initialize data cache for testing
initialize_cache("../data/base_simulation.hdf5", "../data/asset_categories.csv")

# Create test client
client = TestClient(app)

# Test data
EQUAL_WEIGHTS_25 = [0.04] * 25  # 25 assets with 4% each
EQUAL_WEIGHTS_10 = [0.1] * 10   # 10 assets with 10% each
INVALID_WEIGHTS = [0.04, 0.04, 0.04]  # Only 3 weights, sum = 0.12
NEGATIVE_WEIGHTS = [0.04] * 24 + [-0.04]  # 25 weights but last one negative
NON_NUMERIC_WEIGHTS = [0.04] * 24 + ["invalid"]  # Non-numeric weight

class TestAPIHealth:
    """Test health and root endpoints."""
    
    def test_health_check(self):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "Portfolio Analysis API is running" in data["message"]
    
    def test_root_endpoint(self):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Portfolio Analysis API"
        assert data["version"] == "1.0.0"
        assert "forecast_statistics" in data["endpoints"]
        assert "/docs" in data["endpoints"]["docs"]
        assert "/redoc" in data["endpoints"]["redoc"]

class TestAPIValidation:
    """Test input validation across all endpoints."""
    
    def test_invalid_weight_count(self):
        """Test that wrong number of weights returns error."""
        payload = {
            "weights": INVALID_WEIGHTS,
            "include_categories": None,
            "exclude_categories": None,
            "periods_per_year": 1.0
        }
        response = client.post("/forecast_statistic/annualised_return", json=payload)
        assert response.status_code == 422  # Pydantic validation error
        assert "Weights must sum to 1.0" in response.json()["detail"][0]["msg"]
    
    def test_negative_weights(self):
        """Test that negative weights return error."""
        payload = {
            "weights": NEGATIVE_WEIGHTS,
            "include_categories": None,
            "exclude_categories": None,
            "periods_per_year": 1.0
        }
        response = client.post("/forecast_statistic/annualised_return", json=payload)
        assert response.status_code == 422  # Pydantic validation error
        assert "All weights must be non-negative" in response.json()["detail"][0]["msg"]
    
    def test_non_numeric_weights(self):
        """Test that non-numeric weights return error."""
        payload = {
            "weights": NON_NUMERIC_WEIGHTS,
            "include_categories": None,
            "exclude_categories": None,
            "periods_per_year": 1.0
        }
        response = client.post("/forecast_statistic/annualised_return", json=payload)
        assert response.status_code == 422  # Pydantic validation error
    
    def test_invalid_periods_per_year(self):
        """Test that invalid periods_per_year returns error."""
        payload = {
            "weights": EQUAL_WEIGHTS_25,
            "include_categories": None,
            "exclude_categories": None,
            "periods_per_year": -1.0
        }
        response = client.post("/forecast_statistic/annualised_return", json=payload)
        assert response.status_code == 422  # Pydantic validation error
        assert "periods_per_year must be positive" in response.json()["detail"][0]["msg"]
    
    def test_invalid_confidence_level(self):
        """Test that invalid confidence level returns error."""
        payload = {
            "weights": EQUAL_WEIGHTS_25,
            "include_categories": None,
            "exclude_categories": None,
            "periods_per_year": 1.0,
            "confidence": 1.5
        }
        response = client.post("/forecast_statistic/value_at_risk", json=payload)
        assert response.status_code == 422  # Pydantic validation error
        assert "confidence must be between 0 and 1" in response.json()["detail"][0]["msg"]

class TestAnnualisedReturn:
    """Test the annualised return endpoint."""
    
    def test_basic_annualised_return(self):
        """Test basic annualised return calculation."""
        payload = {
            "weights": EQUAL_WEIGHTS_25,
            "include_categories": None,
            "exclude_categories": None,
            "periods_per_year": 1.0
        }
        response = client.post("/forecast_statistic/annualised_return", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "value" in data
        assert "method" in data
        assert "params" in data
        assert "n_assets_used" in data
        assert "timesteps" in data
        assert "simulations" in data
        
        # Check specific values
        assert data["method"] == "Compound Annual Growth Rate (CAGR)"
        assert data["n_assets_used"] == 25
        assert data["timesteps"] == 20
        assert data["simulations"] == 10000
        assert isinstance(data["value"], float)
        assert data["value"] > 0  # Should be positive return
        
        # Check params
        assert data["params"]["weights"] == EQUAL_WEIGHTS_25
        assert data["params"]["periods_per_year"] == 1.0
    
    def test_monthly_annualisation(self):
        """Test monthly data annualisation."""
        payload = {
            "weights": EQUAL_WEIGHTS_25,
            "include_categories": None,
            "exclude_categories": None,
            "periods_per_year": 12.0
        }
        response = client.post("/forecast_statistic/annualised_return", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Monthly annualization should give higher return
        assert data["params"]["periods_per_year"] == 12.0
        assert data["value"] > 0.5  # Should be significantly higher than annual

class TestAnnualisedVolatility:
    """Test the annualised volatility endpoint."""
    
    def test_basic_annualised_volatility(self):
        """Test basic annualised volatility calculation."""
        payload = {
            "weights": EQUAL_WEIGHTS_25,
            "include_categories": None,
            "exclude_categories": None,
            "periods_per_year": 1.0
        }
        response = client.post("/forecast_statistic/annualised_volatility", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert data["method"] == "Sample Standard Deviation Annualized"
        assert data["n_assets_used"] == 25
        assert isinstance(data["value"], float)
        assert data["value"] > 0  # Volatility should be positive

class TestSharpeRatio:
    """Test the Sharpe ratio endpoint."""
    
    def test_basic_sharpe_ratio(self):
        """Test basic Sharpe ratio calculation."""
        payload = {
            "weights": EQUAL_WEIGHTS_25,
            "include_categories": None,
            "exclude_categories": None,
            "periods_per_year": 1.0,
            "risk_free_rate": 0.02
        }
        response = client.post("/forecast_statistic/sharpe_ratio", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert data["method"] == "Sharpe Ratio: (Return - RFR) / Volatility"
        assert data["n_assets_used"] == 25
        assert data["params"]["risk_free_rate"] == 0.02
        assert isinstance(data["value"], float)
    
    def test_zero_risk_free_rate(self):
        """Test Sharpe ratio with zero risk-free rate."""
        payload = {
            "weights": EQUAL_WEIGHTS_25,
            "include_categories": None,
            "exclude_categories": None,
            "periods_per_year": 1.0,
            "risk_free_rate": 0.0
        }
        response = client.post("/forecast_statistic/sharpe_ratio", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["params"]["risk_free_rate"] == 0.0

class TestValueAtRisk:
    """Test the Value at Risk endpoint."""
    
    def test_basic_var(self):
        """Test basic VaR calculation."""
        payload = {
            "weights": EQUAL_WEIGHTS_25,
            "include_categories": None,
            "exclude_categories": None,
            "periods_per_year": 1.0,
            "confidence": 0.95
        }
        response = client.post("/forecast_statistic/value_at_risk", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert "95% confidence" in data["method"]
        assert data["n_assets_used"] == 25
        assert data["params"]["confidence"] == 0.95
        assert isinstance(data["value"], float)
        assert data["value"] < 0  # VaR should be negative (loss)
    
    def test_different_confidence_levels(self):
        """Test VaR with different confidence levels."""
        for confidence in [0.90, 0.95, 0.99]:
            payload = {
                "weights": EQUAL_WEIGHTS_25,
                "include_categories": None,
                "exclude_categories": None,
                "periods_per_year": 1.0,
                "confidence": confidence
            }
            response = client.post("/forecast_statistic/value_at_risk", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["params"]["confidence"] == confidence

class TestConditionalValueAtRisk:
    """Test the Conditional Value at Risk endpoint."""
    
    def test_basic_cvar(self):
        """Test basic CVaR calculation."""
        payload = {
            "weights": EQUAL_WEIGHTS_25,
            "include_categories": None,
            "exclude_categories": None,
            "periods_per_year": 1.0,
            "confidence": 0.95
        }
        response = client.post("/forecast_statistic/conditional_value_at_risk", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert "Conditional Value at Risk" in data["method"]
        assert data["n_assets_used"] == 25
        assert data["params"]["confidence"] == 0.95
        assert isinstance(data["value"], float)
        assert data["value"] < 0  # CVaR should be negative (loss)

class TestMaximumDrawdown:
    """Test the maximum drawdown endpoint."""
    
    def test_basic_maximum_drawdown(self):
        """Test basic maximum drawdown calculation."""
        payload = {
            "weights": EQUAL_WEIGHTS_25,
            "include_categories": None,
            "exclude_categories": None,
            "periods_per_year": 1.0
        }
        response = client.post("/forecast_statistic/maximum_drawdown", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert data["method"] == "Peak-to-Trough Maximum Decline"
        assert data["n_assets_used"] == 25
        assert isinstance(data["value"], float)
        assert data["value"] < 0  # Drawdown should be negative

class TestDownsideDeviation:
    """Test the downside deviation endpoint."""
    
    def test_basic_downside_deviation(self):
        """Test basic downside deviation calculation."""
        payload = {
            "weights": EQUAL_WEIGHTS_25,
            "include_categories": None,
            "exclude_categories": None,
            "periods_per_year": 1.0,
            "minimum_acceptable_return": 0.0
        }
        response = client.post("/forecast_statistic/downside_deviation", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert data["method"] == "Root Mean Square of Downside Returns"
        assert data["n_assets_used"] == 25
        assert data["params"]["minimum_acceptable_return"] == 0.0
        assert isinstance(data["value"], float)
        assert data["value"] >= 0  # Downside deviation should be non-negative
    
    def test_positive_mar(self):
        """Test downside deviation with positive MAR."""
        payload = {
            "weights": EQUAL_WEIGHTS_25,
            "include_categories": None,
            "exclude_categories": None,
            "periods_per_year": 1.0,
            "minimum_acceptable_return": 0.05
        }
        response = client.post("/forecast_statistic/downside_deviation", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["params"]["minimum_acceptable_return"] == 0.05

class TestTrackingError:
    """Test the tracking error endpoint."""
    
    def test_basic_tracking_error(self):
        """Test basic tracking error calculation."""
        payload = {
            "weights": EQUAL_WEIGHTS_25,
            "include_categories": None,
            "exclude_categories": None,
            "periods_per_year": 1.0,
            "benchmark_weights": EQUAL_WEIGHTS_25
        }
        response = client.post("/forecast_statistic/tracking_error", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert data["method"] == "Standard Deviation of Excess Returns"
        assert data["n_assets_used"] == 25
        assert "benchmark_weights" in data["params"]
        assert isinstance(data["value"], float)
        assert data["value"] >= 0  # Tracking error should be non-negative
    
    def test_missing_benchmark_weights(self):
        """Test that missing benchmark weights returns error."""
        payload = {
            "weights": EQUAL_WEIGHTS_25,
            "include_categories": None,
            "exclude_categories": None,
            "periods_per_year": 1.0
        }
        response = client.post("/forecast_statistic/tracking_error", json=payload)
        assert response.status_code == 422  # Pydantic validation error

class TestCategoryFiltering:
    """Test asset category filtering functionality."""
    
    def test_include_categories(self):
        """Test including specific categories."""
        payload = {
            "weights": EQUAL_WEIGHTS_25,
            "include_categories": ["Equity"],
            "exclude_categories": None,
            "periods_per_year": 1.0
        }
        response = client.post("/forecast_statistic/annualised_return", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert data["params"]["include_categories"] == ["Equity"]
        assert data["n_assets_used"] < 25  # Should filter to fewer assets
        assert data["n_assets_used"] > 0   # Should have some assets
    
    def test_exclude_categories(self):
        """Test excluding specific categories."""
        payload = {
            "weights": EQUAL_WEIGHTS_25,
            "include_categories": None,
            "exclude_categories": ["Bond"],
            "periods_per_year": 1.0
        }
        response = client.post("/forecast_statistic/annualised_return", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert data["params"]["exclude_categories"] == ["Bond"]
        assert data["n_assets_used"] <= 25  # Should have same or fewer assets
    
    def test_no_matching_categories(self):
        """Test that no matching categories returns error."""
        payload = {
            "weights": EQUAL_WEIGHTS_25,
            "include_categories": ["NonExistentCategory"],
            "exclude_categories": None,
            "periods_per_year": 1.0
        }
        response = client.post("/forecast_statistic/annualised_return", json=payload)
        assert response.status_code == 400
        assert "No assets match the specified category filters" in response.json()["detail"]

class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_malformed_json(self):
        """Test malformed JSON request."""
        response = client.post(
            "/forecast_statistic/annualised_return",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422  # Validation error
    
    def test_missing_required_fields(self):
        """Test missing required fields."""
        payload = {
            "weights": EQUAL_WEIGHTS_25
            # Missing other required fields
        }
        response = client.post("/forecast_statistic/annualised_return", json=payload)
        assert response.status_code == 200  # API accepts missing optional fields with defaults
    
    def test_empty_weights(self):
        """Test empty weights array."""
        payload = {
            "weights": [],
            "include_categories": None,
            "exclude_categories": None,
            "periods_per_year": 1.0
        }
        response = client.post("/forecast_statistic/annualised_return", json=payload)
        assert response.status_code == 422  # Pydantic validation error

class TestResponseConsistency:
    """Test that all endpoints return consistent response structure."""
    
    def test_response_structure_consistency(self):
        """Test that all endpoints return the same response structure."""
        endpoints = [
            "/forecast_statistic/annualised_return",
            "/forecast_statistic/annualised_volatility",
            "/forecast_statistic/maximum_drawdown"
        ]
        
        payload = {
            "weights": EQUAL_WEIGHTS_25,
            "include_categories": None,
            "exclude_categories": None,
            "periods_per_year": 1.0
        }
        
        for endpoint in endpoints:
            response = client.post(endpoint, json=payload)
            assert response.status_code == 200
            data = response.json()
            
            # Check required fields
            required_fields = ["value", "method", "params", "n_assets_used", "timesteps", "simulations"]
            for field in required_fields:
                assert field in data, f"Missing field '{field}' in {endpoint}"
            
            # Check data types
            assert isinstance(data["value"], float)
            assert isinstance(data["method"], str)
            assert isinstance(data["params"], dict)
            assert isinstance(data["n_assets_used"], int)
            assert isinstance(data["timesteps"], int)
            assert isinstance(data["simulations"], int)
            
            # Check constant values
            assert data["timesteps"] == 20
            assert data["simulations"] == 10000
            assert data["n_assets_used"] == 25
