import axios from 'axios';
import { configureStore } from '@reduxjs/toolkit';
import chartReducer, { calculateChart, clearChart } from '../chartSlice';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('chartSlice', () => {
  let store: ReturnType<typeof configureStore>;

  beforeEach(() => {
    store = configureStore({
      reducer: {
        chart: chartReducer,
      },
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('initial state', () => {
    it('should have correct initial state', () => {
      const state = store.getState().chart;
      expect(state).toEqual({
        chart: null,
        loading: false,
        error: null,
      });
    });
  });

  describe('clearChart', () => {
    it('should clear chart and error state', () => {
      // Set some initial state
      store.dispatch(calculateChart.fulfilled({
        date_time: '2024-01-01T12:00:00Z',
        location: { latitude: 0, longitude: 0, altitude: 0 },
        planetary_positions: {},
        houses: { cusps: [], ascendant: 0, midheaven: 0, armc: 0, vertex: 0 },
        aspects: [],
        nakshatras: {},
      }, '', {
        date_time: '2024-01-01T12:00:00Z',
        latitude: 0,
        longitude: 0,
      }));

      // Clear the state
      store.dispatch(clearChart());

      // Verify state is cleared
      const state = store.getState().chart;
      expect(state.chart).toBeNull();
      expect(state.error).toBeNull();
    });
  });

  describe('calculateChart', () => {
    const mockParams = {
      date_time: '2024-01-01T12:00:00Z',
      latitude: 13.0827,
      longitude: 80.2707,
      altitude: 0,
    };

    const mockResponse = {
      date_time: '2024-01-01T12:00:00Z',
      location: {
        latitude: 13.0827,
        longitude: 80.2707,
        altitude: 0,
      },
      planetary_positions: {
        'Sun': { longitude: 260.5, latitude: 0.0, distance: 0.98, speed: 1.01 },
      },
      houses: {
        cusps: [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330],
        ascendant: 82.5,
        midheaven: 350.2,
        armc: 345.6,
        vertex: 175.3,
      },
      aspects: [],
      nakshatras: {},
    };

    it('should set loading state while pending', () => {
      store.dispatch(calculateChart.pending('', mockParams));
      const state = store.getState().chart;
      expect(state.loading).toBe(true);
      expect(state.error).toBeNull();
    });

    it('should update state on successful API call', async () => {
      mockedAxios.post.mockResolvedValueOnce({ data: mockResponse });

      await store.dispatch(calculateChart(mockParams));

      const state = store.getState().chart;
      expect(state.loading).toBe(false);
      expect(state.chart).toEqual(mockResponse);
      expect(state.error).toBeNull();
    });

    it('should handle API errors', async () => {
      const errorMessage = 'Network Error';
      mockedAxios.post.mockRejectedValueOnce(new Error(errorMessage));

      await store.dispatch(calculateChart(mockParams));

      const state = store.getState().chart;
      expect(state.loading).toBe(false);
      expect(state.chart).toBeNull();
      expect(state.error).toBe(errorMessage);
    });

    it('should make API call with correct parameters', async () => {
      mockedAxios.post.mockResolvedValueOnce({ data: mockResponse });

      await store.dispatch(calculateChart(mockParams));

      expect(mockedAxios.post).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/charts/calculate',
        mockParams
      );
    });
  });
});
