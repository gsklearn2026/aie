const VerificationService = require('../../src/services/verificationService');

jest.mock('../../src/services/claudeService');

describe('VerificationService', () => {
  let service;
  let mockClaudeService;

  beforeEach(() => {
    service = new VerificationService();
    mockClaudeService = service.claudeService;
  });

  test('should reject content with invalid format', async () => {
    const invalidContent = {
      id: 'q1',
      question: 'Test?'
    };

    const result = await service.verifyContent('q1', invalidContent);
    
    expect(result.status).toBe('rejected');
    expect(result.formatValid).toBe(false);
  });

  test('should approve high-quality content', async () => {
    const validContent = {
      id: 'q1',
      question: 'What is the capital of France?',
      options: ['London', 'Berlin', 'Paris', 'Madrid'],
      correctAnswer: 2,
      topic: 'Geography',
      difficulty: 'easy'
    };

    mockClaudeService.verifyFactualAccuracy.mockResolvedValue({
      factuallyAccurate: true,
      confidence: 9,
      qualityScore: 8,
      issues: [],
      reasoning: 'Excellent question'
    });

    const result = await service.verifyContent('q1', validContent);
    
    expect(result.status).toBe('approved');
    expect(result.qualityScore).toBe(8);
  });
}); 