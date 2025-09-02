import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, LineChart, Line, ResponsiveContainer } from 'recharts';
import './App.css';

const COLORS = ['#4ddbd7', '#00bbc3', '#008190', '#006d7a', '#005a66', '#33c4c0', '#66cdc9', '#99d6d2', '#ccdfdb', '#e6f2f1'];

function App() {
  const [portfolioValue, setPortfolioValue] = useState(100000);
  const [allocations, setAllocations] = useState([]);
  const [portfolioMetrics, setPortfolioMetrics] = useState(null);
  const [projectedValues, setProjectedValues] = useState(null);
  const [assetMetrics, setAssetMetrics] = useState(null);
  const [correlationMatrix, setCorrelationMatrix] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showAllocationsGrid, setShowAllocationsGrid] = useState(false);
  const [activeTab, setActiveTab] = useState('allocation');
  const [assetsLoading, setAssetsLoading] = useState(true);
  const [assetsError, setAssetsError] = useState(null);
  
  // New input field states
  const [riskFreeRate, setRiskFreeRate] = useState(null);
  const [mar, setMar] = useState(null);
  const [aggregation, setAggregation] = useState('mean');
  const [varMethod, setVarMethod] = useState('pooled'); // Default to pooled distribution
  const [rebalance, setRebalance] = useState('periodic'); // Default to periodic rebalancing

  // Load asset data from backend API on component mount
  useEffect(() => {
    loadAssetData();
  }, []);

  // Auto-calculate portfolio metrics when weights or parameters change
  useEffect(() => {
    // Only calculate if we have valid parameters and allocations
    if (
      allocations && allocations.length > 0 &&
      getSelectedAllocations().length > 0 &&
      validateWeightsForAPI() && // Use new validation function
      (riskFreeRate === null || validateRiskFreeRate(riskFreeRate)) &&
      (mar === null || validateMar(mar))
    ) {
      // Add a small delay to avoid excessive calculations while typing
      const timeoutId = setTimeout(() => {
        calculatePortfolioMetrics();
      }, 500);

      return () => clearTimeout(timeoutId);
    }
  }, [riskFreeRate, mar, aggregation, varMethod, rebalance, portfolioValue, allocations]);

  // Auto-calculate asset metrics when Asset Metrics or Asset Correlation tab is active
  useEffect(() => {
    if ((activeTab === 'asset-metrics' || activeTab === 'asset-correlation') && allocations && allocations.length > 0) {
      calculateAssetMetrics();
    }
  }, [activeTab, allocations, aggregation]);

  const loadAssetData = async () => {
    setAssetsLoading(true);
    setAssetsError(null);
    
    try {
      // Fetch asset data from backend API
      const response = await fetch('/forecast_statistic/assets');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Initialize allocations with blank weights and deselected state
      // IMPORTANT: Keep original order from backend (sorted alphabetically)
      const initialAllocations = data.assets.map((asset, index) => ({
        id: asset.id,
        name: asset.name,
        category: asset.category,
        weight: '',
        selected: false, // Default all assets to deselected
        originalIndex: asset.id // Store the original backend index
      }));

      setAllocations(initialAllocations);

      // Initialize empty asset metrics (will be calculated when needed)
      setAssetMetrics([]);
      setCorrelationMatrix([]);

      setAssetsLoading(false);
      
    } catch (error) {
      console.error('Error loading asset data:', error);
      setAssetsError(error.message);
      setAssetsLoading(false);
      
      // Fallback to hardcoded data if API fails
      const fallbackAssetData = [
        { name: 'Inflation-Protected Bond', category: 'Fixed Income' },
        { name: 'EM Debt', category: 'Fixed Income' },
        { name: 'Cash', category: 'Cash' },
        { name: 'US Small Cap', category: 'Equity' },
        { name: 'US Equity', category: 'Equity' },
        { name: 'International Small Cap', category: 'Equity' },
        { name: 'International Equity', category: 'Equity' },
        { name: 'Global Equity', category: 'Equity' },
        { name: 'Emerging Markets Equity', category: 'Equity' },
        { name: 'Real Estate', category: 'Real Assets' },
        { name: 'Ultrashort Bond', category: 'Fixed Income' },
        { name: 'Intermediate Core Bond', category: 'Fixed Income' },
        { name: 'Government Bond', category: 'Fixed Income' },
        { name: 'Loans', category: 'Fixed Income' },
        { name: 'Corporate Bond', category: 'Fixed Income' },
        { name: 'High Yield Bond', category: 'Fixed Income' },
        { name: 'Global Bonds', category: 'Fixed Income' },
        { name: 'Hedge Funds', category: 'Alternatives' },
        { name: 'Private Equity', category: 'Private Markets' },
        { name: 'Muni', category: 'Fixed Income' },
        { name: 'Commodities', category: 'Commodities' },
        { name: 'Aust Equity', category: 'Equity' },
        { name: 'Infrastructure', category: 'Real Assets' },
        { name: 'Venture Capital', category: 'Private Markets' },
        { name: 'Private Debt', category: 'Private Markets' }
      ];

      const fallbackAllocations = fallbackAssetData.map((asset, index) => ({
        id: index,
        name: asset.name,
        category: asset.category,
        weight: '',
        selected: false,
        originalIndex: index // Store the original index for fallback data
      }));

      setAllocations(fallbackAllocations);
    }
  };

  const updateAllocation = (id, weight) => {
    setAllocations(prev => 
      prev.map(allocation => 
        allocation.id === id 
          ? { ...allocation, weight: parseFloat(weight) || 0 }
          : allocation
      )
    );
    
    // Clear existing portfolio metrics when weights change
    setPortfolioMetrics(null);
    setProjectedValues(null);
  };

  const toggleAssetSelection = (id) => {
    setAllocations(prev => 
      prev.map(allocation => 
        allocation.id === id 
          ? { ...allocation, selected: !allocation.selected, weight: !allocation.selected ? allocation.weight : '' }
          : allocation
      )
    );
    
    // Clear existing portfolio metrics when asset selection changes
    setPortfolioMetrics(null);
    setProjectedValues(null);
  };

  const selectAllAssets = () => {
    setAllocations(prev => 
      prev.map(allocation => ({ ...allocation, selected: true }))
    );
  };

  const deselectAllAssets = () => {
    setAllocations(prev => 
      prev.map(allocation => ({ ...allocation, selected: false, weight: '' }))
    );
  };

  const getSelectedAllocations = () => {
    // Safety check: return empty array if allocations is not available
    if (!allocations || allocations.length === 0) {
      return [];
    }
    return allocations.filter(allocation => allocation.selected);
  };

  const getTotalAllocation = () => {
    const selectedAllocations = getSelectedAllocations();
    if (selectedAllocations.length === 0) {
      return 0;
    }
    return selectedAllocations.reduce((sum, allocation) => sum + parseFloat(allocation.weight || 0), 0);
  };

  const getCategoryAllocations = () => {
    const selectedAllocations = getSelectedAllocations();
    if (selectedAllocations.length === 0) {
      return [];
    }
    
    const categoryMap = {};
    selectedAllocations.forEach(allocation => {
      const category = allocation.category;
      const weight = parseFloat(allocation.weight || 0);
      categoryMap[category] = (categoryMap[category] || 0) + weight;
    });
    
    return Object.entries(categoryMap).map(([category, weight]) => ({
      category,
      weight: parseFloat(weight.toFixed(2))
    }));
  };

  // Validation functions for new input fields
  const validateRiskFreeRate = (value) => {
    if (value === null) return true; // Allow null/empty values
    const num = parseFloat(value);
    return !isNaN(num) && num >= 0 && num <= 1;
  };

  const validateMar = (value) => {
    if (value === null) return true; // Allow null/empty values
    const num = parseFloat(value);
    return !isNaN(num) && num >= -1 && num <= 1;
  };



  const getInputError = (field) => {
    switch (field) {
      case 'riskFreeRate':
        return !validateRiskFreeRate(riskFreeRate) ? 'Must be between 0% and 100%' : '';
      case 'mar':
        return !validateMar(mar) ? 'Must be between -100% and 100%' : '';

      default:
        return '';
    }
  };

  // Get current parameter values for calculations
  const getCurrentParameters = () => {
    return {
      riskFreeRate,
      mar,
      aggregation,
      varMethod,
      rebalance
    };
  };

  // Formatting functions for graph display
  const formatYAxisLabel = (value) => {
    if (value >= 1e9) {
      return `${(value / 1e9).toFixed(1)}B`;
    } else if (value >= 1e6) {
      return `${(value / 1e6).toFixed(1)}M`;
    } else if (value >= 1e3) {
      return `${(value / 1e3).toFixed(1)}k`;
    } else {
      return value.toFixed(1);
    }
  };

  const formatTooltipValue = (value) => {
    return `$${Math.round(value).toLocaleString()}`;
  };

  // Calculate upside percentage relative to initial portfolio value
  const calculateUpside = (value) => {
    if (!portfolioValue || portfolioValue === 0) return 0;
    const upside = ((value - portfolioValue) / portfolioValue) * 100;
    return upside;
  };

  // Format upside percentage for display
  const formatUpside = (upside) => {
    if (upside >= 0) {
      return `+${upside.toFixed(1)}%`;
    } else {
      return `${upside.toFixed(1)}%`;
    }
  };

  // Generate evenly spaced Y-axis ticks
  const generateYTicks = () => {
    if (!projectedValues || projectedValues.length === 0) return [];
    
    // Find the maximum value across all percentiles and years
    const maxValue = Math.max(...projectedValues.flatMap(year => 
      Object.keys(year).filter(key => key.startsWith('p')).map(key => year[key])
    ));
    
    // Generate 10 evenly spaced ticks from 0 to maxValue
    const ticks = [];
    for (let i = 0; i <= 10; i++) {
      ticks.push(Math.round((maxValue * i) / 10));
    }
    
    return ticks;
  };

  // Build weights array in the correct order for backend API calls
  const buildWeightsArray = () => {
    // Safety check: return empty array if no allocations
    if (!allocations || allocations.length === 0) {
      return [];
    }
    
    // Get the maximum original index to determine array size
    const maxIndex = Math.max(...allocations.map(a => a.originalIndex));
    
    // Safety check: ensure maxIndex is valid
    if (maxIndex < 0 || !Number.isFinite(maxIndex)) {
      console.warn('Invalid maxIndex:', maxIndex, 'allocations:', allocations);
      return [];
    }
    
    // Create array with correct size, initialized to 0
    const weightsArray = new Array(maxIndex + 1).fill(0);
    
    // Fill in weights for selected assets at their correct indices
    getSelectedAllocations().forEach(allocation => {
      if (allocation.selected && allocation.weight !== '') {
        // Convert percentage to decimal (e.g., 4.0% -> 0.04)
        const weight = parseFloat(allocation.weight) / 100;
        weightsArray[allocation.originalIndex] = weight;
      }
    });
    
    return weightsArray;
  };

  // Validate that weights array is ready for API calls
  const validateWeightsForAPI = () => {
    const weights = buildWeightsArray();
    
    // Safety check: return false if weights array is empty
    if (!weights || weights.length === 0) {
      return false;
    }
    
    const totalWeight = weights.reduce((sum, weight) => sum + weight, 0);
    
    // Check if weights sum to 1.0 (with tolerance)
    return Math.abs(totalWeight - 1.0) < 0.000001;
  };

  const calculateAssetMetrics = async () => {
    try {
      setLoading(true);
      
      // Call the asset metrics endpoint
      const response = await fetch('/forecast_statistic/asset_metrics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          weights: buildWeightsArray(),  // Add: Send selected asset weights
          periods_per_year: 1.0,  // Fixed: Annual data
          is_log: false,           // Fixed: Simple returns
          aggregation: "pooled",   // Fixed: Use pooled for asset metrics
          corr_method: "pooled"    // Fixed: Use pooled for correlations
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Transform the data for the frontend
      const assetMetricsData = data.asset_metrics.map(row => ({
        name: row.asset,
        annualisedReturn: row.annualised_return,
        annualisedVolatility: row.annualised_volatility
      }));
      
      setAssetMetrics(assetMetricsData);
      setCorrelationMatrix(data.correlation_matrix);
      
      setLoading(false);
      
    } catch (error) {
      console.error('Error calculating asset metrics:', error);
      setLoading(false);
    }
  };

  const calculatePortfolioMetrics = async () => {
    // Prevent multiple simultaneous calculations
    if (loading) return;
    
    setLoading(true);
    try {
      // Get current parameter values and build weights array
      const params = getCurrentParameters();
      const weights = buildWeightsArray();
      
      console.log('Auto-calculating portfolio with parameters:', params);
      console.log('Portfolio value:', portfolioValue);
      console.log('Weights array:', weights);
      console.log('Weights sum:', weights.reduce((sum, w) => sum + w, 0));
      
      // Make actual API calls to backend endpoints
      const baseRequest = {
        weights: weights,
        periods_per_year: 1.0,  // Fixed: Annual data
        aggregation: params.aggregation,
        rebalance: params.rebalance
      };
      
      // Calculate Annualised Return
      const returnResponse = await fetch('/forecast_statistic/annualised_return', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(baseRequest)
      });
      
      // Calculate Annualised Volatility
      const volatilityResponse = await fetch('/forecast_statistic/annualised_volatility', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(baseRequest)
      });
      
      // Calculate Sharpe Ratio
      const sharpeResponse = await fetch('/forecast_statistic/sharpe_ratio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...baseRequest,
          risk_free_rate: params.riskFreeRate ?? 0
        })
      });
      
      // Calculate Downside Deviation
      const downsideResponse = await fetch('/forecast_statistic/downside_deviation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...baseRequest,
          minimum_acceptable_return: params.mar ?? 0
        })
      });
      
      // Calculate VaR
      const varResponse = await fetch('/forecast_statistic/value_at_risk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...baseRequest,
          confidence: 0.95,  // Fixed: 95% confidence
          var_type: params.varMethod // Dynamic VaR method selection
        })
      });
      
      // Calculate CVaR
      const cvarResponse = await fetch('/forecast_statistic/conditional_value_at_risk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...baseRequest,
          confidence: 0.95,  // Fixed: 95% confidence
          var_type: params.varMethod // Dynamic VaR method selection // Default to pooled distribution
        })
      });
      
      // Calculate Maximum Drawdown
      const mddResponse = await fetch('/forecast_statistic/maximum_drawdown', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(baseRequest)
      });
      
      // Calculate Projected Values
      const projectedResponse = await fetch('/forecast_statistic/projected_values', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...baseRequest,
          initial_value: portfolioValue
        })
      });
      
      // Parse responses
      const returnData = await returnResponse.json();
      const volatilityData = await volatilityResponse.json();
      const sharpeData = await sharpeResponse.json();
      const downsideData = await downsideResponse.json();
      const varData = await varResponse.json();
      const cvarData = await cvarResponse.json();
      const mddData = await mddResponse.json();
      const projectedData = await projectedResponse.json();
      
      // Set portfolio metrics with real data
      setPortfolioMetrics({
        annualisedReturn: returnData.value,
        annualisedVolatility: volatilityData.value,
        annualisedDownsideDeviation: downsideData.value,
        valueAtRisk: varData.value,
        conditionalValueAtRisk: cvarData.value,
        maximumDrawdown: mddData.value,
        // Add parameter info to show what was used
        parameters: {
          riskFreeRate: params.riskFreeRate,
          mar: params.mar,
          aggregation: params.aggregation,
          varMethod: params.varMethod,
          rebalance: params.rebalance
        }
      });
      
      // Set projected values with real data from backend
      setProjectedValues(projectedData.projected_values);
      
      setLoading(false);
      
    } catch (error) {
      console.error('Error calculating metrics:', error);
      setLoading(false);
    }
  };

  const getCorrelationClass = (correlation) => {
    // High positive correlations (80%+)
    if (correlation >= 0.8) return 'high-positive';
    // Very positive correlations (60-80%)
    if (correlation >= 0.6) return 'very-positive';
    // Positive correlations (40-60%)
    if (correlation >= 0.4) return 'positive';
    // Low positive correlations (20-40%)
    if (correlation >= 0.2) return 'low-positive';
    // Very low positive correlations (5-20%)
    if (correlation >= 0.05) return 'very-low-positive';
    // Neutral correlations (-5% to +5%)
    if (correlation > -0.05) return 'neutral';
    // Very low negative correlations (-5% to -20%)
    if (correlation > -0.2) return 'very-low-negative';
    // Low negative correlations (-20% to -40%)
    if (correlation > -0.4) return 'low-negative';
    // Negative correlations (-40% to -60%)
    if (correlation > -0.6) return 'negative';
    // Very negative correlations (-60% to -80%)
    if (correlation > -0.8) return 'very-negative';
    // High negative correlations (-80%+)
    return 'high-negative';
  };

  // Calculate dynamic font size based on number of assets
  const getDynamicFontSize = (assetCount) => {
    if (assetCount <= 8) return '0.9rem';
    if (assetCount <= 12) return '0.8rem';
    if (assetCount <= 16) return '0.75rem';
    if (assetCount <= 20) return '0.7rem';
    if (assetCount <= 25) return '0.65rem';
    return '0.6rem';
  };

  // Calculate dynamic padding based on number of assets
  const getDynamicPadding = (assetCount) => {
    if (assetCount <= 8) return '0.75rem';
    if (assetCount <= 12) return '0.6rem';
    if (assetCount <= 16) return '0.5rem';
    if (assetCount <= 20) return '0.4rem';
    if (assetCount <= 25) return '0.35rem';
    return '0.3rem';
  };

  // Calculate dynamic table width based on number of assets
  const getDynamicTableWidth = (assetCount) => {
    if (assetCount <= 8) return 'auto';
    if (assetCount <= 12) return 'auto';
    if (assetCount <= 16) return 'max-content';
    if (assetCount <= 20) return 'max-content';
    if (assetCount <= 25) return 'max-content';
    return 'max-content';
  };

  return (
    <div className="dashboard">

      
      <div className="dashboard-container">
        {/* Left Panel - dynamic width */}
        <div className={`left-panel ${showAllocationsGrid ? 'allocations-open' : ''}`}>
          {!showAllocationsGrid ? (
            <>
              {/* Initial Portfolio Value Input */}
              <div className="input-section">
                <div className="input-group">
                  <label>Portfolio Value ($)</label>
                  <input
                    type="text"
                    value={portfolioValue.toLocaleString()}
                    onChange={(e) => {
                      // Remove commas and non-numeric characters, then parse
                      const cleanValue = e.target.value.replace(/[^\d]/g, '');
                      const numValue = parseInt(cleanValue) || 0;
                      setPortfolioValue(numValue);
                    }}
                    onBlur={(e) => {
                      // Ensure the value is properly formatted on blur
                      const numValue = parseInt(e.target.value.replace(/[^\d]/g, '')) || 0;
                      setPortfolioValue(numValue);
                    }}
                    placeholder="100,000"
                    className="portfolio-input"
                  />
                </div>

                {/* Asset Allocations Compact Button */}
                <div className="allocations-compact">
                  {assetsLoading ? (
                    <div className="loading-assets">
                      <div className="loading-spinner"></div>
                      <span>Loading assets...</span>
                    </div>
                  ) : assetsError ? (
                    <div className="assets-error">
                      <span>⚠️ Error loading assets</span>
                      <button onClick={loadAssetData} className="retry-btn">Retry</button>
                    </div>
                  ) : (
                    <button 
                      className="allocations-btn"
                      onClick={() => setShowAllocationsGrid(true)}
                    >
                      <div className="btn-content">
                        <span className="btn-title">Asset Allocations</span>
                        <span className="btn-total">Total: {getTotalAllocation().toFixed(2)}%</span>
                        <span className="btn-selected">Selected: {getSelectedAllocations().length}/{allocations.length || 0}</span>
                        {getTotalAllocation() !== 100 && (
                          <span className={`btn-status ${getTotalAllocation() > 100 ? 'over' : 'under'}`}>
                            {getTotalAllocation() > 100 ? 'Over' : 'Under'}
                          </span>
                        )}
                        {loading && (
                          <span className="btn-status btn-calculating">
                            <div className="loading-spinner-small"></div>
                            Calculating...
                          </span>
                        )}
                      </div>
                    </button>
                  )}
                </div>
              </div>

              {/* Risk Management Parameters */}
              <div className="input-section">
                <h3>Risk Parameters</h3>
                
                {/* Auto-calculation Status */}
                {loading && (
                  <div className="auto-calc-status">
                    <div className="loading-spinner-small"></div>
                    <span>Auto-calculating...</span>
                  </div>
                )}
                
                {/* Risk Free Rate */}
                <div className="input-group">
                  <label>Risk Free Rate (%)</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="100"
                    value={riskFreeRate === null ? '' : (riskFreeRate * 100).toFixed(2)}
                    onChange={(e) => {
                      const value = e.target.value;
                      if (value === '' || value === null) {
                        setRiskFreeRate(null);
                      } else {
                        const numValue = parseFloat(value) / 100;
                        if (!isNaN(numValue)) {
                          setRiskFreeRate(numValue);
                        }
                      }
                    }}
                    placeholder="0.00"
                    className={`portfolio-input ${getInputError('riskFreeRate') ? 'input-error' : ''}`}
                  />
                  {getInputError('riskFreeRate') && (
                    <span className="error-message">{getInputError('riskFreeRate')}</span>
                  )}
                </div>

                {/* Minimum Acceptable Return */}
                <div className="input-group">
                  <label>Minimum Acceptable Return (MAR) (%)</label>
                  <input
                    type="number"
                    step="0.01"
                    min="-100"
                    max="100"
                    value={mar === null ? '' : (mar * 100).toFixed(2)}
                    onChange={(e) => {
                      const value = e.target.value;
                      if (value === '' || value === null) {
                        setMar(null);
                      } else {
                        const numValue = parseFloat(value) / 100;
                        if (!isNaN(numValue)) {
                          setMar(numValue);
                        }
                      }
                    }}
                    placeholder="0.00"
                    className={`portfolio-input ${getInputError('mar') ? 'input-error' : ''}`}
                  />
                  {getInputError('mar') && (
                    <span className="error-message">{getInputError('mar')}</span>
                  )}
                </div>



                {/* Aggregation Method */}
                <div className="input-group">
                  <label>Aggregation Method</label>
                  <select
                    value={aggregation}
                    onChange={(e) => setAggregation(e.target.value)}
                    className="portfolio-input"
                  >
                    <option value="mean">Mean Across Simulations</option>
                    <option value="median">Median Across Simulations</option>
                  </select>
                </div>

                {/* VaR Method */}
                <div className="input-group">
                  <label>VaR Calculation Method</label>
                  <select
                    value={varMethod}
                    onChange={(e) => setVarMethod(e.target.value)}
                    className="portfolio-input"
                  >
                    <option value="pooled">Pooled Distribution (All Years Together)</option>
                    <option value="cumulative">Investment Horizon VaR (Cumulative)</option>
                  </select>
                  <small className="input-help">
                    {varMethod === 'pooled' && "Single VaR estimate from all 200,000 simulated returns"}
                    {varMethod === 'cumulative' && "VaR of 20-year terminal portfolio values"}
                  </small>
                </div>

                {/* Rebalancing Strategy */}
                <div className="input-group">
                  <label>Rebalancing Strategy</label>
                  <select
                    value={rebalance}
                    onChange={(e) => setRebalance(e.target.value)}
                    className="portfolio-input"
                  >
                    <option value="periodic">Periodic Rebalancing</option>
                    <option value="none">Buy & Hold (No Rebalancing)</option>
                  </select>
                  <small className="input-help">
                    {rebalance === 'periodic' && "Rebalance to target weights each period"}
                    {rebalance === 'none' && "Let weights drift naturally over time"}
                  </small>
                </div>


              </div>








            </>
          ) : (
            /* Full Screen Allocations View */
            <div className="allocations-fullscreen">
              <div className="fullscreen-header">
                <button 
                  className="close-btn"
                  onClick={() => setShowAllocationsGrid(false)}
                >
                  ×
                </button>
                <div className="selection-controls">
                  <button onClick={selectAllAssets} className="select-all-btn">Select All</button>
                  <button onClick={deselectAllAssets} className="deselect-all-btn">Deselect All</button>
                </div>
              </div>
              
              <div className="fullscreen-grid">
                <div className="grid-header">
                  <span>Select</span>
                  <span>Asset</span>
                  <span>Type</span>
                  <span>Weight (%)</span>
                </div>
                {allocations.map(allocation => (
                  <div key={allocation.id} className={`allocation-row ${!allocation.selected ? 'deselected' : ''}`}>
                    <input
                      type="checkbox"
                      checked={allocation.selected}
                      onChange={() => toggleAssetSelection(allocation.id)}
                      className="asset-checkbox"
                    />
                    <span className="asset-name">{allocation.name}</span>
                    <span className="asset-category">{allocation.category}</span>
                    <input
                      type="number"
                      value={allocation.weight}
                      onChange={(e) => updateAllocation(allocation.id, e.target.value)}
                      className="weight-input"
                      step="0.01"
                      min="0"
                      max="100"
                      disabled={!allocation.selected}
                    />
                  </div>
                ))}
              </div>
              
              {/* Total Allocation Display */}
              <div className="allocations-total">
                <span>Selected Assets: <strong>{getSelectedAllocations().length}</strong></span>
                <span>Total: <strong>{getTotalAllocation().toFixed(2)}%</strong></span>
                {getTotalAllocation() !== 100 && (
                  <span className={`weight-status ${getTotalAllocation() > 100 ? 'over' : 'under'}`}>
                    {getTotalAllocation() > 100 ? 'Over-allocated' : 'Under-allocated'}
                  </span>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right Panel - dynamic width */}
        <div className={`right-panel ${showAllocationsGrid ? 'allocations-open' : ''}`}>
          {/* Auto-calculation Status Bar */}
          {loading && (
            <div className="calc-status-bar">
              <div className="loading-spinner-small"></div>
              <span>Portfolio metrics updating...</span>
            </div>
          )}
          
          {/* Tabs */}
          <div className="tabs-container">
            <button 
              className={`tab ${activeTab === 'allocation' ? 'active' : ''}`}
              onClick={() => setActiveTab('allocation')}
            >
              Allocation
            </button>
            <button 
              className={`tab ${activeTab === 'projected-value' ? 'active' : ''}`}
              onClick={() => setActiveTab('projected-value')}
            >
              Projected Value
            </button>
            <button 
              className={`tab ${activeTab === 'performance-risk' ? 'active' : ''}`}
              onClick={() => setActiveTab('performance-risk')}
            >
              Performance & Risk
            </button>
            <button 
              className={`tab ${activeTab === 'asset-metrics' ? 'active' : ''}`}
              onClick={() => setActiveTab('asset-metrics')}
            >
              Asset Metrics
            </button>
            <button 
              className={`tab ${activeTab === 'asset-correlation' ? 'active' : ''}`}
              onClick={() => setActiveTab('asset-correlation')}
            >
              Asset Correlation
            </button>
          </div>

          {/* Tab Content */}
          <div className="tab-content">
            {/* Allocation Tab */}
            {activeTab === 'allocation' && (
              <div className="allocation-charts">
                {/* Pie Chart - Individual Assets */}
                <div className="chart-container">
                  <h3>Individual Asset Allocation</h3>
                  {getSelectedAllocations().filter(a => parseFloat(a.weight) > 0).length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={getSelectedAllocations().filter(a => parseFloat(a.weight) > 0)}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                          outerRadius="60%"
                          fill="#4ddbd7"
                          dataKey="weight"
                        >
                          {getSelectedAllocations().filter(a => parseFloat(a.weight) > 0).map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="no-data-message">
                      <p>No selected assets with weights assigned</p>
                    </div>
                  )}
                </div>

                {/* Bar Chart - Asset Categories */}
                <div className="chart-container">
                  <h3>Asset Category Allocation</h3>
                  {getCategoryAllocations().length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={getCategoryAllocations()}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="category" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="weight" fill="#4ddbd7" />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="no-data-message">
                      <p>No selected assets with weights assigned</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Projected Value Tab */}
            {activeTab === 'projected-value' && (
              <div className="projected-chart">
                <h3>Projected Portfolio Values</h3>
                <p className="chart-subtitle">Chart starts at initial value (Year 0) and shows projected values with upside percentages</p>
                {projectedValues ? (
                  <ResponsiveContainer width="100%" height="90%">
                    <LineChart data={projectedValues}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="year" 
                        domain={[0, 'dataMax']}
                        ticks={[0, 5, 10, 15, 20]}
                      />
                      <YAxis 
                        tickFormatter={(value) => formatYAxisLabel(value)}
                        domain={[0, 'dataMax']}
                        allowDecimals={true}
                        ticks={generateYTicks()}
                      />
                      <Tooltip 
                        formatter={(value) => [
                          `${formatTooltipValue(value)} (${formatUpside(calculateUpside(value))})`,
                          'Value (Upside)'
                        ]}
                        labelFormatter={(label) => `Year ${label}`}
                      />
                      <Legend />
                      <Line type="monotone" dataKey="p1" stroke="#FF0000" name="1st Percentile" />
                      <Line type="monotone" dataKey="p5" stroke="#FF6600" name="5th Percentile" />
                      <Line type="monotone" dataKey="p25" stroke="#FFCC00" name="25th Percentile" />
                      <Line type="monotone" dataKey="p50" stroke="#00CC00" name="50th Percentile" />
                      <Line type="monotone" dataKey="p75" stroke="#0066FF" name="75th Percentile" />
                      <Line type="monotone" dataKey="p95" stroke="#6600FF" name="95th Percentile" />
                      <Line type="monotone" dataKey="p99" stroke="#CC00FF" name="99th Percentile" />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="no-data-message">
                    <p>Projected values will update automatically when allocations are complete</p>
                  </div>
                )}
              </div>
            )}

            {/* Performance & Risk Tab */}
            {activeTab === 'performance-risk' && (
              <div className="metrics-section">
                <h3>Portfolio Performance & Risk Metrics</h3>
                {portfolioMetrics ? (
                  <div className="metrics-table">
                    <table>
                      <thead>
                        <tr>
                          <th>Metric</th>
                          <th>Value</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td>Annualised Volatility</td>
                          <td>{(portfolioMetrics.annualisedVolatility * 100).toFixed(2)}%</td>
                        </tr>
                        <tr>
                          <td>Annualised Downside Deviation</td>
                          <td>{(portfolioMetrics.annualisedDownsideDeviation * 100).toFixed(2)}%</td>
                        </tr>
                        <tr>
                          <td>5% Value at Risk (VaR)</td>
                          <td>{(portfolioMetrics.valueAtRisk * 100).toFixed(2)}%</td>
                        </tr>
                        <tr>
                          <td>5% Conditional VaR (CVaR)</td>
                          <td>{(portfolioMetrics.conditionalValueAtRisk * 100).toFixed(2)}%</td>
                        </tr>
                        <tr>
                          <td>Maximum Drawdown</td>
                          <td>{(portfolioMetrics.maximumDrawdown * 100).toFixed(2)}%</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                                  ) : (
                    <div className="no-data-message">
                      <p>Portfolio metrics will update automatically when allocations are complete</p>
                    </div>
                  )}
              </div>
            )}

            {/* Asset Metrics Tab */}
            {activeTab === 'asset-metrics' && (
              <div className="asset-metrics-section">
                {loading ? (
                  <div className="loading-message">
                    <div className="loading-spinner"></div>
                    <p>Calculating asset metrics...</p>
                  </div>
                ) : assetMetrics && assetMetrics.length > 0 ? (
                  <>
                                        {/* Asset Returns & Volatility Table */}
                    <div className="asset-metrics-table">
                      <h4>Asset Returns & Volatility</h4>
                      <table>
                        <thead>
                          <tr>
                            <th>Asset</th>
                            <th>Annualised Return</th>
                            <th>Annualised Volatility</th>
                          </tr>
                        </thead>
                        <tbody>
                          {assetMetrics.map((asset, index) => (
                            <tr key={index}>
                              <td>{asset.name}</td>
                              <td>{(asset.annualisedReturn * 100).toFixed(2)}%</td>
                              <td>{(asset.annualisedVolatility * 100).toFixed(2)}%</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </>
                ) : (
                  <div className="no-data-message">
                    <p>Asset metrics will be calculated when you select assets and choose aggregation method</p>
                  </div>
                )}
              </div>
            )}

            {/* Asset Correlation Matrix Tab */}
            {activeTab === 'asset-correlation' && (
              <div className="correlation-section">
                <h3>Asset Correlation Matrix</h3>
                {loading ? (
                  <div className="loading-message">
                    <div className="loading-spinner"></div>
                    <p>Calculating correlation matrix...</p>
                  </div>
                ) : correlationMatrix && correlationMatrix.length > 0 && assetMetrics && assetMetrics.length > 0 ? (
                  <div className="correlation-matrix">
                    <table style={{
                      fontSize: getDynamicFontSize(assetMetrics.length),
                      '--dynamic-padding': getDynamicPadding(assetMetrics.length),
                      width: getDynamicTableWidth(assetMetrics.length)
                    }}>
                      <thead>
                        <tr>
                          <th></th>
                          {assetMetrics.map((asset, index) => (
                            <th key={index}>{asset.name}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {(() => {
                          // Transform correlation matrix to 2D format
                          const n = assetMetrics.length;
                          const matrix = Array(n).fill().map(() => Array(n).fill(0));
                          
                          // Initialize diagonal with 1.0
                          for (let i = 0; i < n; i++) {
                            matrix[i][i] = 1.0;
                          }
                          
                          // Fill in correlations from backend data
                          correlationMatrix.forEach(item => {
                            const i = assetMetrics.findIndex(asset => asset.name === item.asset1);
                            const j = assetMetrics.findIndex(asset => asset.name === item.asset2);
                            
                            if (i !== -1 && j !== -1) {
                              matrix[i][j] = item.correlation;
                              matrix[j][i] = item.correlation; // Symmetric matrix
                            }
                          });
                          
                          return matrix.map((row, rowIndex) => (
                            <tr key={rowIndex}>
                              <th>{assetMetrics[rowIndex]?.name}</th>
                              {row.map((correlation, colIndex) => {
                                // Show only upper triangle (including diagonal)
                                if (colIndex <= rowIndex) {
                                  return (
                                    <td 
                                      key={colIndex}
                                      className={`correlation-cell ${getCorrelationClass(correlation)}`}
                                      title={`${assetMetrics[rowIndex]?.name} vs ${assetMetrics[colIndex]?.name}: ${(correlation * 100).toFixed(1)}%`}
                                    >
                                      {(correlation * 100).toFixed(0)}%
                                    </td>
                                  );
                                } else {
                                  // Lower triangle - show empty cell
                                  return <td key={colIndex} className="correlation-cell empty"></td>;
                                }
                              })}
                            </tr>
                          ));
                        })()}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="no-data-message">
                    <p>Correlation matrix will be calculated when you select assets and choose aggregation method</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
