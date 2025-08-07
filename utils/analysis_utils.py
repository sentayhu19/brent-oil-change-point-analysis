"""
Analysis utilities for change point detection and event association.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from scipy import stats

def associate_events_with_changepoints(changepoints_df: pd.DataFrame,
                                     events_df: pd.DataFrame,
                                     tolerance_days: int = 30) -> pd.DataFrame:
    """
    Associate detected change points with major events.
    
    Parameters:
    -----------
    changepoints_df : pd.DataFrame
        DataFrame with detected change points
    events_df : pd.DataFrame
        DataFrame with major events
    tolerance_days : int
        Maximum days between change point and event for association
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with change point-event associations
    """
    
    associations = []
    
    for _, cp in changepoints_df.iterrows():
        cp_date = cp['mean_date']
        
        # Find events within tolerance window
        nearby_events = []
        
        for _, event in events_df.iterrows():
            event_date = pd.to_datetime(event['date'])
            days_diff = abs((cp_date - event_date).days)
            
            if days_diff <= tolerance_days:
                nearby_events.append({
                    'event_id': event['event_id'],
                    'event_name': event['event_name'],
                    'event_date': event_date,
                    'category': event['category'],
                    'expected_impact': event['expected_impact'],
                    'days_difference': days_diff,
                    'direction': 'before' if event_date < cp_date else 'after'
                })
        
        # Sort by proximity
        nearby_events.sort(key=lambda x: x['days_difference'])
        
        association = {
            'changepoint_id': cp['changepoint_id'],
            'changepoint_date': cp_date,
            'ci_lower_date': cp['ci_lower_date'],
            'ci_upper_date': cp['ci_upper_date'],
            'associated_events': len(nearby_events),
            'closest_event': nearby_events[0] if nearby_events else None,
            'all_nearby_events': nearby_events
        }
        
        associations.append(association)
    
    return pd.DataFrame(associations)

def calculate_price_impact(data: pd.Series, 
                          event_date: pd.Timestamp,
                          pre_window: int = 30,
                          post_window: int = 90) -> Dict:
    """
    Calculate price impact around an event.
    
    Parameters:
    -----------
    data : pd.Series
        Price time series
    event_date : pd.Timestamp
        Event date
    pre_window : int
        Days before event for baseline calculation
    post_window : int
        Days after event for impact measurement
        
    Returns:
    --------
    dict
        Impact metrics
    """
    
    # Define windows
    pre_start = event_date - timedelta(days=pre_window)
    pre_end = event_date - timedelta(days=1)
    post_start = event_date
    post_end = event_date + timedelta(days=post_window)
    
    # Extract data for each window
    pre_data = data[(data.index >= pre_start) & (data.index <= pre_end)]
    post_data = data[(data.index >= post_start) & (data.index <= post_end)]
    event_price = data[data.index >= event_date].iloc[0] if len(data[data.index >= event_date]) > 0 else np.nan
    
    if len(pre_data) == 0 or len(post_data) == 0:
        return {'error': 'Insufficient data for impact calculation'}
    
    # Calculate metrics
    pre_mean = pre_data.mean()
    post_mean = post_data.mean()
    
    # Immediate impact (day of event vs pre-event average)
    immediate_impact_abs = event_price - pre_mean
    immediate_impact_pct = (immediate_impact_abs / pre_mean) * 100
    
    # Average impact (post-event average vs pre-event average)
    avg_impact_abs = post_mean - pre_mean
    avg_impact_pct = (avg_impact_abs / pre_mean) * 100
    
    # Volatility impact
    pre_vol = pre_data.std()
    post_vol = post_data.std()
    vol_change = post_vol - pre_vol
    vol_change_pct = (vol_change / pre_vol) * 100 if pre_vol > 0 else 0
    
    # Statistical significance test
    t_stat, p_value = stats.ttest_ind(pre_data, post_data)
    
    return {
        'event_date': event_date,
        'pre_mean': pre_mean,
        'post_mean': post_mean,
        'event_price': event_price,
        'immediate_impact_abs': immediate_impact_abs,
        'immediate_impact_pct': immediate_impact_pct,
        'avg_impact_abs': avg_impact_abs,
        'avg_impact_pct': avg_impact_pct,
        'pre_volatility': pre_vol,
        'post_volatility': post_vol,
        'volatility_change': vol_change,
        'volatility_change_pct': vol_change_pct,
        't_statistic': t_stat,
        'p_value': p_value,
        'significant': p_value < 0.05,
        'pre_window_days': len(pre_data),
        'post_window_days': len(post_data)
    }

def analyze_regime_characteristics(data: pd.Series,
                                 changepoints: List[pd.Timestamp]) -> pd.DataFrame:
    """
    Analyze characteristics of different regimes defined by change points.
    
    Parameters:
    -----------
    data : pd.Series
        Price time series
    changepoints : list
        List of change point dates
        
    Returns:
    --------
    pd.DataFrame
        Regime characteristics
    """
    
    # Sort change points
    changepoints_sorted = sorted(changepoints)
    
    # Define regime boundaries
    boundaries = [data.index.min()] + changepoints_sorted + [data.index.max()]
    
    regimes = []
    
    for i in range(len(boundaries) - 1):
        start_date = boundaries[i]
        end_date = boundaries[i + 1]
        
        # Extract regime data
        regime_data = data[(data.index >= start_date) & (data.index < end_date)]
        
        if len(regime_data) == 0:
            continue
        
        # Calculate regime statistics
        regime_stats = {
            'regime_id': i + 1,
            'start_date': start_date,
            'end_date': end_date,
            'duration_days': (end_date - start_date).days,
            'n_observations': len(regime_data),
            'mean_price': regime_data.mean(),
            'median_price': regime_data.median(),
            'std_price': regime_data.std(),
            'min_price': regime_data.min(),
            'max_price': regime_data.max(),
            'price_range': regime_data.max() - regime_data.min(),
            'cv': regime_data.std() / regime_data.mean() if regime_data.mean() > 0 else 0,
            'skewness': stats.skew(regime_data),
            'kurtosis': stats.kurtosis(regime_data)
        }
        
        # Calculate trend
        if len(regime_data) > 1:
            x = np.arange(len(regime_data))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, regime_data.values)
            regime_stats.update({
                'trend_slope': slope,
                'trend_r_squared': r_value**2,
                'trend_p_value': p_value,
                'trend_direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'flat'
            })
        
        regimes.append(regime_stats)
    
    return pd.DataFrame(regimes)

def create_impact_summary(events_df: pd.DataFrame,
                         impact_results: List[Dict]) -> pd.DataFrame:
    """
    Create summary of event impacts.
    
    Parameters:
    -----------
    events_df : pd.DataFrame
        Events dataset
    impact_results : list
        List of impact calculation results
        
    Returns:
    --------
    pd.DataFrame
        Impact summary
    """
    
    summary_data = []
    
    for event_idx, impact in enumerate(impact_results):
        if 'error' in impact:
            continue
        
        event_info = events_df.iloc[event_idx]
        
        summary = {
            'event_id': event_info['event_id'],
            'event_name': event_info['event_name'],
            'event_date': impact['event_date'],
            'category': event_info['category'],
            'expected_impact': event_info['expected_impact'],
            'immediate_impact_pct': impact['immediate_impact_pct'],
            'avg_impact_pct': impact['avg_impact_pct'],
            'volatility_change_pct': impact['volatility_change_pct'],
            'statistically_significant': impact['significant'],
            'p_value': impact['p_value'],
            'impact_magnitude': abs(impact['avg_impact_pct']),
            'impact_direction': 'increase' if impact['avg_impact_pct'] > 0 else 'decrease'
        }
        
        summary_data.append(summary)
    
    df = pd.DataFrame(summary_data)
    
    # Sort by impact magnitude
    df = df.sort_values('impact_magnitude', ascending=False)
    
    return df

def plot_event_impact_analysis(data: pd.Series,
                              events_df: pd.DataFrame,
                              impact_results: List[Dict],
                              top_n: int = 10,
                              figsize: Tuple[int, int] = (15, 12)) -> None:
    """
    Create comprehensive event impact visualization.
    
    Parameters:
    -----------
    data : pd.Series
        Price time series
    events_df : pd.DataFrame
        Events dataset
    impact_results : list
        Impact calculation results
    top_n : int
        Number of top events to highlight
    figsize : tuple
        Figure size
    """
    
    fig, axes = plt.subplots(3, 2, figsize=figsize)
    
    # 1. Time series with top events
    ax1 = axes[0, 0]
    ax1.plot(data.index, data.values, 'b-', alpha=0.7, linewidth=1)
    
    # Get impact summary and select top events
    impact_summary = create_impact_summary(events_df, impact_results)
    top_events = impact_summary.head(top_n)
    
    for _, event in top_events.iterrows():
        color = 'red' if event['impact_direction'] == 'increase' else 'green'
        ax1.axvline(event['event_date'], color=color, alpha=0.6, linestyle='--')
    
    ax1.set_title('Price Series with Top Impact Events')
    ax1.set_ylabel('Price (USD)')
    ax1.grid(True, alpha=0.3)
    
    # 2. Impact magnitude distribution
    ax2 = axes[0, 1]
    ax2.hist(impact_summary['impact_magnitude'], bins=20, alpha=0.7, edgecolor='black')
    ax2.set_title('Distribution of Impact Magnitudes')
    ax2.set_xlabel('Impact Magnitude (%)')
    ax2.set_ylabel('Frequency')
    ax2.grid(True, alpha=0.3)
    
    # 3. Impact by category
    ax3 = axes[1, 0]
    category_impact = impact_summary.groupby('category')['impact_magnitude'].mean().sort_values(ascending=True)
    category_impact.plot(kind='barh', ax=ax3)
    ax3.set_title('Average Impact by Event Category')
    ax3.set_xlabel('Average Impact Magnitude (%)')
    
    # 4. Expected vs Actual Impact
    ax4 = axes[1, 1]
    
    # Create mapping for expected impact
    expected_mapping = {'Price Increase': 1, 'Price Decrease': -1, 'Price Volatility': 0}
    impact_summary['expected_direction'] = impact_summary['expected_impact'].map(expected_mapping)
    impact_summary['actual_direction'] = impact_summary['avg_impact_pct'].apply(lambda x: 1 if x > 0 else -1)
    
    # Scatter plot
    colors = ['red' if exp == act else 'blue' for exp, act in 
             zip(impact_summary['expected_direction'], impact_summary['actual_direction'])]
    
    ax4.scatter(impact_summary['expected_direction'], impact_summary['actual_direction'], 
               c=colors, alpha=0.6, s=impact_summary['impact_magnitude']*2)
    ax4.set_xlabel('Expected Impact Direction')
    ax4.set_ylabel('Actual Impact Direction')
    ax4.set_title('Expected vs Actual Impact Direction')
    ax4.grid(True, alpha=0.3)
    
    # 5. Top events table
    ax5 = axes[2, :]
    ax5.axis('tight')
    ax5.axis('off')
    
    # Create table data
    table_data = top_events[['event_name', 'event_date', 'category', 
                           'immediate_impact_pct', 'avg_impact_pct', 'statistically_significant']].copy()
    table_data['event_date'] = table_data['event_date'].dt.strftime('%Y-%m-%d')
    table_data['immediate_impact_pct'] = table_data['immediate_impact_pct'].round(2)
    table_data['avg_impact_pct'] = table_data['avg_impact_pct'].round(2)
    
    table = ax5.table(cellText=table_data.values,
                     colLabels=['Event', 'Date', 'Category', 'Immediate Impact (%)', 
                               'Avg Impact (%)', 'Significant'],
                     cellLoc='center',
                     loc='center')
    
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.2, 1.5)
    ax5.set_title(f'Top {top_n} Events by Impact Magnitude', pad=20)
    
    plt.tight_layout()
    plt.show()

def generate_insights_report(changepoints_df: pd.DataFrame,
                           associations_df: pd.DataFrame,
                           impact_summary: pd.DataFrame,
                           regime_analysis: pd.DataFrame) -> str:
    """
    Generate comprehensive insights report.
    
    Parameters:
    -----------
    changepoints_df : pd.DataFrame
        Detected change points
    associations_df : pd.DataFrame
        Change point-event associations
    impact_summary : pd.DataFrame
        Event impact summary
    regime_analysis : pd.DataFrame
        Regime characteristics
        
    Returns:
    --------
    str
        Formatted insights report
    """
    
    report = []
    report.append("=" * 80)
    report.append("BRENT OIL CHANGE POINT ANALYSIS - INSIGHTS REPORT")
    report.append("=" * 80)
    report.append("")
    
    # Change Points Summary
    report.append("📍 CHANGE POINTS DETECTED")
    report.append("-" * 40)
    report.append(f"Total Change Points: {len(changepoints_df)}")
    
    for _, cp in changepoints_df.iterrows():
        report.append(f"  • Change Point {cp['changepoint_id']}: {cp['mean_date'].strftime('%Y-%m-%d')}")
    
    report.append("")
    
    # Event Associations
    report.append("🔗 EVENT ASSOCIATIONS")
    report.append("-" * 40)
    
    associated_count = sum(1 for _, assoc in associations_df.iterrows() if assoc['associated_events'] > 0)
    report.append(f"Change Points with Associated Events: {associated_count}/{len(associations_df)}")
    
    for _, assoc in associations_df.iterrows():
        if assoc['closest_event']:
            event = assoc['closest_event']
            report.append(f"  • CP {assoc['changepoint_id']} ↔ {event['event_name']}")
            report.append(f"    Date: {event['event_date'].strftime('%Y-%m-%d')} ({event['days_difference']} days {event['direction']})")
    
    report.append("")
    
    # Top Impact Events
    report.append("💥 TOP IMPACT EVENTS")
    report.append("-" * 40)
    
    top_events = impact_summary.head(5)
    for _, event in top_events.iterrows():
        direction = "↑" if event['impact_direction'] == 'increase' else "↓"
        significance = "***" if event['statistically_significant'] else ""
        report.append(f"  {direction} {event['event_name']}: {event['avg_impact_pct']:.1f}% {significance}")
        report.append(f"    Category: {event['category']} | Date: {event['event_date'].strftime('%Y-%m-%d')}")
    
    report.append("")
    
    # Regime Analysis
    report.append("📊 REGIME CHARACTERISTICS")
    report.append("-" * 40)
    
    for _, regime in regime_analysis.iterrows():
        report.append(f"  Regime {regime['regime_id']}: {regime['start_date'].strftime('%Y-%m-%d')} to {regime['end_date'].strftime('%Y-%m-%d')}")
        report.append(f"    Duration: {regime['duration_days']} days | Mean Price: ${regime['mean_price']:.2f}")
        report.append(f"    Volatility: {regime['std_price']:.2f} | Trend: {regime.get('trend_direction', 'N/A')}")
    
    report.append("")
    
    # Key Insights
    report.append("💡 KEY INSIGHTS")
    report.append("-" * 40)
    
    # Most impactful category
    category_impact = impact_summary.groupby('category')['impact_magnitude'].mean()
    top_category = category_impact.idxmax()
    report.append(f"  • Most impactful event category: {top_category}")
    
    # Prediction accuracy
    correct_predictions = sum(1 for _, event in impact_summary.iterrows() 
                            if (event['expected_impact'] == 'Price Increase' and event['impact_direction'] == 'increase') or
                               (event['expected_impact'] == 'Price Decrease' and event['impact_direction'] == 'decrease'))
    
    accuracy = (correct_predictions / len(impact_summary)) * 100
    report.append(f"  • Prediction accuracy: {accuracy:.1f}%")
    
    # Volatility periods
    high_vol_regimes = regime_analysis[regime_analysis['cv'] > regime_analysis['cv'].median()]
    report.append(f"  • High volatility periods: {len(high_vol_regimes)} regimes")
    
    report.append("")
    report.append("=" * 80)
    
    return "\n".join(report)
