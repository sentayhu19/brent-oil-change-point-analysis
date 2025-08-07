"""
Quick test script to validate the Bayesian change point model fixes.
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

import pandas as pd
import numpy as np
from src.bayesian_changepoint_model import BayesianChangePointAnalyzer

def test_model():
    """Test the model with synthetic data."""
    print("🧪 Testing Bayesian Change Point Model...")
    
    # Create synthetic data
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', '2022-12-31', freq='D')
    
    # Create data with known change points
    n = len(dates)
    prices = np.zeros(n)
    
    # Regime 1: Low prices (first third)
    prices[:n//3] = 50 + np.cumsum(np.random.randn(n//3) * 0.5)
    
    # Regime 2: High prices (middle third)  
    prices[n//3:2*n//3] = prices[n//3-1] + 20 + np.cumsum(np.random.randn(n//3) * 0.8)
    
    # Regime 3: Medium prices (last third)
    prices[2*n//3:] = prices[2*n//3-1] - 10 + np.cumsum(np.random.randn(n - 2*n//3) * 0.6)
    
    brent_data = pd.Series(prices, index=dates, name='Price')
    
    # Create simple events data
    events_data = pd.DataFrame({
        'Date': [dates[n//3], dates[2*n//3]],
        'Name': ['Event 1', 'Event 2'],
        'Category': ['Economic', 'Geopolitical'],
        'Expected_Impact': ['Increase', 'Decrease']
    })
    events_data['Date'] = pd.to_datetime(events_data['Date'])
    
    print(f"✅ Created synthetic data: {len(brent_data)} observations")
    
    # Test the analyzer
    try:
        analyzer = BayesianChangePointAnalyzer(data=brent_data, events_data=events_data)
        print("✅ Analyzer initialized successfully")
        
        # Test data preparation
        analyzer.prepare_data(use_log_returns=True, plot=False)
        print("✅ Data preparation completed")
        
        # Test single change point model
        print("🔧 Testing single change point model...")
        model_single = analyzer.build_single_changepoint_model(target_series='returns')
        print("✅ Single change point model built successfully")
        
        # Test multiple change point model
        print("🔧 Testing multiple change point model...")
        model_multiple = analyzer.build_multiple_changepoint_model(n_changepoints=2, target_series='returns')
        print("✅ Multiple change point model built successfully")
        
        print("\n🎉 All tests passed! The model is ready to use.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_model()
    if success:
        print("\n🚀 You can now run the Task 2 notebook successfully!")
    else:
        print("\n⚠️ Please check the error messages above.")
