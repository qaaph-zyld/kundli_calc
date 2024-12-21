import React from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../store/store';
import ChartForm from '../components/ChartForm';
import ChartVisualization from '../components/ChartVisualization';

const ChartCalculator: React.FC = () => {
  const { chart, loading, error } = useSelector((state: RootState) => state.chart);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-6">
            Birth Details
          </h2>
          <ChartForm />
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-6">
            Birth Chart
          </h2>
          {loading && (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
          )}
          {error && (
            <div className="text-red-600 text-center p-4">
              {error}
            </div>
          )}
          {chart && <ChartVisualization chart={chart} />}
        </div>

        {chart && (
          <div className="md:col-span-2 bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-6">
              Planetary Positions and Aspects
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-md font-medium text-gray-700 mb-4">
                  Planetary Positions
                </h3>
                <div className="space-y-2">
                  {Object.entries(chart.planetary_positions).map(([planet, position]) => (
                    <div key={planet} className="flex justify-between">
                      <span className="font-medium">{planet}</span>
                      <span>{Math.floor(position.longitude)}°{Math.floor((position.longitude % 1) * 60)}'</span>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <h3 className="text-md font-medium text-gray-700 mb-4">
                  Major Aspects
                </h3>
                <div className="space-y-2">
                  {chart.aspects
                    .filter(aspect => aspect.is_major)
                    .map((aspect, index) => (
                      <div key={index} className="flex justify-between">
                        <span>{aspect.planet1} - {aspect.planet2}</span>
                        <span>{aspect.aspect} ({aspect.orb.toFixed(1)}°)</span>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChartCalculator;
