# Portfolio Dashboard Frontend

A modern React-based portfolio visualization dashboard with real-time allocation tracking and comprehensive risk metrics.

## Features

### Left Panel (1/3 width)
- **Initial Portfolio Value Input**: Set your starting portfolio value
- **Asset Allocations Grid**: 
  - Real-time weight input for each asset
  - Cumulative weight tracking with visual feedback
  - Assets loaded from `data/asset_categories.csv`
- **Compounding Method Selector**: Choose between geometric or arithmetic compounding
- **Calculate Button**: Trigger portfolio analysis (disabled until 100% allocation)

### Right Panel (2/3 width)
- **Individual Asset Allocation Pie Chart**: Visual breakdown of asset weights
- **Asset Category Allocation Bar Chart**: Grouped view by asset categories
- **Projected Portfolio Values Chart**: Multi-percentile projections across years (1st, 5th, 25th, 50th, 75th, 95th, 99th)
- **Portfolio Performance & Risk Metrics Table**:
  - Annualised volatility
  - Annualised downside deviation
  - 5% Value at Risk (VaR)
  - 5% Conditional Value at Risk (CVaR)
  - Maximum drawdown
- **Asset Metrics Tables**:
  - Annualised return and volatility per asset
  - Asset return correlation matrix with color coding

## Technology Stack

- **React 18.2.0**: Modern React with hooks
- **Recharts 2.8.0**: Professional charting library
- **CSS3**: Modern styling with gradients, shadows, and responsive design
- **Axios**: HTTP client for API calls (configured for backend integration)

## Getting Started

### Prerequisites
- Node.js (v14 or higher)
- npm or yarn

### Installation
```bash
cd frontend
npm install
```

### Development
```bash
npm start
```
The dashboard will open at `http://localhost:3000`

### Build for Production
```bash
npm run build
```

## Data Sources

The dashboard currently uses mock data but is designed to integrate with the FastAPI backend:

- **Asset Categories**: Loaded from `data/asset_categories.csv`
- **Portfolio Metrics**: Mock data (ready for API integration)
- **Projected Values**: Mock percentile data (ready for API integration)
- **Asset Metrics**: Mock return/volatility data (ready for API integration)
- **Correlation Matrix**: Mock correlation data (ready for API integration)

## API Integration Points

The dashboard is prepared to integrate with the following FastAPI endpoints:

1. **Portfolio Analysis**: `POST /forecast_statistic/annualised_return`
2. **Risk Metrics**: Various risk calculation endpoints
3. **Projection Data**: Portfolio value projection endpoints
4. **Asset Data**: Asset performance and correlation endpoints

## Design Features

- **Responsive Layout**: Adapts to different screen sizes
- **Modern UI**: Glassmorphism design with gradients and shadows
- **Real-time Updates**: Live weight calculation and validation
- **Color-coded Feedback**: Visual indicators for allocation status
- **Interactive Charts**: Hover effects and tooltips
- **Accessibility**: Proper contrast ratios and keyboard navigation

## File Structure

```
src/
├── App.js          # Main dashboard component
├── App.css         # Dashboard styling
├── index.js        # React entry point
└── index.css       # Global styles
```

## Customization

### Adding New Assets
Assets are loaded from the CSV file. To add new assets:
1. Update `data/asset_categories.csv`
2. The dashboard will automatically include them in the allocation grid

### Styling
- Main styles: `src/App.css`
- Global styles: `src/index.css`
- Color scheme: Purple gradient theme with white cards

### Chart Customization
- Chart colors: Defined in `COLORS` array in `App.js`
- Chart dimensions: Controlled via `ResponsiveContainer`
- Chart types: Pie, Bar, and Line charts from Recharts

## Future Enhancements

- [ ] Real API integration with FastAPI backend
- [ ] Portfolio save/load functionality
- [ ] Export capabilities (PDF, Excel)
- [ ] Advanced filtering and sorting
- [ ] Historical performance tracking
- [ ] User authentication and profiles
- [ ] Real-time data feeds
- [ ] Mobile-optimized interface

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Development Notes

- The dashboard uses mock data for demonstration
- All API calls are commented out and ready for backend integration
- The layout is fully responsive and mobile-friendly
- Performance optimized with React hooks and efficient re-renders
