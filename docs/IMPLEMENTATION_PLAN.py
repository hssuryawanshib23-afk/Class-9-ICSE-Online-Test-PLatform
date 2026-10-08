"""
═══════════════════════════════════════════════════════════════
COMPREHENSIVE GUIDE: Adding Chapters, Chemistry Subject & User Fields
═══════════════════════════════════════════════════════════════

TASK 1: Add Omitted Physics Chapters (1 & 6)
TASK 2: Add Registration Timestamp to Admin Page
TASK 3: Validate & Add Chemistry Subject (9 Chapters)
TASK 4: Add School/Class/Board Fields to Signup
═══════════════════════════════════════════════════════════════
"""

# ═══════════════════════════════════════════════════════════════
# TASK 1: ADD OMITTED PHYSICS CHAPTERS (1 & 6)
# ═══════════════════════════════════════════════════════════════

"""
WHAT TO DO:
-----------
1. You already have:
   - Question\Physics\chapter_1_omitted.json
   - Question\Physics\chapter_6_omitted.json

2. These files need to be inserted into your Neon PostgreSQL database

STEPS:
------
1. Run the script: insert_omitted_chapters.py (I'll create this)
   - This will insert chapter 1 and 6 questions into your database
   
2. Update streamlit_app.py to include these chapters in CHAPTER_NAMES dict
   - Add chapter 1 and 6 to the list

FILES TO MODIFY:
----------------
- streamlit_app.py (line ~19-27) - Add chapter 1 & 6 to CHAPTER_NAMES
- Run insert_omitted_chapters.py to populate database
"""

# ═══════════════════════════════════════════════════════════════
# TASK 2: ADD REGISTRATION TIMESTAMP
# ═══════════════════════════════════════════════════════════════

"""
WHAT TO DO:
-----------
1. Add 'created_at' column to users table in database
2. Modify create_user() in auth.py to save timestamp
3. Update show_students_list() in streamlit_app.py to display timestamp

SQL COMMAND (Run in Neon.tech console):
----------------------------------------
ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

FILES TO MODIFY:
----------------
- auth.py - Update create_user() to include created_at
- streamlit_app.py - Update show_students_list() to display created_at
"""

# ═══════════════════════════════════════════════════════════════
# TASK 3: VALIDATE & ADD CHEMISTRY SUBJECT
# ═══════════════════════════════════════════════════════════════

"""
WHAT TO DO:
-----------
1. Update Question_Data_valadating_script.py to check Chemistry folder
2. Run validation on all 9 Chemistry JSON files
3. If validation passes, add subject column to database
4. Insert all Chemistry chapters into database

STEPS:
------
1. Update Question_Data_valadating_script.py to scan Physics & Chemistry folders
2. Run: python Question_Data_valadating_script.py
3. If all valid, run SQL migration in Neon.tech
4. Run insert_chemistry_chapters.py to populate database
5. Update streamlit_app.py to support multi-subject selection

SQL COMMANDS (Run in Neon.tech console):
-----------------------------------------
-- Add subject column to chapters table
ALTER TABLE chapters ADD COLUMN IF NOT EXISTS subject VARCHAR(50) DEFAULT 'Physics';

-- Add subject to chapter_number unique constraint
ALTER TABLE chapters DROP CONSTRAINT IF EXISTS chapters_chapter_number_key;
ALTER TABLE chapters ADD CONSTRAINT chapters_subject_number_unique UNIQUE (subject, chapter_number);

FILES TO MODIFY:
----------------
- Question_Data_valadating_script.py - Scan both Physics & Chemistry
- schema_postgres.sql - Add subject column
- streamlit_app.py - Add subject selection UI
"""

# ═══════════════════════════════════════════════════════════════
# TASK 4: ADD SCHOOL/CLASS/BOARD FIELDS TO SIGNUP
# ═══════════════════════════════════════════════════════════════

"""
WHAT TO DO:
-----------
1. Add columns: school_name, class_name, board_name to users table
2. Update signup page to include these 3 mandatory fields
3. Update create_user() in auth.py to accept and save these fields
4. Update show_students_list() to display these fields

SQL COMMAND (Run in Neon.tech console):
----------------------------------------
ALTER TABLE users ADD COLUMN IF NOT EXISTS school_name VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS class_name VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS board_name VARCHAR(100);

FILES TO MODIFY:
----------------
- auth.py - Update create_user() signature and insert statement
- streamlit_app.py - Update signup_page() to collect 3 new fields
- streamlit_app.py - Update show_students_list() to display new fields
"""

# ═══════════════════════════════════════════════════════════════
# EXECUTION ORDER
# ═══════════════════════════════════════════════════════════════

print("""
RECOMMENDED EXECUTION ORDER:
============================

STEP 1: Database Schema Updates (Run in Neon.tech SQL Editor)
--------------------------------------------------------------
Run all_database_migrations.sql

STEP 2: Validate Chemistry Questions
-------------------------------------
python Question_Data_valadating_script.py

STEP 3: Insert Physics Omitted Chapters
----------------------------------------
python insert_omitted_chapters.py

STEP 4: Insert Chemistry Chapters
----------------------------------
python insert_chemistry_chapters.py

STEP 5: Update Application Code
--------------------------------
- Modify auth.py
- Modify streamlit_app.py

STEP 6: Test & Deploy
---------------------
1. Test locally
2. Git commit and push
3. Reboot Streamlit Cloud app
4. Test all features:
   ✓ Signup with new fields
   ✓ Admin sees timestamps and new fields
   ✓ Chapter 1 & 6 available for tests
   ✓ Chemistry subject available
""")
