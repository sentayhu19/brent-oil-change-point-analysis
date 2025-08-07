import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import Skeleton from 'react-loading-skeleton';

import { apiService, handleApiError } from '../services/api';
import ImpactAnalysisChart from '../components/ImpactAnalysisChart';
import ModelDiagnostics from '../components/ModelDiagnostics';

const AnalysisDetails = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [impactAnalysis, setImpactAnalysis] = useState([]);
  const [modelDiagnostics, setModelDiagnostics] = useState(null);
  const [changePoints, setChangePoints] = useState([]);
  const [eventAssociations, setEventAssociations] = useState([]);

  useEffect(() => {
    loadAnalysisData();
  }, []);

  const loadAnalysisData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [
        impactResponse,
        diagnosticsResponse,
        changePointsResponse,
        associationsResponse
      ] = await Promise.all([
        apiService.getImpactAnalysis(),
        apiService.getModelDiagnostics(),
        apiService.getChangePoints(),
        apiService.getEventAssociations()
      ]);

      setImpactAnalysis(impactResponse);
      setModelDiagnostics(diagnosticsResponse);
      setChangePoints(changePointsResponse);
      setEventAssociations(associationsResponse);

      toast.success('Analysis details loaded successfully!');
    } catch (err) {
      const errorInfo = handleApiError(err);
      setError(errorInfo.error);
      toast.error(`Failed to load analysis details: ${errorInfo.error}`);
    } finally {
      setLoading(false);
    }
  };

  if (error) {
    return (
      <div className="container" style={{ padding: '40px 20px' }}>
        <div className="error">
          <h3>Error Loading Analysis Details</h3>
          <p>{error}</p>
          <button 
            className="btn btn-primary" 
            onClick={loadAnalysisData}
            style={{ marginTop: '16px' }}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '20px' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h1>Analysis Details</h1>
        <p style={{ color: '#718096', fontSize: '1.1rem' }}>
          In-depth analysis of change point detection results and model performance
        </p>
      </div>

      {/* Impact Analysis Section */}
      <div className="card" style={{ marginBottom: '32px' }}>
        <div className="card-header">
          <h2>Change Point Impact Analysis</h2>
          <p style={{ color: '#718096', margin: 0 }}>
            Quantified impact of each change point on price levels and volatility
          </p>
        </div>
        {loading ? (
          <Skeleton height={400} />
        ) : (
          <ImpactAnalysisChart 
            impactAnalysis={impactAnalysis}
            changePoints={changePoints}
          />
        )}
      </div>

      {/* Detailed Impact Table */}
      <div className="card" style={{ marginBottom: '32px' }}>
        <div className="card-header">
          <h3>Impact Summary Table</h3>
        </div>
        {loading ? (
          <div>
            {[1, 2, 3, 4].map(i => (
              <div key={i} style={{ marginBottom: '16px' }}>
                <Skeleton height={60} />
              </div>
            ))}
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#f8fafc', borderBottom: '2px solid #e2e8f0' }}>
                  <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Change Point</th>
                  <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Date</th>
                  <th style={{ padding: '12px', textAlign: 'right', fontWeight: '600' }}>Price Impact</th>
                  <th style={{ padding: '12px', textAlign: 'right', fontWeight: '600' }}>Volatility Impact</th>
                  <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Associated Events</th>
                </tr>
              </thead>
              <tbody>
                {impactAnalysis.map((impact, index) => {
                  const associations = eventAssociations.find(
                    assoc => assoc.changepoint_id === impact.changepoint_id
                  );
                  
                  return (
                    <tr key={index} style={{ borderBottom: '1px solid #e2e8f0' }}>
                      <td style={{ padding: '12px', fontWeight: '500' }}>
                        CP #{impact.changepoint_id + 1}
                      </td>
                      <td style={{ padding: '12px' }}>
                        {new Date(impact.changepoint_date).toLocaleDateString()}
                      </td>
                      <td style={{ 
                        padding: '12px', 
                        textAlign: 'right',
                        color: impact.price_impact.change_percent >= 0 ? '#22c55e' : '#ef4444'
                      }}>
                        {impact.price_impact.change_percent >= 0 ? '+' : ''}
                        {impact.price_impact.change_percent.toFixed(1)}%
                        <br />
                        <small style={{ color: '#718096' }}>
                          ${impact.price_impact.before_mean.toFixed(2)} → ${impact.price_impact.after_mean.toFixed(2)}
                        </small>
                      </td>
                      <td style={{ 
                        padding: '12px', 
                        textAlign: 'right',
                        color: impact.volatility_impact.change_percent >= 0 ? '#ef4444' : '#22c55e'
                      }}>
                        {impact.volatility_impact.change_percent >= 0 ? '+' : ''}
                        {impact.volatility_impact.change_percent.toFixed(1)}%
                        <br />
                        <small style={{ color: '#718096' }}>
                          σ: {impact.volatility_impact.before_std.toFixed(3)} → {impact.volatility_impact.after_std.toFixed(3)}
                        </small>
                      </td>
                      <td style={{ padding: '12px' }}>
                        {associations && associations.associated_events.length > 0 ? (
                          <div>
                            {associations.associated_events.slice(0, 2).map((event, eventIndex) => (
                              <div key={eventIndex} style={{ fontSize: '12px', marginBottom: '2px' }}>
                                {event.event_name}
                              </div>
                            ))}
                            {associations.associated_events.length > 2 && (
                              <small style={{ color: '#718096' }}>
                                +{associations.associated_events.length - 2} more
                              </small>
                            )}
                          </div>
                        ) : (
                          <span style={{ color: '#9ca3af', fontSize: '12px', fontStyle: 'italic' }}>
                            No associations
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Model Diagnostics */}
      <div className="card">
        <div className="card-header">
          <h3>Model Diagnostics & Performance</h3>
          <p style={{ color: '#718096', margin: 0 }}>
            Bayesian model convergence and performance metrics
          </p>
        </div>
        {loading ? (
          <div>
            <Skeleton height={200} style={{ marginBottom: '16px' }} />
            <Skeleton height={100} />
          </div>
        ) : (
          <ModelDiagnostics diagnostics={modelDiagnostics} />
        )}
      </div>
    </div>
  );
};

export default AnalysisDetails;
