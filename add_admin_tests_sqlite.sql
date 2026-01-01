-- SQLite Migration Script for Admin Test Feature
-- Run this for local development with SQLite

-- Table: admin_tests (stores test metadata)
CREATE TABLE IF NOT EXISTS admin_tests (
    admin_test_id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_name TEXT NOT NULL,
    chapters TEXT NOT NULL,
    total_questions INTEGER NOT NULL,
    easy_percentage REAL NOT NULL,
    medium_percentage REAL NOT NULL,
    hard_percentage REAL NOT NULL,
    duration_minutes INTEGER NOT NULL,
    created_by INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Table: admin_test_questions (links questions to admin tests)
CREATE TABLE IF NOT EXISTS admin_test_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_test_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    question_order INTEGER NOT NULL,
    FOREIGN KEY (admin_test_id) REFERENCES admin_tests(admin_test_id),
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

-- Table: admin_test_attempts (records when students take admin tests)
CREATE TABLE IF NOT EXISTS admin_test_attempts (
    attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_test_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    score REAL NOT NULL,
    total_questions INTEGER NOT NULL,
    percentage REAL NOT NULL,
    attempted_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_test_id) REFERENCES admin_tests(admin_test_id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Table: admin_test_responses (stores individual question responses)
CREATE TABLE IF NOT EXISTS admin_test_responses (
    response_id INTEGER PRIMARY KEY AUTOINCREMENT,
    attempt_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    selected_answer TEXT NOT NULL,
    is_correct INTEGER NOT NULL,
    FOREIGN KEY (attempt_id) REFERENCES admin_test_attempts(attempt_id),
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_admin_tests_active ON admin_tests(is_active);
CREATE INDEX IF NOT EXISTS idx_admin_test_questions_test ON admin_test_questions(admin_test_id);
CREATE INDEX IF NOT EXISTS idx_admin_test_attempts_user ON admin_test_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_admin_test_attempts_test ON admin_test_attempts(admin_test_id);
CREATE INDEX IF NOT EXISTS idx_admin_test_responses_attempt ON admin_test_responses(attempt_id);
