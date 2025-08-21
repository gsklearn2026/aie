// Demo data service for populating all tabs with working data
import { topicsApi, learningPathApi, usersApi } from './api';

export const demoData = {
  // Sample topics for the Topics tab
  topics: [
    {
      name: "Python Fundamentals",
      description: "Learn the basics of Python programming language including syntax, data types, and control structures.",
      difficulty_level: 3.0,
      estimated_duration: 120,
      prerequisites: [],
      learning_objectives: ["Understand Python syntax", "Write basic programs", "Use data types"],
      content_type: "interactive"
    },
    {
      name: "Data Structures & Algorithms",
      description: "Master fundamental data structures and algorithms in Python for efficient problem solving.",
      difficulty_level: 6.0,
      estimated_duration: 180,
      prerequisites: [],
      learning_objectives: ["Implement data structures", "Analyze algorithms", "Solve coding problems"],
      content_type: "project"
    },
    {
      name: "Web Development with Flask",
      description: "Build web applications using Python Flask framework and modern web technologies.",
      difficulty_level: 7.0,
      estimated_duration: 240,
      prerequisites: [],
      learning_objectives: ["Create web applications", "Use Flask framework", "Handle HTTP requests"],
      content_type: "video"
    },
    {
      name: "Machine Learning Basics",
      description: "Introduction to machine learning concepts and implementation using Python libraries.",
      difficulty_level: 8.0,
      estimated_duration: 300,
      prerequisites: [],
      learning_objectives: ["Understand ML concepts", "Use scikit-learn", "Build ML models"],
      content_type: "interactive"
    },
    {
      name: "Database Design",
      description: "Learn database design principles and SQL implementation for data management.",
      difficulty_level: 5.0,
      estimated_duration: 150,
      prerequisites: [],
      learning_objectives: ["Design databases", "Write SQL queries", "Normalize data"],
      content_type: "text"
    },
    {
      name: "API Development",
      description: "Create RESTful APIs using FastAPI and implement modern web service patterns.",
      difficulty_level: 7.5,
      estimated_duration: 200,
      prerequisites: [],
      learning_objectives: ["Build REST APIs", "Use FastAPI", "Handle authentication"],
      content_type: "project"
    }
  ],

  // Sample user progress data
  userProgress: [
    {
      topic_id: 1,
      mastery_level: 0.9,
      completion_status: "completed",
      time_spent: 110,
      attempts: 1
    },
    {
      topic_id: 2,
      mastery_level: 0.7,
      completion_status: "in_progress",
      time_spent: 140,
      attempts: 2
    },
    {
      topic_id: 3,
      mastery_level: 0.4,
      completion_status: "in_progress",
      time_spent: 100,
      attempts: 1
    },
    {
      topic_id: 4,
      mastery_level: 0.2,
      completion_status: "not_started",
      time_spent: 30,
      attempts: 1
    },
    {
      topic_id: 5,
      mastery_level: 0.8,
      completion_status: "completed",
      time_spent: 130,
      attempts: 1
    },
    {
      topic_id: 6,
      mastery_level: 0.1,
      completion_status: "not_started",
      time_spent: 20,
      attempts: 1
    }
  ],

  // Sample learning paths
  learningPaths: [
    {
      path_name: "Python Web Developer Path",
      topic_sequence: [1, 2, 3, 5, 6],
      estimated_duration: 890,
      completion_rate: 0.6,
      created_at: "2024-01-15T10:00:00Z",
      is_active: true
    },
    {
      path_name: "Data Science Path",
      topic_sequence: [1, 2, 4],
      estimated_duration: 600,
      completion_rate: 0.8,
      created_at: "2024-01-10T14:30:00Z",
      is_active: true
    },
    {
      path_name: "Backend Developer Path",
      topic_sequence: [1, 2, 5, 6],
      estimated_duration: 650,
      completion_rate: 0.7,
      created_at: "2024-01-05T09:15:00Z",
      is_active: false
    }
  ],

  // Sample next recommended topics
  nextTopics: [
    {
      topic_id: 3,
      name: "Web Development with Flask",
      estimated_duration: 240,
      difficulty_level: 7.0
    },
    {
      topic_id: 4,
      name: "Machine Learning Basics",
      estimated_duration: 300,
      difficulty_level: 8.0
    },
    {
      topic_id: 6,
      name: "API Development",
      estimated_duration: 200,
      difficulty_level: 7.5
    }
  ],

  // Sample user statistics
  userStats: {
    totalPaths: 3,
    completedTopics: 2,
    totalTopics: 6,
    avgMastery: 0.52,
    learningStreak: 12
  },

  // Sample progress chart data
  progressData: [
    { day: 'Mon', mastery: 0.45, topics: 2 },
    { day: 'Tue', mastery: 0.52, topics: 3 },
    { day: 'Wed', mastery: 0.58, topics: 2 },
    { day: 'Thu', mastery: 0.61, topics: 4 },
    { day: 'Fri', mastery: 0.65, topics: 3 },
    { day: 'Sat', mastery: 0.68, topics: 1 },
    { day: 'Sun', mastery: 0.72, topics: 2 }
  ],

  // Sample topic relationships
  topicRelationships: [
    {
      source_topic_id: 1,
      target_topic_id: 2,
      relationship_type: "prerequisite",
      strength: 0.9
    },
    {
      source_topic_id: 1,
      target_topic_id: 3,
      relationship_type: "prerequisite",
      strength: 0.8
    },
    {
      source_topic_id: 1,
      target_topic_id: 4,
      relationship_type: "prerequisite",
      strength: 0.7
    },
    {
      source_topic_id: 1,
      target_topic_id: 5,
      relationship_type: "prerequisite",
      strength: 0.6
    },
    {
      source_topic_id: 2,
      target_topic_id: 3,
      relationship_type: "prerequisite",
      strength: 0.8
    },
    {
      source_topic_id: 2,
      target_topic_id: 4,
      relationship_type: "prerequisite",
      strength: 0.9
    },
    {
      source_topic_id: 3,
      target_topic_id: 6,
      relationship_type: "prerequisite",
      strength: 0.8
    },
    {
      source_topic_id: 5,
      target_topic_id: 6,
      relationship_type: "prerequisite",
      strength: 0.7
    }
  ]
};

// Demo service functions
export const demoService = {
  // Create demo user
  createDemoUser: async () => {
    try {
      console.log('Creating demo user...');
      const userData = {
        username: `demo_user_${Date.now()}`,
        email: `demo_${Date.now()}@example.com`,
        learning_preferences: {
          pace: "medium",
          difficulty: "intermediate",
          focus_areas: ["programming", "web_development", "data_science"]
        }
      };
      
      const response = await usersApi.createUser(userData);
      console.log(`Created demo user: ${response.username} (ID: ${response.user_id})`);
      
      // Store the user ID for use in other demo functions
      demoService.demoUserId = response.user_id;
      
      return { 
        success: true, 
        message: `Demo user created successfully!`,
        user: response
      };
    } catch (error) {
      console.error("Error creating demo user:", error);
      return { success: false, message: "Failed to create demo user: " + error.message };
    }
  },

  // Populate topics tab
  populateTopics: async () => {
    try {
      console.log('Creating demo topics...');
      const createdTopics = [];
      
      // Create demo topics
      for (const topic of demoData.topics) {
        try {
          const response = await topicsApi.createTopic(topic);
          createdTopics.push(response);
          console.log(`Created topic: ${topic.name}`);
        } catch (error) {
          console.warn(`Topic ${topic.name} might already exist:`, error.message);
        }
      }
      
      return { 
        success: true, 
        message: `Topics populated successfully! Created ${createdTopics.length} topics.`,
        topics: createdTopics
      };
    } catch (error) {
      console.error("Error populating topics:", error);
      return { success: false, message: "Failed to populate topics: " + error.message };
    }
  },

  // Populate user progress
  populateUserProgress: async () => {
    try {
      console.log('Creating demo user progress...');
      let successCount = 0;
      
      // Use the demo user ID if available, otherwise use 1
      const userId = demoService.demoUserId || 1;
      
      // Update progress for each topic
      for (const progress of demoData.userProgress) {
        try {
          await learningPathApi.updateProgress(userId, progress);
          successCount++;
          console.log(`Updated progress for topic ${progress.topic_id}`);
        } catch (error) {
          console.warn(`Failed to update progress for topic ${progress.topic_id}:`, error.message);
        }
      }
      
      return { 
        success: successCount > 0, 
        message: `User progress populated successfully! Updated ${successCount} topics.`
      };
    } catch (error) {
      console.error("Error populating user progress:", error);
      return { success: false, message: "Failed to populate user progress: " + error.message };
    }
  },

  // Generate demo learning paths
  generateDemoPaths: async () => {
    try {
      console.log('Generating demo learning paths...');
      let successCount = 0;
      
      // Use the demo user ID if available, otherwise use 1
      const userId = demoService.demoUserId || 1;
      
      // Generate paths for different topic combinations
      const pathRequests = [
        {
          user_id: userId,
          target_topics: [1, 2, 3, 5, 6],
          max_difficulty_jump: 1.5,
          preferred_duration: 900
        },
        {
          user_id: userId,
          target_topics: [1, 2, 4],
          max_difficulty_jump: 2.0,
          preferred_duration: 600
        },
        {
          user_id: userId,
          target_topics: [1, 2, 5, 6],
          max_difficulty_jump: 1.8,
          preferred_duration: 650
        }
      ];

      for (const request of pathRequests) {
        try {
          await learningPathApi.generatePath(request);
          successCount++;
          console.log(`Generated path for topics: ${request.target_topics.join(', ')}`);
        } catch (error) {
          console.warn(`Failed to generate path for topics ${request.target_topics.join(', ')}:`, error.message);
        }
      }
      
      return { 
        success: successCount > 0, 
        message: `Demo learning paths generated successfully! Created ${successCount} paths.`
      };
    } catch (error) {
      console.error("Error generating demo paths:", error);
      return { success: false, message: "Failed to generate demo paths: " + error.message };
    }
  },

  // Run full demo
  runFullDemo: async () => {
    try {
      console.log('🚀 Starting full demo...');
      const results = [];
      
      // Step 1: Create demo user
      console.log('Step 1: Creating demo user...');
      const userResult = await demoService.createDemoUser();
      results.push(userResult);
      
      // Step 2: Populate topics
      console.log('Step 2: Populating topics...');
      const topicsResult = await demoService.populateTopics();
      results.push(topicsResult);
      
      // Step 3: Generate learning paths
      console.log('Step 3: Generating learning paths...');
      const pathsResult = await demoService.generateDemoPaths();
      results.push(pathsResult);
      
      // Step 4: Populate user progress
      console.log('Step 4: Populating user progress...');
      const progressResult = await demoService.populateUserProgress();
      results.push(progressResult);
      
      const allSuccess = results.every(r => r.success);
      const successCount = results.filter(r => r.success).length;
      
      console.log('Demo completed!', results);
      
      return {
        success: allSuccess,
        message: `Demo completed! ${successCount}/${results.length} steps successful. Check all tabs for populated data!`,
        results
      };
    } catch (error) {
      console.error("Error running full demo:", error);
      return { success: false, message: "Failed to run full demo: " + error.message };
    }
  }
};
