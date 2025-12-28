"""
Migration script to transfer data from SQLite to PostgreSQL
Run this ONCE after setting up PostgreSQL database
"""
import sqlite3
import psycopg2
import os
import re

# SQLite path
SQLITE_DB = os.path.join(os.path.dirname(__file__), "database", "quiz.db")

print("\n" + "="*60)
print("Choose connection method:")
print("1. Paste full connection string (easier)")
print("2. Enter credentials manually")
print("="*60)
choice = input("\nYour choice (1/2): ").strip()

if choice == "1":
    conn_string = input("\nPaste your PostgreSQL connection string: ").strip()
    
    # Remove 'psql' and quotes if present
    conn_string = conn_string.replace("psql", "").replace("'", "").strip()
    
    # Parse connection string: postgresql://user:password@host:port/database
    pattern = r'postgresql://([^:]+):([^@]+)@([^:/]+)(?::(\d+))?/([^\?]+)'
    match = re.match(pattern, conn_string)
    
    if match:
        PG_CONFIG = {
            "user": match.group(1),
            "password": match.group(2),
            "host": match.group(3),
            "port": match.group(4) or "5432",
            "database": match.group(5)
        }
        print(f"\n✅ Parsed connection:")
        print(f"   Host: {PG_CONFIG['host']}")
        print(f"   Database: {PG_CONFIG['database']}")
        print(f"   User: {PG_CONFIG['user']}")
        print(f"   Port: {PG_CONFIG['port']}")
    else:
        print("❌ Invalid connection string format!")
        exit(1)
else:
    # Manual entry
    PG_CONFIG = {
        "host": input("PostgreSQL Host: "),
        "database": input("Database Name: "),
        "user": input("Username: "),
        "password": input("Password: "),
        "port": input("Port (default 5432): ") or "5432"
    }

def migrate_data():
    print("🔄 Starting migration from SQLite to PostgreSQL...")
    
    # Connect to both databases
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    pg_conn = psycopg2.connect(**PG_CONFIG)
    
    sqlite_cur = sqlite_conn.cursor()
    pg_cur = pg_conn.cursor()
    
    try:
        # Clear existing data first (in correct order to avoid FK violations)
        print("🧹 Clearing existing data...")
        pg_cur.execute("DELETE FROM responses")
        pg_cur.execute("DELETE FROM test_attempts")
        pg_cur.execute("DELETE FROM mcq_options")
        pg_cur.execute("DELETE FROM questions")
        pg_cur.execute("DELETE FROM concepts")
        pg_cur.execute("DELETE FROM chapters")
        pg_cur.execute("DELETE FROM students")
        pg_cur.execute("DELETE FROM users")
        pg_conn.commit()
        print("   ✅ Cleared existing data")
        
        # 1. Migrate users (preserve IDs)
        print("📦 Migrating users...")
        sqlite_cur.execute("SELECT id, username, password_hash, role FROM users")
        users = sqlite_cur.fetchall()
        
        user_ids = []
        for user in users:
            # Convert bytes to string if needed
            password_hash = user[2]
            if isinstance(password_hash, bytes):
                password_hash = password_hash.decode('utf-8')
            
            pg_cur.execute(
                "INSERT INTO users (id, username, password_hash, role) VALUES (%s, %s, %s, %s)",
                (user[0], user[1], password_hash, user[3])
            )
            user_ids.append(user[0])
        
        pg_conn.commit()
        
        # Verify users were inserted
        pg_cur.execute("SELECT id FROM users ORDER BY id")
        inserted_users = [row[0] for row in pg_cur.fetchall()]
        print(f"   ✅ Migrated {len(users)} users (IDs: {inserted_users})")
        
        # 2. Migrate students
        print("📦 Migrating students...")
        sqlite_cur.execute("SELECT user_id, name, class FROM students")
        students = sqlite_cur.fetchall()
        
        for student in students:
            student_user_id = student[0]
            if student_user_id not in inserted_users:
                print(f"   ⚠️  Skipping student with user_id={student_user_id} (user doesn't exist)")
                continue
                
            pg_cur.execute(
                "INSERT INTO students (user_id, name, class) VALUES (%s, %s, %s)",
                student
            )
        
        pg_conn.commit()
        print(f"   ✅ Migrated {len(students)} students")
        
        # 3. Migrate chapters
        print("📦 Migrating chapters...")
        sqlite_cur.execute("SELECT id, chapter_number FROM chapters")
        chapters = sqlite_cur.fetchall()
        for chapter in chapters:
            pg_cur.execute(
                "INSERT INTO chapters (id, chapter_number) VALUES (%s, %s)",
                chapter
            )
        pg_conn.commit()
        print(f"   ✅ Migrated {len(chapters)} chapters")
        
        # 4. Migrate concepts
        print("📦 Migrating concepts...")
        sqlite_cur.execute("SELECT id, chapter_id, concept_name FROM concepts")
        concepts = sqlite_cur.fetchall()
        for concept in concepts:
            pg_cur.execute(
                "INSERT INTO concepts (id, chapter_id, concept_name) VALUES (%s, %s, %s)",
                concept
            )
        pg_conn.commit()
        print(f"   ✅ Migrated {len(concepts)} concepts")
        
        # 5. Migrate questions
        print("📦 Migrating questions...")
        sqlite_cur.execute("SELECT id, concept_id, difficulty, question_text FROM questions")
        questions = sqlite_cur.fetchall()
        for question in questions:
            pg_cur.execute(
                "INSERT INTO questions (id, concept_id, difficulty, question_text) VALUES (%s, %s, %s, %s)",
                question
            )
        pg_conn.commit()
        print(f"   ✅ Migrated {len(questions)} questions")
        
        # 6. Migrate mcq_options
        print("📦 Migrating MCQ options...")
        sqlite_cur.execute("SELECT id, question_id, label, option_text, is_correct FROM mcq_options")
        options = sqlite_cur.fetchall()
        for option in options:
            pg_cur.execute(
                "INSERT INTO mcq_options (id, question_id, label, option_text, is_correct) VALUES (%s, %s, %s, %s, %s)",
                option
            )
        pg_conn.commit()
        print(f"   ✅ Migrated {len(options)} MCQ options")
        
        # 7. Migrate test_attempts
        print("📦 Migrating test attempts...")
        sqlite_cur.execute("SELECT id, student_id, total_questions, score, started_at FROM test_attempts")
        attempts = sqlite_cur.fetchall()
        for attempt in attempts:
            pg_cur.execute(
                "INSERT INTO test_attempts (id, student_id, total_questions, score, started_at) VALUES (%s, %s, %s, %s, %s)",
                attempt
            )
        pg_conn.commit()
        print(f"   ✅ Migrated {len(attempts)} test attempts")
        
        # 8. Migrate responses
        print("📦 Migrating responses...")
        sqlite_cur.execute("SELECT id, attempt_id, question_id, selected_label, is_correct FROM responses")
        responses = sqlite_cur.fetchall()
        for response in responses:
            pg_cur.execute(
                "INSERT INTO responses (id, attempt_id, question_id, selected_label, is_correct) VALUES (%s, %s, %s, %s, %s)",
                response
            )
        pg_conn.commit()
        print(f"   ✅ Migrated {len(responses)} responses")
        
        # Update sequences for auto-increment
        print("🔧 Updating PostgreSQL sequences...")
        tables = ['users', 'chapters', 'concepts', 'questions', 'mcq_options', 'test_attempts', 'responses']
        for table in tables:
            pg_cur.execute(f"SELECT MAX(id) FROM {table}")
            max_id = pg_cur.fetchone()[0]
            if max_id:
                pg_cur.execute(f"SELECT setval('{table}_id_seq', {max_id})")
        
        pg_conn.commit()
        print("\n✅ Migration completed successfully!")
        print("\n📋 Summary:")
        print(f"   Users: {len(users)}")
        print(f"   Students: {len(students)}")
        print(f"   Chapters: {len(chapters)}")
        print(f"   Concepts: {len(concepts)}")
        print(f"   Questions: {len(questions)}")
        print(f"   MCQ Options: {len(options)}")
        print(f"   Test Attempts: {len(attempts)}")
        print(f"   Responses: {len(responses)}")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        pg_conn.rollback()
        
    finally:
        sqlite_conn.close()
        pg_conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("SQLite → PostgreSQL Migration Tool")
    print("=" * 60)
    print("\nMake sure you've:")
    print("1. Created a PostgreSQL database")
    print("2. Run schema_postgres.sql to create tables")
    print("3. Have your PostgreSQL credentials ready\n")
    
    confirm = input("Ready to migrate? (yes/no): ")
    if confirm.lower() == "yes":
        migrate_data()
    else:
        print("Migration cancelled.")
