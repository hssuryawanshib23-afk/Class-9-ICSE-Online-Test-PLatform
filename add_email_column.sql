-- Add phone_number column to users table (run this on your PostgreSQL database)

-- Add phone_number column (allow NULL initially for existing users)
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_number VARCHAR(15);

-- For existing users without phone number, set a default pattern
-- You should update these manually later
UPDATE users 
SET phone_number = '9999' || LPAD(id::text, 6, '0')
WHERE phone_number IS NULL;

-- Now make phone_number NOT NULL and UNIQUE
ALTER TABLE users ALTER COLUMN phone_number SET NOT NULL;
ALTER TABLE users ADD CONSTRAINT users_phone_number_unique UNIQUE (phone_number);
