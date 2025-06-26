const axios = require('axios');

const BASE_URL = 'http://localhost:3003/api/verification';

const sampleQuestion = {
  id: 'demo-q1',
  question: 'What is the capital of France?',
  options: ['London', 'Berlin', 'Paris', 'Madrid'],
  correctAnswer: 2,
  topic: 'Geography',
  difficulty: 'easy',
  explanation: 'Paris is the capital and largest city of France.'
};

const sampleQuestions = [
  sampleQuestion,
  {
    id: 'demo-q2',
    question: 'What is 2 + 2?',
    options: ['3', '4', '5', '6'],
    correctAnswer: 1,
    topic: 'Mathematics',
    difficulty: 'easy'
  }
];

async function runDemo() {
  console.log('🎬 Content Verification Service Demo');
  console.log('=====================================\n');

  try {
    // Health check
    console.log('1. Health Check...');
    const healthResponse = await axios.get(`${BASE_URL}/health`);
    console.log('✅ Service is healthy\n');

    // Single verification
    console.log('2. Single Question Verification...');
    const verifyResponse = await axios.post(`${BASE_URL}/verify`, {
      questionId: sampleQuestion.id,
      content: sampleQuestion
    });
    
    console.log('📊 Verification Result:');
    console.log(`   Status: ${verifyResponse.data.data.status}`);
    console.log(`   Quality Score: ${verifyResponse.data.data.qualityScore}`);
    console.log(`   Format Valid: ${verifyResponse.data.data.formatValid}\n`);

    // Batch verification
    console.log('3. Batch Verification...');
    const batchResponse = await axios.post(`${BASE_URL}/verify/batch`, {
      questions: sampleQuestions
    });
    
    console.log('📊 Batch Results:');
    console.log(`   Total: ${batchResponse.data.summary.total}`);
    console.log(`   Approved: ${batchResponse.data.summary.approved}`);
    console.log(`   Rejected: ${batchResponse.data.summary.rejected}`);
    console.log(`   Flagged: ${batchResponse.data.summary.flagged}\n`);

    // Async verification
    console.log('4. Async Verification...');
    const asyncResponse = await axios.post(`${BASE_URL}/verify/async`, {
      questionId: 'async-q1',
      content: sampleQuestion
    });
    
    console.log(`📋 Job queued with ID: ${asyncResponse.data.jobId}`);
    
    // Check job status
    setTimeout(async () => {
      try {
        const statusResponse = await axios.get(`${BASE_URL}/job/${asyncResponse.data.jobId}`);
        console.log(`📊 Job Status: ${JSON.stringify(statusResponse.data.data, null, 2)}\n`);
      } catch (error) {
        console.log('ℹ️  Job still processing or completed\n');
      }
    }, 2000);

    console.log('🎉 Demo completed successfully!');

  } catch (error) {
    if (error.response) {
      console.error('❌ Demo failed:', error.response.data);
    } else {
      console.error('❌ Demo failed:', error.message);
    }
    
    if (error.message.includes('ECONNREFUSED')) {
      console.log('\n💡 Make sure the service is running with: npm start');
    }
  }
}

runDemo(); 