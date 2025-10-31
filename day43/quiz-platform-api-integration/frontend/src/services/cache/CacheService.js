/**
 * Frontend cache service with localStorage fallback
 */
class CacheService {
  constructor() {
    this.memoryCache = new Map()
    this.defaultTTL = 300000 // 5 minutes
  }
  
  // Generate cache key
  _generateKey(key) {
    return `quiz_app_cache:${key}`
  }
  
  // Check if item is expired
  _isExpired(item) {
    return item.expiry && Date.now() > item.expiry
  }
  
  // Get from cache
  async get(key) {
    const cacheKey = this._generateKey(key)
    
    // Try memory cache first
    if (this.memoryCache.has(cacheKey)) {
      const item = this.memoryCache.get(cacheKey)
      if (!this._isExpired(item)) {
        return item.data
      }
      this.memoryCache.delete(cacheKey)
    }
    
    // Try localStorage
    try {
      const stored = localStorage.getItem(cacheKey)
      if (stored) {
        const item = JSON.parse(stored)
        if (!this._isExpired(item)) {
          // Also store in memory for faster access
          this.memoryCache.set(cacheKey, item)
          return item.data
        }
        localStorage.removeItem(cacheKey)
      }
    } catch (error) {
      console.warn('Cache read error:', error)
    }
    
    return null
  }
  
  // Set in cache
  async set(key, data, ttl = this.defaultTTL) {
    const cacheKey = this._generateKey(key)
    const item = {
      data,
      expiry: ttl ? Date.now() + ttl : null,
      timestamp: Date.now()
    }
    
    // Store in memory
    this.memoryCache.set(cacheKey, item)
    
    // Store in localStorage
    try {
      localStorage.setItem(cacheKey, JSON.stringify(item))
    } catch (error) {
      console.warn('Cache write error:', error)
      // If localStorage is full, clear old items
      this._cleanupLocalStorage()
      try {
        localStorage.setItem(cacheKey, JSON.stringify(item))
      } catch (secondError) {
        console.warn('Cache write failed after cleanup:', secondError)
      }
    }
  }
  
  // Delete from cache
  async delete(key) {
    const cacheKey = this._generateKey(key)
    this.memoryCache.delete(cacheKey)
    
    try {
      localStorage.removeItem(cacheKey)
    } catch (error) {
      console.warn('Cache delete error:', error)
    }
  }
  
  // Clear all cache
  async clear() {
    this.memoryCache.clear()
    
    try {
      const keys = Object.keys(localStorage)
      keys.forEach(key => {
        if (key.startsWith('quiz_app_cache:')) {
          localStorage.removeItem(key)
        }
      })
    } catch (error) {
      console.warn('Cache clear error:', error)
    }
  }
  
  // Cleanup old items from localStorage
  _cleanupLocalStorage() {
    try {
      const keys = Object.keys(localStorage)
      const cacheKeys = keys.filter(key => key.startsWith('quiz_app_cache:'))
      
      // Remove expired items
      cacheKeys.forEach(key => {
        try {
          const item = JSON.parse(localStorage.getItem(key))
          if (this._isExpired(item)) {
            localStorage.removeItem(key)
          }
        } catch (error) {
          // Remove corrupted items
          localStorage.removeItem(key)
        }
      })
    } catch (error) {
      console.warn('Cache cleanup error:', error)
    }
  }
  
  // Get cache statistics
  getStats() {
    return {
      memoryItems: this.memoryCache.size,
      localStorageItems: Object.keys(localStorage).filter(
        key => key.startsWith('quiz_app_cache:')
      ).length
    }
  }
}

export { CacheService }
