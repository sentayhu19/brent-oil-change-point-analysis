import React from 'react';
import { format, parseISO } from 'date-fns';

const EventsList = ({ events, eventAssociations, maxItems = null }) => {
  if (!events || events.length === 0) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#718096' }}>
        <p>No events data available</p>
      </div>
    );
  }

  const displayEvents = maxItems ? events.slice(0, maxItems) : events;

  const isEventAssociated = (eventId) => {
    if (!eventAssociations) return false;
    return eventAssociations.some(assoc => 
      assoc.associated_events.some(event => event.event_id === eventId)
    );
  };

  const getEventTypeColor = (type) => {
    const colors = {
      'geopolitical': '#dc2626',
      'economic': '#2563eb',
      'supply': '#059669',
      'demand': '#7c3aed',
      'default': '#6b7280'
    };
    return colors[type?.toLowerCase()] || colors.default;
  };

  const getEventTypeIcon = (type) => {
    const icons = {
      'geopolitical': '⚔️',
      'economic': '💰',
      'supply': '🛢️',
      'demand': '📈',
      'default': '📅'
    };
    return icons[type?.toLowerCase()] || icons.default;
  };

  const getImpactLevelColor = (level) => {
    const colors = {
      'high': '#dc2626',
      'medium': '#d97706',
      'low': '#059669',
      'default': '#6b7280'
    };
    return colors[level?.toLowerCase()] || colors.default;
  };

  return (
    <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
      {displayEvents.map((event, index) => {
        const isAssociated = isEventAssociated(event.id);
        const typeColor = getEventTypeColor(event.type);
        const typeIcon = getEventTypeIcon(event.type);
        const impactColor = getImpactLevelColor(event.impact_level);
        
        return (
          <div
            key={event.id || index}
            style={{
              padding: '12px',
              marginBottom: '8px',
              border: `1px solid ${isAssociated ? '#0d9488' : '#e2e8f0'}`,
              borderRadius: '6px',
              backgroundColor: isAssociated ? '#f0fdfa' : '#ffffff',
              position: 'relative',
            }}
          >
            {/* Association Indicator */}
            {isAssociated && (
              <div
                style={{
                  position: 'absolute',
                  top: '8px',
                  right: '8px',
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  backgroundColor: '#0d9488',
                  title: 'Associated with change point'
                }}
              />
            )}

            {/* Event Header */}
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', marginBottom: '6px' }}>
              <span style={{ fontSize: '16px', flexShrink: 0 }}>{typeIcon}</span>
              <div style={{ flex: 1 }}>
                <h5 style={{ 
                  margin: '0 0 4px 0', 
                  fontSize: '14px', 
                  fontWeight: '600',
                  color: '#2d3748',
                  lineHeight: '1.3'
                }}>
                  {event.event}
                </h5>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                  <span style={{ fontSize: '12px', color: '#718096' }}>
                    {format(parseISO(event.date), 'MMM dd, yyyy')}
                  </span>
                  <span
                    style={{
                      padding: '2px 6px',
                      borderRadius: '10px',
                      fontSize: '10px',
                      fontWeight: '500',
                      backgroundColor: typeColor + '20',
                      color: typeColor,
                    }}
                  >
                    {event.type}
                  </span>
                  {event.impact_level && (
                    <span
                      style={{
                        padding: '2px 6px',
                        borderRadius: '10px',
                        fontSize: '10px',
                        fontWeight: '500',
                        backgroundColor: impactColor + '20',
                        color: impactColor,
                      }}
                    >
                      {event.impact_level} impact
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Event Description */}
            {event.description && (
              <p style={{ 
                margin: '6px 0 0 24px', 
                fontSize: '11px', 
                color: '#4a5568',
                lineHeight: '1.4'
              }}>
                {event.description}
              </p>
            )}

            {/* Association Status */}
            {isAssociated && (
              <div style={{
                marginTop: '8px',
                marginLeft: '24px',
                fontSize: '10px',
                color: '#0d9488',
                fontWeight: '500'
              }}>
                🔗 Associated with detected change point
              </div>
            )}
          </div>
        );
      })}

      {/* Show More Link */}
      {maxItems && events.length > maxItems && (
        <div style={{ textAlign: 'center', marginTop: '12px' }}>
          <p style={{ fontSize: '12px', color: '#718096', margin: '0 0 8px 0' }}>
            Showing {maxItems} of {events.length} events
          </p>
          <button className="btn btn-secondary btn-sm">
            View All Events
          </button>
        </div>
      )}

      {/* Legend */}
      <div style={{ 
        marginTop: '16px', 
        padding: '8px', 
        backgroundColor: '#f8fafc', 
        borderRadius: '4px',
        fontSize: '10px',
        color: '#718096'
      }}>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <span>⚔️ Geopolitical</span>
          <span>💰 Economic</span>
          <span>🛢️ Supply</span>
          <span>📈 Demand</span>
          <span style={{ color: '#0d9488' }}>🔗 Change Point Associated</span>
        </div>
      </div>
    </div>
  );
};

export default EventsList;
