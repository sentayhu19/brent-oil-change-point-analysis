import React from 'react';

const ModelDiagnostics = ({ diagnostics }) => {
  if (!diagnostics) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#718096' }}>
        <p>No model diagnostics available</p>
      </div>
    );
  }

  // Helper function to get status color and icon
  const getStatusInfo = (value, threshold, higherIsBetter = false) => {
    const isGood = higherIsBetter ? value >= threshold : value <= threshold;
    return {
      color: isGood ? '#22c55e' : '#ef4444',
      icon: isGood ? '✅' : '⚠️',
      status: isGood ? 'Good' : 'Warning'
    };
  };

  // Extract key metrics
  const rhat = diagnostics.r_hat_max || diagnostics.rhat_max || diagnostics.r_hat || null;
  const essMin = diagnostics.ess_min || diagnostics.ess_bulk_min || null;
  const mcseMax = diagnostics.mcse_max || null;
  const divergences = diagnostics.divergences || diagnostics.n_divergent || 0;
  const energyBfmi = diagnostics.energy_bfmi || diagnostics.bfmi || null;

  // Diagnostic cards data
  const diagnosticCards = [
    {
      title: 'R-hat (Convergence)',
      value: rhat ? rhat.toFixed(4) : 'N/A',
      description: 'Should be < 1.1 for convergence',
      status: rhat ? getStatusInfo(rhat, 1.1, false) : null,
      details: 'R-hat measures convergence of MCMC chains. Values close to 1.0 indicate good convergence.'
    },
    {
      title: 'Effective Sample Size',
      value: essMin ? Math.round(essMin) : 'N/A',
      description: 'Should be > 400 for reliable inference',
      status: essMin ? getStatusInfo(essMin, 400, true) : null,
      details: 'ESS measures the effective number of independent samples from the posterior.'
    },
    {
      title: 'MCSE (Monte Carlo SE)',
      value: mcseMax ? mcseMax.toFixed(6) : 'N/A',
      description: 'Should be small relative to posterior SD',
      status: mcseMax ? getStatusInfo(mcseMax, 0.01, false) : null,
      details: 'Monte Carlo Standard Error measures uncertainty due to finite sampling.'
    },
    {
      title: 'Divergent Transitions',
      value: divergences,
      description: 'Should be 0 for optimal sampling',
      status: getStatusInfo(divergences, 0, false),
      details: 'Divergent transitions indicate problems with the sampling process.'
    }
  ];

  // Add energy BFMI if available
  if (energyBfmi !== null) {
    diagnosticCards.push({
      title: 'Energy BFMI',
      value: energyBfmi.toFixed(3),
      description: 'Should be > 0.2 for good sampling',
      status: getStatusInfo(energyBfmi, 0.2, true),
      details: 'Bayesian Fraction of Missing Information from energy diagnostic.'
    });
  }

  // Overall model status
  const getOverallStatus = () => {
    const issues = diagnosticCards.filter(card => 
      card.status && card.status.status === 'Warning'
    ).length;
    
    if (issues === 0) {
      return { color: '#22c55e', icon: '✅', text: 'Model converged successfully' };
    } else if (issues <= 2) {
      return { color: '#f59e0b', icon: '⚠️', text: `${issues} diagnostic warning(s)` };
    } else {
      return { color: '#ef4444', icon: '❌', text: `${issues} diagnostic issues detected` };
    }
  };

  const overallStatus = getOverallStatus();

  return (
    <div>
      {/* Overall Status */}
      <div style={{
        padding: '16px',
        marginBottom: '24px',
        backgroundColor: overallStatus.color + '10',
        border: `1px solid ${overallStatus.color}40`,
        borderRadius: '8px',
        display: 'flex',
        alignItems: 'center',
        gap: '12px'
      }}>
        <span style={{ fontSize: '1.5rem' }}>{overallStatus.icon}</span>
        <div>
          <h4 style={{ margin: 0, color: overallStatus.color }}>
            Model Diagnostics Status
          </h4>
          <p style={{ margin: '4px 0 0 0', color: overallStatus.color, fontSize: '14px' }}>
            {overallStatus.text}
          </p>
        </div>
      </div>

      {/* Diagnostic Cards */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', 
        gap: '16px',
        marginBottom: '24px'
      }}>
        {diagnosticCards.map((card, index) => (
          <div
            key={index}
            style={{
              padding: '16px',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              backgroundColor: 'white'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <h5 style={{ margin: 0, fontSize: '14px', fontWeight: '600' }}>
                {card.title}
              </h5>
              {card.status && (
                <span style={{ fontSize: '1.2rem' }}>{card.status.icon}</span>
              )}
            </div>
            
            <div style={{ marginBottom: '8px' }}>
              <span style={{ 
                fontSize: '1.5rem', 
                fontWeight: '700',
                color: card.status ? card.status.color : '#4a5568'
              }}>
                {card.value}
              </span>
            </div>
            
            <p style={{ 
              margin: '0 0 8px 0', 
              fontSize: '12px', 
              color: '#718096',
              fontWeight: '500'
            }}>
              {card.description}
            </p>
            
            <p style={{ 
              margin: 0, 
              fontSize: '11px', 
              color: '#9ca3af',
              lineHeight: '1.4'
            }}>
              {card.details}
            </p>
          </div>
        ))}
      </div>

      {/* Additional Diagnostics */}
      {Object.keys(diagnostics).length > 5 && (
        <div style={{ 
          padding: '16px', 
          backgroundColor: '#f8fafc', 
          borderRadius: '8px',
          marginTop: '16px'
        }}>
          <h5 style={{ margin: '0 0 12px 0', fontSize: '14px', fontWeight: '600' }}>
            Additional Diagnostics
          </h5>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '12px',
            fontSize: '12px'
          }}>
            {Object.entries(diagnostics).map(([key, value]) => {
              // Skip already displayed metrics
              if (['r_hat_max', 'rhat_max', 'r_hat', 'ess_min', 'ess_bulk_min', 'mcse_max', 'divergences', 'n_divergent', 'energy_bfmi', 'bfmi'].includes(key)) {
                return null;
              }
              
              return (
                <div key={key} style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#4a5568', fontWeight: '500' }}>
                    {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                  </span>
                  <span style={{ color: '#718096' }}>
                    {typeof value === 'number' ? value.toFixed(4) : String(value)}
                  </span>
                </div>
              );
            }).filter(Boolean)}
          </div>
        </div>
      )}

      {/* Recommendations */}
      <div style={{ 
        marginTop: '24px', 
        padding: '16px', 
        backgroundColor: '#fffbeb', 
        border: '1px solid #fbbf24',
        borderRadius: '8px'
      }}>
        <h5 style={{ margin: '0 0 8px 0', fontSize: '14px', fontWeight: '600', color: '#92400e' }}>
          💡 Recommendations
        </h5>
        <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '12px', color: '#78350f' }}>
          {rhat && rhat > 1.1 && (
            <li>Consider increasing the number of sampling iterations or chains</li>
          )}
          {essMin && essMin < 400 && (
            <li>Increase sampling iterations to improve effective sample size</li>
          )}
          {divergences > 0 && (
            <li>Consider increasing target acceptance rate or reparameterizing the model</li>
          )}
          {energyBfmi && energyBfmi < 0.2 && (
            <li>Model may benefit from reparameterization to improve sampling efficiency</li>
          )}
          {diagnosticCards.every(card => !card.status || card.status.status === 'Good') && (
            <li>Model diagnostics look good! Results should be reliable for inference.</li>
          )}
        </ul>
      </div>
    </div>
  );
};

export default ModelDiagnostics;
