import React from 'react';
import { Provider } from 'react-redux';
import { store } from './store/store';
import ChartCalculator from './pages/ChartCalculator';

const App: React.FC = () => {
  return (
    <Provider store={store}>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
            <h1 className="text-3xl font-bold text-gray-900">
              South Indian Kundli Calculator
            </h1>
          </div>
        </header>
        <main>
          <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <ChartCalculator />
          </div>
        </main>
      </div>
    </Provider>
  );
};

export default App;
