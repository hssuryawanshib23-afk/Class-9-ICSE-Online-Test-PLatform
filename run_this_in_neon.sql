-- Run this SQL directly in your Neon.tech console
-- Go to: https://console.neon.tech > Your Project > SQL Editor

-- Add phone_number column
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_number VARCHAR(15);

-- Set default phone numbers for existing users
UPDATE users 
SET phone_number = '9999' || LPAD(id::text, 6, '0')
WHERE phone_number IS NULL;

-- Make phone_number NOT NULL
ALTER TABLE users ALTER COLUMN phone_number SET NOT NULL;

-- Add UNIQUE constraint
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'users_phone_number_unique'
    ) THEN
        ALTER TABLE users ADD CONSTRAINT users_phone_number_unique UNIQUE (phone_number);
    END IF;
END $$;

-- Verify the change
SELECT id, username, phone_number FROM users;
