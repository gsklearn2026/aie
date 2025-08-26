const Anthropic = require('@anthropic-ai/sdk');
const config = require('../config/config');
const logger = require('../utils/logger');

class ClaudeService {
  constructor() {
    this.client = new Anthropic({
      apiKey: config.anthropic.apiKey
    });
  }

  async verifyFactualAccuracy(content) {
    try {
      const prompt = this.buildVerificationPrompt(content);
      
      const response = await this.client.messages.create({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 1000,
        messages: [{
          role: 'user',
          content: prompt
        }]
      });

      return this.parseVerificationResponse(response.content[0].text);
    } catch (error) {
      logger.error('Claude API error:', error);
      throw new Error(`Verification failed: ${error.message}`);
    }
  }

  buildVerificationPrompt(content) {
    return `
Please verify the factual accuracy of this quiz question and provide a quality assessment:

Question: ${content.question}
Options: ${content.options.join(', ')}
Correct Answer: ${content.options[content.correctAnswer]}
Topic: ${content.topic}
Difficulty: ${content.difficulty}

Please respond with a JSON object containing:
- "factuallyAccurate": boolean (true if factually correct)
- "confidence": number (1-10, confidence in accuracy)
- "qualityScore": number (1-10, overall question quality)
- "issues": array of strings (any concerns or problems)
- "reasoning": string (brief explanation of assessment)

Focus on:
1. Factual correctness of the question and answers
2. Clarity and appropriateness for the stated difficulty
3. Whether the correct answer is definitively correct
4. Quality of distractors (incorrect options)
`;
  }

  parseVerificationResponse(response) {
    try {
      // Extract JSON from response if it's wrapped in markdown
      const jsonMatch = response.match(/```json\s*([\s\S]*?)\s*```/) || 
                       response.match(/\{[\s\S]*\}/);
      
      if (jsonMatch) {
        return JSON.parse(jsonMatch[1] || jsonMatch[0]);
      }
      
      return JSON.parse(response);
    } catch (error) {
      logger.warn('Failed to parse Claude response, using fallback');
      return {
        factuallyAccurate: false,
        confidence: 1,
        qualityScore: 1,
        issues: ['Failed to parse verification response'],
        reasoning: 'Response parsing error'
      };
    }
  }
}

module.exports = ClaudeService;
