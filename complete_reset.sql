-- COMPLETE DATABASE RESET - Delete ALL users and test data
-- Run this in Neon.tech SQL Editor: https://console.neon.tech

-- Step 1: Delete all responses (test answers)
DELETE FROM responses;

-- Step 2: Delete all test attempts
DELETE FROM test_attempts;

-- Step 3: Delete all student records
DELETE FROM students;

-- Step 4: Delete ALL users (including admins and corrupted accounts)
DELETE FROM users;

-- Verify everything is clean
SELECT 'Users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'Students', COUNT(*) FROM students
UNION ALL
SELECT 'Test Attempts', COUNT(*) FROM test_attempts
UNION ALL
SELECT 'Responses', COUNT(*) FROM responses;

-- All counts should be 0
