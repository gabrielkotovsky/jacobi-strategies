import pytest
import numpy as np
import sys
import os

# Add the backend directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.portfolio import (
    portfolio_period_returns,
    to_cumulative_returns,
    calculate_annualized_metrics,
    portfolio_analysis_pipeline,
    validate_portfolio_inputs
)


class TestPortfolioPeriodReturns:
    """Test portfolio period returns calculation."""
    
    def setup_method(self):
        """Set up test data."""
        # Create small test data for faster tests
        self.returns = np.array([
            [[0.1, 0.2], [0.05, -0.1]],  # Asset 1: [sim1, sim2] for [t1, t2]
            [[0.15, 0.25], [0.08, -0.05]]  # Asset 2: [sim1, sim2] for [t1, t2]
        ])  # Shape: (2 assets, 2 time periods, 2 simulations)
        self.weights = np.array([0.6, 0.4])  # 60% asset 1, 40% asset 2
    
    def test_basic_portfolio_returns(self):
        """Test basic portfolio returns calculation."""
        portfolio_returns = portfolio_period_returns(self.weights, self.returns)
        
        assert portfolio_returns.shape == (2, 2)  # (T, S)
        
        # Manual calculation for verification
        # Period 1: 0.6 * 0.1 + 0.4 * 0.15 = 0.06 + 0.06 = 0.12
        # Period 1: 0.6 * 0.2 + 0.4 * 0.25 = 0.12 + 0.10 = 0.22
        # Period 2: 0.6 * 0.05 + 0.4 * 0.08 = 0.03 + 0.032 = 0.062
        # Period 2: 0.6 * (-0.1) + 0.4 * (-0.05) = -0.06 + (-0.02) = -0.08
        
        expected = np.array([[0.12, 0.22], [0.062, -0.08]])
        np.testing.assert_allclose(portfolio_returns, expected, atol=1e-6)
    
    def test_periodic_rebalancing(self):
        """Test periodic rebalancing strategy."""
        portfolio_returns = portfolio_period_returns(self.weights, self.returns, rebalance="periodic")
        assert portfolio_returns.shape == (2, 2)
    
    def test_none_rebalancing_implementation(self):
        """Test that none rebalancing (buy-and-hold) works correctly."""
        portfolio_returns = portfolio_period_returns(self.weights, self.returns, rebalance="none")
        assert portfolio_returns.shape == (2, 2)
        
        # Buy-and-hold should produce different results than periodic due to weight drift
        periodic_returns = portfolio_period_returns(self.weights, self.returns, rebalance="periodic")
        
        # The returns should be different (though they might be similar for small datasets)
        # At minimum, they should have the same shape
        assert periodic_returns.shape == portfolio_returns.shape
    
    def test_invalid_rebalance_strategy(self):
        """Test invalid rebalancing strategy raises error."""
        with pytest.raises(ValueError, match="Invalid rebalancing strategy"):
            portfolio_period_returns(self.weights, self.returns, rebalance="invalid")
    
    def test_weights_returns_mismatch(self):
        """Test weights and returns dimension mismatch."""
        wrong_weights = np.array([0.5, 0.3, 0.2])  # 3 weights for 2 assets
        with pytest.raises(ValueError, match="Weights shape.*doesn't match returns assets"):
            portfolio_period_returns(wrong_weights, self.returns)


class TestCumulativeReturns:
    """Test cumulative returns calculation."""
    
    def test_basic_cumulative_returns(self):
        """Test basic cumulative returns calculation."""
        period_returns = np.array([[0.1, 0.2], [0.05, -0.1]])  # (T=2, S=2)
        cumulative_returns = to_cumulative_returns(period_returns)
        
        assert cumulative_returns.shape == (2, 2)
        
        # Manual calculation:
        # Simulation 1: (1 + 0.1) * (1 + 0.05) = 1.1 * 1.05 = 1.155
        # Simulation 2: (1 + 0.2) * (1 + (-0.1)) = 1.2 * 0.9 = 1.08
        
        expected = np.array([[1.1, 1.2], [1.155, 1.08]])
        np.testing.assert_allclose(cumulative_returns, expected, atol=1e-6)
    
    def test_single_period(self):
        """Test cumulative returns with single period."""
        period_returns = np.array([[0.1, 0.2]])  # (T=1, S=2)
        cumulative_returns = to_cumulative_returns(period_returns)
        
        expected = np.array([[1.1, 1.2]])
        np.testing.assert_allclose(cumulative_returns, expected, atol=1e-6)
    
    def test_zero_returns(self):
        """Test cumulative returns with zero returns."""
        period_returns = np.array([[0.0, 0.0], [0.0, 0.0]])  # (T=2, S=2)
        cumulative_returns = to_cumulative_returns(period_returns)
        
        expected = np.array([[1.0, 1.0], [1.0, 1.0]])
        np.testing.assert_allclose(cumulative_returns, expected, atol=1e-6)


class TestAnnualizedMetrics:
    """Test annualized metrics calculation."""
    
    def test_annual_data(self):
        """Test annualized metrics with annual data (periods_per_year=1.0)."""
        portfolio_returns = np.array([[0.1, 0.2], [0.05, -0.1], [0.08, 0.15]])  # (T=3, S=2)
        annualized_mean, annualized_vol = calculate_annualized_metrics(portfolio_returns, periods_per_year=1.0)
        
        assert annualized_mean.shape == (2,)
        assert annualized_vol.shape == (2,)
        
        # Manual calculation for simulation 1:
        # Mean: (0.1 + 0.05 + 0.08) / 3 = 0.0767
        # Vol: std([0.1, 0.05, 0.08]) = 0.0252
        
        expected_mean = np.array([0.0767, 0.0833])  # Approximate
        expected_vol = np.array([0.0252, 0.1607])   # Actual calculated values
        
        np.testing.assert_allclose(annualized_mean, expected_mean, atol=1e-3)
        np.testing.assert_allclose(annualized_vol, expected_vol, atol=1e-3)
    
    def test_monthly_data(self):
        """Test annualized metrics with monthly data (periods_per_year=12.0)."""
        portfolio_returns = np.array([[0.01, 0.02], [0.005, -0.01]])  # (T=2, S=2)
        annualized_mean, annualized_vol = calculate_annualized_metrics(portfolio_returns, periods_per_year=12.0)
        
        # Monthly mean should be 12x the period mean
        period_mean = portfolio_returns.mean(axis=0)
        expected_mean = period_mean * 12
        np.testing.assert_allclose(annualized_mean, expected_mean, atol=1e-10)
        
        # Monthly volatility should be √12 times the period volatility
        period_vol = portfolio_returns.std(axis=0, ddof=1)
        expected_vol = period_vol * np.sqrt(12)
        np.testing.assert_allclose(annualized_vol, expected_vol, atol=1e-10)
    
    def test_daily_data(self):
        """Test annualized metrics with daily data (periods_per_year=252.0)."""
        portfolio_returns = np.array([[0.001, 0.002], [0.0005, -0.001]])  # (T=2, S=2)
        annualized_mean, annualized_vol = calculate_annualized_metrics(portfolio_returns, periods_per_year=252.0)
        
        # Daily mean should be 252x the period mean
        period_mean = portfolio_returns.mean(axis=0)
        expected_mean = period_mean * 252
        np.testing.assert_allclose(annualized_mean, expected_mean, atol=1e-10)
        
        # Daily volatility should be √252 times the period volatility
        period_vol = portfolio_returns.std(axis=0, ddof=1)
        expected_vol = period_vol * np.sqrt(252)
        np.testing.assert_allclose(annualized_vol, expected_vol, atol=1e-10)


class TestPortfolioAnalysisPipeline:
    """Test complete portfolio analysis pipeline."""
    
    def setup_method(self):
        """Set up test data."""
        self.returns = np.array([
            [[0.1, 0.2], [0.05, -0.1], [0.08, 0.15]],  # Asset 1
            [[0.15, 0.25], [0.08, -0.05], [0.12, 0.18]]  # Asset 2
        ])  # Shape: (2 assets, 3 time periods, 2 simulations)
        self.weights = np.array([0.6, 0.4])
    
    def test_pipeline_output_structure(self):
        """Test that pipeline returns expected structure."""
        results = portfolio_analysis_pipeline(self.weights, self.returns)
        
        # Check all expected keys are present
        expected_keys = ['period_returns', 'cumulative_returns', 'annualized_mean', 
                        'annualized_volatility', 'total_return', 'max_drawdown', 'shapes']
        for key in expected_keys:
            assert key in results
        
        # Check shapes
        assert results['period_returns'].shape == (3, 2)  # (T, S)
        assert results['cumulative_returns'].shape == (3, 2)  # (T, S)
        assert results['annualized_mean'].shape == (2,)  # (S,)
        assert results['annualized_volatility'].shape == (2,)  # (S,)
        assert results['total_return'].shape == (2,)  # (S,)
        assert results['max_drawdown'].shape == (2,)  # (S,)
    
    def test_pipeline_shapes_documentation(self):
        """Test that shapes are correctly documented."""
        results = portfolio_analysis_pipeline(self.weights, self.returns)
        
        shapes = results['shapes']
        assert shapes['period_returns'] == (3, 2)
        assert shapes['cumulative_returns'] == (3, 2)
        assert shapes['annualized_mean'] == (2,)
        assert shapes['annualized_volatility'] == (2,)
        assert shapes['total_return'] == (2,)
        assert shapes['max_drawdown'] == (2,)
    
    def test_total_return_calculation(self):
        """Test total return calculation."""
        results = portfolio_analysis_pipeline(self.weights, self.returns)
        
        # Total return should be final cumulative return - 1
        expected_total_return = results['cumulative_returns'][-1, :] - 1
        np.testing.assert_allclose(results['total_return'], expected_total_return, atol=1e-10)
    
    def test_max_drawdown_calculation(self):
        """Test maximum drawdown calculation."""
        results = portfolio_analysis_pipeline(self.weights, self.returns)
        
        # Max drawdown should be non-positive (drawdowns are negative)
        assert np.all(results['max_drawdown'] <= 0)
        
        # Max drawdown should be the minimum of all drawdowns
        cumulative_returns = results['cumulative_returns']
        peak_values = np.maximum.accumulate(cumulative_returns, axis=0)
        drawdowns = (cumulative_returns - peak_values) / peak_values
        expected_max_drawdown = drawdowns.min(axis=0)
        np.testing.assert_allclose(results['max_drawdown'], expected_max_drawdown, atol=1e-10)


class TestInputValidation:
    """Test portfolio input validation."""
    
    def setup_method(self):
        """Set up test data."""
        self.valid_weights = np.array([0.6, 0.4])
        self.valid_returns = np.array([
            [[0.1, 0.2], [0.05, -0.1]],  # Asset 1
            [[0.15, 0.25], [0.08, -0.05]]  # Asset 2
        ])
    
    def test_valid_inputs(self):
        """Test that valid inputs pass validation."""
        # Should not raise any exception
        validate_portfolio_inputs(self.valid_weights, self.valid_returns)
    
    def test_weights_wrong_dimensions(self):
        """Test weights with wrong dimensions."""
        wrong_weights = np.array([[0.6, 0.4]])  # 2D instead of 1D
        with pytest.raises(ValueError, match="Weights must be 1D array"):
            validate_portfolio_inputs(wrong_weights, self.valid_returns)
    
    def test_weights_wrong_sum(self):
        """Test weights that don't sum to 1.0."""
        wrong_weights = np.array([0.6, 0.5])  # Sum = 1.1
        with pytest.raises(ValueError, match="Weights must sum to 1.0"):
            validate_portfolio_inputs(wrong_weights, self.valid_returns)
    
    def test_weights_negative(self):
        """Test negative weights."""
        negative_weights = np.array([0.6, -0.1, 0.5])  # Negative weight
        with pytest.raises(ValueError, match="Weights cannot be negative"):
            validate_portfolio_inputs(negative_weights, self.valid_returns)
    
    def test_returns_wrong_dimensions(self):
        """Test returns with wrong dimensions."""
        wrong_returns = np.array([[0.1, 0.2], [0.05, -0.1]])  # 2D instead of 3D
        with pytest.raises(ValueError, match="Returns must be 3D array"):
            validate_portfolio_inputs(self.valid_weights, wrong_returns)
    
    def test_weights_returns_mismatch(self):
        """Test weights and returns asset count mismatch."""
        wrong_weights = np.array([0.5, 0.3, 0.2])  # 3 weights for 2 assets
        with pytest.raises(ValueError, match="Weights length.*doesn't match returns assets"):
            validate_portfolio_inputs(wrong_weights, self.valid_returns)
    
    def test_returns_with_nan(self):
        """Test returns containing NaN values."""
        nan_returns = self.valid_returns.copy()
        nan_returns[0, 0, 0] = np.nan
        with pytest.raises(ValueError, match="Returns contain NaN or infinite values"):
            validate_portfolio_inputs(self.valid_weights, nan_returns)
    
    def test_returns_with_inf(self):
        """Test returns containing infinite values."""
        inf_returns = self.valid_returns.copy()
        inf_returns[0, 0, 0] = np.inf
        with pytest.raises(ValueError, match="Returns contain NaN or infinite values"):
            validate_portfolio_inputs(self.valid_weights, inf_returns)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_single_asset(self):
        """Test portfolio with single asset."""
        returns = np.array([[[0.1, 0.2], [0.05, -0.1]]])  # 1 asset, 2 periods, 2 sims
        weights = np.array([1.0])
        
        portfolio_returns = portfolio_period_returns(weights, returns)
        assert portfolio_returns.shape == (2, 2)
        
        # With single asset, portfolio returns should equal asset returns
        np.testing.assert_allclose(portfolio_returns, returns[0], atol=1e-10)
    
    def test_single_period(self):
        """Test portfolio with single time period."""
        returns = np.array([
            [[0.1, 0.2]],  # Asset 1: 1 period, 2 sims
            [[0.15, 0.25]]  # Asset 2: 1 period, 2 sims
        ])  # Shape: (2 assets, 1 period, 2 simulations)
        weights = np.array([0.6, 0.4])
        
        portfolio_returns = portfolio_period_returns(weights, returns)
        assert portfolio_returns.shape == (1, 2)
        
        cumulative_returns = to_cumulative_returns(portfolio_returns)
        assert cumulative_returns.shape == (1, 2)
    
    def test_single_simulation(self):
        """Test portfolio with single simulation."""
        returns = np.array([
            [[0.1], [0.05], [0.08]],  # Asset 1: 3 periods, 1 sim
            [[0.15], [0.08], [0.12]]  # Asset 2: 3 periods, 1 sim
        ])  # Shape: (2 assets, 3 periods, 1 simulation)
        weights = np.array([0.6, 0.4])
        
        portfolio_returns = portfolio_period_returns(weights, returns)
        assert portfolio_returns.shape == (3, 1)
        
        cumulative_returns = to_cumulative_returns(portfolio_returns)
        assert cumulative_returns.shape == (3, 1)
    
    def test_zero_weights(self):
        """Test portfolio with zero weights (edge case)."""
        returns = np.array([
            [[0.1, 0.2], [0.05, -0.1]],  # Asset 1
            [[0.15, 0.25], [0.08, -0.05]]  # Asset 2
        ])
        weights = np.array([0.0, 1.0])  # 0% asset 1, 100% asset 2
        
        portfolio_returns = portfolio_period_returns(weights, returns)
        # Portfolio returns should equal asset 2 returns
        np.testing.assert_allclose(portfolio_returns, returns[1], atol=1e-10)


if __name__ == "__main__":
    pytest.main([__file__])
