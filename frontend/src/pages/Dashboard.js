import React, { useState, useEffect } from 'react';

import { apiService, handleApiError } from '../services/api';
import PriceChart from '../components/PriceChart';
import SummaryStats from '../components/SummaryStats';
import ChangePointsList from '../components/ChangePointsList';
import EventsList from '../components/EventsList';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Data state
  const [historicalData, setHistoricalData] = useState(null);
  const [changePoints, setChangePoints] = useState([]);
  const [events, setEvents] = useState([]);
  const [summary, setSummary] = useState(null);
  const [eventAssociations, setEventAssociations] = useState([]);
  
  // Filter state
  const [dateRange, setDateRange] = useState({
    startDate: null,
    endDate: null
  });
  const [selectedEventTypes, setSelectedEventTypes] = useState([]);

  // Load initial data
  useEffect(() => {
    loadDashboardData();
  }, []);

  // Load data when filters change
  useEffect(() => {
    if (!loading) {
      loadFilteredData();
    }
  }, [dateRange, selectedEventTypes]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load all data in parallel
      const [
        historicalResponse,
        changePointsResponse,
        eventsResponse,
        summaryResponse,
        associationsResponse
      ] = await Promise.all([
        apiService.getHistoricalData(),
        apiService.getChangePoints(),
        apiService.getEvents(),
        apiService.getSummary(),
        apiService.getEventAssociations()
      ]);

      setHistoricalData(historicalResponse);
      setChangePoints(changePointsResponse);
      setEvents(eventsResponse);
      setSummary(summaryResponse);
      setEventAssociations(associationsResponse);

      toast.success('Dashboard data loaded successfully!');
    } catch (err) {
      const errorInfo = handleApiError(err);
      setError(errorInfo.error);
      toast.error(`Failed to load dashboard data: ${errorInfo.error}`);
    } finally {
      setLoading(false);
    }
  };

  const loadFilteredData = async () => {
    try {
      const startDate = dateRange.startDate?.toISOString().split('T')[0];
      const endDate = dateRange.endDate?.toISOString().split('T')[0];
      
      // Load filtered historical data and events
      const [historicalResponse, eventsResponse] = await Promise.all([
        apiService.getHistoricalData(startDate, endDate),
        apiService.getEvents(startDate, endDate, selectedEventTypes.join(','))
      ]);

      setHistoricalData(historicalResponse);
      setEvents(eventsResponse);
    } catch (err) {
      const errorInfo = handleApiError(err);
      toast.error(`Failed to load filtered data: ${errorInfo.error}`);
    }
  };

  const handleDateRangeChange = (startDate, endDate) => {
    setDateRange({ startDate, endDate });
  };

  const handleEventTypeFilter = (eventTypes) => {
    setSelectedEventTypes(eventTypes);
  };

  if (error) {
    return (
      <div className="container" style={{ padding: '40px 20px' }}>
        <div className="error">
          <h3>Error Loading Dashboard</h3>
          <p>{error}</p>
          <button 
            className="btn btn-primary" 
            onClick={loadDashboardData}
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
        <h1>Brent Oil Price Analysis Dashboard</h1>
        <p style={{ color: '#718096', fontSize: '1.1rem' }}>
          Interactive visualization of Bayesian change point detection results
        </p>
      </div>

      {/* Summary Stats */}
      <div style={{ marginBottom: '32px' }}>
        {loading ? (
          <div className="stats-grid">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="stat-card">
                <Skeleton height={40} style={{ marginBottom: '8px' }} />
                <Skeleton height={20} />
              </div>
            ))}
          </div>
        ) : (
          <SummaryStats 
            summary={summary}
            changePoints={changePoints}
            events={events}
            historicalData={historicalData}
          />
        )}
      </div>

      {/* Filters */}
      <div className="filters">
        <DateRangeFilter
          onDateRangeChange={handleDateRangeChange}
          dateRange={dateRange}
          disabled={loading}
        />
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <label className="form-label" style={{ margin: 0 }}>Event Types:</label>
          <select
            className="form-input"
            style={{ width: 'auto', minWidth: '150px' }}
            multiple
            value={selectedEventTypes}
            onChange={(e) => handleEventTypeFilter(Array.from(e.target.selectedOptions, option => option.value))}
            disabled={loading}
          >
            <option value="">All Types</option>
            <option value="geopolitical">Geopolitical</option>
            <option value="economic">Economic</option>
            <option value="supply">Supply</option>
            <option value="demand">Demand</option>
          </select>
        </div>
      </div>

      {/* Main Chart */}
      <div className="card">
        <div className="card-header">
          <h2>Price Timeline with Change Points</h2>
          <p style={{ color: '#718096', margin: 0 }}>
            Interactive chart showing Brent oil prices, detected change points, and major events
          </p>
        </div>
        {loading ? (
          <Skeleton height={400} />
        ) : (
          <PriceChart
            historicalData={historicalData}
            changePoints={changePoints}
            events={events}
            eventAssociations={eventAssociations}
          />
        )}
      </div>

      {/* Bottom Grid */}
      <div className="grid grid-cols-2" style={{ marginTop: '32px' }}>
        {/* Change Points */}
        <div className="card">
          <div className="card-header">
            <h3>Detected Change Points</h3>
            <p style={{ color: '#718096', margin: 0 }}>
              Bayesian change point detection results
            </p>
          </div>
          {loading ? (
            <div>
              {[1, 2, 3].map(i => (
                <div key={i} style={{ marginBottom: '16px' }}>
                  <Skeleton height={20} style={{ marginBottom: '8px' }} />
                  <Skeleton height={40} />
                </div>
              ))}
            </div>
          ) : (
            <ChangePointsList
              changePoints={changePoints}
              eventAssociations={eventAssociations}
            />
          )}
        </div>

        {/* Events */}
        <div className="card">
          <div className="card-header">
            <h3>Major Events</h3>
            <p style={{ color: '#718096', margin: 0 }}>
              Geopolitical and economic events affecting oil prices
            </p>
          </div>
          {loading ? (
            <div>
              {[1, 2, 3, 4].map(i => (
                <div key={i} style={{ marginBottom: '16px' }}>
                  <Skeleton height={20} style={{ marginBottom: '8px' }} />
                  <Skeleton height={30} />
                </div>
              ))}
            </div>
          ) : (
            <EventsList
              events={events}
              eventAssociations={eventAssociations}
              maxItems={5}
            />
          )}
        </div>
      </div>

      {/* Health Status */}
      {!loading && (
        <div style={{ 
          marginTop: '32px', 
          padding: '16px', 
          backgroundColor: '#f0fff4', 
          border: '1px solid #9ae6b4',
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          <span style={{ color: '#22543d', fontSize: '14px' }}>
            ✅ Dashboard is connected and data is up to date
          </span>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
