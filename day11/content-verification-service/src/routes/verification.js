const express = require('express');
const VerificationController = require('../controllers/verificationController');

const router = express.Router();
const controller = new VerificationController();

router.post('/verify', controller.verifyContent.bind(controller));
router.post('/verify/async', controller.verifyContentAsync.bind(controller));
router.post('/verify/batch', controller.batchVerify.bind(controller));
router.get('/job/:jobId', controller.getJobStatus.bind(controller));
router.get('/health', controller.healthCheck.bind(controller));

module.exports = router; 