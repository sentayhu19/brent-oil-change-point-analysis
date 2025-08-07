"""
Time series analysis utilities for Brent oil price data.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import warnings

def analyze_stationarity(series: pd.Series, significance_level: float = 0.05) -> dict:
    """
    Analyze stationarity of time series using ADF and KPSS tests.
    
    Parameters:
    -----------
    series : pd.Series
        Time series data
    significance_level : float
        Significance level for hypothesis tests
        
    Returns:
    --------
    dict
        Stationarity test results
    """
    # Remove NaN values
    clean_series = series.dropna()
    
    # Augmented Dickey-Fuller test
    adf_result = adfuller(clean_series, autolag='AIC')
    
    # KPSS test
    kpss_result = kpss(clean_series, regression='c', nlags='auto')
    
    results = {
        'adf_test': {
            'statistic': adf_result[0],
            'p_value': adf_result[1],
            'critical_values': adf_result[4],
            'is_stationary': adf_result[1] < significance_level
        },
        'kpss_test': {
            'statistic': kpss_result[0],
            'p_value': kpss_result[1],
            'critical_values': kpss_result[3],
            'is_stationary': kpss_result[1] > significance_level
        }
    }
    
    # Overall conclusion
    adf_stationary = results['adf_test']['is_stationary']
    kpss_stationary = results['kpss_test']['is_stationary']
    
    if adf_stationary and kpss_stationary:
        results['conclusion'] = 'Stationary'
    elif not adf_stationary and not kpss_stationary:
        results['conclusion'] = 'Non-stationary'
    else:
        results['conclusion'] = 'Inconclusive'
    
    return results

def detect_trend(series: pd.Series) -> dict:
    """
    Detect trend in time series using various methods.
    
    Parameters:
    -----------
    series : pd.Series
        Time series data
        
    Returns:
    --------
    dict
        Trend analysis results
    """
    # Remove NaN values
    clean_series = series.dropna()
    
    # Linear trend using scipy
    x = np.arange(len(clean_series))
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, clean_series.values)
    
    # Mann-Kendall trend test
    mk_result = mann_kendall_test(clean_series.values)
    
    results = {
        'linear_trend': {
            'slope': slope,
            'r_squared': r_value**2,
            'p_value': p_value,
            'trend_direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'no trend'
        },
        'mann_kendall': mk_result,
        'overall_change': {
            'start_value': clean_series.iloc[0],
            'end_value': clean_series.iloc[-1],
            'total_change': clean_series.iloc[-1] - clean_series.iloc[0],
            'percent_change': ((clean_series.iloc[-1] - clean_series.iloc[0]) / clean_series.iloc[0]) * 100
        }
    }
    
    return results

def mann_kendall_test(data: np.array, alpha: float = 0.05) -> dict:
    """
    Perform Mann-Kendall trend test.
    
    Parameters:
    -----------
    data : np.array
        Time series data
    alpha : float
        Significance level
        
    Returns:
    --------
    dict
        Mann-Kendall test results
    """
    n = len(data)
    
    # Calculate S statistic
    s = 0
    for i in range(n-1):
        for j in range(i+1, n):
            s += np.sign(data[j] - data[i])
    
    # Calculate variance
    var_s = n * (n - 1) * (2 * n + 5) / 18
    
    # Calculate Z statistic
    if s > 0:
        z = (s - 1) / np.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / np.sqrt(var_s)
    else:
        z = 0
    
    # Calculate p-value
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))
    
    # Determine trend
    if p_value < alpha:
        if z > 0:
            trend = 'increasing'
        else:
            trend = 'decreasing'
        has_trend = True
    else:
        trend = 'no trend'
        has_trend = False
    
    return {
        's_statistic': s,
        'z_statistic': z,
        'p_value': p_value,
        'trend': trend,
        'has_significant_trend': has_trend
    }

def analyze_volatility(series: pd.Series, window: int = 30) -> dict:
    """
    Analyze volatility patterns in the time series.
    
    Parameters:
    -----------
    series : pd.Series
        Time series data
    window : int
        Rolling window for volatility calculation
        
    Returns:
    --------
    dict
        Volatility analysis results
    """
    # Calculate returns
    returns = series.pct_change().dropna()
    
    # Rolling volatility (standard deviation of returns)
    rolling_vol = returns.rolling(window=window).std()
    
    # Volatility statistics
    vol_stats = {
        'mean_volatility': rolling_vol.mean(),
        'std_volatility': rolling_vol.std(),
        'min_volatility': rolling_vol.min(),
        'max_volatility': rolling_vol.max(),
        'volatility_of_volatility': rolling_vol.std() / rolling_vol.mean()  # Coefficient of variation
    }
    
    # Identify high volatility periods (above 95th percentile)
    high_vol_threshold = rolling_vol.quantile(0.95)
    high_vol_periods = rolling_vol[rolling_vol > high_vol_threshold]
    
    results = {
        'volatility_stats': vol_stats,
        'high_volatility_threshold': high_vol_threshold,
        'high_volatility_periods': len(high_vol_periods),
        'rolling_volatility': rolling_vol
    }
    
    return results

def seasonal_analysis(series: pd.Series, model: str = 'additive', period: int = 365) -> dict:
    """
    Perform seasonal decomposition analysis.
    
    Parameters:
    -----------
    series : pd.Series
        Time series data with datetime index
    model : str
        Type of seasonal decomposition ('additive' or 'multiplicative')
    period : int
        Seasonal period (365 for yearly seasonality)
        
    Returns:
    --------
    dict
        Seasonal decomposition results
    """
    try:
        # Perform seasonal decomposition
        decomposition = seasonal_decompose(series.dropna(), model=model, period=period)
        
        # Calculate seasonal strength
        seasonal_strength = np.var(decomposition.seasonal) / np.var(decomposition.seasonal + decomposition.resid)
        
        # Calculate trend strength
        trend_strength = np.var(decomposition.trend.dropna()) / np.var(decomposition.trend.dropna() + decomposition.resid.dropna())
        
        results = {
            'seasonal_strength': seasonal_strength,
            'trend_strength': trend_strength,
            'decomposition': decomposition,
            'has_strong_seasonality': seasonal_strength > 0.6,
            'has_strong_trend': trend_strength > 0.6
        }
        
        return results
        
    except Exception as e:
        warnings.warn(f"Seasonal decomposition failed: {str(e)}")
        return {'error': str(e)}

def plot_time_series_properties(series: pd.Series, title: str = "Time Series Analysis") -> None:
    """
    Create comprehensive plots for time series analysis.
    
    Parameters:
    -----------
    series : pd.Series
        Time series data
    title : str
        Plot title
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(title, fontsize=16)
    
    # Original time series
    axes[0, 0].plot(series.index, series.values)
    axes[0, 0].set_title('Original Time Series')
    axes[0, 0].set_xlabel('Date')
    axes[0, 0].set_ylabel('Price (USD)')
    axes[0, 0].grid(True)
    
    # Returns
    returns = series.pct_change().dropna()
    axes[0, 1].plot(returns.index, returns.values)
    axes[0, 1].set_title('Daily Returns')
    axes[0, 1].set_xlabel('Date')
    axes[0, 1].set_ylabel('Return (%)')
    axes[0, 1].grid(True)
    
    # Distribution of prices
    axes[1, 0].hist(series.dropna().values, bins=50, alpha=0.7, edgecolor='black')
    axes[1, 0].set_title('Price Distribution')
    axes[1, 0].set_xlabel('Price (USD)')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].grid(True)
    
    # Rolling volatility
    rolling_vol = returns.rolling(window=30).std()
    axes[1, 1].plot(rolling_vol.index, rolling_vol.values)
    axes[1, 1].set_title('30-Day Rolling Volatility')
    axes[1, 1].set_xlabel('Date')
    axes[1, 1].set_ylabel('Volatility')
    axes[1, 1].grid(True)
    
    plt.tight_layout()
    plt.show()
