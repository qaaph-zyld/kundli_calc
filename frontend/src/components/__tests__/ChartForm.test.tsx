import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import ChartForm from '../ChartForm';
import chartReducer, { calculateChart } from '../../store/chartSlice';

// Mock Redux store
const createMockStore = () => {
  return configureStore({
    reducer: {
      chart: chartReducer,
    },
  });
};

describe('ChartForm', () => {
  const mockStore = createMockStore();
  const renderComponent = () =>
    render(
      <Provider store={mockStore}>
        <ChartForm />
      </Provider>
    );

  beforeEach(() => {
    jest.clearAllMocks();
    // Mock dispatch
    jest.spyOn(mockStore, 'dispatch');
  });

  it('renders all form fields', () => {
    renderComponent();
    
    expect(screen.getByLabelText(/date/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/time/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/latitude/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/longitude/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/altitude/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /calculate chart/i })).toBeInTheDocument();
  });

  it('updates form fields when user types', () => {
    renderComponent();
    
    const dateInput = screen.getByLabelText(/date/i);
    const timeInput = screen.getByLabelText(/time/i);
    const latitudeInput = screen.getByLabelText(/latitude/i);
    const longitudeInput = screen.getByLabelText(/longitude/i);
    const altitudeInput = screen.getByLabelText(/altitude/i);

    fireEvent.change(dateInput, { target: { value: '2024-01-01' } });
    fireEvent.change(timeInput, { target: { value: '12:00' } });
    fireEvent.change(latitudeInput, { target: { value: '13.0827' } });
    fireEvent.change(longitudeInput, { target: { value: '80.2707' } });
    fireEvent.change(altitudeInput, { target: { value: '100' } });

    expect(dateInput).toHaveValue('2024-01-01');
    expect(timeInput).toHaveValue('12:00');
    expect(latitudeInput).toHaveValue(13.0827);
    expect(longitudeInput).toHaveValue(80.2707);
    expect(altitudeInput).toHaveValue(100);
  });

  it('dispatches calculateChart action on form submission', () => {
    renderComponent();
    
    // Fill out the form
    fireEvent.change(screen.getByLabelText(/date/i), { target: { value: '2024-01-01' } });
    fireEvent.change(screen.getByLabelText(/time/i), { target: { value: '12:00' } });
    fireEvent.change(screen.getByLabelText(/latitude/i), { target: { value: '13.0827' } });
    fireEvent.change(screen.getByLabelText(/longitude/i), { target: { value: '80.2707' } });
    fireEvent.change(screen.getByLabelText(/altitude/i), { target: { value: '100' } });

    // Submit the form
    fireEvent.submit(screen.getByRole('button', { name: /calculate chart/i }));

    // Check if dispatch was called with correct action
    expect(mockStore.dispatch).toHaveBeenCalledWith(
      expect.any(Function) // calculateChart returns a thunk
    );
  });

  it('requires all fields except altitude', () => {
    renderComponent();
    
    const dateInput = screen.getByLabelText(/date/i);
    const timeInput = screen.getByLabelText(/time/i);
    const latitudeInput = screen.getByLabelText(/latitude/i);
    const longitudeInput = screen.getByLabelText(/longitude/i);
    const altitudeInput = screen.getByLabelText(/altitude/i);

    expect(dateInput).toBeRequired();
    expect(timeInput).toBeRequired();
    expect(latitudeInput).toBeRequired();
    expect(longitudeInput).toBeRequired();
    expect(altitudeInput).not.toBeRequired();
  });

  it('validates numeric input for coordinates', () => {
    renderComponent();
    
    const latitudeInput = screen.getByLabelText(/latitude/i);
    const longitudeInput = screen.getByLabelText(/longitude/i);

    expect(latitudeInput).toHaveAttribute('type', 'number');
    expect(latitudeInput).toHaveAttribute('step', 'any');
    expect(longitudeInput).toHaveAttribute('type', 'number');
    expect(longitudeInput).toHaveAttribute('step', 'any');
  });
});
