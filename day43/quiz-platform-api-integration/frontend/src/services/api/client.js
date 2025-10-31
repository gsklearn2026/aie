/**
 * API Client with retry logic, error handling, and caching
 */
import axios from 'axios'
import { CacheService } from '../cache/CacheService'

class APIClient {
  constructor(baseURL = 'http://localhost:8000/api/v1') {
    this.baseURL = baseURL
    this.cache = new CacheService()
    
    // Create axios instance
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })
    
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add request ID for tracking
        config.headers['X-Request-ID'] = this.generateRequestId()
        
        console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`)
        return config
      },
      (error) => {
        console.error('❌ Request Error:', error)
        return Promise.reject(error)
      }
    )
    
    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        console.log(`✅ API Response: ${response.status} ${response.config.url}`)
        return response
      },
      (error) => {
        console.error(`❌ API Error: ${error.response?.status} ${error.config?.url}`)
        return this.handleError(error)
      }
    )
  }
  
  generateRequestId() {
    return Math.random().toString(36).substring(2) + Date.now().toString(36)
  }
  
  async handleError(error) {
    const { response, config } = error
    
    // Network error or timeout
    if (!response) {
      console.error('Network error or timeout:', error.message)
      throw new Error('Network error. Please check your connection.')
    }
    
    // Server errors (5xx)
    if (response.status >= 500) {
      console.error('Server error:', response.status, response.data)
      
      // Implement retry logic for server errors
      if (!config._retryCount) {
        config._retryCount = 0
      }
      
      if (config._retryCount < 3) {
        config._retryCount++
        const delay = Math.pow(2, config._retryCount) * 1000 // Exponential backoff
        
        console.log(`🔄 Retrying request in ${delay}ms (attempt ${config._retryCount})`)
        
        await this.delay(delay)
        return this.client(config)
      }
      
      throw new Error('Server temporarily unavailable. Please try again later.')
    }
    
    // Client errors (4xx)
    if (response.status >= 400) {
      const errorMessage = response.data?.error || response.data?.detail || 'Request failed'
      throw new Error(errorMessage)
    }
    
    throw error
  }
  
  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
  
  // Cache-aware GET method
  async get(url, options = {}) {
    const { useCache = true, cacheTime = 300000 } = options // 5 minutes default
    const cacheKey = `api:${url}:${JSON.stringify(options.params || {})}`
    
    // Check cache first
    if (useCache) {
      const cachedData = await this.cache.get(cacheKey)
      if (cachedData) {
        console.log(`📦 Cache hit: ${url}`)
        return { data: cachedData }
      }
    }
    
    try {
      const response = await this.client.get(url, options)
      
      // Cache successful response
      if (useCache && response.data) {
        await this.cache.set(cacheKey, response.data, cacheTime)
      }
      
      return response
    } catch (error) {
      // Fallback to cache if request fails
      if (useCache) {
        const cachedData = await this.cache.get(cacheKey)
        if (cachedData) {
          console.log(`📦 Fallback to cache: ${url}`)
          return { data: cachedData }
        }
      }
      throw error
    }
  }
  
  async post(url, data, options = {}) {
    return this.client.post(url, data, options)
  }
  
  async put(url, data, options = {}) {
    return this.client.put(url, data, options)
  }
  
  async delete(url, options = {}) {
    return this.client.delete(url, options)
  }
  
  // Health check with circuit breaker pattern
  async healthCheck() {
    try {
      const response = await this.client.get('/integration/health', { timeout: 5000 })
      return response.data
    } catch (error) {
      throw new Error('API health check failed')
    }
  }
}

export const apiClient = new APIClient()
export default APIClient
