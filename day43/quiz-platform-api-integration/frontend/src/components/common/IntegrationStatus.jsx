/**
 * Integration status component
 */
import React, { useState, useEffect } from 'react'
import { Activity, Wifi, WifiOff } from 'lucide-react'
import { QuizService } from '../../services/api/quizService'

export function IntegrationStatus() {
  const [status, setStatus] = useState('checking')
  const [metrics, setMetrics] = useState(null)
  
  useEffect(() => {
    checkStatus()
    const interval = setInterval(checkStatus, 30000) // Check every 30 seconds
    
    return () => clearInterval(interval)
  }, [])
  
  const checkStatus = async () => {
    try {
      const [healthData, metricsData] = await Promise.all([
        QuizService.getHealthStatus(),
        QuizService.getMetrics()
      ])
      
      if (healthData.success && metricsData.success) {
        setStatus('healthy')
        setMetrics(metricsData.data)
      } else {
        setStatus('degraded')
      }
    } catch (error) {
      setStatus('down')
      console.error('Status check failed:', error)
    }
  }
  
  const getStatusColor = () => {
    switch (status) {
      case 'healthy': return 'text-green-500'
      case 'degraded': return 'text-yellow-500'
      case 'down': return 'text-red-500'
      default: return 'text-gray-500'
    }
  }
  
  const getStatusIcon = () => {
    switch (status) {
      case 'healthy':
      case 'degraded':
        return <Wifi className="w-4 h-4" />
      case 'down':
        return <WifiOff className="w-4 h-4" />
      default:
        return <Activity className="w-4 h-4 animate-pulse" />
    }
  }
  
  return (
    <div className="integration-status">
      <div className={`status-indicator ${getStatusColor()}`}>
        {getStatusIcon()}
        <span className="ml-2 text-sm">
          API: {status === 'checking' ? 'Checking...' : status}
        </span>
      </div>
      
      {metrics && (
        <div className="status-details text-xs text-gray-600 mt-1">
          Cache: {metrics.cache_type} | 
          Version: {metrics.api_version}
        </div>
      )}
    </div>
  )
}
