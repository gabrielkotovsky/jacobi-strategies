import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, LineChart, Line, ResponsiveContainer } from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658', '#FF6B6B', '#4ECDC4', '#45B7D1'];

function App() {
  const [portfolioValue, setPortfolioValue] = useState(100000);
  const [allocations, setAllocations] = useState([]);
  const [assetNames, setAssetNames] = useState([]);
  const [assetCategories, setAssetCategories] = useState({});
  const [portfolioMetrics, setPortfolioMetrics] = useState(null);
  const [projectedValues, setProjectedValues] = useState(null);
  const [loading, setLoading] = useState(false);

  // Load asset names and categories on component mount
  useEffect(() => {
    loadAssetData();
  }, []);

  const loadAssetData = async () => {
    try {
      // In a real app, you'd get this from your API
      // For now, we'll use placeholder data
      const mockAssetNames = [
        'Inflation-Protected Bond', 'EM Debt', 'Cash', 'US Small Cap', 'US Equity',
        'International Equity', 'Emerging Markets', 'Real Estate', 'Commodities', 'TIPS',
        'Corporate Bonds', 'Municipal Bonds', 'High Yield', 'Preferred Stock', 'Convertibles',
        'Master Limited Partnerships', 'REITs', 'Infrastructure', 'Private Equity', 'Hedge Funds',
        'Venture Capital', 'Angel Investing', 'Crowdfunding', 'Cryptocurrency', 'Gold'
      ];
      
      setAssetNames(mockAssetNames);
      
      // Initialize allocations with equal weights
      const initialAllocations = mockAssetNames.map((name, index) => ({
        id: index,
        name: name,
        weight: (100 / mockAssetNames.length).toFixed(2),
        category: getAssetCategory(name)
      }));
      
      setAllocations(initialAllocations);
      
      // Mock asset categories
      const categories = {
        'Inflation-Protected Bond': 'Fixed Income',
        'EM Debt': 'Fixed Income',
        'Cash': 'Cash & Equivalents',
        'US Small Cap': 'Equity',
        'US Equity': 'Equity',
        'International Equity': 'Equity',
        'Emerging Markets': 'Equity',
        'Real Estate': 'Alternative',
        'Commodities': 'Alternative',
        'TIPS': 'Fixed Income',
        'Corporate Bonds': 'Fixed Income',
        'Municipal Bonds': 'Fixed Income',
        'High Yield': 'Fixed Income',
        'Preferred Stock': 'Equity',
        'Convertibles': 'Hybrid',
        'Master Limited Partnerships': 'Alternative',
        'REITs': 'Alternative',
        'Infrastructure': 'Alternative',
        'Private Equity': 'Alternative',
        'Hedge Funds': 'Alternative',
        'Venture Capital': 'Alternative',
        'Angel Investing': 'Alternative',
        'Crowdfunding': 'Alternative',
        'Cryptocurrency': 'Alternative',
        'Gold': 'Alternative'
      };
      
      setAssetCategories(categories);
    } catch (error) {
      console.error('Error loading asset data:', error);
    }
  };

  const getAssetCategory = (assetName) => {
    const categories = {
      'Inflation-Protected Bond': 'Fixed Income',
      'EM Debt': 'Fixed Income',
      'Cash': 'Cash & Equivalents',
      'US Small Cap': 'Equity',
      'US Equity': 'Equity',
      'International Equity': 'Equity',
      'Emerging Markets': 'Equity',
      'Real Estate': 'Alternative',
      'Commodities': 'Alternative',
      'TIPS': 'Fixed Income',
      'Corporate Bonds': 'Fixed Income',
      'Municipal Bonds': 'Fixed Income',
      'High Yield': 'Fixed Income',
      'Preferred Stock': 'Equity',
      'Convertibles': 'Hybrid',
      'Master Limited Partnerships': 'Alternative',
      'REITs': 'Alternative',
      'Infrastructure': 'Alternative',
      'Private Equity': 'Alternative',
      'Hedge Funds': 'Alternative',
      'Venture Capital': 'Alternative',
      'Angel Investing': 'Alternative',
      'Crowdfunding': 'Alternative',
      'Cryptocurrency': 'Alternative',
      'Gold': 'Alternative'
    };
    return categories[assetName] || 'Other';
  };

  const updateAllocation = (id, weight) => {
    setAllocations(prev => 
      prev.map(allocation => 
        allocation.id === id 
          ? { ...allocation, weight: parseFloat(weight) }
          : allocation
      )
    );
  };

  const addAsset = () => {
    const newAsset = {
      id: Date.now(),
      name: 'New Asset',
      weight: 0,
      category: 'Other'
    };
    setAllocations(prev => [...prev, newAsset]);
  };

  const removeAsset = (id) => {
    setAllocations(prev => prev.filter(allocation => allocation.id !== id));
  };

  const getTotalAllocation = () => {
    return allocations.reduce((sum, allocation) => sum + parseFloat(allocation.weight || 0), 0);
  };

  const calculatePortfolioMetrics = async () => {
    setLoading(true);
    try {
      // In a real app, this would call your FastAPI endpoints
      // For now, we'll simulate the API calls
      
      const portfolioData = {
        allocations: allocations.map(a => ({ name: a.name, weight: parseFloat(a.weight) })),
        portfolio_value: portfolioValue
      };

      // Simulate API calls to your FastAPI backend
      // const response = await axios.post('http://localhost:8000/forecast_statistic/annualised_return', portfolioData);
      
      // Mock response for demonstration
      setTimeout(() => {
        setPortfolioMetrics({
          annualised_return: 0.085,
          annualised_volatility: 0.156,
          sharpe_ratio: 0.544,
          tracking_error: 0.023,
          downside_deviation: 0.112,
          value_at_risk: -0.089,
          conditional_value_at_risk: -0.134,
          maximum_drawdown: -0.234
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

  const getCategoryAllocations = () => {
    const categoryMap = {};
    allocations.forEach(allocation => {
      const category = allocation.category;
      const weight = parseFloat(allocation.weight || 0);
      categoryMap[category] = (categoryMap[category] || 0) + weight;
    });
    
    return Object.entries(categoryMap).map(([category, weight]) => ({
      category,
      weight
    }));
  };

  return (
    <div className="container">
      <h1>Portfolio Dashboard</h1>
      
      {/* Portfolio Inputs */}
      <div className="card">
        <h2>Portfolio Configuration</h2>
        
        <div className="form-group">
          <label>Starting Portfolio Value ($)</label>
          <input
            type="number"
            value={portfolioValue}
            onChange={(e) => setPortfolioValue(parseFloat(e.target.value))}
            placeholder="100000"
          />
        </div>
        
        <div className="form-group">
          <label>Asset Allocations (%)</label>
          <div style={{ marginBottom: '10px' }}>
            <strong>Total: {getTotalAllocation().toFixed(2)}%</strong>
            {getTotalAllocation() !== 100 && (
              <span style={{ color: 'red', marginLeft: '10px' }}>
                {getTotalAllocation() > 100 ? 'Over-allocated' : 'Under-allocated'}
              </span>
            )}
          </div>
          
          <table className="table">
            <thead>
              <tr>
                <th>Asset</th>
                <th>Category</th>
                <th>Weight (%)</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {allocations.map(allocation => (
                <tr key={allocation.id}>
                  <td>{allocation.name}</td>
                  <td>{allocation.category}</td>
                  <td>
                    <input
                      type="number"
                      value={allocation.weight}
                      onChange={(e) => updateAllocation(allocation.id, e.target.value)}
                      style={{ width: '80px' }}
                      step="0.01"
                    />
                  </td>
                  <td>
                    <button 
                      className="btn btn-danger" 
                      onClick={() => removeAsset(allocation.id)}
                    >
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          <button className="btn" onClick={addAsset}>
            Add Asset
          </button>
          
          <button 
            className="btn" 
            onClick={calculatePortfolioMetrics}
            disabled={loading || getTotalAllocation() !== 100}
            style={{ marginLeft: '10px' }}
          >
            {loading ? 'Calculating...' : 'Calculate Portfolio Metrics'}
          </button>
        </div>
      </div>

      {/* Allocation Charts */}
      <div className="card">
        <h2>Portfolio Allocations</h2>
        
        <div style={{ display: 'flex', gap: '20px' }}>
          {/* Individual Asset Pie Chart */}
          <div style={{ flex: 1 }}>
            <h3>Individual Assets</h3>
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
          
          {/* Category Bar Chart */}
          <div style={{ flex: 1 }}>
            <h3>By Asset Category</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={getCategoryAllocations()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="weight" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Portfolio Metrics */}
      {portfolioMetrics && (
        <div className="card">
          <h2>Portfolio Metrics</h2>
          <table className="table">
            <thead>
              <tr>
                <th>Metric</th>
                <th>Value</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Annualised Return</td>
                <td>{(portfolioMetrics.annualised_return * 100).toFixed(2)}%</td>
              </tr>
              <tr>
                <td>Annualised Volatility</td>
                <td>{(portfolioMetrics.annualised_volatility * 100).toFixed(2)}%</td>
              </tr>
              <tr>
                <td>Sharpe Ratio</td>
                <td>{portfolioMetrics.sharpe_ratio.toFixed(3)}</td>
              </tr>
              <tr>
                <td>Tracking Error</td>
                <td>{(portfolioMetrics.tracking_error * 100).toFixed(2)}%</td>
              </tr>
              <tr>
                <td>Downside Deviation</td>
                <td>{(portfolioMetrics.downside_deviation * 100).toFixed(2)}%</td>
              </tr>
              <tr>
                <td>5% Value at Risk</td>
                <td>{(portfolioMetrics.value_at_risk * 100).toFixed(2)}%</td>
              </tr>
              <tr>
                <td>5% Conditional VaR</td>
                <td>{(portfolioMetrics.conditional_value_at_risk * 100).toFixed(2)}%</td>
              </tr>
              <tr>
                <td>Maximum Drawdown</td>
                <td>{(portfolioMetrics.maximum_drawdown * 100).toFixed(2)}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      )}

      {/* Projected Portfolio Values */}
      {projectedValues && (
        <div className="card">
          <h2>Projected Portfolio Values</h2>
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
        </div>
      )}
    </div>
  );
}

export default App;
