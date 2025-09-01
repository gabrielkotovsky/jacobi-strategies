import pytest
import numpy as np
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.schemas.inputs import BaseInputs, PortfolioRequest, BatchPortfolioRequest


class TestBaseInputs:
    """Test suite for BaseInputs schema validation."""
    
    def setup_method(self):
        """Setup test data and initialize asset count."""
        # Initialize data cache to set asset count
        from app.data.loader import initialize_cache
        initialize_cache()
        
        self.asset_count = BaseInputs.get_asset_count()
        assert self.asset_count is not None, "Asset count should be set after cache initialization"
        
        # Create valid weights for testing
        self.valid_weights = [1.0 / self.asset_count] * self.asset_count
        self.valid_benchmark = [0.05] * 20 + [0.0] * 5  # 5% for first 20, 0% for last 5
    
    def test_default_values(self):
        """Test that default values work correctly."""
        portfolio = BaseInputs()
        
        # Test default values
        assert portfolio.rfr == 0.0
        assert portfolio.mar == 0.0
        assert portfolio.confidence == 0.95
        assert portfolio.rebalance == "periodic"
        assert portfolio.weights is None
        assert portfolio.benchmark_weights is None
        
        # Test default weights generation
        default_weights = portfolio.get_weights()
        assert len(default_weights) == self.asset_count
        assert np.isclose(sum(default_weights), 1.0, atol=1e-6)
        assert all(w == 1.0 / self.asset_count for w in default_weights)
    
    def test_custom_values(self):
        """Test custom values work correctly."""
        portfolio = BaseInputs(
            weights=self.valid_weights,
            rfr=0.02,
            mar=0.03,
            confidence=0.99,
            benchmark_weights=self.valid_benchmark,
            rebalance="none"
        )
        
        assert portfolio.rfr == 0.02
        assert portfolio.mar == 0.03
        assert portfolio.confidence == 0.99
        assert portfolio.rebalance == "none"
        assert portfolio.weights == self.valid_weights
        assert portfolio.benchmark_weights == self.valid_benchmark
    
    def test_weight_length_validation(self):
        """Test weight length validation."""
        # Test too few weights
        with pytest.raises(ValueError, match=f"Portfolio weights must have exactly {self.asset_count} elements"):
            BaseInputs(weights=[0.5, 0.5])
        
        # Test too many weights
        with pytest.raises(ValueError, match=f"Portfolio weights must have exactly {self.asset_count} elements"):
            BaseInputs(weights=[0.04] * (self.asset_count + 1))
    
    def test_weight_numeric_validation(self):
        """Test weight numeric validation."""
        # Test non-numeric weights
        invalid_weights = [0.04] * (self.asset_count - 1) + ["invalid"]
        with pytest.raises(ValueError):
            BaseInputs(weights=invalid_weights)
    
    def test_weight_finiteness_validation(self):
        """Test weight finiteness validation."""
        # Test NaN
        with_nan = [0.04] * (self.asset_count - 1) + [np.nan]
        with pytest.raises(ValueError, match="All portfolio weights must be finite"):
            BaseInputs(weights=with_nan)
        
        # Test inf
        with_inf = [0.04] * (self.asset_count - 1) + [np.inf]
        with pytest.raises(ValueError, match="All portfolio weights must be finite"):
            BaseInputs(weights=with_inf)
        
        # Test -inf
        with_neg_inf = [0.04] * (self.asset_count - 1) + [-np.inf]
        with pytest.raises(ValueError, match="All portfolio weights must be finite"):
            BaseInputs(weights=with_neg_inf)
    
    def test_weight_negative_validation(self):
        """Test negative weight validation."""
        negative_weights = [0.04] * (self.asset_count - 1) + [-0.1]
        with pytest.raises(ValueError, match="Portfolio weights cannot be negative"):
            BaseInputs(weights=negative_weights)
    
    def test_weight_sum_validation(self):
        """Test weight sum validation."""
        # Test weights that don't sum to 1.0
        wrong_sum_weights = [0.1] * self.asset_count  # Sum = 0.1 * asset_count
        with pytest.raises(ValueError, match="Portfolio weights must sum to 1.0"):
            BaseInputs(weights=wrong_sum_weights)
    
    def test_benchmark_weight_validation(self):
        """Test benchmark weight validation."""
        # Test benchmark weights with wrong length
        with pytest.raises(ValueError, match=f"Benchmark weights must have exactly {self.asset_count} elements"):
            BaseInputs(weights=self.valid_weights, benchmark_weights=[0.5, 0.5])
        
        # Test benchmark weights that don't sum to 1.0
        invalid_benchmark = [0.05] * (self.asset_count - 1) + [0.1]  # Sum ≠ 1.0
        with pytest.raises(ValueError, match="Benchmark weights must sum to 1.0"):
            BaseInputs(weights=self.valid_weights, benchmark_weights=invalid_benchmark)
        
        # Test benchmark weights with NaN
        benchmark_with_nan = [0.04] * (self.asset_count - 1) + [np.nan]
        with pytest.raises(ValueError, match="All benchmark weights must be finite"):
            BaseInputs(weights=self.valid_weights, benchmark_weights=benchmark_with_nan)
    
    def test_confidence_validation(self):
        """Test confidence level validation."""
        # Test confidence > 1.0
        with pytest.raises(ValueError):
            BaseInputs(confidence=1.5)
    
        # Test confidence < 0.0
        with pytest.raises(ValueError):
            BaseInputs(confidence=-0.1)
    
        # Test confidence = 0.0 (exclusive range)
        with pytest.raises(ValueError):
            BaseInputs(confidence=0.0)
    
        # Test confidence = 1.0 (exclusive range)
        with pytest.raises(ValueError):
            BaseInputs(confidence=1.0)
    
        # Test valid confidence values
        BaseInputs(confidence=0.1)  # Should work
        BaseInputs(confidence=0.5)  # Should work
        BaseInputs(confidence=0.99)  # Should work
    
    def test_rfr_mar_validation(self):
        """Test risk-free rate and MAR validation."""
        # RFR and MAR are now unconstrained (any finite float)
        # Test extreme values that should still work
        BaseInputs(rfr=-1000.0)  # Should work
        BaseInputs(rfr=0.0)      # Should work
        BaseInputs(rfr=1000.0)   # Should work
        BaseInputs(mar=-1000.0)  # Should work
        BaseInputs(mar=0.0)      # Should work
        BaseInputs(mar=1000.0)   # Should work
        
        # Test very large values
        BaseInputs(rfr=1e6)      # Should work
        BaseInputs(rfr=-1e6)     # Should work
        BaseInputs(mar=1e6)      # Should work
        BaseInputs(mar=-1e6)     # Should work
    
    def test_rebalance_validation(self):
        """Test rebalance strategy validation."""
        # Test valid values
        BaseInputs(rebalance="none")
        BaseInputs(rebalance="periodic")
        
        # Test invalid value (this would be caught by Pydantic's Literal type)
        with pytest.raises(ValueError):
            BaseInputs(rebalance="invalid")
    
    def test_get_weights_method(self):
        """Test get_weights method."""
        # Test with provided weights
        portfolio = BaseInputs(weights=self.valid_weights)
        assert portfolio.get_weights() == self.valid_weights
        
        # Test with default weights
        portfolio = BaseInputs()
        default_weights = portfolio.get_weights()
        assert len(default_weights) == self.asset_count
        assert np.isclose(sum(default_weights), 1.0, atol=1e-6)
    
    def test_get_benchmark_weights_method(self):
        """Test get_benchmark_weights method."""
        # Test with provided benchmark weights
        portfolio = BaseInputs(benchmark_weights=self.valid_benchmark)
        assert portfolio.get_benchmark_weights() == self.valid_benchmark
        
        # Test without benchmark weights
        portfolio = BaseInputs()
        assert portfolio.get_benchmark_weights() is None


class TestPortfolioRequest:
    """Test suite for PortfolioRequest schema."""
    
    def setup_method(self):
        """Setup test data."""
        from app.data.loader import initialize_cache
        initialize_cache()
        
        self.asset_count = BaseInputs.get_asset_count()
        self.valid_weights = [1.0 / self.asset_count] * self.asset_count
    
    def test_portfolio_request_creation(self):
        """Test PortfolioRequest creation with all fields."""
        portfolio = PortfolioRequest(
            portfolio_name="Test Portfolio",
            description="A test portfolio",
            weights=self.valid_weights,
            rfr=0.02,
            mar=0.03,
            confidence=0.99,
            benchmark_weights=[0.05] * 20 + [0.0] * 5,
            rebalance="none"
        )
        
        assert portfolio.portfolio_name == "Test Portfolio"
        assert portfolio.description == "A test portfolio"
        assert portfolio.weights == self.valid_weights
        assert portfolio.rfr == 0.02
        assert portfolio.mar == 0.03
        assert portfolio.confidence == 0.99
        assert portfolio.rebalance == "none"
    
    def test_portfolio_request_defaults(self):
        """Test PortfolioRequest with default values."""
        portfolio = PortfolioRequest()
        
        assert portfolio.portfolio_name is None
        assert portfolio.description is None
        assert portfolio.weights is None
        assert portfolio.rfr == 0.0
        assert portfolio.mar == 0.0
        assert portfolio.confidence == 0.95
        assert portfolio.rebalance == "periodic"
    
    def test_portfolio_request_inheritance(self):
        """Test that PortfolioRequest inherits validation from BaseInputs."""
        # Test that weight validation still works
        with pytest.raises(ValueError, match="Portfolio weights must sum to 1.0"):
            PortfolioRequest(weights=[0.1] * self.asset_count)
        
        # Test that confidence validation still works
        with pytest.raises(ValueError):
            PortfolioRequest(confidence=1.5)


class TestBatchPortfolioRequest:
    """Test suite for BatchPortfolioRequest schema."""
    
    def setup_method(self):
        """Setup test data."""
        from app.data.loader import initialize_cache
        initialize_cache()
        
        self.asset_count = BaseInputs.get_asset_count()
        self.valid_weights = [1.0 / self.asset_count] * self.asset_count
    
    def test_batch_request_creation(self):
        """Test BatchPortfolioRequest creation."""
        portfolios = [
            PortfolioRequest(weights=self.valid_weights, portfolio_name="Portfolio A"),
            PortfolioRequest(weights=self.valid_weights, portfolio_name="Portfolio B"),
            PortfolioRequest(weights=self.valid_weights, portfolio_name="Portfolio C")
        ]
        
        batch_request = BatchPortfolioRequest(portfolios=portfolios)
        assert len(batch_request.portfolios) == 3
        assert batch_request.portfolios[0].portfolio_name == "Portfolio A"
        assert batch_request.portfolios[1].portfolio_name == "Portfolio B"
        assert batch_request.portfolios[2].portfolio_name == "Portfolio C"
    
    def test_batch_request_empty_validation(self):
        """Test that empty batch requests are rejected."""
        with pytest.raises(ValueError, match="At least one portfolio must be provided"):
            BatchPortfolioRequest(portfolios=[])
    
    def test_batch_request_size_limit(self):
        """Test that batch requests are limited to 100 portfolios."""
        portfolios = [PortfolioRequest(weights=self.valid_weights) for _ in range(101)]
        
        with pytest.raises(ValueError, match="Maximum of 100 portfolios allowed"):
            BatchPortfolioRequest(portfolios=portfolios)
    
    def test_batch_request_validation_cascade(self):
        """Test that validation errors in individual portfolios are caught."""
        valid_portfolio = PortfolioRequest(weights=self.valid_weights)
        
        # This should fail because we're trying to create a portfolio with invalid weights
        with pytest.raises(ValueError, match="Portfolio weights must sum to 1.0"):
            invalid_portfolio = PortfolioRequest(weights=[0.1] * self.asset_count)
        
        # Test that valid portfolios work
        batch_request = BatchPortfolioRequest(portfolios=[valid_portfolio])
        assert len(batch_request.portfolios) == 1


class TestAssetCountManagement:
    """Test suite for asset count management."""
    
    def test_asset_count_setting(self):
        """Test asset count setting and retrieval."""
        # Clear any existing asset count
        BaseInputs._expected_asset_count = None
        
        # Test setting asset count
        BaseInputs.set_asset_count(25)
        assert BaseInputs.get_asset_count() == 25
        
        # Test setting invalid asset count
        with pytest.raises(ValueError, match="Asset count must be positive"):
            BaseInputs.set_asset_count(0)
        
        with pytest.raises(ValueError, match="Asset count must be positive"):
            BaseInputs.set_asset_count(-1)
    
    def test_validation_without_asset_count(self):
        """Test validation behavior when asset count is not set."""
        # Clear asset count
        BaseInputs._expected_asset_count = None
        
        # Test that validation fails without asset count
        with pytest.raises(ValueError, match="Asset count not set"):
            BaseInputs(weights=[0.04] * 25)
        
        with pytest.raises(ValueError, match="Asset count not set"):
            BaseInputs(benchmark_weights=[0.04] * 25)
        
        with pytest.raises(ValueError, match="Asset count not set"):
            BaseInputs().get_weights()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
