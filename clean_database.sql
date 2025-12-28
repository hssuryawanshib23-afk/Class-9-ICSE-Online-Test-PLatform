-- Clean database - Remove all student data and test records
-- Run this in Neon.tech SQL Editor: https://console.neon.tech

-- Step 1: Delete all responses (test answers)
DELETE FROM responses;

-- Step 2: Delete all test attempts
DELETE FROM test_attempts;

-- Step 3: Delete all student records
DELETE FROM students;

-- Step 4: Delete all users with role='student' (keep admin accounts)
DELETE FROM users WHERE role = 'student';

-- Verify cleanup
SELECT 'Users (should only show admins)' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'Students', COUNT(*) FROM students
UNION ALL
SELECT 'Test Attempts', COUNT(*) FROM test_attempts
UNION ALL
SELECT 'Responses', COUNT(*) FROM responses;

-- Show remaining users (admins)
SELECT id, username, phone_number, role FROM users;
