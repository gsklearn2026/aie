/**
 * API Client tests
 */
import { describe, it, expect, vi } from 'vitest'
import { APIClient } from '../src/services/api/client'

// Mock axios
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() }
      }
    }))
  }
}))

describe('APIClient', () => {
  it('should create client with correct baseURL', () => {
    const client = new APIClient('http://test.com')
    expect(client.baseURL).toBe('http://test.com')
  })
  
  it('should generate unique request IDs', () => {
    const client = new APIClient()
    const id1 = client.generateRequestId()
    const id2 = client.generateRequestId()
    
    expect(id1).not.toBe(id2)
    expect(typeof id1).toBe('string')
    expect(typeof id2).toBe('string')
  })
  
  it('should handle delay correctly', async () => {
    const client = new APIClient()
    const start = Date.now()
    await client.delay(100)
    const end = Date.now()
    
    expect(end - start).toBeGreaterThanOrEqual(100)
  })
})
