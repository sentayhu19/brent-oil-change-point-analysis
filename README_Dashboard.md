# Brent Oil Change Point Analysis Dashboard

Interactive web dashboard for visualizing Bayesian change point analysis results of Brent oil prices.

## Architecture

The dashboard consists of two main components:

### Backend (Flask API)
- **Location**: `/backend/`
- **Technology**: Flask + Flask-CORS
- **Purpose**: Serves analysis results from the Bayesian change point model via REST API
- **Port**: 5000

### Frontend (React App)
- **Location**: `/frontend/`
- **Technology**: React 18 + Recharts + Styled Components
- **Purpose**: Interactive user interface for data visualization and exploration
- **Port**: 3000

## Features

### 📊 Main Dashboard
- Real-time price chart with change points and events overlay
- Summary statistics cards
- Interactive date range filtering
- Change points list with event associations
- Major events timeline

### 🔍 Analysis Details
- Quantified impact analysis of each change point
- Price and volatility impact charts
- Model diagnostics and convergence metrics
- Detailed impact summary table

### 📅 Event Explorer
- Comprehensive event filtering and search
- Event type categorization
- Association status indicators
- Chronological event timeline

### 🎨 UI/UX Features
- Responsive design (desktop and mobile)
- Interactive charts with tooltips
- Real-time data loading with skeleton screens
- Toast notifications for user feedback
- Clean, modern interface

## Quick Start

### Prerequisites
- Python 3.8+ with dependencies from main `requirements.txt`
- Node.js 16+ and npm
- Completed Task 1 and Task 2 analysis

### 1. Start the Backend API

```bash
cd backend
pip install -r requirements.txt
python app.py
```

The API will be available at `http://localhost:5000`

### 2. Start the Frontend

```bash
cd frontend
npm install
npm start
```

The dashboard will open at `http://localhost:3000`

## API Endpoints

### Core Data Endpoints
- `GET /api/health` - Health check and status
- `GET /api/historical-data` - Brent oil price data with optional date filtering
- `GET /api/change-points` - Detected change points with confidence intervals
- `GET /api/events` - Major events with filtering options
- `GET /api/event-associations` - Change point to event associations
- `GET /api/impact-analysis` - Quantified impact analysis
- `GET /api/model-diagnostics` - Model performance metrics
- `GET /api/summary` - Analysis summary statistics

### Query Parameters
- `start_date`, `end_date` - Date range filtering (YYYY-MM-DD)
- `type` - Event type filtering
- All endpoints support CORS for frontend integration

## Component Structure

### Frontend Components
```
src/
├── components/
│   ├── Header.js                 # Navigation header
│   ├── PriceChart.js            # Main interactive price chart
│   ├── SummaryStats.js          # Statistics cards
│   ├── DateRangeFilter.js       # Date filtering component
│   ├── ChangePointsList.js      # Change points display
│   ├── EventsList.js            # Events display
│   ├── ImpactAnalysisChart.js   # Impact visualization
│   └── ModelDiagnostics.js      # Model performance display
├── pages/
│   ├── Dashboard.js             # Main dashboard page
│   ├── AnalysisDetails.js       # Detailed analysis page
│   └── EventExplorer.js         # Event exploration page
├── services/
│   └── api.js                   # API service layer
└── App.js                       # Main application component
```

### Backend Structure
```
backend/
├── app.py                       # Flask application with API endpoints
└── requirements.txt             # Python dependencies
```

## Data Flow

1. **Initialization**: Backend loads and processes analysis results from Task 2
2. **API Layer**: Flask serves processed data via REST endpoints
3. **Frontend**: React components fetch data and render interactive visualizations
4. **User Interaction**: Filters and selections trigger API calls for updated data
5. **Real-time Updates**: Dashboard reflects changes immediately

## Customization

### Adding New Visualizations
1. Create new component in `/frontend/src/components/`
2. Add API endpoint in `/backend/app.py` if needed
3. Integrate component into relevant page

### Extending API
1. Add new endpoint function in `/backend/app.py`
2. Update API service in `/frontend/src/services/api.js`
3. Use new endpoint in React components

### Styling
- Global styles in `/frontend/src/index.css`
- Component-specific styles using inline styles or styled-components
- Responsive design with CSS Grid and Flexbox

## Deployment

### Development
- Backend: `python backend/app.py`
- Frontend: `npm start` in frontend directory

### Production
- Backend: Use production WSGI server (gunicorn, uWSGI)
- Frontend: `npm run build` and serve static files
- Consider containerization with Docker

## Troubleshooting

### Common Issues
1. **Backend not starting**: Check if Task 2 analysis data is available
2. **Frontend API errors**: Ensure backend is running on port 5000
3. **Chart not rendering**: Check browser console for JavaScript errors
4. **Data not loading**: Verify API endpoints return valid JSON

### Performance
- Large datasets may require pagination
- Consider caching for frequently accessed data
- Optimize chart rendering for better performance

## Future Enhancements

### Planned Features
- Real-time data updates
- Export functionality (PDF, CSV)
- Advanced filtering options
- User preferences and settings
- Mobile app version

### Technical Improvements
- Database integration for data persistence
- Authentication and user management
- Advanced caching strategies
- Performance monitoring
- Automated testing suite

## Dependencies

### Backend
- Flask 2.3.3
- Flask-CORS 4.0.0
- pandas, numpy, pymc, arviz (from main requirements.txt)

### Frontend
- React 18.2.0
- Recharts 2.8.0 (charting library)
- React Router DOM 6.15.0 (routing)
- React DatePicker 4.16.0 (date selection)
- React Toastify 9.1.3 (notifications)
- Axios 1.5.0 (HTTP client)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review browser console and backend logs
3. Ensure all dependencies are correctly installed
4. Verify data files are present and accessible
