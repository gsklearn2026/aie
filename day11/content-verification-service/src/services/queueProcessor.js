const Queue = require('bull');
const config = require('../config/config');
const VerificationService = require('./verificationService');
const logger = require('../utils/logger');

class QueueProcessor {
  constructor() {
    this.verificationQueue = new Queue('content verification', config.redis.url);
    this.verificationService = new VerificationService();
    this.setupProcessors();
  }

  setupProcessors() {
    this.verificationQueue.process('verify-content', async (job) => {
      const { questionId, content } = job.data;
      
      try {
        const result = await this.verificationService.verifyContent(questionId, content);
        
        // Update job progress
        job.progress(100);
        
        return result;
      } catch (error) {
        logger.error(`Queue processing failed for ${questionId}:`, error);
        throw error;
      }
    });

    this.verificationQueue.on('completed', (job, result) => {
      logger.info(`Verification completed for job ${job.id}: ${result.status}`);
    });

    this.verificationQueue.on('failed', (job, err) => {
      logger.error(`Verification failed for job ${job.id}:`, err);
    });
  }

  async addVerificationJob(questionId, content, options = {}) {
    const job = await this.verificationQueue.add('verify-content', {
      questionId,
      content
    }, {
      attempts: 3,
      backoff: {
        type: 'exponential',
        delay: 2000
      },
      ...options
    });

    return job;
  }

  async getJobStatus(jobId) {
    const job = await this.verificationQueue.getJob(jobId);
    if (!job) return null;

    return {
      id: job.id,
      progress: job.progress(),
      processedOn: job.processedOn,
      finishedOn: job.finishedOn,
      failedReason: job.failedReason
    };
  }
}

module.exports = QueueProcessor;
