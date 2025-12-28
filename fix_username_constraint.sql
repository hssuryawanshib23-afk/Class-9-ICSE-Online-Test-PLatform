-- Fix username constraint - allow duplicate names
-- Only phone_number should be unique, not username!
-- Run this in Neon.tech SQL Editor

-- Drop the unique constraint on username
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_username_key;

-- Verify - these should show constraints
SELECT constraint_name, constraint_type 
FROM information_schema.table_constraints 
WHERE table_name = 'users';

-- Should only see users_phone_number_unique, not users_username_key
