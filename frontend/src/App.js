import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, LineChart, Line, ResponsiveContainer } from 'recharts';
import './App.css';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658', '#FF6B6B', '#4ECDC4', '#45B7D1'];

function App() {
  const [portfolioValue, setPortfolioValue] = useState(100000);
  const [allocations, setAllocations] = useState([]);
  const [compoundingType, setCompoundingType] = useState('geometric');
  const [portfolioMetrics, setPortfolioMetrics] = useState(null);
  const [projectedValues, setProjectedValues] = useState(null);
  const [assetMetrics, setAssetMetrics] = useState(null);
  const [correlationMatrix, setCorrelationMatrix] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showAllocationsGrid, setShowAllocationsGrid] = useState(false);
  const [activeTab, setActiveTab] = useState('allocation');

  // Load asset data from CSV on component mount
  useEffect(() => {
    loadAssetData();
  }, []);

  const loadAssetData = async () => {
    try {
      // In a real app, you'd fetch this from your API
      // For now, using the data from asset_categories.csv
      const assetData = [
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

      // Initialize allocations with blank weights
      const initialAllocations = assetData.map((asset, index) => ({
        id: index,
        name: asset.name,
        category: asset.category,
        weight: ''
      }));

      setAllocations(initialAllocations);

      // Create category mapping (stored locally for now)
      const categories = {};
      assetData.forEach(asset => {
        categories[asset.name] = asset.category;
      });

      // Mock asset metrics data
      setAssetMetrics(assetData.map(asset => ({
        name: asset.name,
        annualisedReturn: (Math.random() * 0.15 + 0.02).toFixed(4),
        annualisedVolatility: (Math.random() * 0.25 + 0.05).toFixed(4)
      })));

      // Mock correlation matrix
      const mockCorrelationMatrix = assetData.map(asset1 => 
        assetData.map(asset2 => ({
          asset1: asset1.name,
          asset2: asset2.name,
          correlation: asset1.name === asset2.name ? 1 : (Math.random() * 0.8 - 0.4).toFixed(3)
        }))
      ).flat();
      setCorrelationMatrix(mockCorrelationMatrix);

    } catch (error) {
      console.error('Error loading asset data:', error);
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
  };

  const getTotalAllocation = () => {
    return allocations.reduce((sum, allocation) => sum + parseFloat(allocation.weight || 0), 0);
  };

  const getCategoryAllocations = () => {
    const categoryMap = {};
    allocations.forEach(allocation => {
      const category = allocation.category;
      const weight = parseFloat(allocation.weight || 0);
      categoryMap[category] = (categoryMap[category] || 0) + weight;
    });
    
    return Object.entries(categoryMap).map(([category, weight]) => ({
      category,
      weight: parseFloat(weight.toFixed(2))
    }));
  };

  const calculatePortfolioMetrics = async () => {
    setLoading(true);
    try {
      // Mock API call - in real app this would call your FastAPI endpoints
      setTimeout(() => {
        setPortfolioMetrics({
          annualisedVolatility: 0.156,
          annualisedDownsideDeviation: 0.112,
          valueAtRisk: -0.089,
          conditionalValueAtRisk: -0.134,
          maximumDrawdown: -0.234
        });
        
        // Mock projected values
        setProjectedValues([
          { year: 1, p1: 85000, p5: 92000, p25: 98000, p50: 108500, p75: 119000, p95: 132000, p99: 142000 },
          { year: 2, p1: 78000, p5: 89000, p25: 102000, p50: 118000, p75: 135000, p95: 158000, p99: 175000 },
          { year: 3, p1: 72000, p5: 87000, p25: 108000, p50: 128000, p75: 152000, p95: 185000, p99: 210000 },
          { year: 4, p1: 68000, p5: 86000, p25: 115000, p50: 139000, p75: 170000, p95: 215000, p99: 250000 },
          { year: 5, p1: 65000, p5: 85000, p25: 122000, p50: 151000, p75: 190000, p95: 245000, p99: 290000 }
        ]);
        
        setLoading(false);
      }, 1000);
      
    } catch (error) {
      console.error('Error calculating metrics:', error);
      setLoading(false);
    }
  };

  return (
    <div className="dashboard">

      
      <div className="dashboard-container">
        {/* Left Panel - 1/5 width */}
        <div className="left-panel">
          {!showAllocationsGrid ? (
            <>
              {/* Initial Portfolio Value Input */}
              <div className="input-section">
                <div className="input-group">
                  <label>Portfolio Value ($)</label>
                  <input
                    type="number"
                    value={portfolioValue}
                    onChange={(e) => setPortfolioValue(parseFloat(e.target.value) || 0)}
                    placeholder="100000"
                    className="portfolio-input"
                  />
                </div>
              </div>

              {/* Asset Allocations Compact Button */}
              <div className="allocations-compact">
                <button 
                  className="allocations-btn"
                  onClick={() => setShowAllocationsGrid(true)}
                >
                  <div className="btn-content">
                    <span className="btn-title">Asset Allocations</span>
                    <span className="btn-total">Total: {getTotalAllocation().toFixed(2)}%</span>
                    {getTotalAllocation() !== 100 && (
                      <span className={`btn-status ${getTotalAllocation() > 100 ? 'over' : 'under'}`}>
                        {getTotalAllocation() > 100 ? 'Over' : 'Under'}
                      </span>
                    )}
                  </div>
                </button>
              </div>

              {/* Compounding Type Selector */}
              <div className="compounding-section">
                <h3>Compounding Method</h3>
                <div className="compounding-options">
                  <button
                    className={`compounding-btn ${compoundingType === 'geometric' ? 'active' : ''}`}
                    onClick={() => setCompoundingType('geometric')}
                  >
                    Geometric
                  </button>
                  <button
                    className={`compounding-btn ${compoundingType === 'arithmetic' ? 'active' : ''}`}
                    onClick={() => setCompoundingType('arithmetic')}
                  >
                    Arithmetic
                  </button>
                </div>
              </div>

              {/* Calculate Button */}
              <button 
                className="calculate-btn"
                onClick={calculatePortfolioMetrics}
                disabled={loading || getTotalAllocation() !== 100}
              >
                {loading ? 'Calculating...' : 'Calculate Portfolio'}
              </button>
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
              </div>
              
              <div className="fullscreen-grid">
                <div className="grid-header">
                  <span>Asset</span>
                  <span>Weight (%)</span>
                </div>
                {allocations.map(allocation => (
                  <div key={allocation.id} className="allocation-row">
                    <span className="asset-name">{allocation.name}</span>
                    <input
                      type="number"
                      value={allocation.weight}
                      onChange={(e) => updateAllocation(allocation.id, e.target.value)}
                      className="weight-input"
                      step="0.01"
                      min="0"
                      max="100"
                    />
                  </div>
                ))}
              </div>
              
              {/* Total Allocation Display */}
              <div className="allocations-total">
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

        {/* Right Panel - 4/5 width */}
        <div className="right-panel">
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
          </div>

          {/* Tab Content */}
          <div className="tab-content">
            {/* Allocation Tab */}
            {activeTab === 'allocation' && (
              <div className="allocation-charts">
                {/* Pie Chart - Individual Assets */}
                <div className="chart-container">
                  <h3>Individual Asset Allocation</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={allocations.filter(a => parseFloat(a.weight) > 0)}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="weight"
                      >
                        {allocations.filter(a => parseFloat(a.weight) > 0).map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                {/* Bar Chart - Asset Categories */}
                <div className="chart-container">
                  <h3>Asset Category Allocation</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={getCategoryAllocations()}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="category" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="weight" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}

            {/* Projected Value Tab */}
            {activeTab === 'projected-value' && (
              <div className="projected-chart">
                <h3>Projected Portfolio Values</h3>
                {projectedValues ? (
                  <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={projectedValues}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="year" />
                      <YAxis />
                      <Tooltip />
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
                    <p>Click "Calculate Portfolio" to see projected values</p>
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
                    <p>Click "Calculate Portfolio" to see performance metrics</p>
                  </div>
                  )}
              </div>
            )}

            {/* Asset Metrics Tab */}
            {activeTab === 'asset-metrics' && (
              <div className="asset-metrics-section">
                {assetMetrics ? (
                  <div className="metrics-row">
                    {/* Asset Returns & Volatility */}
                    <div className="asset-metrics-table">
                      <h3>Asset Returns & Volatility</h3>
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
                              <td>{(parseFloat(asset.annualisedReturn) * 100).toFixed(2)}%</td>
                              <td>{(parseFloat(asset.annualisedVolatility) * 100).toFixed(2)}%</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    {/* Correlation Matrix */}
                    <div className="correlation-matrix">
                      <h3>Asset Correlation Matrix</h3>
                      <div className="matrix-container">
                        <table>
                          <thead>
                            <tr>
                              <th></th>
                              {allocations.slice(0, 8).map(asset => (
                                <th key={asset.id}>{asset.name.substring(0, 8)}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {allocations.slice(0, 8).map((asset1, i) => (
                              <tr key={asset1.id}>
                                <td>{asset1.name.substring(0, 8)}</td>
                                {allocations.slice(0, 8).map((asset2, j) => {
                                  const correlation = correlationMatrix?.find(
                                    corr => corr.asset1 === asset1.name && corr.asset2 === asset2.name
                                  )?.correlation || (i === j ? '1.000' : '0.000');
                                  return (
                                    <td key={asset2.id} className={`correlation-cell ${parseFloat(correlation) > 0.5 ? 'high' : parseFloat(correlation) < -0.5 ? 'low' : 'medium'}`}>
                                      {correlation}
                                    </td>
                                  );
                                })}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="no-data-message">
                    <p>Asset metrics will be available after calculation</p>
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
