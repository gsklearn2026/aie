import React from 'react';
import { useParams } from 'react-router-dom';

const QuizView = () => {
  const { quizId } = useParams();
  
  return (
    <div style={{padding: '20px', textAlign: 'center'}}>
      <h2>Quiz View for {quizId}</h2>
      <p>Individual quiz interface would be implemented here.</p>
      <p>This demo focuses on the caching infrastructure.</p>
    </div>
  );
};

export default QuizView;
