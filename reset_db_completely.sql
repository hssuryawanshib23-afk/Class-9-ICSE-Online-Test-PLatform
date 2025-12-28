-- COMPLETE DATABASE RESET
-- Run this in Neon.tech SQL Editor

-- Delete all data
DELETE FROM responses;
DELETE FROM test_attempts;
DELETE FROM students;
DELETE FROM users;

-- Verify everything is deleted
SELECT 'All tables should show 0' as status;
SELECT 'Users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'Students', COUNT(*) FROM students
UNION ALL
SELECT 'Test Attempts', COUNT(*) FROM test_attempts
UNION ALL
SELECT 'Responses', COUNT(*) FROM responses;
