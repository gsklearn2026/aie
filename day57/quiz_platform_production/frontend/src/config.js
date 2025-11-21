const config = {
  development: {
    apiUrl: 'http://localhost:8000'
  },
  staging: {
    apiUrl: 'http://localhost:8001'
  },
  production: {
    apiUrl: ''  // Use relative URL - same origin (nginx on port 80)
  }
};

const environment = process.env.REACT_APP_ENV || 'development';
export default config[environment];
