import React from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

const DateRangeFilter = ({ onDateRangeChange, dateRange, disabled = false }) => {
  const handleStartDateChange = (date) => {
    onDateRangeChange(date, dateRange.endDate);
  };

  const handleEndDateChange = (date) => {
    onDateRangeChange(dateRange.startDate, date);
  };

  const clearFilters = () => {
    onDateRangeChange(null, null);
  };

  return (
    <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
      <label className="form-label" style={{ margin: 0, whiteSpace: 'nowrap' }}>
        Date Range:
      </label>
      
      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
        <DatePicker
          selected={dateRange.startDate}
          onChange={handleStartDateChange}
          selectsStart
          startDate={dateRange.startDate}
          endDate={dateRange.endDate}
          placeholderText="Start Date"
          className="form-input"
          style={{ width: '140px' }}
          disabled={disabled}
          dateFormat="yyyy-MM-dd"
          maxDate={new Date()}
        />
        
        <span style={{ color: '#718096' }}>to</span>
        
        <DatePicker
          selected={dateRange.endDate}
          onChange={handleEndDateChange}
          selectsEnd
          startDate={dateRange.startDate}
          endDate={dateRange.endDate}
          minDate={dateRange.startDate}
          placeholderText="End Date"
          className="form-input"
          style={{ width: '140px' }}
          disabled={disabled}
          dateFormat="yyyy-MM-dd"
          maxDate={new Date()}
        />
      </div>
      
      {(dateRange.startDate || dateRange.endDate) && (
        <button
          onClick={clearFilters}
          className="btn btn-secondary btn-sm"
          disabled={disabled}
          style={{ whiteSpace: 'nowrap' }}
        >
          Clear Filters
        </button>
      )}
      
      <div style={{ fontSize: '12px', color: '#718096' }}>
        {dateRange.startDate || dateRange.endDate ? (
          <span>
            Filtered: {dateRange.startDate ? dateRange.startDate.toLocaleDateString() : 'Start'} - {' '}
            {dateRange.endDate ? dateRange.endDate.toLocaleDateString() : 'End'}
          </span>
        ) : (
          <span>All available data</span>
        )}
      </div>
    </div>
  );
};

export default DateRangeFilter;
