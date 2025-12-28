-- Fix corrupted admin passwords
-- Run this in Neon.tech SQL Editor

-- First, let's see what admins exist
SELECT id, username, phone_number, role FROM users WHERE role = 'admin';

-- OPTION 1: Delete corrupted admin and create new one
-- (Replace with your desired admin credentials)
DELETE FROM users WHERE role = 'admin';

-- Create fresh admin account
-- Username: admin
-- Phone: 9999000001  
-- Password: You'll set this through the create_admin.py script below
