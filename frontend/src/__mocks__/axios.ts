const mockAxios = {
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn(),
  create: jest.fn(() => mockAxios),
  defaults: {
    baseURL: '',
    headers: {
      common: {},
    },
  },
};

export default mockAxios;
