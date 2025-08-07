import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import Skeleton from 'react-loading-skeleton';

import { apiService, handleApiError } from '../services/api';
import EventsList from '../components/EventsList';
import DateRangeFilter from '../components/DateRangeFilter';

const EventExplorer = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [events, setEvents] = useState([]);
  const [eventAssociations, setEventAssociations] = useState([]);
  const [filteredEvents, setFilteredEvents] = useState([]);
  
  // Filter state
  const [dateRange, setDateRange] = useState({ startDate: null, endDate: null });
  const [selectedEventType, setSelectedEventType] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [showOnlyAssociated, setShowOnlyAssociated] = useState(false);

  useEffect(() => {
    loadEventData();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [events, eventAssociations, dateRange, selectedEventType, searchQuery, showOnlyAssociated]);

  const loadEventData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [eventsResponse, associationsResponse] = await Promise.all([
        apiService.getEvents(),
        apiService.getEventAssociations()
      ]);

      setEvents(eventsResponse);
      setEventAssociations(associationsResponse);

      toast.success('Event data loaded successfully!');
    } catch (err) {
      const errorInfo = handleApiError(err);
      setError(errorInfo.error);
      toast.error(`Failed to load event data: ${errorInfo.error}`);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...events];

    // Date range filter
    if (dateRange.startDate) {
      filtered = filtered.filter(event => new Date(event.date) >= dateRange.startDate);
    }
    if (dateRange.endDate) {
      filtered = filtered.filter(event => new Date(event.date) <= dateRange.endDate);
    }

    // Event type filter
    if (selectedEventType) {
      filtered = filtered.filter(event => 
        event.type.toLowerCase().includes(selectedEventType.toLowerCase())
      );
    }

    // Search query filter
    if (searchQuery) {
      filtered = filtered.filter(event =>
        event.event.toLowerCase().includes(searchQuery.toLowerCase()) ||
        event.description?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Show only associated events
    if (showOnlyAssociated) {
      const associatedEventIds = new Set();
      eventAssociations.forEach(assoc => {
        assoc.associated_events.forEach(event => {
          associatedEventIds.add(event.event_id);
        });
      });
      filtered = filtered.filter(event => associatedEventIds.has(event.id));
    }

    // Sort by date (most recent first)
    filtered.sort((a, b) => new Date(b.date) - new Date(a.date));

    setFilteredEvents(filtered);
  };

  const getEventTypeStats = () => {
    const stats = {};
    events.forEach(event => {
      const type = event.type || 'unknown';
      stats[type] = (stats[type] || 0) + 1;
    });
    return stats;
  };

  const getAssociationStats = () => {
    const associatedEventIds = new Set();
    eventAssociations.forEach(assoc => {
      assoc.associated_events.forEach(event => {
        associatedEventIds.add(event.event_id);
      });
    });
    return {
      total: events.length,
      associated: associatedEventIds.size,
      unassociated: events.length - associatedEventIds.size
    };
  };

  if (error) {
    return (
      <div className="container" style={{ padding: '40px 20px' }}>
        <div className="error">
          <h3>Error Loading Event Data</h3>
          <p>{error}</p>
          <button 
            className="btn btn-primary" 
            onClick={loadEventData}
            style={{ marginTop: '16px' }}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const eventTypeStats = !loading ? getEventTypeStats() : {};
  const associationStats = !loading ? getAssociationStats() : {};

  return (
    <div className="container" style={{ padding: '20px' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h1>Event Explorer</h1>
        <p style={{ color: '#718096', fontSize: '1.1rem' }}>
          Explore major geopolitical and economic events affecting Brent oil prices
        </p>
      </div>

      {/* Statistics Cards */}
      <div className="stats-grid" style={{ marginBottom: '32px' }}>
        {loading ? (
          [1, 2, 3, 4].map(i => (
            <div key={i} className="stat-card">
              <Skeleton height={40} style={{ marginBottom: '8px' }} />
              <Skeleton height={20} />
            </div>
          ))
        ) : (
          <>
            <div className="stat-card">
              <div className="stat-value" style={{ color: '#3182ce' }}>
                {events.length}
              </div>
              <div className="stat-label">Total Events</div>
            </div>
            <div className="stat-card">
              <div className="stat-value" style={{ color: '#22c55e' }}>
                {associationStats.associated}
              </div>
              <div className="stat-label">Associated with Change Points</div>
            </div>
            <div className="stat-card">
              <div className="stat-value" style={{ color: '#dc2626' }}>
                {eventTypeStats.geopolitical || 0}
              </div>
              <div className="stat-label">Geopolitical Events</div>
            </div>
            <div className="stat-card">
              <div className="stat-value" style={{ color: '#2563eb' }}>
                {eventTypeStats.economic || 0}
              </div>
              <div className="stat-label">Economic Events</div>
            </div>
          </>
        )}
      </div>

      {/* Filters */}
      <div className="card" style={{ marginBottom: '32px' }}>
        <div className="card-header">
          <h3>Filter Events</h3>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Date Range Filter */}
          <DateRangeFilter
            onDateRangeChange={(startDate, endDate) => setDateRange({ startDate, endDate })}
            dateRange={dateRange}
            disabled={loading}
          />
          
          {/* Other Filters */}
          <div style={{ display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
            {/* Event Type Filter */}
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <label className="form-label" style={{ margin: 0 }}>Type:</label>
              <select
                value={selectedEventType}
                onChange={(e) => setSelectedEventType(e.target.value)}
                className="form-input"
                style={{ width: 'auto', minWidth: '120px' }}
                disabled={loading}
              >
                <option value="">All Types</option>
                <option value="geopolitical">Geopolitical</option>
                <option value="economic">Economic</option>
                <option value="supply">Supply</option>
                <option value="demand">Demand</option>
              </select>
            </div>

            {/* Search Filter */}
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flex: 1 }}>
              <label className="form-label" style={{ margin: 0 }}>Search:</label>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search events..."
                className="form-input"
                disabled={loading}
              />
            </div>

            {/* Association Filter */}
            <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '14px' }}>
              <input
                type="checkbox"
                checked={showOnlyAssociated}
                onChange={(e) => setShowOnlyAssociated(e.target.checked)}
                disabled={loading}
              />
              Show only associated events
            </label>
          </div>
        </div>
      </div>

      {/* Results Summary */}
      <div style={{ 
        marginBottom: '16px', 
        padding: '12px 16px', 
        backgroundColor: '#f8fafc', 
        borderRadius: '6px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <span style={{ fontSize: '14px', color: '#4a5568' }}>
          {loading ? (
            <Skeleton width={200} height={20} />
          ) : (
            `Showing ${filteredEvents.length} of ${events.length} events`
          )}
        </span>
        {!loading && filteredEvents.length !== events.length && (
          <button
            onClick={() => {
              setDateRange({ startDate: null, endDate: null });
              setSelectedEventType('');
              setSearchQuery('');
              setShowOnlyAssociated(false);
            }}
            className="btn btn-secondary btn-sm"
          >
            Clear Filters
          </button>
        )}
      </div>

      {/* Events List */}
      <div className="card">
        <div className="card-header">
          <h3>Events Timeline</h3>
          <p style={{ color: '#718096', margin: 0 }}>
            Chronological list of major events with change point associations
          </p>
        </div>
        {loading ? (
          <div>
            {[1, 2, 3, 4, 5].map(i => (
              <div key={i} style={{ marginBottom: '16px' }}>
                <Skeleton height={80} />
              </div>
            ))}
          </div>
        ) : filteredEvents.length > 0 ? (
          <EventsList
            events={filteredEvents}
            eventAssociations={eventAssociations}
            maxItems={null} // Show all filtered events
          />
        ) : (
          <div style={{ padding: '40px', textAlign: 'center', color: '#718096' }}>
            <p>No events match the current filters</p>
            <button
              onClick={() => {
                setDateRange({ startDate: null, endDate: null });
                setSelectedEventType('');
                setSearchQuery('');
                setShowOnlyAssociated(false);
              }}
              className="btn btn-secondary"
              style={{ marginTop: '16px' }}
            >
              Reset Filters
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default EventExplorer;
