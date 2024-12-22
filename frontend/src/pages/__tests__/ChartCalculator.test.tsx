import React from 'react';
import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import ChartCalculator from '../ChartCalculator';
import { createMockStore } from '../../store/__mocks__/mockStore';

const mockChart = {
  date_time: '2024-01-01T12:00:00Z',
  location: {
    latitude: 13.0827,
    longitude: 80.2707,
    altitude: 0,
  },
  planetary_positions: {
    'Sun': { longitude: 260.5, latitude: 0.0, distance: 0.98, speed: 1.01 },
    'Moon': { longitude: 45.3, latitude: -4.5, distance: 60.3, speed: 13.2 },
  },
  houses: {
    cusps: [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330],
    ascendant: 82.5,
    midheaven: 350.2,
    armc: 345.6,
    vertex: 175.3,
  },
  aspects: [
    {
      planet1: 'Sun',
      planet2: 'Moon',
      aspect: 'Square',
      angle: 90,
      orb: 1.2,
      is_major: true,
      is_applying: false,
    },
  ],
  nakshatras: {},
};

describe('ChartCalculator', () => {
  const renderComponent = (initialState = {}) => {
    const store = createMockStore(initialState);
    return render(
      <Provider store={store}>
        <ChartCalculator />
      </Provider>
    );
  };

  it('renders without crashing', () => {
    const { container } = renderComponent();
    expect(container).toBeInTheDocument();
  });

  it('displays form fields', () => {
    renderComponent();
    expect(screen.getByLabelText('Date')).toBeInTheDocument();
    expect(screen.getByLabelText('Time')).toBeInTheDocument();
    expect(screen.getByLabelText('Latitude')).toBeInTheDocument();
    expect(screen.getByLabelText('Longitude')).toBeInTheDocument();
    expect(screen.getByLabelText('Altitude (meters)')).toBeInTheDocument();
  });

  it('displays planetary positions correctly', () => {
    renderComponent({
      chart: {
        data: mockChart,
        loading: false,
        error: null,
      },
    });

    // Check for planet names
    expect(screen.getByText('Sun')).toBeInTheDocument();
    expect(screen.getByText('Moon')).toBeInTheDocument();

    // Check for positions using regex to match formatted values
    expect(screen.getByText(/260°/)).toBeInTheDocument();
    expect(screen.getByText(/45°/)).toBeInTheDocument();
  });

  it('displays major aspects', () => {
    renderComponent({
      chart: {
        data: mockChart,
        loading: false,
        error: null,
      },
    });

    expect(screen.getByText('Sun - Moon')).toBeInTheDocument();
    expect(screen.getByText(/Square/)).toBeInTheDocument();
  });

  it('handles loading state', () => {
    renderComponent({
      chart: {
        data: null,
        loading: true,
        error: null,
      },
    });
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('handles error state', () => {
    const errorMessage = 'Failed to calculate chart';
    renderComponent({
      chart: {
        data: null,
        loading: false,
        error: errorMessage,
      },
    });
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });
});
