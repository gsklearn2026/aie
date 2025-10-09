-- Initialize quiz platform database
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS quizzes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    quiz_id INTEGER REFERENCES quizzes(id),
    question_text TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    ai_generated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_responses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    question_id INTEGER REFERENCES questions(id),
    response_text TEXT,
    is_correct BOOLEAN,
    response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO users (username, email) VALUES 
    ('student1', 'student1@example.com'),
    ('student2', 'student2@example.com'),
    ('teacher1', 'teacher1@example.com');

INSERT INTO quizzes (title, description, created_by) VALUES 
    ('Python Basics', 'Introduction to Python programming', 3),
    ('Database Design', 'Fundamentals of database design', 3);

INSERT INTO questions (quiz_id, question_text, correct_answer, ai_generated) VALUES 
    (1, 'What is a Python list?', 'A mutable sequence of items', true),
    (1, 'How do you create a function in Python?', 'def function_name():', true),
    (2, 'What is normalization?', 'Process of organizing data to reduce redundancy', false);
