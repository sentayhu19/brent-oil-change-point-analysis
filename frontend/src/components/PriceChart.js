import React, { useState, useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Scatter,
  ComposedChart,
  ScatterChart,
} from 'recharts';
import { format, parseISO } from 'date-fns';

const PriceChart = ({ historicalData, changePoints, events, eventAssociations }) => {
  const [showEvents, setShowEvents] = useState(true);
  const [showChangePoints, setShowChangePoints] = useState(true);
  const [selectedMetric, setSelectedMetric] = useState('price');

  // Prepare chart data
  const chartData = useMemo(() => {
    if (!historicalData || !historicalData.dates) return [];

    return historicalData.dates.map((date, index) => ({
      date: date,
      dateObj: parseISO(date),
      price: historicalData.prices[index],
      logReturns: historicalData.log_returns ? historicalData.log_returns[index] : null,
    }));
  }, [historicalData]);

  // Prepare change points for visualization
  const changePointMarkers = useMemo(() => {
    if (!changePoints || !showChangePoints) return [];

    return changePoints.map((cp, index) => {
      const dataPoint = chartData.find(d => d.date === cp.date);
      return {
        ...cp,
        index,
        price: dataPoint?.price || 0,
        x: cp.date,
        y: dataPoint?.price || 0,
      };
    });
  }, [changePoints, chartData, showChangePoints]);

  // Prepare events for visualization
  const eventMarkers = useMemo(() => {
    if (!events || !showEvents) return [];

    return events.slice(0, 10).map((event, index) => { // Limit to 10 events for clarity
      const dataPoint = chartData.find(d => d.date === event.date);
      return {
        ...event,
        index,
        price: dataPoint?.price || 0,
        x: event.date,
        y: dataPoint?.price || 0,
      };
    });
  }, [events, chartData, showEvents]);

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload || !payload.length) return null;

    const date = parseISO(label);
    const formattedDate = format(date, 'MMM dd, yyyy');
    
    // Find associated change point
    const changePoint = changePointMarkers.find(cp => cp.date === label);
    const event = eventMarkers.find(e => e.date === label);

    return (
      <div style={{
        backgroundColor: 'white',
        padding: '12px',
        border: '1px solid #e2e8f0',
        borderRadius: '8px',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        maxWidth: '300px'
      }}>
        <p style={{ margin: '0 0 8px 0', fontWeight: 'bold' }}>{formattedDate}</p>
        
        {payload.map((entry, index) => (
          <p key={index} style={{ margin: '4px 0', color: entry.color }}>
            {entry.name}: {entry.name === 'Price' ? `$${entry.value.toFixed(2)}` : entry.value?.toFixed(4)}
          </p>
        ))}
        
        {changePoint && (
          <div style={{ marginTop: '8px', padding: '8px', backgroundColor: '#fef5e7', borderRadius: '4px' }}>
            <p style={{ margin: 0, fontSize: '12px', fontWeight: 'bold', color: '#d69e2e' }}>
              🔄 Change Point Detected
            </p>
            <p style={{ margin: '4px 0 0 0', fontSize: '11px', color: '#744210' }}>
              Probability: {(changePoint.probability * 100).toFixed(1)}%
            </p>
          </div>
        )}
        
        {event && (
          <div style={{ marginTop: '8px', padding: '8px', backgroundColor: '#e6fffa', borderRadius: '4px' }}>
            <p style={{ margin: 0, fontSize: '12px', fontWeight: 'bold', color: '#0d9488' }}>
              📅 {event.event}
            </p>
            <p style={{ margin: '4px 0 0 0', fontSize: '11px', color: '#134e4a' }}>
              Type: {event.type}
            </p>
          </div>
        )}
      </div>
    );
  };

  // Chart controls
  const ChartControls = () => (
    <div style={{ 
      display: 'flex', 
      gap: '16px', 
      alignItems: 'center', 
      marginBottom: '16px',
      flexWrap: 'wrap'
    }}>
      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
        <label style={{ fontSize: '14px', fontWeight: '500' }}>Metric:</label>
        <select
          value={selectedMetric}
          onChange={(e) => setSelectedMetric(e.target.value)}
          style={{
            padding: '4px 8px',
            border: '1px solid #e2e8f0',
            borderRadius: '4px',
            fontSize: '14px'
          }}
        >
          <option value="price">Price ($)</option>
          <option value="logReturns">Log Returns</option>
        </select>
      </div>
      
      <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '14px' }}>
        <input
          type="checkbox"
          checked={showChangePoints}
          onChange={(e) => setShowChangePoints(e.target.checked)}
        />
        Show Change Points
      </label>
      
      <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '14px' }}>
        <input
          type="checkbox"
          checked={showEvents}
          onChange={(e) => setShowEvents(e.target.checked)}
        />
        Show Events
      </label>
    </div>
  );

  if (!chartData || chartData.length === 0) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: '#718096' }}>
        <p>No data available for chart visualization</p>
      </div>
    );
  }

  return (
    <div>
      <ChartControls />
      
      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="date"
              tickFormatter={(date) => format(parseISO(date), 'MMM yyyy')}
              stroke="#718096"
              fontSize={12}
            />
            <YAxis
              stroke="#718096"
              fontSize={12}
              tickFormatter={(value) => 
                selectedMetric === 'price' ? `$${value.toFixed(0)}` : value.toFixed(3)
              }
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            
            {/* Main price/returns line */}
            <Line
              type="monotone"
              dataKey={selectedMetric}
              stroke="#3182ce"
              strokeWidth={2}
              dot={false}
              name={selectedMetric === 'price' ? 'Price' : 'Log Returns'}
            />
            
            {/* Change point markers */}
            {showChangePoints && changePointMarkers.map((cp, index) => (
              <ReferenceLine
                key={`cp-${index}`}
                x={cp.date}
                stroke="#d69e2e"
                strokeWidth={2}
                strokeDasharray="5 5"
                label={{
                  value: `CP${index + 1}`,
                  position: 'topLeft',
                  style: { fill: '#d69e2e', fontSize: '12px', fontWeight: 'bold' }
                }}
              />
            ))}
            
            {/* Event markers */}
            {showEvents && eventMarkers.map((event, index) => (
              <ReferenceLine
                key={`event-${index}`}
                x={event.date}
                stroke="#0d9488"
                strokeWidth={1}
                strokeDasharray="2 2"
                label={{
                  value: '📅',
                  position: 'top',
                  style: { fontSize: '16px' }
                }}
              />
            ))}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      
      {/* Chart Legend */}
      <div style={{ 
        marginTop: '16px', 
        display: 'flex', 
        gap: '24px', 
        fontSize: '12px',
        flexWrap: 'wrap'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <div style={{ width: '20px', height: '2px', backgroundColor: '#3182ce' }}></div>
          <span>{selectedMetric === 'price' ? 'Brent Oil Price' : 'Log Returns'}</span>
        </div>
        {showChangePoints && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <div style={{ 
              width: '20px', 
              height: '2px', 
              backgroundColor: '#d69e2e',
              borderStyle: 'dashed',
              borderWidth: '1px 0'
            }}></div>
            <span>Change Points</span>
          </div>
        )}
        {showEvents && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <div style={{ 
              width: '20px', 
              height: '1px', 
              backgroundColor: '#0d9488',
              borderStyle: 'dotted',
              borderWidth: '1px 0'
            }}></div>
            <span>Major Events</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default PriceChart;
