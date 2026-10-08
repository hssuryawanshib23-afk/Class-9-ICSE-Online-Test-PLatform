"""
Apply admin test migration to local SQLite database
Run this script to add the admin test tables to your local database.
"""

import sqlite3
import os

def apply_migration():
    print("=" * 60)
    print("APPLYING ADMIN TEST MIGRATION TO SQLite")
    print("=" * 60)
    print()
    
    db_path = "database/quiz.db"
    sql_file = "add_admin_tests_sqlite.sql"
    
    # Check if files exist
    if not os.path.exists(db_path):
        print(f"❌ Error: Database file not found at: {db_path}")
        return False
    
    if not os.path.exists(sql_file):
        print(f"❌ Error: SQL file not found: {sql_file}")
        return False
    
    print(f"📂 Database: {db_path}")
    print(f"📄 SQL File: {sql_file}")
    print()
    
    # Read SQL file
    print("📖 Reading SQL file...")
    with open(sql_file, 'r') as f:
        sql = f.read()
    
    # Connect to database
    print("🔌 Connecting to database...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Use executescript to run entire SQL file at once
        # This properly handles multi-statement SQL files
        print("🔄 Executing migration...")
        cursor.executescript(sql)
        print("✅ Migration completed!")
        print()
        print("✅ All tables and indexes created successfully!")
        print()
        
        # Verify tables created
        print("📊 Verifying tables created...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'admin%'")
        tables = cursor.fetchall()
        
        if tables:
            print(f"✅ Found {len(tables)} admin tables:")
            for table in tables:
                # Count rows in each table
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"   - {table[0]} ({count} rows)")
        else:
            print("⚠️  Warning: No admin tables found after migration")
        
        return True
        
    except Exception as e:
        print()
        print(f"❌ Error: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    success = apply_migration()
    print()
    print("=" * 60)
    
    if success:
        print("🎉 MIGRATION COMPLETE!")
        print()
        print("Next steps:")
        print("1. Test connection: python test_db_connection.py")
        print("2. Run app: streamlit run streamlit_app.py")
    else:
        print("❌ MIGRATION FAILED!")
        print()
        print("Troubleshooting:")
        print("1. Check if database file exists")
        print("2. Check if SQL file exists")
        print("3. Make sure database is not locked")
    
    print("=" * 60)
