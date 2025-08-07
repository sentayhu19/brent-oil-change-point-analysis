"""
Data loading and preprocessing utilities for Brent oil price analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Tuple, Optional
import warnings

def load_brent_data(file_path: str) -> pd.DataFrame:
    """
    Load Brent oil price data from CSV file.
    
    Parameters:
    -----------
    file_path : str
        Path to the CSV file containing Brent oil data
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with Date and Price columns, Date as datetime index
    """
    try:
        # Load the data
        df = pd.read_csv(file_path)
        
        # Convert Date column to datetime
        df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%y', errors='coerce')
        
        # Handle any parsing errors
        if df['Date'].isna().any():
            warnings.warn("Some dates could not be parsed. Check date format.")
        
        # Set Date as index
        df.set_index('Date', inplace=True)
        
        # Sort by date
        df.sort_index(inplace=True)
        
        # Convert Price to numeric
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        
        print(f"Data loaded successfully: {len(df)} records from {df.index.min()} to {df.index.max()}")
        
        return df
        
    except Exception as e:
        raise Exception(f"Error loading data: {str(e)}")

def get_data_summary(df: pd.DataFrame) -> dict:
    """
    Get summary statistics of the Brent oil data.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with Brent oil price data
        
    Returns:
    --------
    dict
        Summary statistics
    """
    summary = {
        'total_records': len(df),
        'date_range': (df.index.min(), df.index.max()),
        'price_stats': df['Price'].describe().to_dict(),
        'missing_values': df['Price'].isna().sum(),
        'data_frequency': pd.infer_freq(df.index)
    }
    
    return summary

def check_data_quality(df: pd.DataFrame) -> dict:
    """
    Check data quality issues in the Brent oil dataset.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with Brent oil price data
        
    Returns:
    --------
    dict
        Data quality report
    """
    quality_report = {
        'missing_dates': df.index.duplicated().sum(),
        'missing_prices': df['Price'].isna().sum(),
        'zero_prices': (df['Price'] == 0).sum(),
        'negative_prices': (df['Price'] < 0).sum(),
        'outliers_iqr': detect_outliers_iqr(df['Price']),
        'data_gaps': detect_data_gaps(df)
    }
    
    return quality_report

def detect_outliers_iqr(series: pd.Series, multiplier: float = 1.5) -> int:
    """
    Detect outliers using IQR method.
    
    Parameters:
    -----------
    series : pd.Series
        Price series
    multiplier : float
        IQR multiplier for outlier detection
        
    Returns:
    --------
    int
        Number of outliers detected
    """
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR
    
    outliers = ((series < lower_bound) | (series > upper_bound)).sum()
    
    return outliers

def detect_data_gaps(df: pd.DataFrame, max_gap_days: int = 7) -> int:
    """
    Detect significant gaps in the time series data.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with datetime index
    max_gap_days : int
        Maximum acceptable gap in days
        
    Returns:
    --------
    int
        Number of significant gaps detected
    """
    date_diffs = df.index.to_series().diff()
    significant_gaps = (date_diffs > pd.Timedelta(days=max_gap_days)).sum()
    
    return significant_gaps
