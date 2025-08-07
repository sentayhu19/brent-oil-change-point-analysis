"""
Bayesian Change Point Detection Model for Brent Oil Price Analysis.

This module implements a Bayesian change point detection model using PyMC
to identify structural breaks in Brent oil price time series data.
"""

import numpy as np
import pandas as pd
import pymc as pm
import arviz as az
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple, List, Dict, Optional
import warnings

class BayesianChangePointModel:
    """
    Bayesian Change Point Detection Model for time series analysis.
    
    This class implements a Bayesian approach to detect change points in 
    time series data, specifically designed for oil price analysis.
    """
    
    def __init__(self, data: pd.Series, max_changepoints: int = 5):
        """
        Initialize the change point model.
        
        Parameters:
        -----------
        data : pd.Series
            Time series data with datetime index
        max_changepoints : int
            Maximum number of change points to detect
        """
        self.data = data.dropna()
        self.max_changepoints = max_changepoints
        self.n_obs = len(self.data)
        self.model = None
        self.trace = None
        self.summary = None
        
        # Prepare data for modeling
        self.y = self.data.values
        self.t = np.arange(self.n_obs)
        self.dates = self.data.index
        
        print(f"📊 Initialized model with {self.n_obs} observations")
        print(f"📅 Date range: {self.dates.min()} to {self.dates.max()}")
        print(f"🔍 Max change points: {self.max_changepoints}")
    
    def build_model(self, 
                   prior_alpha: float = 1.0,
                   prior_beta: float = 1.0,
                   sigma_prior: float = 10.0) -> pm.Model:
        """
        Build the Bayesian change point model.
        
        Parameters:
        -----------
        prior_alpha : float
            Alpha parameter for Beta prior on change point probabilities
        prior_beta : float
            Beta parameter for Beta prior on change point probabilities
        sigma_prior : float
            Prior standard deviation for noise parameter
            
        Returns:
        --------
        pm.Model
            PyMC model object
        """
        
        with pm.Model() as model:
            # Prior for change point locations
            # Use Uniform prior over the time range
            tau = pm.DiscreteUniform(
                'tau', 
                lower=1, 
                upper=self.n_obs-2, 
                shape=self.max_changepoints
            )
            
            # Sort change points to ensure ordering
            tau_sorted = pm.math.sort(tau)
            
            # Prior for regime means
            # Use Normal priors centered around data mean
            data_mean = np.mean(self.y)
            data_std = np.std(self.y)
            
            mu = pm.Normal(
                'mu', 
                mu=data_mean, 
                sigma=data_std,
                shape=self.max_changepoints + 1
            )
            
            # Prior for noise parameter
            sigma = pm.HalfNormal('sigma', sigma=sigma_prior)
            
            # Create regime indicators
            # This determines which regime each observation belongs to
            regime = pm.math.zeros(self.n_obs, dtype='int32')
            
            for i in range(self.max_changepoints):
                regime = pm.math.switch(
                    self.t >= tau_sorted[i],
                    i + 1,
                    regime
                )
            
            # Expected value for each observation
            mu_t = mu[regime]
            
            # Likelihood
            likelihood = pm.Normal(
                'likelihood',
                mu=mu_t,
                sigma=sigma,
                observed=self.y
            )
            
        self.model = model
        return model
    
    def fit_model(self, 
                  draws: int = 2000,
                  tune: int = 1000,
                  chains: int = 4,
                  target_accept: float = 0.9,
                  random_seed: int = 42) -> az.InferenceData:
        """
        Fit the Bayesian change point model using MCMC sampling.
        
        Parameters:
        -----------
        draws : int
            Number of MCMC samples to draw
        tune : int
            Number of tuning steps
        chains : int
            Number of MCMC chains
        target_accept : float
            Target acceptance rate for NUTS sampler
        random_seed : int
            Random seed for reproducibility
            
        Returns:
        --------
        az.InferenceData
            ArviZ inference data object containing samples
        """
        
        if self.model is None:
            raise ValueError("Model not built. Call build_model() first.")
        
        print("🔄 Starting MCMC sampling...")
        print(f"   Draws: {draws}, Tune: {tune}, Chains: {chains}")
        
        with self.model:
            # Use NUTS sampler with specified parameters
            self.trace = pm.sample(
                draws=draws,
                tune=tune,
                chains=chains,
                target_accept=target_accept,
                random_seed=random_seed,
                return_inferencedata=True,
                progressbar=True
            )
        
        print("✅ MCMC sampling completed!")
        
        # Generate summary statistics
        self.summary = az.summary(self.trace)
        
        return self.trace
    
    def get_change_points(self, credible_interval: float = 0.95) -> pd.DataFrame:
        """
        Extract change point estimates with credible intervals.
        
        Parameters:
        -----------
        credible_interval : float
            Credible interval level (e.g., 0.95 for 95% CI)
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with change point estimates and intervals
        """
        
        if self.trace is None:
            raise ValueError("Model not fitted. Call fit_model() first.")
        
        # Extract tau samples
        tau_samples = self.trace.posterior['tau'].values
        
        # Reshape to combine chains
        tau_flat = tau_samples.reshape(-1, self.max_changepoints)
        
        # Calculate statistics for each change point
        results = []
        alpha = 1 - credible_interval
        
        for i in range(self.max_changepoints):
            tau_i = tau_flat[:, i]
            
            # Convert to dates
            tau_dates = [self.dates[int(t)] for t in tau_i]
            
            result = {
                'changepoint_id': i + 1,
                'mean_position': np.mean(tau_i),
                'mean_date': self.dates[int(np.mean(tau_i))],
                'median_position': np.median(tau_i),
                'median_date': self.dates[int(np.median(tau_i))],
                'ci_lower': np.percentile(tau_i, 100 * alpha/2),
                'ci_upper': np.percentile(tau_i, 100 * (1 - alpha/2)),
                'ci_lower_date': self.dates[int(np.percentile(tau_i, 100 * alpha/2))],
                'ci_upper_date': self.dates[int(np.percentile(tau_i, 100 * (1 - alpha/2)))],
                'std': np.std(tau_i)
            }
            
            results.append(result)
        
        return pd.DataFrame(results)
    
    def get_regime_parameters(self, credible_interval: float = 0.95) -> pd.DataFrame:
        """
        Extract regime parameter estimates.
        
        Parameters:
        -----------
        credible_interval : float
            Credible interval level
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with regime parameter estimates
        """
        
        if self.trace is None:
            raise ValueError("Model not fitted. Call fit_model() first.")
        
        # Extract mu samples
        mu_samples = self.trace.posterior['mu'].values
        mu_flat = mu_samples.reshape(-1, self.max_changepoints + 1)
        
        # Extract sigma samples
        sigma_samples = self.trace.posterior['sigma'].values.flatten()
        
        results = []
        alpha = 1 - credible_interval
        
        for i in range(self.max_changepoints + 1):
            mu_i = mu_flat[:, i]
            
            result = {
                'regime_id': i + 1,
                'mean_mu': np.mean(mu_i),
                'median_mu': np.median(mu_i),
                'ci_lower_mu': np.percentile(mu_i, 100 * alpha/2),
                'ci_upper_mu': np.percentile(mu_i, 100 * (1 - alpha/2)),
                'std_mu': np.std(mu_i)
            }
            
            results.append(result)
        
        # Add sigma statistics
        sigma_stats = {
            'mean_sigma': np.mean(sigma_samples),
            'median_sigma': np.median(sigma_samples),
            'ci_lower_sigma': np.percentile(sigma_samples, 100 * alpha/2),
            'ci_upper_sigma': np.percentile(sigma_samples, 100 * (1 - alpha/2)),
            'std_sigma': np.std(sigma_samples)
        }
        
        df = pd.DataFrame(results)
        
        # Add sigma as a separate row or return as tuple
        return df, sigma_stats
    
    def plot_diagnostics(self, figsize: Tuple[int, int] = (15, 10)) -> None:
        """
        Plot MCMC diagnostics.
        
        Parameters:
        -----------
        figsize : tuple
            Figure size for plots
        """
        
        if self.trace is None:
            raise ValueError("Model not fitted. Call fit_model() first.")
        
        # Plot trace plots
        az.plot_trace(self.trace, figsize=figsize)
        plt.suptitle('MCMC Trace Plots', fontsize=16)
        plt.tight_layout()
        plt.show()
        
        # Plot posterior distributions
        az.plot_posterior(self.trace, figsize=figsize)
        plt.suptitle('Posterior Distributions', fontsize=16)
        plt.tight_layout()
        plt.show()
        
        # Print summary statistics
        print("\n📊 MODEL SUMMARY")
        print("=" * 60)
        print(self.summary)
        
        # Print diagnostics
        print("\n🔍 MCMC DIAGNOSTICS")
        print("=" * 60)
        
        # R-hat statistics
        rhat_max = self.summary['r_hat'].max()
        print(f"Max R-hat: {rhat_max:.4f}")
        
        if rhat_max < 1.01:
            print("✅ Excellent convergence (R-hat < 1.01)")
        elif rhat_max < 1.05:
            print("⚠️ Good convergence (R-hat < 1.05)")
        else:
            print("❌ Poor convergence (R-hat >= 1.05) - consider more samples")
        
        # Effective sample size
        ess_min = self.summary['ess_bulk'].min()
        print(f"Min ESS: {ess_min:.0f}")
        
        if ess_min > 400:
            print("✅ Good effective sample size")
        else:
            print("⚠️ Low effective sample size - consider more samples")
    
    def plot_change_points(self, 
                          events_df: Optional[pd.DataFrame] = None,
                          figsize: Tuple[int, int] = (15, 8)) -> None:
        """
        Plot detected change points with the original time series.
        
        Parameters:
        -----------
        events_df : pd.DataFrame, optional
            DataFrame with major events for comparison
        figsize : tuple
            Figure size for plot
        """
        
        if self.trace is None:
            raise ValueError("Model not fitted. Call fit_model() first.")
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot original time series
        ax.plot(self.dates, self.y, 'b-', alpha=0.7, linewidth=1, label='Brent Oil Price')
        
        # Get change point estimates
        changepoints_df = self.get_change_points()
        
        # Plot change points
        for _, cp in changepoints_df.iterrows():
            ax.axvline(
                cp['mean_date'], 
                color='red', 
                linestyle='--', 
                alpha=0.8,
                label=f'Change Point {cp["changepoint_id"]}' if cp['changepoint_id'] == 1 else ""
            )
            
            # Add confidence interval
            ax.axvspan(
                cp['ci_lower_date'],
                cp['ci_upper_date'],
                alpha=0.2,
                color='red'
            )
        
        # Plot major events if provided
        if events_df is not None:
            for _, event in events_df.iterrows():
                if event['date'] >= self.dates.min() and event['date'] <= self.dates.max():
                    ax.axvline(
                        event['date'],
                        color='green',
                        linestyle=':',
                        alpha=0.6,
                        label='Major Events' if _ == 0 else ""
                    )
        
        ax.set_xlabel('Date')
        ax.set_ylabel('Price (USD)')
        ax.set_title('Brent Oil Prices with Detected Change Points')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        # Print change point summary
        print("\n📍 DETECTED CHANGE POINTS")
        print("=" * 60)
        for _, cp in changepoints_df.iterrows():
            print(f"Change Point {cp['changepoint_id']}: {cp['mean_date'].strftime('%Y-%m-%d')}")
            print(f"  95% CI: {cp['ci_lower_date'].strftime('%Y-%m-%d')} to {cp['ci_upper_date'].strftime('%Y-%m-%d')}")
            print()

def compare_models(models: List[BayesianChangePointModel], 
                  model_names: List[str]) -> pd.DataFrame:
    """
    Compare multiple change point models using information criteria.
    
    Parameters:
    -----------
    models : list
        List of fitted BayesianChangePointModel objects
    model_names : list
        Names for each model
        
    Returns:
    --------
    pd.DataFrame
        Model comparison results
    """
    
    results = []
    
    for model, name in zip(models, model_names):
        if model.trace is None:
            raise ValueError(f"Model {name} not fitted.")
        
        # Calculate information criteria
        waic = az.waic(model.trace)
        loo = az.loo(model.trace)
        
        result = {
            'model': name,
            'waic': waic.waic,
            'waic_se': waic.se,
            'loo': loo.loo,
            'loo_se': loo.se,
            'p_waic': waic.p_waic,
            'p_loo': loo.p_loo
        }
        
        results.append(result)
    
    df = pd.DataFrame(results)
    df = df.sort_values('waic')  # Lower is better
    
    return df
