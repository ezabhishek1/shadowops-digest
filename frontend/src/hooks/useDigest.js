import { useState, useCallback, useMemo } from 'react';
import axios from 'axios';

// API Configuration with environment-specific endpoints
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Validate API URL configuration
if (!API_BASE_URL) {
  console.warn('REACT_APP_API_URL not configured, using default localhost:8000');
}

const useDigest = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastRequestData, setLastRequestData] = useState(null);

  // Create axios instance with default configuration
  const apiClient = useMemo(() => axios.create({
    baseURL: API_BASE_URL,
    timeout: 35000, // 35 seconds to account for 30s backend timeout + buffer
    headers: {
      'Content-Type': 'application/json',
    },
  }), []);

  // Retry logic with exponential backoff
  const retryRequest = async (requestFn, maxRetries = 3, baseDelay = 1000) => {
    let lastError;
    
    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        return await requestFn();
      } catch (error) {
        lastError = error;
        
        // Don't retry on client errors (4xx) except for 408 (timeout) and 429 (rate limit)
        if (error.response && error.response.status >= 400 && error.response.status < 500) {
          if (error.response.status !== 408 && error.response.status !== 429) {
            throw error;
          }
        }
        
        // Don't retry on the last attempt
        if (attempt === maxRetries - 1) {
          throw error;
        }
        
        // Exponential backoff with jitter
        const delay = baseDelay * Math.pow(2, attempt) + Math.random() * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
    
    throw lastError;
  };

  // Format error message for user display
  const formatErrorMessage = (error) => {
    if (error.code === 'ECONNABORTED') {
      return 'Request timed out. The analysis is taking longer than expected. Please try again.';
    }
    
    if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
      return 'Unable to connect to the server. Please check if the backend is running.';
    }
    
    if (error.response) {
      const status = error.response.status;
      const data = error.response.data;
      
      switch (status) {
        case 400:
          return data.detail || 'Invalid request. Please check your input data.';
        case 422:
          if (data.detail && Array.isArray(data.detail)) {
            const fieldErrors = data.detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join(', ');
            return `Validation error: ${fieldErrors}`;
          }
          return data.detail || 'Invalid input data format.';
        case 429:
          return 'Too many requests. Please wait a moment and try again.';
        case 500:
          return 'Server error occurred during analysis. Please try again.';
        case 503:
          return 'Service temporarily unavailable. Please try again later.';
        default:
          return data.detail || `Server error (${status}). Please try again.`;
      }
    }
    
    return error.message || 'An unexpected error occurred. Please try again.';
  };

  // Main function to generate digest
  const generateDigest = useCallback(async (requestData) => {
    setLoading(true);
    setError(null);
    setData(null);
    setLastRequestData(requestData);

    try {
      // Validate input data
      if (!requestData.tickets || !Array.isArray(requestData.tickets) || requestData.tickets.length === 0) {
        throw new Error('Please provide at least one ticket description.');
      }

      if (requestData.tickets.length > 1000) {
        throw new Error('Maximum 1000 tickets allowed per request.');
      }

      if (!requestData.avg_time_per_ticket_minutes || requestData.avg_time_per_ticket_minutes < 1 || requestData.avg_time_per_ticket_minutes > 480) {
        throw new Error('Average time per ticket must be between 1 and 480 minutes.');
      }

      if (!requestData.hourly_cost_usd || requestData.hourly_cost_usd < 1 || requestData.hourly_cost_usd > 500) {
        throw new Error('Hourly cost must be between $1.00 and $500.00.');
      }

      // Make API request with retry logic
      const response = await retryRequest(async () => {
        return await apiClient.post('/digest', requestData);
      });

      setData(response.data);
    } catch (err) {
      const errorMessage = formatErrorMessage(err);
      setError(errorMessage);
      console.error('Digest generation error:', err);
    } finally {
      setLoading(false);
    }
  }, [apiClient]);

  // Function to clear previous results
  const clearResults = useCallback(() => {
    setData(null);
    setError(null);
    setLastRequestData(null);
  }, []);

  // Function to retry the last request
  const retry = useCallback(() => {
    if (data || loading || !lastRequestData) return;
    generateDigest(lastRequestData);
  }, [data, loading, lastRequestData, generateDigest]);

  // Function to test API connection
  const testConnection = useCallback(async () => {
    try {
      const response = await apiClient.get('/health');
      return {
        success: true,
        status: response.status,
        data: response.data
      };
    } catch (err) {
      return {
        success: false,
        error: formatErrorMessage(err)
      };
    }
  }, [apiClient]);

  return {
    data,
    loading,
    error,
    generateDigest,
    clearResults,
    retry,
    testConnection,
    apiBaseUrl: API_BASE_URL
  };
};

export default useDigest;