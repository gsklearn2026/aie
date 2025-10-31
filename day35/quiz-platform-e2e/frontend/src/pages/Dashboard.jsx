import React from 'react';
import { Link } from 'react-router-dom';

function Dashboard() {
  const quizTypes = [
    { id: 'science', name: 'Science Quiz', description: 'Test your scientific knowledge' },
    { id: 'history', name: 'History Quiz', description: 'Explore historical events' },
    { id: 'mathematics', name: 'Math Quiz', description: 'Challenge your math skills' },
    { id: 'literature', name: 'Literature Quiz', description: 'Dive into literary works' }
  ];

  return (
    <div className="page" data-testid="dashboard">
      <h1>Quiz Platform Dashboard</h1>
      <Link data-testid="dashboard-link" to="/dashboard">Home</Link>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginTop: '20px' }}>
        {quizTypes.map(quiz => (
          <div key={quiz.id} className="card">
            <h3>{quiz.name}</h3>
            <p>{quiz.description}</p>
            <Link to={`/quiz/${quiz.id}`}>
              <button data-testid={`quiz-type-${quiz.id}`}>
                Start Quiz
              </button>
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Dashboard;
