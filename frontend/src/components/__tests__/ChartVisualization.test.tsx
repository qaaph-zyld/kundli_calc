import React from 'react';
import { render } from '@testing-library/react';
import ChartVisualization from '../ChartVisualization';

// Create mock selection chain
const createMockSelection = () => {
  const selection = {
    select: jest.fn(),
    selectAll: jest.fn(),
    append: jest.fn(),
    attr: jest.fn(),
    style: jest.fn(),
    data: jest.fn(),
    enter: jest.fn(),
    exit: jest.fn(),
    join: jest.fn(),
    text: jest.fn(),
    remove: jest.fn(),
  };

  // Set up method chaining
  Object.keys(selection).forEach(key => {
    selection[key].mockReturnValue(selection);
  });

  return selection;
};

// Create mock selection instance
const mockSelection = createMockSelection();

// Mock SVG element
const mockSvgElement = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
mockSvgElement.setAttribute('class', 'w-full h-auto');

// Mock d3 module
jest.mock('d3', () => ({
  select: jest.fn(() => mockSelection),
  arc: jest.fn(() => ({
    innerRadius: jest.fn().mockReturnThis(),
    outerRadius: jest.fn().mockReturnThis(),
    startAngle: jest.fn().mockReturnThis(),
    endAngle: jest.fn().mockReturnThis(),
  })),
  pie: jest.fn(() => ({
    value: jest.fn().mockReturnThis(),
    sort: jest.fn().mockReturnThis(),
  })),
  scaleLinear: jest.fn(() => ({
    domain: jest.fn().mockReturnThis(),
    range: jest.fn().mockReturnThis(),
  })),
}));

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

describe('ChartVisualization', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Mock the ref to return our SVG element
    jest.spyOn(React, 'useRef').mockReturnValue({ current: mockSvgElement });
  });

  it('renders without crashing', () => {
    const { container } = render(<ChartVisualization chart={mockChart} />);
    expect(container).toBeInTheDocument();
  });

  it('initializes D3 visualization', () => {
    render(<ChartVisualization chart={mockChart} />);
    expect(mockSelection.attr).toHaveBeenCalledWith('width', expect.any(Number));
    expect(mockSelection.attr).toHaveBeenCalledWith('height', expect.any(Number));
  });

  it('cleans up previous content before drawing', () => {
    render(<ChartVisualization chart={mockChart} />);
    // The component should clean up any existing content
    expect(mockSelection.selectAll).toHaveBeenCalled();
    expect(mockSelection.remove).toHaveBeenCalled();
  });

  it('draws chart elements', () => {
    render(<ChartVisualization chart={mockChart} />);
    
    // Verify that D3 methods are called to create chart elements
    expect(mockSelection.append).toHaveBeenCalled();
    expect(mockSelection.attr).toHaveBeenCalled();
    expect(mockSelection.style).toHaveBeenCalled();
  });

  it('handles empty chart data', () => {
    const emptyChart = {
      ...mockChart,
      planetary_positions: {},
      aspects: [],
    };
    const { container } = render(<ChartVisualization chart={emptyChart} />);
    expect(container).toBeInTheDocument();
  });
});
