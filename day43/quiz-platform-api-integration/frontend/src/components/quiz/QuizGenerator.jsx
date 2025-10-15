/**
 * Quiz generator component with API integration
 */
import React, { useState } from 'react'
import { useQuery, useMutation } from 'react-query'
import { QuizService } from '../../services/api/quizService'
import { Brain, CheckCircle, XCircle, Loader } from 'lucide-react'

export function QuizGenerator() {
  const [topic, setTopic] = useState('JavaScript')
  const [difficulty, setDifficulty] = useState('medium')
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [userAnswers, setUserAnswers] = useState({})
  const [showResults, setShowResults] = useState(false)
  
  // Generate quiz mutation
  const generateQuizMutation = useMutation(
    ({ topic, difficulty }) => QuizService.generateQuiz(topic, difficulty, 5),
    {
      onSuccess: (data) => {
        setCurrentQuestionIndex(0)
        setUserAnswers({})
        setShowResults(false)
      },
      onError: (error) => {
        console.error('Quiz generation failed:', error)
      }
    }
  )
  
  // Submit answer mutation
  const submitAnswerMutation = useMutation(
    ({ questionId, answer }) => QuizService.submitResponse(questionId, answer, 'user123'),
    {
      onSuccess: (data) => {
        console.log('Answer submitted:', data)
      }
    }
  )
  
  const handleGenerateQuiz = () => {
    generateQuizMutation.mutate({ topic, difficulty })
  }
  
  const handleAnswerSelect = (answer) => {
    const questions = generateQuizMutation.data || []
    const currentQuestion = questions[currentQuestionIndex]
    
    if (!currentQuestion) return
    
    // Update user answers
    const newAnswers = {
      ...userAnswers,
      [currentQuestion.id]: answer
    }
    setUserAnswers(newAnswers)
    
    // Submit answer to backend
    submitAnswerMutation.mutate({
      questionId: currentQuestion.id,
      answer: answer
    })
    
    // Move to next question or show results
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1)
    } else {
      setShowResults(true)
    }
  }
  
  const calculateScore = () => {
    const questions = generateQuizMutation.data || []
    let correct = 0
    
    questions.forEach(question => {
      if (userAnswers[question.id] === question.correct_answer) {
        correct++
      }
    })
    
    return { correct, total: questions.length }
  }
  
  const resetQuiz = () => {
    setCurrentQuestionIndex(0)
    setUserAnswers({})
    setShowResults(false)
  }
  
  const questions = generateQuizMutation.data || []
  const currentQuestion = questions[currentQuestionIndex]
  const { correct, total } = showResults ? calculateScore() : { correct: 0, total: 0 }
  
  return (
    <div className="quiz-generator">
      <div className="quiz-header">
        <h2 className="text-2xl font-bold mb-6 flex items-center">
          <Brain className="mr-2" />
          AI Quiz Generator
        </h2>
      </div>
      
      {!generateQuizMutation.data && (
        <div className="quiz-setup">
          <div className="setup-form">
            <div className="form-group">
              <label htmlFor="topic">Topic:</label>
              <select
                id="topic"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
              >
                <option value="JavaScript">JavaScript</option>
                <option value="Python">Python</option>
                <option value="React">React</option>
                <option value="Node.js">Node.js</option>
                <option value="Database">Database</option>
              </select>
            </div>
            
            <div className="form-group">
              <label htmlFor="difficulty">Difficulty:</label>
              <select
                id="difficulty"
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
              >
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>
            
            <button
              onClick={handleGenerateQuiz}
              disabled={generateQuizMutation.isLoading}
              className="generate-btn"
            >
              {generateQuizMutation.isLoading ? (
                <>
                  <Loader className="w-4 h-4 animate-spin mr-2" />
                  Generating...
                </>
              ) : (
                'Generate Quiz'
              )}
            </button>
          </div>
          
          {generateQuizMutation.error && (
            <div className="error-message">
              Error: {generateQuizMutation.error.message}
            </div>
          )}
        </div>
      )}
      
      {generateQuizMutation.data && !showResults && currentQuestion && (
        <div className="quiz-question">
          <div className="question-header">
            <span className="question-counter">
              Question {currentQuestionIndex + 1} of {questions.length}
            </span>
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }}
              />
            </div>
          </div>
          
          <h3 className="question-text">{currentQuestion.question}</h3>
          
          <div className="options">
            {currentQuestion.options.map((option, index) => {
              const optionLetter = String.fromCharCode(65 + index) // A, B, C, D
              return (
                <button
                  key={index}
                  onClick={() => handleAnswerSelect(optionLetter)}
                  className="option-btn"
                  disabled={submitAnswerMutation.isLoading}
                >
                  <span className="option-letter">{optionLetter}</span>
                  <span className="option-text">{option}</span>
                </button>
              )
            })}
          </div>
        </div>
      )}
      
      {showResults && (
        <div className="quiz-results">
          <h3 className="results-title">Quiz Complete!</h3>
          
          <div className="score-display">
            <div className="score-circle">
              <span className="score-text">
                {correct}/{total}
              </span>
              <span className="score-percentage">
                {Math.round((correct / total) * 100)}%
              </span>
            </div>
          </div>
          
          <div className="results-summary">
            {questions.map((question, index) => {
              const userAnswer = userAnswers[question.id]
              const isCorrect = userAnswer === question.correct_answer
              
              return (
                <div key={question.id} className="result-item">
                  <div className="result-header">
                    {isCorrect ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : (
                      <XCircle className="w-5 h-5 text-red-500" />
                    )}
                    <span className="question-number">Q{index + 1}</span>
                  </div>
                  <div className="result-details">
                    <p className="question-text">{question.question}</p>
                    <p className="answer-info">
                      Your answer: <span className={isCorrect ? 'correct' : 'incorrect'}>
                        {userAnswer}
                      </span>
                      {!isCorrect && (
                        <span className="correct-answer">
                          {' '}(Correct: {question.correct_answer})
                        </span>
                      )}
                    </p>
                  </div>
                </div>
              )
            })}
          </div>
          
          <div className="results-actions">
            <button onClick={resetQuiz} className="retry-btn">
              Try Again
            </button>
            <button 
              onClick={() => generateQuizMutation.reset()} 
              className="new-quiz-btn"
            >
              New Topic
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
