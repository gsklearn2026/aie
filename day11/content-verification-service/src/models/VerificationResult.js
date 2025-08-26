class VerificationResult {
  constructor(questionId, content) {
    this.questionId = questionId;
    this.content = content;
    this.status = 'pending';
    this.formatValid = false;
    this.factuallyAccurate = false;
    this.qualityScore = 0;
    this.confidence = 0;
    this.issues = [];
    this.claudeResponse = null;
    this.createdAt = new Date();
    this.updatedAt = new Date();
  }

  approve(qualityScore, confidence) {
    this.status = 'approved';
    this.qualityScore = qualityScore;
    this.confidence = confidence;
    this.updatedAt = new Date();
  }

  reject(issues) {
    this.status = 'rejected';
    this.issues = issues;
    this.updatedAt = new Date();
  }

  flagForReview(reason) {
    this.status = 'review';
    this.issues.push(reason);
    this.updatedAt = new Date();
  }
}

module.exports = VerificationResult;
