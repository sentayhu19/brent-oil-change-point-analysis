import React from 'react';
import { format, parseISO } from 'date-fns';

const SummaryStats = ({ summary, changePoints, events, historicalData }) => {
  if (!summary) {
    return (
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">-</div>
          <div className="stat-label">No data available</div>
        </div>
      </div>
    );
  }

  const stats = [
    {
      label: 'Change Points Detected',
      value: summary.total_changepoints || 0,
      icon: '🔄',
      color: '#d69e2e',
      description: 'Bayesian change points identified'
    },
    {
      label: 'Major Events',
      value: summary.total_events || 0,
      icon: '📅',
      color: '#0d9488',
      description: 'Geopolitical & economic events'
    },
    {
      label: 'Event Associations',
      value: summary.associated_events || 0,
      icon: '🔗',
      color: '#7c3aed',
      description: 'Events linked to change points'
    },
    {
      label: 'Data Period (Days)',
      value: summary.data_period?.total_days || 0,
      icon: '📊',
      color: '#3182ce',
      description: `${summary.data_period?.start || 'N/A'} to ${summary.data_period?.end || 'N/A'}`
    }
  ];

  // Additional derived stats
  const currentPrice = historicalData?.prices ? historicalData.prices[historicalData.prices.length - 1] : null;
  const priceChange = historicalData?.prices && historicalData.prices.length > 1 
    ? historicalData.prices[historicalData.prices.length - 1] - historicalData.prices[historicalData.prices.length - 2]
    : null;

  if (currentPrice) {
    stats.push({
      label: 'Latest Price',
      value: `$${currentPrice.toFixed(2)}`,
      icon: '💰',
      color: priceChange >= 0 ? '#22c55e' : '#ef4444',
      description: priceChange 
        ? `${priceChange >= 0 ? '+' : ''}${priceChange.toFixed(2)} from previous`
        : 'Current Brent oil price'
    });
  }

  // Model performance stats
  if (summary.model_performance && Object.keys(summary.model_performance).length > 0) {
    const rhat = summary.model_performance.r_hat_max || summary.model_performance.rhat_max;
    if (rhat) {
      stats.push({
        label: 'Model Convergence',
        value: rhat < 1.1 ? 'Good' : 'Warning',
        icon: rhat < 1.1 ? '✅' : '⚠️',
        color: rhat < 1.1 ? '#22c55e' : '#f59e0b',
        description: `R-hat: ${rhat.toFixed(3)} ${rhat < 1.1 ? '(converged)' : '(check convergence)'}`
      });
    }
  }

  return (
    <div className="stats-grid">
      {stats.map((stat, index) => (
        <div key={index} className="stat-card">
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            marginBottom: '8px'
          }}>
            <span style={{ fontSize: '1.5rem', marginRight: '8px' }}>{stat.icon}</span>
            <div 
              className="stat-value" 
              style={{ color: stat.color, fontSize: '1.8rem' }}
            >
              {stat.value}
            </div>
          </div>
          <div className="stat-label">{stat.label}</div>
          {stat.description && (
            <div style={{ 
              fontSize: '0.75rem', 
              color: '#9ca3af', 
              marginTop: '4px',
              textAlign: 'center'
            }}>
              {stat.description}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default SummaryStats;
