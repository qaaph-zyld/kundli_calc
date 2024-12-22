import '@testing-library/jest-dom';
import { TextEncoder, TextDecoder } from 'util';

// Mock browser APIs that aren't available in Jest
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  observe() { return null; }
  unobserve() { return null; }
  disconnect() { return null; }
};

// Mock D3
const createMockSelection = () => ({
  attr: jest.fn().mockReturnThis(),
  style: jest.fn().mockReturnThis(),
  text: jest.fn().mockReturnThis(),
  append: jest.fn().mockImplementation(() => createMockSelection()),
  remove: jest.fn().mockReturnThis(),
  selectAll: jest.fn().mockImplementation(() => createMockSelection()),
  data: jest.fn().mockReturnThis(),
  enter: jest.fn().mockReturnThis(),
  exit: jest.fn().mockReturnThis(),
});

jest.mock('d3', () => ({
  select: jest.fn().mockImplementation(() => createMockSelection()),
  selectAll: jest.fn().mockImplementation(() => createMockSelection()),
  arc: jest.fn(() => ({
    innerRadius: jest.fn().mockReturnThis(),
    outerRadius: jest.fn().mockReturnThis(),
    startAngle: jest.fn().mockReturnThis(),
    endAngle: jest.fn().mockReturnThis(),
  })),
}));
