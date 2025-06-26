const Joi = require('joi');

const questionSchema = Joi.object({
  id: Joi.string().required(),
  question: Joi.string().min(10).required(),
  options: Joi.array().items(Joi.string()).min(2).max(6).required(),
  correctAnswer: Joi.number().integer().min(0).required(),
  topic: Joi.string().required(),
  difficulty: Joi.string().valid('easy', 'medium', 'hard').required(),
  explanation: Joi.string().optional(),
  metadata: Joi.object().optional()
});

class FormatValidator {
  validate(content) {
    const result = {
      valid: false,
      issues: []
    };

    try {
      const { error } = questionSchema.validate(content);
      
      if (error) {
        result.issues = error.details.map(detail => detail.message);
        return result;
      }

      // Additional validation
      if (content.correctAnswer >= content.options.length) {
        result.issues.push('Correct answer index exceeds available options');
        return result;
      }

      result.valid = true;
      return result;
    } catch (err) {
      result.issues.push('Invalid JSON structure');
      return result;
    }
  }
}

module.exports = FormatValidator;
