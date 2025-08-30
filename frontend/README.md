# Portfolio Dashboard Frontend

A React-based dashboard for portfolio analysis and risk management.

## Features

- **Portfolio Configuration**: Input starting value and asset allocations
- **Dynamic Asset Management**: Add/remove assets with real-time allocation tracking
- **Visualization**: Pie charts for individual assets and bar charts for categories
- **Portfolio Metrics**: Display key performance and risk measures
- **Projection Charts**: Show projected portfolio values across different percentiles

## Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start development server**:
   ```bash
   npm start
   ```

3. **Open browser**: Navigate to `http://localhost:3000`

## Dependencies

- **React 18**: Modern React with hooks
- **Recharts**: Charting library for data visualization
- **Axios**: HTTP client for API calls
- **CSS**: Custom styling with responsive design

## Project Structure

```
src/
├── App.js          # Main application component
├── index.js        # React entry point
└── index.css       # Global styles
```

## Usage

1. **Configure Portfolio**: Set starting value and asset allocations
2. **Manage Assets**: Add/remove assets and adjust weights
3. **Calculate Metrics**: Click "Calculate Portfolio Metrics" to run analysis
4. **View Results**: See charts, metrics table, and projections

## API Integration

The frontend is designed to work with your FastAPI backend. Currently uses mock data, but can easily be connected to real API endpoints.

## Building for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` folder.
