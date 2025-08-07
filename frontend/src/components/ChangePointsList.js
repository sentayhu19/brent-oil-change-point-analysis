import React from 'react';
import { format, parseISO } from 'date-fns';

const ChangePointsList = ({ changePoints, eventAssociations, maxItems = null }) => {
  if (!changePoints || changePoints.length === 0) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#718096' }}>
        <p>No change points detected</p>
      </div>
    );
  }

  const displayPoints = maxItems ? changePoints.slice(0, maxItems) : changePoints;

  const getAssociatedEvents = (changePointId) => {
    if (!eventAssociations) return [];
    const association = eventAssociations.find(assoc => assoc.changepoint_id === changePointId);
    return association ? association.associated_events : [];
  };

  const getProbabilityColor = (probability) => {
    if (probability >= 0.8) return '#22c55e';
    if (probability >= 0.6) return '#f59e0b';
    return '#ef4444';
  };

  const getProbabilityLabel = (probability) => {
    if (probability >= 0.8) return 'High';
    if (probability >= 0.6) return 'Medium';
    return 'Low';
  };

  return (
    <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
      {displayPoints.map((changePoint, index) => {
        const associatedEvents = getAssociatedEvents(index);
        const probability = changePoint.probability || 0;
        
        return (
          <div
            key={index}
            style={{
              padding: '16px',
              marginBottom: '12px',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              backgroundColor: '#fafafa',
            }}
          >
            {/* Change Point Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <h4 style={{ margin: 0, color: '#2d3748' }}>
                Change Point #{index + 1}
              </h4>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span
                  style={{
                    padding: '2px 8px',
                    borderRadius: '12px',
                    fontSize: '12px',
                    fontWeight: '500',
                    backgroundColor: getProbabilityColor(probability) + '20',
                    color: getProbabilityColor(probability),
                  }}
                >
                  {getProbabilityLabel(probability)} Confidence
                </span>
                <span style={{ fontSize: '12px', color: '#718096' }}>
                  {(probability * 100).toFixed(1)}%
                </span>
              </div>
            </div>

            {/* Date and Price */}
            <div style={{ marginBottom: '8px' }}>
              <p style={{ margin: '4px 0', fontSize: '14px' }}>
                <strong>Date:</strong> {format(parseISO(changePoint.date), 'MMM dd, yyyy')}
              </p>
              {changePoint.price_at_changepoint && (
                <p style={{ margin: '4px 0', fontSize: '14px' }}>
                  <strong>Price:</strong> ${changePoint.price_at_changepoint.toFixed(2)}
                </p>
              )}
            </div>

            {/* Confidence Interval */}
            {changePoint.confidence_interval && (
              <div style={{ marginBottom: '8px' }}>
                <p style={{ margin: '4px 0', fontSize: '12px', color: '#718096' }}>
                  <strong>95% CI:</strong> {' '}
                  {format(parseISO(changePoint.confidence_interval.lower), 'MMM dd, yyyy')} - {' '}
                  {format(parseISO(changePoint.confidence_interval.upper), 'MMM dd, yyyy')}
                </p>
              </div>
            )}

            {/* Associated Events */}
            {associatedEvents.length > 0 && (
              <div style={{ marginTop: '12px', paddingTop: '8px', borderTop: '1px solid #e2e8f0' }}>
                <p style={{ margin: '0 0 6px 0', fontSize: '12px', fontWeight: '500', color: '#4a5568' }}>
                  Associated Events:
                </p>
                {associatedEvents.slice(0, 2).map((event, eventIndex) => (
                  <div
                    key={eventIndex}
                    style={{
                      padding: '6px 8px',
                      marginBottom: '4px',
                      backgroundColor: '#e6fffa',
                      borderRadius: '4px',
                      fontSize: '11px',
                    }}
                  >
                    <div style={{ fontWeight: '500', color: '#0d9488' }}>
                      {event.event_name}
                    </div>
                    <div style={{ color: '#134e4a' }}>
                      {format(parseISO(event.event_date), 'MMM dd, yyyy')} 
                      ({Math.abs(event.days_difference)} days {event.days_difference >= 0 ? 'after' : 'before'})
                    </div>
                  </div>
                ))}
                {associatedEvents.length > 2 && (
                  <p style={{ margin: '4px 0 0 0', fontSize: '10px', color: '#718096' }}>
                    +{associatedEvents.length - 2} more events
                  </p>
                )}
              </div>
            )}

            {/* No Associated Events */}
            {associatedEvents.length === 0 && (
              <div style={{ marginTop: '8px', fontSize: '11px', color: '#9ca3af', fontStyle: 'italic' }}>
                No major events associated within the detection window
              </div>
            )}
          </div>
        );
      })}

      {/* Show More Link */}
      {maxItems && changePoints.length > maxItems && (
        <div style={{ textAlign: 'center', marginTop: '16px' }}>
          <p style={{ fontSize: '12px', color: '#718096' }}>
            Showing {maxItems} of {changePoints.length} change points
          </p>
          <button className="btn btn-secondary btn-sm">
            View All Change Points
          </button>
        </div>
      )}
    </div>
  );
};

export default ChangePointsList;
