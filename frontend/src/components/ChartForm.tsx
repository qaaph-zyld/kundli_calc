import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '../store/store';
import { calculateChart } from '../store/chartSlice';

const ChartForm: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const [formData, setFormData] = useState({
    date: '',
    time: '',
    latitude: '',
    longitude: '',
    altitude: '0',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const dateTime = new Date(`${formData.date}T${formData.time}`).toISOString();

    dispatch(calculateChart({
      date_time: dateTime,
      latitude: parseFloat(formData.latitude),
      longitude: parseFloat(formData.longitude),
      altitude: parseFloat(formData.altitude),
    }));
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label htmlFor="date" className="block text-sm font-medium text-gray-700">
          Date
        </label>
        <input
          type="date"
          name="date"
          id="date"
          required
          value={formData.date}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
        />
      </div>

      <div>
        <label htmlFor="time" className="block text-sm font-medium text-gray-700">
          Time
        </label>
        <input
          type="time"
          name="time"
          id="time"
          required
          value={formData.time}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
        />
      </div>

      <div>
        <label htmlFor="latitude" className="block text-sm font-medium text-gray-700">
          Latitude
        </label>
        <input
          type="number"
          step="any"
          name="latitude"
          id="latitude"
          required
          value={formData.latitude}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          placeholder="e.g., 13.0827"
        />
      </div>

      <div>
        <label htmlFor="longitude" className="block text-sm font-medium text-gray-700">
          Longitude
        </label>
        <input
          type="number"
          step="any"
          name="longitude"
          id="longitude"
          required
          value={formData.longitude}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          placeholder="e.g., 80.2707"
        />
      </div>

      <div>
        <label htmlFor="altitude" className="block text-sm font-medium text-gray-700">
          Altitude (meters)
        </label>
        <input
          type="number"
          step="any"
          name="altitude"
          id="altitude"
          value={formData.altitude}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          placeholder="e.g., 0"
        />
      </div>

      <button
        type="submit"
        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        Calculate Chart
      </button>
    </form>
  );
};

export default ChartForm;
