import axios from 'axios'

// Always use absolute URL - browser makes requests, not the Docker container
// In Docker, browser accesses frontend at localhost:3000 and backend at localhost:8000
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})
