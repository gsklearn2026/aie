const asyncRetry = require('async-retry');
const FormatValidator = require('../validators/formatValidator');
const ClaudeService = require('./claudeService');
const VerificationResult = require('../models/VerificationResult');
const config = require('../config/config');
const logger = require('../utils/logger');

class VerificationService {
  constructor() {
    this.formatValidator = new FormatValidator();
    this.claudeService = new ClaudeService();
  }

  async verifyContent(questionId, content) {
    const result = new VerificationResult(questionId, content);
    
    try {
      logger.info(`Starting verification for question ${questionId}`);
      
      // Step 1: Format validation
      const formatResult = this.formatValidator.validate(content);
      result.formatValid = formatResult.valid;
      
      if (!formatResult.valid) {
        result.reject(formatResult.issues);
        return result;
      }

      // Step 2: Factual accuracy check with retry
      const claudeResult = await asyncRetry(
        async () => await this.claudeService.verifyFactualAccuracy(content),
        {
          retries: config.verification.maxRetryAttempts,
          factor: 2,
          minTimeout: 1000,
          maxTimeout: 10000
        }
      );

      result.claudeResponse = claudeResult;
      result.factuallyAccurate = claudeResult.factuallyAccurate;
      result.confidence = claudeResult.confidence;
      result.qualityScore = claudeResult.qualityScore;

      // Step 3: Make final decision
      if (claudeResult.factuallyAccurate && 
          claudeResult.qualityScore >= config.verification.qualityThreshold) {
        result.approve(claudeResult.qualityScore, claudeResult.confidence);
      } else if (claudeResult.qualityScore >= 5) {
        result.flagForReview('Quality score below threshold but above minimum');
      } else {
        result.reject(claudeResult.issues || ['Quality score too low']);
      }

      logger.info(`Verification completed for question ${questionId}: ${result.status}`);
      return result;

    } catch (error) {
      logger.error(`Verification failed for question ${questionId}:`, error);
      result.reject([`Verification error: ${error.message}`]);
      return result;
    }
  }

  async batchVerify(questions) {
    const results = [];
    
    for (const question of questions) {
      const result = await this.verifyContent(question.id, question);
      results.push(result);
    }
    
    return results;
  }
}

module.exports = VerificationService;
