import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API service functions
export const apiService = {
  // Health check
  async healthCheck() {
    const response = await api.get('/health');
    return response.data;
  },

  // Historical data
  async getHistoricalData(startDate = null, endDate = null) {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    
    const response = await api.get('/historical-data', { params });
    return response.data;
  },

  // Change points
  async getChangePoints() {
    const response = await api.get('/change-points');
    return response.data;
  },

  // Events
  async getEvents(startDate = null, endDate = null, eventType = null) {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    if (eventType) params.type = eventType;
    
    const response = await api.get('/events', { params });
    return response.data;
  },

  // Event associations
  async getEventAssociations() {
    const response = await api.get('/event-associations');
    return response.data;
  },

  // Impact analysis
  async getImpactAnalysis() {
    const response = await api.get('/impact-analysis');
    return response.data;
  },

  // Model diagnostics
  async getModelDiagnostics() {
    const response = await api.get('/model-diagnostics');
    return response.data;
  },

  // Summary
  async getSummary() {
    const response = await api.get('/summary');
    return response.data;
  },
};

// Utility function to handle API errors
export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error status
    const message = error.response.data?.error || `Server error: ${error.response.status}`;
    return { error: message, status: error.response.status };
  } else if (error.request) {
    // Request was made but no response received
    return { error: 'No response from server. Please check if the backend is running.', status: null };
  } else {
    // Something else happened
    return { error: error.message || 'An unexpected error occurred', status: null };
  }
};

export default api;
