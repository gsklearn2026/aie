import React, { useState } from 'react';
import './GenerationForm.css';

function GenerationForm({ onGenerate, loading, profiles }) {
  const [formData, setFormData] = useState({
    question_type: 'multiple_choice',
    subject: '',
    difficulty: 'medium',
    additional_context: ''
  });

  const questionTypes = [
    { value: 'multiple_choice', label: 'Multiple Choice' },
    { value: 'true_false', label: 'True/False' },
    { value: 'short_answer', label: 'Short Answer' },
    { value: 'essay', label: 'Essay' },
    { value: 'coding', label: 'Coding' }
  ];

  const difficulties = [
    { value: 'easy', label: 'Easy' },
    { value: 'medium', label: 'Medium' },
    { value: 'hard', label: 'Hard' }
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.subject.trim()) {
      alert('Please enter a subject');
      return;
    }
    onGenerate(formData);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const selectedProfile = profiles[
    formData.question_type === 'multiple_choice' ? 'multiple_choice_expert' :
    formData.question_type === 'true_false' ? 'true_false_efficient' :
    formData.question_type === 'short_answer' ? 'short_answer_balanced' :
    formData.question_type === 'essay' ? 'essay_creative' :
    formData.question_type === 'coding' ? 'coding_specialist' :
    'general_fallback'
  ];

  return (
    <div className="generation-form-container">
      <form onSubmit={handleSubmit} className="generation-form">
        <h2>Generate Question</h2>
        
        <div className="form-group">
          <label>Question Type</label>
          <select 
            name="question_type" 
            value={formData.question_type}
            onChange={handleChange}
            disabled={loading}
          >
            {questionTypes.map(type => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Subject</label>
          <input
            type="text"
            name="subject"
            value={formData.subject}
            onChange={handleChange}
            placeholder="e.g., Python Programming, World History"
            disabled={loading}
            required
          />
        </div>

        <div className="form-group">
          <label>Difficulty</label>
          <select 
            name="difficulty" 
            value={formData.difficulty}
            onChange={handleChange}
            disabled={loading}
          >
            {difficulties.map(diff => (
              <option key={diff.value} value={diff.value}>
                {diff.label}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Additional Context (Optional)</label>
          <textarea
            name="additional_context"
            value={formData.additional_context}
            onChange={handleChange}
            placeholder="Any specific requirements or context..."
            rows="3"
            disabled={loading}
          />
        </div>

        {selectedProfile && (
          <div className="profile-info">
            <h3>Selected AI Profile</h3>
            <div className="profile-details">
              <span className="profile-badge">{selectedProfile.model}</span>
              <span className={`cost-badge ${selectedProfile.cost_tier}`}>
                {selectedProfile.cost_tier}
              </span>
              <span className="temp-badge">
                Temp: {selectedProfile.temperature}
              </span>
            </div>
          </div>
        )}

        <button type="submit" disabled={loading} className="generate-button">
          {loading ? 'Generating...' : 'Generate Question'}
        </button>
      </form>
    </div>
  );
}

export default GenerationForm;
