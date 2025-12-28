-- Add email column to users table (run this on your PostgreSQL database)

-- Add email column (allow NULL initially for existing users)
ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(255);

-- For existing users without email, set a default email pattern
-- You should update these manually later
UPDATE users 
SET email = username || '@temporary.local' 
WHERE email IS NULL;

-- Now make email NOT NULL and UNIQUE
ALTER TABLE users ALTER COLUMN email SET NOT NULL;
ALTER TABLE users ADD CONSTRAINT users_email_unique UNIQUE (email);
