const FormatValidator = require('../../src/validators/formatValidator');

describe('FormatValidator', () => {
  let validator;

  beforeEach(() => {
    validator = new FormatValidator();
  });

  test('should validate correct question format', () => {
    const validQuestion = {
      id: 'q1',
      question: 'What is the capital of France?',
      options: ['London', 'Berlin', 'Paris', 'Madrid'],
      correctAnswer: 2,
      topic: 'Geography',
      difficulty: 'easy'
    };

    const result = validator.validate(validQuestion);
    expect(result.valid).toBe(true);
    expect(result.issues).toHaveLength(0);
  });

  test('should reject question with missing fields', () => {
    const invalidQuestion = {
      id: 'q1',
      question: 'What is the capital of France?'
    };

    const result = validator.validate(invalidQuestion);
    expect(result.valid).toBe(false);
    expect(result.issues.length).toBeGreaterThan(0);
  });

  test('should reject question with invalid correct answer index', () => {
    const invalidQuestion = {
      id: 'q1',
      question: 'What is the capital of France?',
      options: ['London', 'Berlin'],
      correctAnswer: 5,
      topic: 'Geography',
      difficulty: 'easy'
    };

    const result = validator.validate(invalidQuestion);
    expect(result.valid).toBe(false);
    expect(result.issues).toContain('Correct answer index exceeds available options');
  });
}); 