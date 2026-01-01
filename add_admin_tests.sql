-- Migration: Add Admin Test Creation Feature
-- Run this in your PostgreSQL database (Neon.tech)

-- Table to store admin-created tests
CREATE TABLE IF NOT EXISTS admin_tests (
    admin_test_id SERIAL PRIMARY KEY,
    test_name VARCHAR(255) NOT NULL,
    created_by INTEGER REFERENCES users(id) ON DELETE CASCADE,
    total_questions INTEGER NOT NULL,
    duration_minutes INTEGER NOT NULL,
    easy_percentage INTEGER DEFAULT 30,
    medium_percentage INTEGER DEFAULT 30,
    hard_percentage INTEGER DEFAULT 40,
    chapters TEXT NOT NULL,  -- Store as comma-separated values: "2,3,4,5"
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table to link admin tests with specific questions (pre-generated)
CREATE TABLE IF NOT EXISTS admin_test_questions (
    id SERIAL PRIMARY KEY,
    admin_test_id INTEGER REFERENCES admin_tests(admin_test_id) ON DELETE CASCADE,
    question_id INTEGER REFERENCES questions(id) ON DELETE CASCADE,
    question_order INTEGER NOT NULL,
    UNIQUE(admin_test_id, question_id)
);

-- Table to track student attempts on admin tests
CREATE TABLE IF NOT EXISTS admin_test_attempts (
    attempt_id SERIAL PRIMARY KEY,
    admin_test_id INTEGER REFERENCES admin_tests(admin_test_id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    score INTEGER NOT NULL,
    total_questions INTEGER NOT NULL,
    percentage NUMERIC(5,2) NOT NULL,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table to store responses for admin test attempts
CREATE TABLE IF NOT EXISTS admin_test_responses (
    response_id SERIAL PRIMARY KEY,
    attempt_id INTEGER REFERENCES admin_test_attempts(attempt_id) ON DELETE CASCADE,
    question_id INTEGER REFERENCES questions(id) ON DELETE CASCADE,
    selected_answer CHAR(1),
    is_correct INTEGER DEFAULT 0
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_admin_tests_created_by ON admin_tests(created_by);
CREATE INDEX IF NOT EXISTS idx_admin_tests_active ON admin_tests(is_active);
CREATE INDEX IF NOT EXISTS idx_admin_test_questions_test ON admin_test_questions(admin_test_id);
CREATE INDEX IF NOT EXISTS idx_admin_test_attempts_user ON admin_test_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_admin_test_attempts_test ON admin_test_attempts(admin_test_id);
CREATE INDEX IF NOT EXISTS idx_admin_test_responses_attempt ON admin_test_responses(attempt_id);

-- Insert sample admin test (optional - for testing)
-- Uncomment if you want to add a sample test
-- INSERT INTO admin_tests (test_name, description, created_by, total_questions, duration_minutes, easy_percentage, medium_percentage, hard_percentage, chapters)
-- VALUES ('Sample Physics Test', 'A balanced test covering multiple chapters', 1, 30, 60, 30, 30, 40, '2,3,4,5');
