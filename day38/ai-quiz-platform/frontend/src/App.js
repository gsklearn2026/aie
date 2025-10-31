/**
 * AI Quiz Platform - Frontend Application
 * Day 38: Docker Compose Multi-Service Setup
 */

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';

// Styled Components
const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  font-family: 'Arial', sans-serif;
`;

const Header = styled.header`
  text-align: center;
  color: white;
  margin-bottom: 30px;
`;

const Title = styled.h1`
  font-size: 2.5rem;
  margin: 0;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
`;

const Subtitle = styled.p`
  font-size: 1.2rem;
  margin: 10px 0;
  opacity: 0.9;
`;

const StatusBadge = styled.div`
  display: inline-block;
  padding: 5px 15px;
  background: ${props => props.$healthy ? '#10b981' : '#ef4444'};
  color: white;
  border-radius: 20px;
  font-size: 0.9rem;
  margin: 10px;
`;

const MainContent = styled.main`
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const Card = styled.div`
  background: white;
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;
  
  &:hover {
    transform: translateY(-5px);
  }
`;

const CardTitle = styled.h2`
  color: #333;
  margin-bottom: 20px;
  font-size: 1.5rem;
`;

const QuizCard = styled(Card)`
  cursor: pointer;
  border: 2px solid transparent;
  
  &:hover {
    border-color: #667eea;
  }
`;

const Button = styled.button`
  background: ${props => props.$primary ? '#667eea' : '#f3f4f6'};
  color: ${props => props.$primary ? 'white' : '#333'};
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  margin: 5px;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const QuestionContainer = styled.div`
  background: #f8fafc;
  padding: 20px;
  border-radius: 10px;
  margin: 15px 0;
`;

const OptionButton = styled.button`
  display: block;
  width: 100%;
  text-align: left;
  padding: 12px;
  margin: 8px 0;
  border: 2px solid #e5e7eb;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #667eea;
    background: #f0f4ff;
  }
  
  &.selected {
    border-color: #667eea;
    background: #e0e7ff;
  }
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
  margin: 20px 0;
`;

const StatItem = styled.div`
  text-align: center;
  padding: 15px;
  background: #f8fafc;
  border-radius: 10px;
`;

const StatNumber = styled.div`
  font-size: 2rem;
  font-weight: bold;
  color: #667eea;
`;

const StatLabel = styled.div`
  font-size: 0.9rem;
  color: #6b7280;
  margin-top: 5px;
`;

// API Service
const apiService = {
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  
  async checkHealth() {
    const response = await axios.get(`${this.baseURL}/health`);
    return response.data;
  },
  
  async getQuizzes() {
    const response = await axios.get(`${this.baseURL}/api/quizzes`);
    return response.data;
  },
  
  async generateQuestion(topic, difficulty) {
    const response = await axios.post(`${this.baseURL}/api/generate-question`, {
      topic,
      difficulty
    });
    return response.data;
  },
  
  async submitAnswer(answer, correct_answer, question_id) {
    const response = await axios.post(`${this.baseURL}/api/submit-answer`, {
      answer,
      correct_answer,
      question_id
    });
    return response.data;
  },
  
  async getStats() {
    const response = await axios.get(`${this.baseURL}/api/stats`);
    return response.data;
  }
};

function App() {
  const [health, setHealth] = useState(null);
  const [quizzes, setQuizzes] = useState([]);
  const [stats, setStats] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [showResult, setShowResult] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      // Check system health
      const healthData = await apiService.checkHealth();
      setHealth(healthData);
      
      // Load quizzes
      const quizzesData = await apiService.getQuizzes();
      setQuizzes(quizzesData);
      
      // Load stats
      const statsData = await apiService.getStats();
      setStats(statsData);
      
    } catch (error) {
      console.error('Failed to initialize app:', error);
      setHealth({ status: 'unhealthy', error: error.message });
    }
  };

  const generateQuestion = async (topic = 'Docker Containers', difficulty = 'medium') => {
    setLoading(true);
    try {
      const question = await apiService.generateQuestion(topic, difficulty);
      setCurrentQuestion(question);
      setSelectedAnswer('');
      setShowResult(false);
      setResult(null);
    } catch (error) {
      console.error('Failed to generate question:', error);
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!selectedAnswer || !currentQuestion) return;
    
    try {
      const response = await apiService.submitAnswer(
        selectedAnswer,
        currentQuestion.correct_answer,
        'demo_question_id'
      );
      setResult(response);
      setShowResult(true);
    } catch (error) {
      console.error('Failed to submit answer:', error);
    }
  };

  return (
    <AppContainer>
      <Header>
        <Title>🤖 AI Quiz Platform</Title>
        <Subtitle>Day 38: Docker Compose Multi-Service Architecture</Subtitle>
        {health && (
          <StatusBadge $healthy={health.status === 'healthy'}>
            System Status: {health.status === 'healthy' ? '🟢 All Services Running' : '🔴 Service Issues'}
          </StatusBadge>
        )}
      </Header>

      <MainContent>
        {/* Interactive Quiz Section */}
        <Card>
          <CardTitle>🎯 Interactive AI Quiz</CardTitle>
          
          {!currentQuestion && (
            <div>
              <p>Test your knowledge with AI-generated questions!</p>
              <Button 
                $primary 
                onClick={() => generateQuestion('Docker Containers', 'medium')}
                disabled={loading}
              >
                {loading ? 'Generating...' : 'Start Docker Quiz'}
              </Button>
              <Button 
                onClick={() => generateQuestion('Microservices', 'intermediate')}
                disabled={loading}
              >
                Microservices Quiz
              </Button>
            </div>
          )}

          {currentQuestion && (
            <QuestionContainer>
              <h3>{currentQuestion.question}</h3>
              
              {currentQuestion.options?.map((option, index) => (
                <OptionButton
                  key={index}
                  className={selectedAnswer === option ? 'selected' : ''}
                  onClick={() => setSelectedAnswer(option)}
                >
                  {option}
                </OptionButton>
              ))}
              
              <div style={{ marginTop: '15px' }}>
                <Button 
                  $primary 
                  onClick={submitAnswer}
                  disabled={!selectedAnswer}
                >
                  Submit Answer
                </Button>
                <Button onClick={() => setCurrentQuestion(null)}>
                  New Question
                </Button>
              </div>

              {showResult && result && (
                <div style={{ 
                  marginTop: '20px', 
                  padding: '15px', 
                  background: result.is_correct ? '#dcfce7' : '#fef2f2',
                  borderRadius: '8px',
                  border: `2px solid ${result.is_correct ? '#10b981' : '#ef4444'}`
                }}>
                  <h4>{result.is_correct ? '✅ Correct!' : '❌ Incorrect'}</h4>
                  <p><strong>Correct Answer:</strong> {result.correct_answer}</p>
                  {currentQuestion.explanation && (
                    <p><strong>Explanation:</strong> {currentQuestion.explanation}</p>
                  )}
                </div>
              )}
            </QuestionContainer>
          )}
        </Card>

        {/* Available Quizzes */}
        <Card>
          <CardTitle>📚 Available Quizzes</CardTitle>
          
          {quizzes.length === 0 ? (
            <p>Loading quizzes from database...</p>
          ) : (
            quizzes.map(quiz => (
              <QuizCard key={quiz.id} onClick={() => generateQuestion(quiz.title, quiz.difficulty)}>
                <h3>{quiz.title}</h3>
                <p>{quiz.description}</p>
                <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                  <span style={{ 
                    padding: '3px 8px', 
                    background: '#e0e7ff', 
                    borderRadius: '15px',
                    fontSize: '0.8rem'
                  }}>
                    {quiz.category}
                  </span>
                  <span style={{ 
                    padding: '3px 8px', 
                    background: '#fef3c7', 
                    borderRadius: '15px',
                    fontSize: '0.8rem'
                  }}>
                    {quiz.difficulty}
                  </span>
                </div>
              </QuizCard>
            ))
          )}
        </Card>

        {/* System Statistics */}
        <Card>
          <CardTitle>📊 Platform Statistics</CardTitle>
          
          {stats ? (
            <StatsGrid>
              <StatItem>
                <StatNumber>{stats.total_quizzes}</StatNumber>
                <StatLabel>Total Quizzes</StatLabel>
              </StatItem>
              <StatItem>
                <StatNumber>{stats.total_users}</StatNumber>
                <StatLabel>Active Users</StatLabel>
              </StatItem>
              <StatItem>
                <StatNumber>{stats.total_questions}</StatNumber>
                <StatLabel>Questions</StatLabel>
              </StatItem>
              <StatItem>
                <StatNumber>5</StatNumber>
                <StatLabel>Services</StatLabel>
              </StatItem>
            </StatsGrid>
          ) : (
            <p>Loading statistics...</p>
          )}
          
          <div style={{ marginTop: '20px', padding: '15px', background: '#f8fafc', borderRadius: '8px' }}>
            <h4>🐳 Docker Services Status</h4>
            {health?.services && (
              <div>
                <p>Database: <span style={{ color: health.services.database === 'connected' ? '#10b981' : '#ef4444' }}>
                  {health.services.database}
                </span></p>
                <p>Redis Cache: <span style={{ color: health.services.redis === 'connected' ? '#10b981' : '#ef4444' }}>
                  {health.services.redis}
                </span></p>
                <p>AI Service: <span style={{ color: health.services.gemini === 'configured' ? '#10b981' : '#f59e0b' }}>
                  {health.services.gemini}
                </span></p>
              </div>
            )}
          </div>
        </Card>

        {/* Service Architecture */}
        <Card>
          <CardTitle>🏗️ Architecture Overview</CardTitle>
          
          <div style={{ textAlign: 'center' }}>
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(3, 1fr)', 
              gap: '15px',
              margin: '20px 0' 
            }}>
              <div style={{ padding: '15px', background: '#e0f2fe', borderRadius: '10px' }}>
                <strong>Frontend</strong>
                <br />React + Docker
              </div>
              <div style={{ padding: '15px', background: '#f0fdf4', borderRadius: '10px' }}>
                <strong>Backend</strong>
                <br />Python + Flask
              </div>
              <div style={{ padding: '15px', background: '#fef7cd', borderRadius: '10px' }}>
                <strong>Database</strong>
                <br />PostgreSQL
              </div>
              <div style={{ padding: '15px', background: '#fce7f3', borderRadius: '10px' }}>
                <strong>Cache</strong>
                <br />Redis
              </div>
              <div style={{ padding: '15px', background: '#f3e8ff', borderRadius: '10px' }}>
                <strong>Proxy</strong>
                <br />Nginx
              </div>
              <div style={{ padding: '15px', background: '#ecfdf5', borderRadius: '10px' }}>
                <strong>AI</strong>
                <br />Gemini API
              </div>
            </div>
            
            <p style={{ fontSize: '0.9rem', color: '#6b7280' }}>
              All services orchestrated with Docker Compose
            </p>
          </div>
        </Card>
      </MainContent>
    </AppContainer>
  );
}

export default App;
