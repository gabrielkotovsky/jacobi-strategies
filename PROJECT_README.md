# Portfolio Dashboard - Investment Engineer Technical Test

A complete portfolio analysis system with FastAPI backend and React frontend for calculating portfolio statistics using simulated asset-class projections.

## 🏗️ Project Structure

```
jacobi-strategies/
├── README.md                    # Original project requirements
├── PROJECT_README.md            # This file - setup instructions
├── requirements.txt             # Python backend dependencies
├── start_dev.sh                 # Development startup script
├── data/                        # Data files
│   ├── base_simulation.hdf5    # HDF5 simulation data
│   └── asset_categories.csv    # Asset categorization
├── frontend/                    # React frontend application
│   ├── package.json            # Node.js dependencies
│   ├── src/                    # React source code
│   │   ├── App.js             # Main dashboard component
│   │   ├── index.js           # React entry point
│   │   └── index.css          # Styling
│   └── public/                 # Static assets
└── main.py                     # FastAPI backend (to be created)
```

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)
```bash
./start_dev.sh
```

This script will:
- Start the FastAPI backend on port 8000
- Start the React frontend on port 3000
- Open both servers automatically

### Option 2: Manual Startup

#### Backend (Terminal 1)
```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Start FastAPI server
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend (Terminal 2)
```bash
cd frontend

# Install Node.js dependencies
npm install

# Start React development server
npm start
```

## 🌐 Access Points

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Interactive API Docs**: http://localhost:8000/redoc

## 📊 Features

### Frontend Dashboard
- ✅ Portfolio configuration with starting value input
- ✅ Dynamic asset allocation management (add/remove assets)
- ✅ Real-time allocation tracking (must equal 100%)
- ✅ Individual asset pie chart
- ✅ Asset category bar chart
- ✅ Portfolio metrics table
- ✅ Projected portfolio values chart (percentile-based)
- ✅ Responsive design with modern UI

### Backend API (To be implemented)
- 🔄 Portfolio statistics endpoints
- 🔄 Monte Carlo simulation integration
- 🔄 Risk metrics calculations
- 🔄 Data validation and error handling

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Uvicorn**: ASGI server
- **h5py**: HDF5 file processing
- **NumPy/Pandas**: Numerical computing and data analysis
- **Pydantic**: Data validation

### Frontend
- **React 18**: Modern React with hooks
- **Recharts**: Professional charting library
- **Axios**: HTTP client for API calls
- **CSS3**: Custom responsive styling

## 📈 Data Structure

Your HDF5 file contains:
- **25 asset classes** (bonds, equities, alternatives, etc.)
- **20 time periods** (simulated years)
- **10,000 simulation scenarios** (Monte Carlo paths)
- **Periodic returns** (not cumulative)

## 🔧 Development

### Backend Development
1. Create `main.py` with FastAPI app
2. Implement the 8 required endpoints:
   - `/forecast_statistic/annualised_return`
   - `/forecast_statistic/annualised_volatility`
   - `/forecast_statistic/sharpe_ratio`
   - `/forecast_statistic/tracking_error`
   - `/forecast_statistic/downside_deviation`
   - `/forecast_statistic/value_at_risk`
   - `/forecast_statistic/conditional_value_at_risk`
   - `/forecast_statistic/maximum_drawdown`

### Frontend Development
1. Connect mock data to real API calls
2. Replace placeholder asset names with real data from HDF5
3. Implement real-time portfolio calculations
4. Add error handling and loading states

## 🧪 Testing

### Backend Testing
```bash
# Run Python tests
python3 -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

## 📦 Building for Production

### Frontend Build
```bash
cd frontend
npm run build
```

### Backend Deployment
```bash
# Install production dependencies
pip3 install -r requirements.txt

# Run with production server
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🔍 Troubleshooting

### Common Issues
1. **Port conflicts**: Ensure ports 8000 and 3000 are available
2. **Python dependencies**: Run `pip3 install -r requirements.txt`
3. **Node dependencies**: Run `cd frontend && npm install`
4. **HDF5 file access**: Ensure data files are in the `data/` directory

### Backend Issues
- Check FastAPI logs for error messages
- Verify HDF5 file path and permissions
- Ensure all Python packages are installed

### Frontend Issues
- Check browser console for JavaScript errors
- Verify React development server is running
- Check network tab for API call failures

## 📚 Next Steps

1. **Implement FastAPI backend** with portfolio calculation endpoints
2. **Connect frontend to real API** instead of mock data
3. **Add comprehensive error handling** and validation
4. **Implement unit tests** for both backend and frontend
5. **Add data persistence** for portfolio configurations
6. **Enhance visualization** with more chart types and interactivity

## 🤝 Contributing

This is a technical assessment project. The code structure is designed to be:
- **Clean and maintainable**
- **Well-documented**
- **Easy to extend**
- **Production-ready**

## 📄 License

This project is created for the Investment Engineer Technical Test.
