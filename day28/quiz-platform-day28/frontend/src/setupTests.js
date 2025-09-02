// Mock axios for Jest tests
jest.mock('axios', () => ({
  get: jest.fn(() => Promise.resolve({ data: {} })),
  post: jest.fn(() => Promise.resolve({ data: {} })),
  put: jest.fn(() => Promise.resolve({ data: {} })),
  delete: jest.fn(() => Promise.resolve({ data: {} })),
  create: jest.fn(() => ({
    get: jest.fn(() => Promise.resolve({ data: {} })),
    post: jest.fn(() => Promise.resolve({ data: {} })),
    put: jest.fn(() => Promise.resolve({ data: {} })),
    delete: jest.fn(() => Promise.resolve({ data: {} })),
  })),
}));

// Mock CSS properties for DOM environment
Object.defineProperty(window, 'getComputedStyle', {
  value: () => ({
    getPropertyValue: () => '',
  }),
});

// Mock document.documentElement.style
Object.defineProperty(document, 'documentElement', {
  value: {
    style: {
      WebkitAnimation: '',
      MozAnimation: '',
      OAnimation: '',
      msAnimation: '',
      animation: '',
    },
  },
  writable: true,
});

// Mock window.URL for download functionality
Object.defineProperty(window, 'URL', {
  value: {
    createObjectURL: jest.fn(() => 'mock-url'),
    revokeObjectURL: jest.fn(),
  },
  writable: true,
});

// Mock document methods for download functionality
Object.defineProperty(document, 'createElement', {
  value: jest.fn(() => ({
    href: '',
    download: '',
    click: jest.fn(),
  })),
  writable: true,
});

Object.defineProperty(document.body, 'appendChild', {
  value: jest.fn(),
  writable: true,
});

Object.defineProperty(document.body, 'removeChild', {
  value: jest.fn(),
  writable: true,
});
