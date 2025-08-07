"""
Flask API Backend for Brent Oil Change Point Analysis Dashboard

This module provides REST API endpoints to serve analysis results from the
Bayesian change point model for interactive visualization.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from bayesian_changepoint_model import BayesianChangePointAnalyzer
from data_loader import load_brent_data
from event_data import load_events_from_csv

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Global variables to cache analysis results
analyzer = None
analysis_results = None
historical_data = None
events_data = None

def initialize_analysis():
    """Initialize the Bayesian change point analysis and cache results."""
    global analyzer, analysis_results, historical_data, events_data
    
    try:
        # Load data
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data')
        brent_file = os.path.join(data_path, 'BrentOilPrices.csv')
        events_file = os.path.join(data_path, 'major_events.csv')
        
        historical_data = load_brent_data(brent_file)
        events_data = load_events_from_csv(events_file)
        
        # Fix column names for compatibility
        if 'Price' in historical_data.columns:
            historical_data['price'] = historical_data['Price']
        
        # Map events column names for API compatibility
        if 'event_name' in events_data.columns:
            events_data['event'] = events_data['event_name']
        if 'category' in events_data.columns:
            events_data['type'] = events_data['category']
        
        print(f"Historical data columns: {historical_data.columns.tolist()}")
        print(f"Historical data shape: {historical_data.shape}")
        print(f"Events data columns: {events_data.columns.tolist()}")
        print(f"Events data shape: {events_data.shape}")
        
        # Initialize analyzer
        analyzer = BayesianChangePointAnalyzer(historical_data, events_data)
        
        # Initialize analyzer (but don't run heavy computations yet)
        print("🔄 Initializing Bayesian change point analyzer...")
        analyzer.prepare_data(plot=False)  # Skip plotting during startup
        
        print("✅ Analyzer initialized successfully!")
        print("📊 Model fitting will be performed on-demand when API endpoints are called")
        
        # Initialize empty results (will be populated on first API call)
        analysis_results = {
            'change_points': [],
            'event_associations': [],
            'impact_analysis': [],
            'model_diagnostics': {}
        }
        
        print("Analysis initialized successfully!")
        return True
        
    except Exception as e:
        print(f"Error initializing analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def ensure_analysis_complete():
    """Ensure the full analysis has been run, run it if needed."""
    global analyzer, analysis_results
    
    if not analysis_results or not analysis_results.get('change_points'):
        print("🔄 Running Bayesian change point analysis...")
        try:
            # Build and fit multiple change point model
            analyzer.build_multiple_changepoint_model(n_changepoints=4)
            analyzer.fit_model(draws=1000, tune=1000, chains=2)
            
            # Extract results
            change_points = analyzer.extract_changepoints()
            event_associations = analyzer.associate_events_with_changepoints()
            impact_analysis = analyzer.quantify_changepoint_impacts()
            
            analysis_results.update({
                'change_points': change_points,
                'event_associations': event_associations,
                'impact_analysis': impact_analysis,
                'model_diagnostics': analyzer.get_model_diagnostics()
            })
            
            print("✅ Analysis completed successfully!")
            return True
        except Exception as e:
            print(f"❌ Error during analysis: {str(e)}")
            return False
    return True

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'analysis_ready': analysis_results is not None
    })

@app.route('/api/historical-data', methods=['GET'])
def get_historical_data():
    """Get historical Brent oil price data with optional date filtering."""
    if historical_data is None:
        return jsonify({'error': 'Historical data not available'}), 500
    
    # Get query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    data = historical_data.copy()
    
    # Apply date filtering if provided
    if start_date:
        data = data[data.index >= pd.to_datetime(start_date)]
    if end_date:
        data = data[data.index <= pd.to_datetime(end_date)]
    
    # Convert to JSON-serializable format
    result = {
        'dates': data.index.strftime('%Y-%m-%d').tolist(),
        'prices': data['price'].tolist(),
        'log_returns': data['log_returns'].tolist() if 'log_returns' in data.columns else None,
        'total_records': len(data),
        'date_range': {
            'start': data.index.min().strftime('%Y-%m-%d'),
            'end': data.index.max().strftime('%Y-%m-%d')
        }
    }
    
    return jsonify(result)

@app.route('/api/change-points', methods=['GET'])
def get_change_points():
    """Get detected change points with uncertainty intervals."""
    if not ensure_analysis_complete():
        return jsonify({'error': 'Change point analysis failed'}), 500
    
    if analysis_results is None or 'change_points' not in analysis_results:
        return jsonify({'error': 'Change point analysis not available'}), 500
    
    change_points = analysis_results['change_points']
    
    # Convert to JSON-serializable format
    result = []
    for i, cp in enumerate(change_points):
        result.append({
            'id': i,
            'date': cp['date'].strftime('%Y-%m-%d'),
            'probability': float(cp['probability']),
            'confidence_interval': {
                'lower': cp['confidence_interval'][0].strftime('%Y-%m-%d'),
                'upper': cp['confidence_interval'][1].strftime('%Y-%m-%d')
            },
            'price_at_changepoint': float(cp.get('price_at_changepoint', 0))
        })
    
    return jsonify(result)

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get major events data with optional filtering."""
    if events_data is None:
        return jsonify({'error': 'Events data not available'}), 500
    
    # Get query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    event_type = request.args.get('type')
    
    data = events_data.copy()
    
    # Apply filters
    if start_date:
        data = data[data['date'] >= pd.to_datetime(start_date)]
    if end_date:
        data = data[data['date'] <= pd.to_datetime(end_date)]
    if event_type:
        data = data[data['type'].str.contains(event_type, case=False, na=False)]
    
    # Convert to JSON-serializable format
    result = []
    for _, event in data.iterrows():
        result.append({
            'id': event.name,
            'date': event['date'].strftime('%Y-%m-%d'),
            'event': event['event'],
            'type': event['type'],
            'description': event.get('description', ''),
            'impact_level': event.get('impact_level', 'medium')
        })
    
    return jsonify(result)

@app.route('/api/event-associations', methods=['GET'])
def get_event_associations():
    """Get associations between change points and events."""
    if not ensure_analysis_complete():
        return jsonify({'error': 'Event associations analysis failed'}), 500
    
    if analysis_results is None or 'event_associations' not in analysis_results:
        return jsonify({'error': 'Event associations not available'}), 500
    
    associations = analysis_results['event_associations']
    
    # Convert to JSON-serializable format
    result = []
    for assoc in associations:
        result.append({
            'changepoint_id': assoc['changepoint_id'],
            'changepoint_date': assoc['changepoint_date'].strftime('%Y-%m-%d'),
            'associated_events': [
                {
                    'event_id': event['event_id'],
                    'event_date': event['event_date'].strftime('%Y-%m-%d'),
                    'event_name': event['event_name'],
                    'days_difference': int(event['days_difference']),
                    'confidence': float(event.get('confidence', 0.5))
                }
                for event in assoc['associated_events']
            ]
        })
    
    return jsonify(result)

@app.route('/api/impact-analysis', methods=['GET'])
def get_impact_analysis():
    """Get quantified impact analysis of change points."""
    if not ensure_analysis_complete():
        return jsonify({'error': 'Impact analysis failed'}), 500
    
    if analysis_results is None or 'impact_analysis' not in analysis_results:
        return jsonify({'error': 'Impact analysis not available'}), 500
    
    impacts = analysis_results['impact_analysis']
    
    # Convert to JSON-serializable format
    result = []
    for impact in impacts:
        result.append({
            'changepoint_id': impact['changepoint_id'],
            'changepoint_date': impact['changepoint_date'].strftime('%Y-%m-%d'),
            'price_impact': {
                'before_mean': float(impact['price_impact']['before_mean']),
                'after_mean': float(impact['price_impact']['after_mean']),
                'change_percent': float(impact['price_impact']['change_percent']),
                'significance': impact['price_impact'].get('significance', 'unknown')
            },
            'volatility_impact': {
                'before_std': float(impact['volatility_impact']['before_std']),
                'after_std': float(impact['volatility_impact']['after_std']),
                'change_percent': float(impact['volatility_impact']['change_percent']),
                'significance': impact['volatility_impact'].get('significance', 'unknown')
            }
        })
    
    return jsonify(result)

@app.route('/api/model-diagnostics', methods=['GET'])
def get_model_diagnostics():
    """Get model diagnostics and performance metrics."""
    if analysis_results is None or 'model_diagnostics' not in analysis_results:
        return jsonify({'error': 'Model diagnostics not available'}), 500
    
    diagnostics = analysis_results['model_diagnostics']
    
    # Convert to JSON-serializable format (handle numpy types)
    result = {}
    for key, value in diagnostics.items():
        if isinstance(value, (np.integer, np.floating)):
            result[key] = float(value)
        elif isinstance(value, np.ndarray):
            result[key] = value.tolist()
        elif isinstance(value, dict):
            result[key] = {k: float(v) if isinstance(v, (np.integer, np.floating)) else v 
                          for k, v in value.items()}
        else:
            result[key] = value
    
    return jsonify(result)

@app.route('/api/summary', methods=['GET'])
def get_summary():
    """Get a summary of the analysis results."""
    if analysis_results is None:
        return jsonify({'error': 'Analysis results not available'}), 500
    
    summary = {
        'total_changepoints': len(analysis_results.get('change_points', [])),
        'total_events': len(events_data) if events_data is not None else 0,
        'associated_events': sum(len(assoc['associated_events']) 
                               for assoc in analysis_results.get('event_associations', [])),
        'data_period': {
            'start': historical_data.index.min().strftime('%Y-%m-%d') if historical_data is not None else None,
            'end': historical_data.index.max().strftime('%Y-%m-%d') if historical_data is not None else None,
            'total_days': len(historical_data) if historical_data is not None else 0
        },
        'model_performance': analysis_results.get('model_diagnostics', {}).get('summary_stats', {}),
        'last_updated': datetime.now().isoformat()
    }
    
    return jsonify(summary)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("Initializing Brent Oil Change Point Analysis API...")
    
    # Initialize analysis on startup
    if initialize_analysis():
        print("Starting Flask server...")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("Failed to initialize analysis. Please check your data files and dependencies.")
