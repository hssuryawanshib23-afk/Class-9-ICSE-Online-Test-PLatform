-- ═══════════════════════════════════════════════════════════════
-- ALL DATABASE MIGRATIONS
-- Run this in Neon.tech PostgreSQL Console
-- ═══════════════════════════════════════════════════════════════

-- MIGRATION 1: Add registration timestamp
-- ═══════════════════════════════════════════════════════════════
ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Update existing users to have current timestamp if NULL
UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL;

-- MIGRATION 2: Add school, class, board fields
-- ═══════════════════════════════════════════════════════════════
ALTER TABLE users ADD COLUMN IF NOT EXISTS school_name VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS class_name VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS board_name VARCHAR(100);

-- MIGRATION 3: Add subject support to chapters table
-- ═══════════════════════════════════════════════════════════════
-- Add subject column (default to Physics for existing data)
ALTER TABLE chapters ADD COLUMN IF NOT EXISTS subject VARCHAR(50) DEFAULT 'Physics';

-- Update existing Physics chapters to have subject explicitly set
UPDATE chapters SET subject = 'Physics' WHERE subject IS NULL OR subject = '';

-- Drop old unique constraint on chapter_number only
ALTER TABLE chapters DROP CONSTRAINT IF EXISTS chapters_chapter_number_key;

-- Add new unique constraint on (subject, chapter_number) combination
ALTER TABLE chapters ADD CONSTRAINT IF NOT EXISTS chapters_subject_number_unique 
    UNIQUE (subject, chapter_number);

-- ═══════════════════════════════════════════════════════════════
-- VERIFICATION QUERIES (Run these to check migrations worked)
-- ═══════════════════════════════════════════════════════════════

-- Check users table structure
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY ordinal_position;

-- Check chapters table structure
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'chapters' 
ORDER BY ordinal_position;

-- Check existing chapters
SELECT subject, chapter_number, COUNT(*) as concept_count
FROM chapters c
LEFT JOIN concepts con ON c.id = con.chapter_id
GROUP BY subject, chapter_number
ORDER BY subject, chapter_number;

-- ═══════════════════════════════════════════════════════════════
-- SUCCESS MESSAGES
-- ═══════════════════════════════════════════════════════════════
-- If all queries run successfully, you should see:
-- ✅ users table now has: created_at, school_name, class_name, board_name
-- ✅ chapters table now has: subject column
-- ✅ Unique constraint on (subject, chapter_number)
-- ✅ Existing Physics chapters remain intact
-- ═══════════════════════════════════════════════════════════════
