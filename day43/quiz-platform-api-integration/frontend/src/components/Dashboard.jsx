/**
 * Main dashboard component
 */
import React from 'react'
import { Link } from 'react-router-dom'
import { QuizGenerator } from './quiz/QuizGenerator'
import { BookOpen, Zap, Shield, BarChart3 } from 'lucide-react'

export function Dashboard() {
  const features = [
    {
      icon: <Zap className="w-8 h-8" />,
      title: "Smart Retry Logic",
      description: "Automatic retry with exponential backoff for failed requests"
    },
    {
      icon: <Shield className="w-8 h-8" />,
      title: "Error Boundaries",
      description: "Graceful error handling with fallback responses"
    },
    {
      icon: <BarChart3 className="w-8 h-8" />,
      title: "Performance Caching",
      description: "Intelligent caching layer for optimal performance"
    },
    {
      icon: <BookOpen className="w-8 h-8" />,
      title: "AI Integration",
      description: "Seamless integration with Gemini AI for content generation"
    }
  ]
  
  return (
    <div className="dashboard">
      <div className="hero-section">
        <h1 className="hero-title">
          API Integration Layer Demo
        </h1>
        <p className="hero-subtitle">
          Experience production-ready API integration with intelligent error handling,
          caching, and retry mechanisms.
        </p>
      </div>
      
      <div className="features-grid">
        {features.map((feature, index) => (
          <div key={index} className="feature-card">
            <div className="feature-icon">
              {feature.icon}
            </div>
            <h3 className="feature-title">{feature.title}</h3>
            <p className="feature-description">{feature.description}</p>
          </div>
        ))}
      </div>
      
      <div className="demo-section">
        <QuizGenerator />
      </div>
    </div>
  )
}
