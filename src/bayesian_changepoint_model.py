"""
Bayesian Change Point Detection Model for Brent Oil Price Analysis.

This module implements a clean, modular Bayesian change point detection model using PyMC
to identify structural breaks in Brent oil price time series data following Task 2 requirements.
"""

import numpy as np
import pandas as pd
import pymc as pm
import arviz as az
import pytensor.tensor as pt
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple, List, Dict, Optional, Union
import warnings
from datetime import datetime, timedelta

class BayesianChangePointAnalyzer:
    """
    Clean, modular Bayesian Change Point Detection Model for time series analysis.
    
    This class implements Task 2 requirements with a focus on:
    - Data preparation and EDA
    - Bayesian model building with PyMC
    - Change point identification and interpretation
    - Event association and impact quantification
    """
    
    def __init__(self, data: pd.Series, events_data: pd.DataFrame = None):
        """
        Initialize the change point analyzer.
        
        Parameters:
        -----------
        data : pd.Series
            Time series data with datetime index (Brent oil prices)
        events_data : pd.DataFrame, optional
            Major events data for association analysis
        """
        self.data = data.dropna().copy()
        self.events_data = events_data
        self.log_returns = None
        self.model = None
        self.trace = None
        self.change_points = None
        self.results = {}
        
        # Ensure datetime index
        if not isinstance(self.data.index, pd.DatetimeIndex):
            raise ValueError("Data must have a datetime index")
    
    def prepare_data(self, use_log_returns: bool = True, plot: bool = True):
        """
        Prepare data for analysis including log returns transformation.
        
        Parameters:
        -----------
        use_log_returns : bool
            Whether to use log returns for modeling (recommended for price data)
        plot : bool
            Whether to create exploratory plots
        """
        print("📊 Preparing data for change point analysis...")
        
        # Calculate log returns if requested
        if use_log_returns:
            self.log_returns = np.log(self.data).diff().dropna()
            print(f"✅ Calculated log returns: {len(self.log_returns)} observations")
        
        # Store data summary
        self.results['data_summary'] = {
            'start_date': self.data.index.min(),
            'end_date': self.data.index.max(),
            'n_observations': len(self.data),
            'price_range': (self.data.min(), self.data.max()),
            'mean_price': self.data.mean(),
            'std_price': self.data.std()
        }
        
        if use_log_returns and self.log_returns is not None:
            self.results['returns_summary'] = {
                'mean_return': self.log_returns.mean(),
                'std_return': self.log_returns.std(),
                'skewness': self.log_returns.skew(),
                'kurtosis': self.log_returns.kurtosis()
            }
        
        if plot:
            self._plot_exploratory_analysis()
    
    def _plot_exploratory_analysis(self):
        """Create exploratory data analysis plots."""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Brent Oil Price - Exploratory Data Analysis', fontsize=16, fontweight='bold')
        
        # Raw price series
        axes[0, 0].plot(self.data.index, self.data.values, linewidth=1, alpha=0.8)
        axes[0, 0].set_title('Brent Oil Prices Over Time')
        axes[0, 0].set_ylabel('Price (USD)')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Add major events if available
        if self.events_data is not None:
            for _, event in self.events_data.iterrows():
                event_date = pd.to_datetime(event['Date'])
                if event_date >= self.data.index.min() and event_date <= self.data.index.max():
                    axes[0, 0].axvline(event_date, color='red', alpha=0.6, linestyle='--', linewidth=1)
        
        # Log returns if calculated
        if self.log_returns is not None:
            axes[0, 1].plot(self.log_returns.index, self.log_returns.values, linewidth=0.8, alpha=0.7)
            axes[0, 1].set_title('Log Returns')
            axes[0, 1].set_ylabel('Log Return')
            axes[0, 1].grid(True, alpha=0.3)
        
        # Price distribution
        axes[1, 0].hist(self.data.values, bins=50, alpha=0.7, edgecolor='black')
        axes[1, 0].set_title('Price Distribution')
        axes[1, 0].set_xlabel('Price (USD)')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Returns distribution if available
        if self.log_returns is not None:
            axes[1, 1].hist(self.log_returns.values, bins=50, alpha=0.7, edgecolor='black')
            axes[1, 1].set_title('Log Returns Distribution')
            axes[1, 1].set_xlabel('Log Return')
            axes[1, 1].set_ylabel('Frequency')
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def build_single_changepoint_model(self, target_series: str = 'returns', 
                                     prior_changepoint_prob: float = 0.2):
        """
        Build a single change point Bayesian model.
        
        Parameters:
        -----------
        target_series : str
            Which series to model ('prices' or 'returns')
        prior_changepoint_prob : float
            Prior probability of change point occurrence
        """
        print(f"🔧 Building single change point model for {target_series}...")
        
        # Select target data
        if target_series == 'returns' and self.log_returns is not None:
            y = self.log_returns.values
            dates = self.log_returns.index
        else:
            y = self.data.values
            dates = self.data.index
        
        n_obs = len(y)
        
        with pm.Model() as model:
            # Change point location (discrete uniform prior)
            tau = pm.DiscreteUniform('tau', lower=1, upper=n_obs-2)
            
            # Parameters before and after change point
            mu_1 = pm.Normal('mu_before', mu=np.mean(y), sigma=np.std(y))
            mu_2 = pm.Normal('mu_after', mu=np.mean(y), sigma=np.std(y))
            
            # Precision (inverse variance) parameters
            lambda_1 = pm.Gamma('lambda_before', alpha=1, beta=1)
            lambda_2 = pm.Gamma('lambda_after', alpha=1, beta=1)
            
            # Switch function to select parameters based on change point
            idx = np.arange(n_obs)
            mu = pt.switch(tau >= idx, mu_1, mu_2)
            lambda_param = pt.switch(tau >= idx, lambda_1, lambda_2)
            
            # Likelihood
            obs = pm.Normal('obs', mu=mu, tau=lambda_param, observed=y)
        
        self.model = model
        self.results['model_type'] = 'single_changepoint'
        self.results['target_series'] = target_series
        self.results['dates'] = dates
        
        print("✅ Single change point model built successfully")
        return model
    
    def build_multiple_changepoint_model(self, n_changepoints: int = 3, 
                                       target_series: str = 'returns'):
        """
        Build a multiple change point Bayesian model.
        
        Parameters:
        -----------
        n_changepoints : int
            Number of change points to detect
        target_series : str
            Which series to model ('prices' or 'returns')
        """
        print(f"🔧 Building multiple change point model ({n_changepoints} change points) for {target_series}...")
        
        # Select target data
        if target_series == 'returns' and self.log_returns is not None:
            y = self.log_returns.values
            dates = self.log_returns.index
        else:
            y = self.data.values
            dates = self.data.index
        
        n_obs = len(y)
        
        with pm.Model() as model:
            # Change point locations (sorted)
            tau_raw = pm.DiscreteUniform('tau_raw', lower=1, upper=n_obs-2, shape=n_changepoints)
            tau = pm.Deterministic('tau', pt.sort(tau_raw))
            
            # Parameters for each regime (n_changepoints + 1 regimes)
            mu = pm.Normal('mu', mu=np.mean(y), sigma=np.std(y), shape=n_changepoints + 1)
            lambda_param = pm.Gamma('lambda', alpha=1, beta=1, shape=n_changepoints + 1)
            
            # Assign regime to each observation
            idx = np.arange(n_obs)
            regime = pt.sum([tau[i] < idx for i in range(n_changepoints)], axis=0)
            
            # Select parameters based on regime
            mu_selected = mu[regime]
            lambda_selected = lambda_param[regime]
            
            # Likelihood
            obs = pm.Normal('obs', mu=mu_selected, tau=lambda_selected, observed=y)
        
        self.model = model
        self.results['model_type'] = 'multiple_changepoint'
        self.results['n_changepoints'] = n_changepoints
        self.results['target_series'] = target_series
        self.results['dates'] = dates
        
        print(f"✅ Multiple change point model ({n_changepoints} change points) built successfully")
        return model
    
    def fit_model(self, draws: int = 2000, tune: int = 1000, chains: int = 4, 
                  target_accept: float = 0.95):
        """
        Fit the Bayesian model using MCMC sampling.
        
        Parameters:
        -----------
        draws : int
            Number of samples to draw
        tune : int
            Number of tuning samples
        chains : int
            Number of MCMC chains
        target_accept : float
            Target acceptance rate
        """
        if self.model is None:
            raise ValueError("Model must be built before fitting. Call build_*_model() first.")
        
        print(f"🔥 Fitting model with {draws} draws, {tune} tune, {chains} chains...")
        
        with self.model:
            # Sample from posterior
            self.trace = pm.sample(
                draws=draws,
                tune=tune,
                chains=chains,
                target_accept=target_accept,
                return_inferencedata=True,
                random_seed=42
            )
        
        print("✅ Model fitting completed")
        self._extract_results()
    
    def _extract_results(self):
        """Extract and summarize model results."""
        if self.trace is None:
            return
        
        # Model diagnostics
        summary = az.summary(self.trace)
        self.results['summary'] = summary
        self.results['diagnostics'] = {
            'r_hat_max': summary['r_hat'].max(),
            'ess_bulk_min': summary['ess_bulk'].min(),
            'ess_tail_min': summary['ess_tail'].min(),
            'converged': (summary['r_hat'] < 1.1).all()
        }
        
        # Extract change points
        if self.results['model_type'] == 'single_changepoint':
            tau_samples = self.trace.posterior['tau'].values.flatten()
            self.change_points = [{
                'tau_mean': np.mean(tau_samples),
                'tau_median': np.median(tau_samples),
                'tau_std': np.std(tau_samples),
                'tau_hdi': az.hdi(self.trace, var_names=['tau'])['tau'].values,
                'date_estimate': self.results['dates'][int(np.median(tau_samples))]
            }]
        else:
            tau_samples = self.trace.posterior['tau'].values
            n_cp = self.results['n_changepoints']
            self.change_points = []
            
            for i in range(n_cp):
                tau_i = tau_samples[:, :, i].flatten()
                self.change_points.append({
                    'tau_mean': np.mean(tau_i),
                    'tau_median': np.median(tau_i),
                    'tau_std': np.std(tau_i),
                    'tau_hdi': az.hdi(self.trace, var_names=['tau'])['tau'].values[i],
                    'date_estimate': self.results['dates'][int(np.median(tau_i))]
                })
        
        print(f"✅ Extracted {len(self.change_points)} change points")
    
    def plot_diagnostics(self):
        """Plot model diagnostics."""
        if self.trace is None:
            print("❌ No trace available. Fit model first.")
            return
        
        print("📊 Plotting model diagnostics...")
        
        # Trace plots
        az.plot_trace(self.trace, var_names=['tau'], compact=True)
        plt.suptitle('MCMC Trace Plots', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()
        
        # Summary plot
        az.plot_forest(self.trace, var_names=['mu', 'lambda'], combined=True)
        plt.suptitle('Parameter Posterior Distributions', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()
        
        # Print diagnostics
        print("\n🔍 Model Diagnostics:")
        print(f"Max R-hat: {self.results['diagnostics']['r_hat_max']:.4f}")
        print(f"Min ESS Bulk: {self.results['diagnostics']['ess_bulk_min']:.0f}")
        print(f"Min ESS Tail: {self.results['diagnostics']['ess_tail_min']:.0f}")
        print(f"Converged: {self.results['diagnostics']['converged']}")
    
    def plot_changepoints(self, figsize: Tuple[int, int] = (15, 8)):
        """Plot detected change points on the time series."""
        if self.change_points is None:
            print("❌ No change points detected. Fit model first.")
            return
        
        fig, axes = plt.subplots(2, 1, figsize=figsize, sharex=True)
        
        # Plot original price series
        axes[0].plot(self.data.index, self.data.values, linewidth=1, alpha=0.8, label='Brent Oil Price')
        axes[0].set_ylabel('Price (USD)')
        axes[0].set_title('Detected Change Points in Brent Oil Prices')
        axes[0].grid(True, alpha=0.3)
        
        # Plot change points
        for i, cp in enumerate(self.change_points):
            date_est = cp['date_estimate']
            axes[0].axvline(date_est, color='red', linestyle='--', alpha=0.8, 
                          label=f'Change Point {i+1}' if i == 0 else "")
        
        # Add major events if available
        if self.events_data is not None:
            for _, event in self.events_data.iterrows():
                event_date = pd.to_datetime(event['Date'])
                if event_date >= self.data.index.min() and event_date <= self.data.index.max():
                    axes[0].axvline(event_date, color='orange', alpha=0.4, linestyle=':', linewidth=2)
        
        axes[0].legend()
        
        # Plot log returns if available
        if self.log_returns is not None:
            axes[1].plot(self.log_returns.index, self.log_returns.values, linewidth=0.8, alpha=0.7)
            axes[1].set_ylabel('Log Returns')
            axes[1].set_xlabel('Date')
            axes[1].grid(True, alpha=0.3)
            
            # Plot change points on returns
            for cp in self.change_points:
                date_est = cp['date_estimate']
                axes[1].axvline(date_est, color='red', linestyle='--', alpha=0.8)
        
        plt.tight_layout()
        plt.show()
    
    def associate_with_events(self, tolerance_days: int = 60) -> pd.DataFrame:
        """
        Associate detected change points with major events.
        
        Parameters:
        -----------
        tolerance_days : int
            Number of days around change point to look for events
        
        Returns:
        --------
        pd.DataFrame
            Association results
        """
        if self.change_points is None or self.events_data is None:
            print("❌ Change points or events data not available.")
            return pd.DataFrame()
        
        print(f"🔗 Associating change points with events (±{tolerance_days} days tolerance)...")
        
        associations = []
        
        for i, cp in enumerate(self.change_points):
            cp_date = cp['date_estimate']
            tolerance = timedelta(days=tolerance_days)
            
            # Find events within tolerance window
            nearby_events = []
            for _, event in self.events_data.iterrows():
                event_date = pd.to_datetime(event['Date'])
                days_diff = abs((event_date - cp_date).days)
                
                if days_diff <= tolerance_days:
                    nearby_events.append({
                        'event_name': event['Name'],
                        'event_date': event_date,
                        'days_difference': (event_date - cp_date).days,
                        'category': event['Category'],
                        'expected_impact': event['Expected_Impact']
                    })
            
            # Sort by proximity
            nearby_events.sort(key=lambda x: abs(x['days_difference']))
            
            associations.append({
                'changepoint_id': i + 1,
                'changepoint_date': cp_date,
                'tau_median': cp['tau_median'],
                'tau_std': cp['tau_std'],
                'associated_events': nearby_events[:3],  # Top 3 closest events
                'n_nearby_events': len(nearby_events)
            })
        
        self.results['event_associations'] = associations
        
        # Create summary DataFrame
        summary_data = []
        for assoc in associations:
            if assoc['associated_events']:
                closest_event = assoc['associated_events'][0]
                summary_data.append({
                    'Change Point': assoc['changepoint_id'],
                    'CP Date': assoc['changepoint_date'].strftime('%Y-%m-%d'),
                    'Closest Event': closest_event['event_name'],
                    'Event Date': closest_event['event_date'].strftime('%Y-%m-%d'),
                    'Days Difference': closest_event['days_difference'],
                    'Event Category': closest_event['category'],
                    'Expected Impact': closest_event['expected_impact']
                })
            else:
                summary_data.append({
                    'Change Point': assoc['changepoint_id'],
                    'CP Date': assoc['changepoint_date'].strftime('%Y-%m-%d'),
                    'Closest Event': 'No nearby events',
                    'Event Date': '',
                    'Days Difference': '',
                    'Event Category': '',
                    'Expected Impact': ''
                })
        
        association_df = pd.DataFrame(summary_data)
        print(f"✅ Found associations for {len(association_df)} change points")
        
        return association_df
    
    def quantify_impact(self, window_days: int = 30) -> Dict:
        """
        Quantify the impact of detected change points.
        
        Parameters:
        -----------
        window_days : int
            Number of days before/after change point for impact calculation
        
        Returns:
        --------
        Dict
            Impact quantification results
        """
        if self.change_points is None:
            print("❌ No change points detected. Fit model first.")
            return {}
        
        print(f"📈 Quantifying impact with ±{window_days} days window...")
        
        impact_results = []
        
        for i, cp in enumerate(self.change_points):
            cp_date = cp['date_estimate']
            window = timedelta(days=window_days)
            
            # Define before/after periods
            before_start = cp_date - window
            before_end = cp_date
            after_start = cp_date
            after_end = cp_date + window
            
            # Extract price data for periods
            before_data = self.data[(self.data.index >= before_start) & (self.data.index < before_end)]
            after_data = self.data[(self.data.index > after_start) & (self.data.index <= after_end)]
            
            if len(before_data) > 0 and len(after_data) > 0:
                # Calculate impact metrics
                mean_before = before_data.mean()
                mean_after = after_data.mean()
                std_before = before_data.std()
                std_after = after_data.std()
                
                price_change = mean_after - mean_before
                percent_change = (price_change / mean_before) * 100
                volatility_change = std_after - std_before
                
                impact_results.append({
                    'changepoint_id': i + 1,
                    'changepoint_date': cp_date,
                    'mean_price_before': mean_before,
                    'mean_price_after': mean_after,
                    'price_change': price_change,
                    'percent_change': percent_change,
                    'std_before': std_before,
                    'std_after': std_after,
                    'volatility_change': volatility_change,
                    'n_obs_before': len(before_data),
                    'n_obs_after': len(after_data)
                })
        
        self.results['impact_analysis'] = impact_results
        
        print(f"✅ Quantified impact for {len(impact_results)} change points")
        return impact_results
    
    def generate_insights_report(self) -> str:
        """Generate a comprehensive insights report."""
        if not self.results:
            return "❌ No results available. Run analysis first."
        
        report = []
        report.append("# Brent Oil Price Change Point Analysis - Insights Report")
        report.append("=" * 60)
        report.append("")
        
        # Data summary
        if 'data_summary' in self.results:
            ds = self.results['data_summary']
            report.append("## Data Summary")
            report.append(f"• Analysis Period: {ds['start_date'].strftime('%Y-%m-%d')} to {ds['end_date'].strftime('%Y-%m-%d')}")
            report.append(f"• Total Observations: {ds['n_observations']:,}")
            report.append(f"• Price Range: ${ds['price_range'][0]:.2f} - ${ds['price_range'][1]:.2f}")
            report.append(f"• Average Price: ${ds['mean_price']:.2f} ± ${ds['std_price']:.2f}")
            report.append("")
        
        # Model diagnostics
        if 'diagnostics' in self.results:
            diag = self.results['diagnostics']
            report.append("## Model Diagnostics")
            report.append(f"• Model Convergence: {'✅ Converged' if diag['converged'] else '❌ Not Converged'}")
            report.append(f"• Max R-hat: {diag['r_hat_max']:.4f}")
            report.append(f"• Min ESS Bulk: {diag['ess_bulk_min']:.0f}")
            report.append("")
        
        # Change points summary
        if self.change_points:
            report.append("## Detected Change Points")
            for i, cp in enumerate(self.change_points):
                report.append(f"### Change Point {i+1}")
                report.append(f"• Date: {cp['date_estimate'].strftime('%Y-%m-%d')}")
                report.append(f"• Uncertainty: ±{cp['tau_std']:.1f} days")
                report.append("")
        
        # Event associations
        if 'event_associations' in self.results:
            report.append("## Event Associations")
            for assoc in self.results['event_associations']:
                if assoc['associated_events']:
                    closest = assoc['associated_events'][0]
                    report.append(f"### Change Point {assoc['changepoint_id']}")
                    report.append(f"• Closest Event: {closest['event_name']}")
                    report.append(f"• Time Difference: {closest['days_difference']} days")
                    report.append(f"• Event Category: {closest['category']}")
                    report.append("")
        
        # Impact analysis
        if 'impact_analysis' in self.results:
            report.append("## Impact Quantification")
            for impact in self.results['impact_analysis']:
                report.append(f"### Change Point {impact['changepoint_id']}")
                report.append(f"• Price Change: ${impact['price_change']:.2f} ({impact['percent_change']:.1f}%)")
                report.append(f"• Before: ${impact['mean_price_before']:.2f} ± ${impact['std_before']:.2f}")
                report.append(f"• After: ${impact['mean_price_after']:.2f} ± ${impact['std_after']:.2f}")
                report.append(f"• Volatility Change: {impact['volatility_change']:.2f}")
                report.append("")
        
        return "\n".join(report)
