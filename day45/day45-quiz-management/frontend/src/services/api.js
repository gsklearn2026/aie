import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authService = {
  login: async (email, password) => {
    const response = await api.post('/api/auth/login', { email, password })
    return response.data
  },
  register: async (email, password) => {
    const response = await api.post('/api/auth/register', { email, password })
    return response.data
  }
}

export const quizService = {
  getQuizzes: async (params = {}) => {
    const response = await api.get('/api/quiz/', { params })
    return response.data
  },
  getQuiz: async (id) => {
    const response = await api.get(`/api/quiz/${id}`)
    return response.data
  },
  createQuiz: async (quiz) => {
    const response = await api.post('/api/quiz/', quiz)
    return response.data
  },
  updateQuiz: async (id, quiz) => {
    const response = await api.put(`/api/quiz/${id}`, quiz)
    return response.data
  },
  deleteQuiz: async (id) => {
    const response = await api.delete(`/api/quiz/${id}`)
    return response.data
  },
  bulkDelete: async (ids) => {
    const response = await api.post('/api/quiz/bulk-delete', ids)
    return response.data
  }
}

export default api
