import { useState, useCallback } from 'react';
import { quizService } from '../services/quizService';

export const useQuiz = () => {
  const [quiz, setQuiz] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [answers, setAnswers] = useState([]);

  const generateQuiz = useCallback(async (topic, difficulty = 'medium') => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await quizService.generateQuiz({
        topic,
        difficulty,
        num_questions: 5
      });
      
      setQuiz(response);
      setCurrentQuestion(0);
      setAnswers([]);
    } catch (err) {
      console.error('Failed to generate quiz:', err);
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const submitAnswer = useCallback(async (quizId, questionIndex, selectedAnswer) => {
    try {
      // Get the correct answer from the current question
      const currentQuestion = quiz.questions[questionIndex];
      const correctAnswer = currentQuestion?.correct_answer;
      
      const response = await quizService.submitAnswer({
        quiz_id: quizId,
        question_index: questionIndex,
        selected_answer: selectedAnswer,
        correct_answer: correctAnswer  // Send correct answer for verification
      });
      
      const newAnswer = {
        questionIndex,
        selectedAnswer,
        correct: response.correct,
        score: response.score,
        explanation: response.explanation || currentQuestion?.explanation
      };
      
      setAnswers(prev => [...prev, newAnswer]);
      
      // Move to next question
      if (questionIndex < quiz.questions.length - 1) {
        setCurrentQuestion(prev => prev + 1);
      }
      
      return response;
    } catch (err) {
      console.error('Failed to submit answer:', err);
      throw err;
    }
  }, [quiz]);

  const retry = useCallback(() => {
    setError(null);
    setLoading(false);
  }, []);

  return {
    quiz,
    currentQuestion,
    loading,
    error,
    answers,
    generateQuiz,
    submitAnswer,
    retry
  };
};
