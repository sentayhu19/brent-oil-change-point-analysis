import React, { useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from 'recharts';
import { format, parseISO } from 'date-fns';

const ImpactAnalysisChart = ({ impactAnalysis, changePoints }) => {
  const [selectedMetric, setSelectedMetric] = useState('price');

  if (!impactAnalysis || impactAnalysis.length === 0) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: '#718096' }}>
        <p>No impact analysis data available</p>
      </div>
    );
  }

  // Prepare chart data
  const chartData = impactAnalysis.map((impact, index) => ({
    id: index,
    name: `CP ${impact.changepoint_id + 1}`,
    date: format(parseISO(impact.changepoint_date), 'MMM yyyy'),
    fullDate: impact.changepoint_date,
    priceChange: impact.price_impact.change_percent,
    volatilityChange: impact.volatility_impact.change_percent,
    priceBefore: impact.price_impact.before_mean,
    priceAfter: impact.price_impact.after_mean,
    volBefore: impact.volatility_impact.before_std,
    volAfter: impact.volatility_impact.after_std,
    priceSignificance: impact.price_impact.significance,
    volSignificance: impact.volatility_impact.significance
  }));

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload || !payload.length) return null;

    const data = payload[0].payload;
    
    return (
      <div style={{
        backgroundColor: 'white',
        padding: '12px',
        border: '1px solid #e2e8f0',
        borderRadius: '8px',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        maxWidth: '300px'
      }}>
        <p style={{ margin: '0 0 8px 0', fontWeight: 'bold' }}>
          {label} ({format(parseISO(data.fullDate), 'MMM dd, yyyy')})
        </p>
        
        {selectedMetric === 'price' ? (
          <div>
            <p style={{ margin: '4px 0', color: '#3182ce' }}>
              Price Change: {data.priceChange >= 0 ? '+' : ''}{data.priceChange.toFixed(1)}%
            </p>
            <p style={{ margin: '4px 0', fontSize: '12px', color: '#718096' }}>
              Before: ${data.priceBefore.toFixed(2)}
            </p>
            <p style={{ margin: '4px 0', fontSize: '12px', color: '#718096' }}>
              After: ${data.priceAfter.toFixed(2)}
            </p>
            <p style={{ margin: '4px 0', fontSize: '11px', color: '#9ca3af' }}>
              Significance: {data.priceSignificance || 'Unknown'}
            </p>
          </div>
        ) : (
          <div>
            <p style={{ margin: '4px 0', color: '#7c3aed' }}>
              Volatility Change: {data.volatilityChange >= 0 ? '+' : ''}{data.volatilityChange.toFixed(1)}%
            </p>
            <p style={{ margin: '4px 0', fontSize: '12px', color: '#718096' }}>
              Before: σ = {data.volBefore.toFixed(4)}
            </p>
            <p style={{ margin: '4px 0', fontSize: '12px', color: '#718096' }}>
              After: σ = {data.volAfter.toFixed(4)}
            </p>
            <p style={{ margin: '4px 0', fontSize: '11px', color: '#9ca3af' }}>
              Significance: {data.volSignificance || 'Unknown'}
            </p>
          </div>
        )}
      </div>
    );
  };

  // Color function for bars
  const getBarColor = (value, metric) => {
    if (metric === 'price') {
      return value >= 0 ? '#22c55e' : '#ef4444';
    } else {
      // For volatility, higher is typically worse (more risk)
      return value >= 0 ? '#ef4444' : '#22c55e';
    }
  };

  return (
    <div>
      {/* Controls */}
      <div style={{ 
        display: 'flex', 
        gap: '16px', 
        alignItems: 'center', 
        marginBottom: '24px',
        flexWrap: 'wrap'
      }}>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <label style={{ fontSize: '14px', fontWeight: '500' }}>Impact Metric:</label>
          <select
            value={selectedMetric}
            onChange={(e) => setSelectedMetric(e.target.value)}
            style={{
              padding: '6px 12px',
              border: '1px solid #e2e8f0',
              borderRadius: '6px',
              fontSize: '14px'
            }}
          >
            <option value="price">Price Impact (%)</option>
            <option value="volatility">Volatility Impact (%)</option>
          </select>
        </div>
        
        <div style={{ fontSize: '12px', color: '#718096' }}>
          {selectedMetric === 'price' ? (
            <span>📊 Green: Price increase, Red: Price decrease</span>
          ) : (
            <span>📊 Red: Volatility increase, Green: Volatility decrease</span>
          )}
        </div>
      </div>

      {/* Chart */}
      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="name"
              stroke="#718096"
              fontSize={12}
            />
            <YAxis
              stroke="#718096"
              fontSize={12}
              tickFormatter={(value) => `${value.toFixed(1)}%`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            
            <Bar
              dataKey={selectedMetric === 'price' ? 'priceChange' : 'volatilityChange'}
              name={selectedMetric === 'price' ? 'Price Change (%)' : 'Volatility Change (%)'}
              radius={[4, 4, 0, 0]}
            >
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={getBarColor(
                    selectedMetric === 'price' ? entry.priceChange : entry.volatilityChange,
                    selectedMetric
                  )}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Summary Statistics */}
      <div style={{ 
        marginTop: '24px', 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
        gap: '16px' 
      }}>
        <div style={{ 
          padding: '16px', 
          backgroundColor: '#f8fafc', 
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#3182ce' }}>
            {chartData.filter(d => d.priceChange > 0).length}
          </div>
          <div style={{ fontSize: '12px', color: '#718096' }}>
            Price Increases
          </div>
        </div>
        
        <div style={{ 
          padding: '16px', 
          backgroundColor: '#fef5e7', 
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#d69e2e' }}>
            {chartData.filter(d => d.volatilityChange > 0).length}
          </div>
          <div style={{ fontSize: '12px', color: '#718096' }}>
            Volatility Increases
          </div>
        </div>
        
        <div style={{ 
          padding: '16px', 
          backgroundColor: '#f0fff4', 
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#22c55e' }}>
            {(chartData.reduce((sum, d) => sum + Math.abs(d.priceChange), 0) / chartData.length).toFixed(1)}%
          </div>
          <div style={{ fontSize: '12px', color: '#718096' }}>
            Avg Price Impact
          </div>
        </div>
        
        <div style={{ 
          padding: '16px', 
          backgroundColor: '#fdf2f8', 
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#ec4899' }}>
            {(chartData.reduce((sum, d) => sum + Math.abs(d.volatilityChange), 0) / chartData.length).toFixed(1)}%
          </div>
          <div style={{ fontSize: '12px', color: '#718096' }}>
            Avg Volatility Impact
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImpactAnalysisChart;
