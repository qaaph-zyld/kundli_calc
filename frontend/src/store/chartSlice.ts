import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';
import { BirthChart } from '../types/chart';

interface ChartState {
  chart: BirthChart | null;
  loading: boolean;
  error: string | null;
}

const initialState: ChartState = {
  chart: null,
  loading: false,
  error: null,
};

export const calculateChart = createAsyncThunk(
  'chart/calculate',
  async (params: {
    date_time: string;
    latitude: number;
    longitude: number;
    altitude?: number;
    ayanamsa?: number;
    house_system?: string;
  }) => {
    const response = await axios.post<BirthChart>(
      'http://localhost:8000/api/v1/charts/calculate',
      params
    );
    return response.data;
  }
);

const chartSlice = createSlice({
  name: 'chart',
  initialState,
  reducers: {
    clearChart: (state) => {
      state.chart = null;
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(calculateChart.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(calculateChart.fulfilled, (state, action) => {
        state.loading = false;
        state.chart = action.payload;
      })
      .addCase(calculateChart.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to calculate chart';
      });
  },
});

export const { clearChart } = chartSlice.actions;
export default chartSlice.reducer;
