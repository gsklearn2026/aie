const VerificationService = require('../services/verificationService');
const QueueProcessor = require('../services/queueProcessor');
const logger = require('../utils/logger');

class VerificationController {
  constructor() {
    this.verificationService = new VerificationService();
    this.queueProcessor = new QueueProcessor();
  }

  async verifyContent(req, res) {
    try {
      const { questionId, content } = req.body;
      
      if (!questionId || !content) {
        return res.status(400).json({
          error: 'Missing required fields: questionId and content'
        });
      }

      const result = await this.verificationService.verifyContent(questionId, content);
      
      res.json({
        success: true,
        data: result
      });
    } catch (error) {
      logger.error('Verification controller error:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: error.message
      });
    }
  }

  async verifyContentAsync(req, res) {
    try {
      const { questionId, content } = req.body;
      
      if (!questionId || !content) {
        return res.status(400).json({
          error: 'Missing required fields: questionId and content'
        });
      }

      const job = await this.queueProcessor.addVerificationJob(questionId, content);
      
      res.json({
        success: true,
        jobId: job.id,
        message: 'Verification job queued'
      });
    } catch (error) {
      logger.error('Async verification controller error:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: error.message
      });
    }
  }

  async getJobStatus(req, res) {
    try {
      const { jobId } = req.params;
      const status = await this.queueProcessor.getJobStatus(jobId);
      
      if (!status) {
        return res.status(404).json({
          error: 'Job not found'
        });
      }

      res.json({
        success: true,
        data: status
      });
    } catch (error) {
      logger.error('Job status controller error:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: error.message
      });
    }
  }

  async batchVerify(req, res) {
    try {
      const { questions } = req.body;
      
      if (!Array.isArray(questions) || questions.length === 0) {
        return res.status(400).json({
          error: 'Invalid questions array'
        });
      }

      const results = await this.verificationService.batchVerify(questions);
      
      res.json({
        success: true,
        data: results,
        summary: {
          total: results.length,
          approved: results.filter(r => r.status === 'approved').length,
          rejected: results.filter(r => r.status === 'rejected').length,
          flagged: results.filter(r => r.status === 'review').length
        }
      });
    } catch (error) {
      logger.error('Batch verification controller error:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: error.message
      });
    }
  }

  async healthCheck(req, res) {
    res.json({
      success: true,
      service: 'content-verification-service',
      status: 'healthy',
      timestamp: new Date().toISOString()
    });
  }
}

module.exports = VerificationController;
