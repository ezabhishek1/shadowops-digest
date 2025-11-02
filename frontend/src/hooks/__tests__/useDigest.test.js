import { renderHook, act, waitFor } from '@testing-library/react';
import axios from 'axios';
import useDigest from '../useDigest';

// Mock axios
jest.mock('axios');
const mockedAxios = axios;

// Mock console.error to avoid noise in tests
const originalConsoleError = console.error;
beforeAll(() => {
  console.error = jest.fn();
});

afterAll(() => {
  console.error = originalConsoleError;
});

describe('useDigest Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Mock axios.create to return a mock instance
    mockedAxios.create.mockReturnValue({
      post: jest.fn(),
      get: jest.fn()
    });
  });

  test('initializes with correct default state', () => {
    const { result } = renderHook(() => useDigest());

    expect(result.current.data).toBeNull();
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(typeof result.current.generateDigest).toBe('function');
    expect(typeof result.current.clearResults).toBe('function');
    expect(typeof result.current.retry).toBe('function');
    expect(typeof result.current.testConnection).toBe('function');
  });

  test('validates input data before making API call', async () => {
    const { result } = renderHook(() => useDigest());

    // Test empty tickets
    await act(async () => {
      await result.current.generateDigest({
        tickets: [],
        avg_time_per_ticket_minutes: 30,
        hourly_cost_usd: 40.0
      });
    });

    expect(result.current.error).toBe('Please provide at least one ticket description.');
    expect(result.current.loading).toBe(false);
  });

  test('validates ticket count limit', async () => {
    const { result } = renderHook(() => useDigest());

    // Create array with more than 1000 tickets
    const tooManyTickets = Array(1001).fill('Test ticket');

    await act(async () => {
      await result.current.generateDigest({
        tickets: tooManyTickets,
        avg_time_per_ticket_minutes: 30,
        hourly_cost_usd: 40.0
      });
    });

    expect(result.current.error).toBe('Maximum 1000 tickets allowed per request.');
  });

  test('validates time range', async () => {
    const { result } = renderHook(() => useDigest());

    await act(async () => {
      await result.current.generateDigest({
        tickets: ['Test ticket'],
        avg_time_per_ticket_minutes: 500, // Too high
        hourly_cost_usd: 40.0
      });
    });

    expect(result.current.error).toBe('Average time per ticket must be between 1 and 480 minutes.');
  });

  test('validates cost range', async () => {
    const { result } = renderHook(() => useDigest());

    await act(async () => {
      await result.current.generateDigest({
        tickets: ['Test ticket'],
        avg_time_per_ticket_minutes: 30,
        hourly_cost_usd: 600.0 // Too high
      });
    });

    expect(result.current.error).toBe('Hourly cost must be between $1.00 and $500.00.');
  });

  test('handles successful API response', async () => {
    const mockApiClient = {
      post: jest.fn().mockResolvedValue({
        data: {
          clusters: { 'Test Cluster': [0] },
          suggestion: 'Test suggestion',
          time_wasted_hours: 1.5,
          cost_saved_usd: 60.0,
          digest_summary: 'Test summary'
        }
      }),
      get: jest.fn()
    };

    mockedAxios.create.mockReturnValue(mockApiClient);

    const { result } = renderHook(() => useDigest());

    await act(async () => {
      await result.current.generateDigest({
        tickets: ['Test ticket'],
        avg_time_per_ticket_minutes: 30,
        hourly_cost_usd: 40.0
      });
    });

    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.data).toEqual({
      clusters: { 'Test Cluster': [0] },
      suggestion: 'Test suggestion',
      time_wasted_hours: 1.5,
      cost_saved_usd: 60.0,
      digest_summary: 'Test summary'
    });
  });

  test('handles API errors correctly', async () => {
    const mockApiClient = {
      post: jest.fn().mockRejectedValue({
        response: {
          status: 500,
          data: { detail: 'Internal server error' }
        }
      }),
      get: jest.fn()
    };

    mockedAxios.create.mockReturnValue(mockApiClient);

    const { result } = renderHook(() => useDigest());

    await act(async () => {
      await result.current.generateDigest({
        tickets: ['Test ticket'],
        avg_time_per_ticket_minutes: 30,
        hourly_cost_usd: 40.0
      });
    });

    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe('Internal server error');
    expect(result.current.data).toBeNull();
  });

  test('handles network errors', async () => {
    const mockApiClient = {
      post: jest.fn().mockRejectedValue({
        code: 'ECONNREFUSED'
      }),
      get: jest.fn()
    };

    mockedAxios.create.mockReturnValue(mockApiClient);

    const { result } = renderHook(() => useDigest());

    await act(async () => {
      await result.current.generateDigest({
        tickets: ['Test ticket'],
        avg_time_per_ticket_minutes: 30,
        hourly_cost_usd: 40.0
      });
    });

    expect(result.current.error).toBe('Unable to connect to the server. Please check if the backend is running.');
  });

  test('handles timeout errors', async () => {
    const mockApiClient = {
      post: jest.fn().mockRejectedValue({
        code: 'ECONNABORTED'
      }),
      get: jest.fn()
    };

    mockedAxios.create.mockReturnValue(mockApiClient);

    const { result } = renderHook(() => useDigest());

    await act(async () => {
      await result.current.generateDigest({
        tickets: ['Test ticket'],
        avg_time_per_ticket_minutes: 30,
        hourly_cost_usd: 40.0
      });
    });

    expect(result.current.error).toBe('Request timed out. The analysis is taking longer than expected. Please try again.');
  });

  test('clearResults function works correctly', () => {
    const { result } = renderHook(() => useDigest());

    // Set some initial state
    act(() => {
      result.current.clearResults();
    });

    expect(result.current.data).toBeNull();
    expect(result.current.error).toBeNull();
  });

  test('testConnection function works correctly', async () => {
    const mockApiClient = {
      post: jest.fn(),
      get: jest.fn().mockResolvedValue({
        status: 200,
        data: { status: 'healthy' }
      })
    };

    mockedAxios.create.mockReturnValue(mockApiClient);

    const { result } = renderHook(() => useDigest());

    let connectionResult;
    await act(async () => {
      connectionResult = await result.current.testConnection();
    });

    expect(connectionResult.success).toBe(true);
    expect(connectionResult.status).toBe(200);
    expect(connectionResult.data).toEqual({ status: 'healthy' });
  });

  test('testConnection handles errors', async () => {
    const mockApiClient = {
      post: jest.fn(),
      get: jest.fn().mockRejectedValue({
        code: 'ECONNREFUSED'
      })
    };

    mockedAxios.create.mockReturnValue(mockApiClient);

    const { result } = renderHook(() => useDigest());

    let connectionResult;
    await act(async () => {
      connectionResult = await result.current.testConnection();
    });

    expect(connectionResult.success).toBe(false);
    expect(connectionResult.error).toBe('Unable to connect to the server. Please check if the backend is running.');
  });

  test('sets loading state correctly during API call', async () => {
    const mockApiClient = {
      post: jest.fn().mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({ data: {} }), 100))
      ),
      get: jest.fn()
    };

    mockedAxios.create.mockReturnValue(mockApiClient);

    const { result } = renderHook(() => useDigest());

    act(() => {
      result.current.generateDigest({
        tickets: ['Test ticket'],
        avg_time_per_ticket_minutes: 30,
        hourly_cost_usd: 40.0
      });
    });

    // Should be loading immediately after call
    expect(result.current.loading).toBe(true);

    // Wait for completion
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
  });
});