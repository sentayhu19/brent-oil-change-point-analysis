"""
Event data management utilities for associating geopolitical events with oil price changes.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional

def create_major_events_dataset() -> pd.DataFrame:
    """
    Create a structured dataset of major geopolitical and economic events
    that potentially impacted Brent oil prices.
    
    Returns:
    --------
    pd.DataFrame
        DataFrame with event information
    """
    
    events_data = [
        {
            'event_id': 1,
            'date': '1990-08-02',
            'event_name': 'Iraq Invasion of Kuwait',
            'category': 'Geopolitical Conflict',
            'description': 'Iraq invaded Kuwait, leading to Gulf War and oil supply disruption',
            'expected_impact': 'Price Increase',
            'region': 'Middle East',
            'duration_days': 210  # Until end of Gulf War
        },
        {
            'event_id': 2,
            'date': '1997-07-02',
            'event_name': 'Asian Financial Crisis',
            'category': 'Economic Crisis',
            'description': 'Financial crisis in Asia leading to reduced oil demand',
            'expected_impact': 'Price Decrease',
            'region': 'Asia',
            'duration_days': 365
        },
        {
            'event_id': 3,
            'date': '2001-09-11',
            'event_name': '9/11 Terrorist Attacks',
            'category': 'Geopolitical Event',
            'description': 'Terrorist attacks in US causing market uncertainty',
            'expected_impact': 'Price Volatility',
            'region': 'North America',
            'duration_days': 30
        },
        {
            'event_id': 4,
            'date': '2003-03-20',
            'event_name': 'Iraq War Begins',
            'category': 'Geopolitical Conflict',
            'description': 'US-led invasion of Iraq disrupting oil production',
            'expected_impact': 'Price Increase',
            'region': 'Middle East',
            'duration_days': 180
        },
        {
            'event_id': 5,
            'date': '2008-09-15',
            'event_name': 'Lehman Brothers Collapse',
            'category': 'Economic Crisis',
            'description': 'Global financial crisis reducing oil demand',
            'expected_impact': 'Price Decrease',
            'region': 'Global',
            'duration_days': 365
        },
        {
            'event_id': 6,
            'date': '2010-12-17',
            'event_name': 'Arab Spring Begins',
            'category': 'Geopolitical Unrest',
            'description': 'Political upheaval across Middle East and North Africa',
            'expected_impact': 'Price Increase',
            'region': 'Middle East/North Africa',
            'duration_days': 730
        },
        {
            'event_id': 7,
            'date': '2011-03-11',
            'event_name': 'Fukushima Nuclear Disaster',
            'category': 'Natural/Industrial Disaster',
            'description': 'Nuclear disaster affecting energy markets and demand',
            'expected_impact': 'Price Increase',
            'region': 'Asia',
            'duration_days': 90
        },
        {
            'event_id': 8,
            'date': '2014-11-27',
            'event_name': 'OPEC Maintains Production',
            'category': 'OPEC Policy',
            'description': 'OPEC decides not to cut production despite falling prices',
            'expected_impact': 'Price Decrease',
            'region': 'Global',
            'duration_days': 180
        },
        {
            'event_id': 9,
            'date': '2016-11-30',
            'event_name': 'OPEC Production Cut Agreement',
            'category': 'OPEC Policy',
            'description': 'OPEC agrees to cut oil production for first time since 2008',
            'expected_impact': 'Price Increase',
            'region': 'Global',
            'duration_days': 365
        },
        {
            'event_id': 10,
            'date': '2018-05-08',
            'event_name': 'US Withdraws from Iran Nuclear Deal',
            'category': 'Sanctions/Trade',
            'description': 'US reimposed sanctions on Iran affecting oil exports',
            'expected_impact': 'Price Increase',
            'region': 'Middle East',
            'duration_days': 180
        },
        {
            'event_id': 11,
            'date': '2020-03-06',
            'event_name': 'Saudi-Russia Oil Price War',
            'category': 'OPEC Policy',
            'description': 'Saudi Arabia and Russia failed to agree on production cuts',
            'expected_impact': 'Price Decrease',
            'region': 'Global',
            'duration_days': 60
        },
        {
            'event_id': 12,
            'date': '2020-03-11',
            'event_name': 'COVID-19 Pandemic Declaration',
            'category': 'Health Crisis',
            'description': 'WHO declares COVID-19 pandemic, massive demand destruction',
            'expected_impact': 'Price Decrease',
            'region': 'Global',
            'duration_days': 365
        },
        {
            'event_id': 13,
            'date': '2021-03-23',
            'event_name': 'Suez Canal Blockage',
            'category': 'Supply Chain Disruption',
            'description': 'Ever Given ship blocks Suez Canal affecting oil transport',
            'expected_impact': 'Price Increase',
            'region': 'Middle East',
            'duration_days': 6
        },
        {
            'event_id': 14,
            'date': '2022-02-24',
            'event_name': 'Russia Invades Ukraine',
            'category': 'Geopolitical Conflict',
            'description': 'Russia invasion of Ukraine leading to energy supply concerns',
            'expected_impact': 'Price Increase',
            'region': 'Europe/Russia',
            'duration_days': 180
        },
        {
            'event_id': 15,
            'date': '2022-03-31',
            'event_name': 'IEA Strategic Reserve Release',
            'category': 'Policy Response',
            'description': 'IEA coordinates largest strategic petroleum reserve release',
            'expected_impact': 'Price Decrease',
            'region': 'Global',
            'duration_days': 90
        }
    ]
    
    # Convert to DataFrame
    df = pd.DataFrame(events_data)
    
    # Convert date to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Calculate end date
    df['end_date'] = df['date'] + pd.to_timedelta(df['duration_days'], unit='D')
    
    return df

def save_events_to_csv(df: pd.DataFrame, file_path: str) -> None:
    """
    Save events dataset to CSV file.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Events DataFrame
    file_path : str
        Path to save CSV file
    """
    df.to_csv(file_path, index=False)
    print(f"Events data saved to {file_path}")

def load_events_from_csv(file_path: str) -> pd.DataFrame:
    """
    Load events dataset from CSV file.
    
    Parameters:
    -----------
    file_path : str
        Path to CSV file
        
    Returns:
    --------
    pd.DataFrame
        Events DataFrame
    """
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    df['end_date'] = pd.to_datetime(df['end_date'])
    return df

def get_events_in_period(events_df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Filter events that occurred within a specific time period.
    
    Parameters:
    -----------
    events_df : pd.DataFrame
        Events DataFrame
    start_date : str
        Start date (YYYY-MM-DD format)
    end_date : str
        End date (YYYY-MM-DD format)
        
    Returns:
    --------
    pd.DataFrame
        Filtered events DataFrame
    """
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    
    mask = (events_df['date'] >= start) & (events_df['date'] <= end)
    return events_df[mask]

def get_events_by_category(events_df: pd.DataFrame, category: str) -> pd.DataFrame:
    """
    Filter events by category.
    
    Parameters:
    -----------
    events_df : pd.DataFrame
        Events DataFrame
    category : str
        Event category to filter by
        
    Returns:
    --------
    pd.DataFrame
        Filtered events DataFrame
    """
    return events_df[events_df['category'] == category]

def create_event_impact_windows(events_df: pd.DataFrame, 
                               pre_event_days: int = 30, 
                               post_event_days: int = 90) -> pd.DataFrame:
    """
    Create time windows around events for impact analysis.
    
    Parameters:
    -----------
    events_df : pd.DataFrame
        Events DataFrame
    pre_event_days : int
        Number of days before event to include
    post_event_days : int
        Number of days after event to include
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with impact windows
    """
    events_with_windows = events_df.copy()
    
    events_with_windows['window_start'] = (
        events_with_windows['date'] - pd.Timedelta(days=pre_event_days)
    )
    events_with_windows['window_end'] = (
        events_with_windows['date'] + pd.Timedelta(days=post_event_days)
    )
    
    return events_with_windows
