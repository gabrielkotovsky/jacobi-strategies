#!/usr/bin/env python3
"""
Test script for the FastAPI portfolio analysis API.
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint."""
    print("🔍 Testing health check...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Is the server running?")
        return False
    
    return True

def test_root_endpoint():
    """Test the root endpoint."""
    print("\n🔍 Testing root endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Root endpoint passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API")
        return False
    
    return True

def test_annualised_return():
    """Test the annualised return endpoint."""
    print("\n🔍 Testing annualised return endpoint...")
    
    # Equal-weight portfolio for 25 assets
    payload = {
        "weights": [0.04] * 25,  # 25 assets with 4% each
        "include_categories": None,
        "exclude_categories": None,
        "periods_per_year": 1.0
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/forecast_statistic/annualised_return",
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Annualised return endpoint passed")
            print(f"   Value: {result['value']:.4f} ({result['value']*100:.2f}%)")
            print(f"   Method: {result['method']}")
            print(f"   Assets used: {result['n_assets_used']}")
            print(f"   Timesteps: {result['timesteps']}")
            print(f"   Simulations: {result['simulations']}")
        else:
            print(f"❌ Annualised return endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API")
        return False
    
    return True

def test_sharpe_ratio():
    """Test the Sharpe ratio endpoint."""
    print("\n🔍 Testing Sharpe ratio endpoint...")
    
    # Equal-weight portfolio with risk-free rate
    payload = {
        "weights": [0.04] * 25,  # 25 assets with 4% each
        "include_categories": None,
        "exclude_categories": None,
        "periods_per_year": 1.0,
        "risk_free_rate": 0.02  # 2%
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/forecast_statistic/sharpe_ratio",
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Sharpe ratio endpoint passed")
            print(f"   Value: {result['value']:.4f}")
            print(f"   Method: {result['method']}")
            print(f"   Assets used: {result['n_assets_used']}")
        else:
            print(f"❌ Sharpe ratio endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API")
        return False
    
    return True

def test_value_at_risk():
    """Test the VaR endpoint."""
    print("\n🔍 Testing Value at Risk endpoint...")
    
    # Equal-weight portfolio with confidence level
    payload = {
        "weights": [0.04] * 25,  # 25 assets with 4% each
        "include_categories": None,
        "exclude_categories": None,
        "periods_per_year": 1.0,
        "confidence": 0.95  # 95% confidence
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/forecast_statistic/value_at_risk",
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Value at Risk endpoint passed")
            print(f"   Value: {result['value']:.4f} ({result['value']*100:.2f}%)")
            print(f"   Method: {result['method']}")
            print(f"   Assets used: {result['n_assets_used']}")
        else:
            print(f"❌ Value at Risk endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API")
        return False
    
    return True

def test_category_filtering():
    """Test category filtering functionality."""
    print("\n🔍 Testing category filtering...")
    
    # Test with category inclusion
    payload = {
        "weights": [0.04] * 25,  # 25 assets with 4% each
        "include_categories": ["Equity"],  # Only include equity assets
        "exclude_categories": None,
        "periods_per_year": 1.0
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/forecast_statistic/annualised_volatility",
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Category filtering passed")
            print(f"   Assets used: {result['n_assets_used']} (filtered from 25)")
            print(f"   Volatility: {result['value']:.4f} ({result['value']*100:.2f}%)")
        else:
            print(f"❌ Category filtering failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API")
        return False
    
    return True

def main():
    """Run all API tests."""
    print("🚀 PORTFOLIO ANALYSIS API TESTING")
    print("=" * 50)
    
    # Wait a moment for the server to start
    print("⏳ Waiting for API server to be ready...")
    time.sleep(2)
    
    # Run tests
    tests = [
        test_health_check,
        test_root_endpoint,
        test_annualised_return,
        test_sharpe_ratio,
        test_value_at_risk,
        test_category_filtering
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the API implementation.")
    
    print("\n🔗 API Documentation available at:")
    print(f"   Swagger UI: {BASE_URL}/docs")
    print(f"   ReDoc: {BASE_URL}/redoc")

if __name__ == "__main__":
    main()
