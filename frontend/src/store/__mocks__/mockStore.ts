import { configureStore } from '@reduxjs/toolkit';
import chartReducer from '../chartSlice';

export const createMockStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      chart: chartReducer,
    },
    preloadedState: {
      chart: {
        data: null,
        loading: false,
        error: null,
        ...initialState,
      },
    },
  });
};
