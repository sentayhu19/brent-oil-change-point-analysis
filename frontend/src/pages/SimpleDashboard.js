import React, { useState, useEffect } from 'react';
import axios from 'axios';

const SimpleDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState({
    historical: null,
    changePoints: [],
    events: [],
    summary: null
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Test backend connection first
      const healthResponse = await axios.get('http://localhost:5000/api/health');
      console.log('Backend health:', healthResponse.data);

      // Load basic data
      const [historicalResponse, eventsResponse, summaryResponse] = await Promise.all([
        axios.get('http://localhost:5000/api/historical-data'),
        axios.get('http://localhost:5000/api/events'),
        axios.get('http://localhost:5000/api/summary')
      ]);

      setData({
        historical: historicalResponse.data,
        events: eventsResponse.data,
        summary: summaryResponse.data,
        changePoints: [] // Will load on demand
      });

      console.log('Data loaded successfully');
    } catch (err) {
      console.error('Error loading data:', err);
      setError(err.response?.data?.error || err.message || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const loadChangePoints = async () => {
    try {
      console.log('Loading change points...');
      const response = await axios.get('http://localhost:5000/api/change-points');
      setData(prev => ({ ...prev, changePoints: response.data }));
      console.log('Change points loaded:', response.data);
    } catch (err) {
      console.error('Error loading change points:', err);
      alert('Error loading change points: ' + (err.response?.data?.error || err.message));
    }
  };

  if (error) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <h2 style={{ color: '#ef4444' }}>Error Loading Dashboard</h2>
        <p>{error}</p>
        <button 
          onClick={loadData}
          style={{
            padding: '10px 20px',
            backgroundColor: '#3182ce',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer'
          }}
        >
          Retry
        </button>
      </div>
    );
  }

  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <h2>Loading Dashboard...</h2>
        <p>Please wait while we load your Brent oil analysis data.</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px', textAlign: 'center' }}>
        <h1 style={{ color: '#2d3748', marginBottom: '8px' }}>
          🛢️ Brent Oil Change Point Analysis Dashboard
        </h1>
        <p style={{ color: '#718096', fontSize: '1.1rem' }}>
          Interactive visualization of Bayesian change point detection results
        </p>
      </div>

      {/* Summary Stats */}
      {data.summary && (
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
          gap: '16px',
          marginBottom: '32px'
        }}>
          <div style={{ 
            padding: '20px', 
            backgroundColor: 'white', 
            borderRadius: '8px', 
            border: '1px solid #e2e8f0',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2rem', fontWeight: '700', color: '#3182ce' }}>
              {data.summary.total_changepoints || 0}
            </div>
            <div style={{ fontSize: '0.875rem', color: '#718096' }}>
              Change Points Detected
            </div>
          </div>
          
          <div style={{ 
            padding: '20px', 
            backgroundColor: 'white', 
            borderRadius: '8px', 
            border: '1px solid #e2e8f0',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2rem', fontWeight: '700', color: '#0d9488' }}>
              {data.summary.total_events || 0}
            </div>
            <div style={{ fontSize: '0.875rem', color: '#718096' }}>
              Major Events
            </div>
          </div>
          
          <div style={{ 
            padding: '20px', 
            backgroundColor: 'white', 
            borderRadius: '8px', 
            border: '1px solid #e2e8f0',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2rem', fontWeight: '700', color: '#7c3aed' }}>
              {data.summary.associated_events || 0}
            </div>
            <div style={{ fontSize: '0.875rem', color: '#718096' }}>
              Event Associations
            </div>
          </div>
          
          <div style={{ 
            padding: '20px', 
            backgroundColor: 'white', 
            borderRadius: '8px', 
            border: '1px solid #e2e8f0',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2rem', fontWeight: '700', color: '#dc2626' }}>
              {data.summary.data_period?.total_days || 0}
            </div>
            <div style={{ fontSize: '0.875rem', color: '#718096' }}>
              Data Period (Days)
            </div>
          </div>
        </div>
      )}

      {/* Data Overview */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', 
        gap: '24px' 
      }}>
        {/* Historical Data Info */}
        <div style={{ 
          padding: '24px', 
          backgroundColor: 'white', 
          borderRadius: '12px', 
          border: '1px solid #e2e8f0' 
        }}>
          <h3 style={{ marginBottom: '16px', color: '#2d3748' }}>Historical Price Data</h3>
          {data.historical ? (
            <div>
              <p><strong>Total Records:</strong> {data.historical.total_records}</p>
              <p><strong>Date Range:</strong> {data.historical.date_range?.start} to {data.historical.date_range?.end}</p>
              <p><strong>Latest Price:</strong> ${data.historical.prices?.[data.historical.prices.length - 1]?.toFixed(2)}</p>
              
              {/* Simple price chart placeholder */}
              <div style={{ 
                marginTop: '16px', 
                padding: '20px', 
                backgroundColor: '#f8fafc', 
                borderRadius: '6px',
                textAlign: 'center'
              }}>
                📈 Price Chart
                <br />
                <small style={{ color: '#718096' }}>
                  {data.historical.prices?.length} price points loaded
                </small>
              </div>
            </div>
          ) : (
            <p>No historical data available</p>
          )}
        </div>

        {/* Events Data */}
        <div style={{ 
          padding: '24px', 
          backgroundColor: 'white', 
          borderRadius: '12px', 
          border: '1px solid #e2e8f0' 
        }}>
          <h3 style={{ marginBottom: '16px', color: '#2d3748' }}>Major Events</h3>
          {data.events && data.events.length > 0 ? (
            <div>
              <p><strong>Total Events:</strong> {data.events.length}</p>
              <div style={{ maxHeight: '200px', overflowY: 'auto', marginTop: '12px' }}>
                {data.events.slice(0, 5).map((event, index) => (
                  <div key={index} style={{ 
                    padding: '8px', 
                    marginBottom: '8px', 
                    backgroundColor: '#f8fafc', 
                    borderRadius: '4px',
                    fontSize: '14px'
                  }}>
                    <strong>{event.event}</strong>
                    <br />
                    <small style={{ color: '#718096' }}>
                      {event.date} - {event.type}
                    </small>
                  </div>
                ))}
                {data.events.length > 5 && (
                  <p style={{ fontSize: '12px', color: '#718096', textAlign: 'center' }}>
                    ... and {data.events.length - 5} more events
                  </p>
                )}
              </div>
            </div>
          ) : (
            <p>No events data available</p>
          )}
        </div>
      </div>

      {/* Change Points Section */}
      <div style={{ 
        marginTop: '32px',
        padding: '24px', 
        backgroundColor: 'white', 
        borderRadius: '12px', 
        border: '1px solid #e2e8f0' 
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h3 style={{ margin: 0, color: '#2d3748' }}>Change Points Analysis</h3>
          <button
            onClick={loadChangePoints}
            style={{
              padding: '8px 16px',
              backgroundColor: '#3182ce',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer'
            }}
          >
            🔄 Run Analysis
          </button>
        </div>
        
        {data.changePoints.length > 0 ? (
          <div>
            <p><strong>Detected Change Points:</strong> {data.changePoints.length}</p>
            <div style={{ maxHeight: '300px', overflowY: 'auto', marginTop: '12px' }}>
              {data.changePoints.map((cp, index) => (
                <div key={index} style={{ 
                  padding: '12px', 
                  marginBottom: '8px', 
                  backgroundColor: '#fef5e7', 
                  borderRadius: '6px',
                  border: '1px solid #fbbf24'
                }}>
                  <strong>Change Point #{index + 1}</strong>
                  <br />
                  <span>Date: {cp.date}</span>
                  <br />
                  <span>Confidence: {(cp.probability * 100).toFixed(1)}%</span>
                  {cp.price_at_changepoint && (
                    <>
                      <br />
                      <span>Price: ${cp.price_at_changepoint.toFixed(2)}</span>
                    </>
                  )}
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div style={{ 
            padding: '20px', 
            backgroundColor: '#f8fafc', 
            borderRadius: '6px',
            textAlign: 'center'
          }}>
            <p style={{ color: '#718096' }}>
              Click "Run Analysis" to detect change points using Bayesian methods.
              <br />
              <small>This may take a few moments to complete.</small>
            </p>
          </div>
        )}
      </div>

      {/* Backend Status */}
      <div style={{ 
        marginTop: '32px', 
        padding: '16px', 
        backgroundColor: '#f0fff4', 
        border: '1px solid #9ae6b4',
        borderRadius: '8px',
        textAlign: 'center'
      }}>
        <span style={{ color: '#22543d', fontSize: '14px' }}>
          ✅ Backend API is connected and ready
        </span>
      </div>
    </div>
  );
};

export default SimpleDashboard;
