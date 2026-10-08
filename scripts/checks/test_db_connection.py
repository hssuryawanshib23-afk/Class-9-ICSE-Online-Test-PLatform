# Test Database Connection Script
# Run this to verify both SQLite (local) and PostgreSQL (hosted) work

from db_connection import get_connection, get_db_type, get_placeholder, USE_POSTGRES

def test_connection():
    print("=" * 60)
    print("DATABASE CONNECTION TEST")
    print("=" * 60)
    
    # Show current database type
    db_type = get_db_type()
    print(f"\n✅ Current Database: {db_type}")
    print(f"✅ USE_POSTGRES: {USE_POSTGRES}")
    print(f"✅ Placeholder: {get_placeholder()}")
    
    # Test connection
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Test basic query
        placeholder = get_placeholder()
        
        # Count users
        cur.execute("SELECT COUNT(*) FROM users")
        user_count = cur.fetchone()[0]
        print(f"\n📊 Total users: {user_count}")
        
        # Check if admin_tests table exists
        if USE_POSTGRES:
            cur.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_name = 'admin_tests'
            """)
        else:
            cur.execute("""
                SELECT COUNT(*) FROM sqlite_master 
                WHERE type='table' AND name='admin_tests'
            """)
        
        admin_table_exists = cur.fetchone()[0] > 0
        
        if admin_table_exists:
            print("✅ admin_tests table exists")
            
            # Count admin tests
            cur.execute("SELECT COUNT(*) FROM admin_tests")
            test_count = cur.fetchone()[0]
            print(f"📝 Total admin tests: {test_count}")
        else:
            print("❌ admin_tests table NOT found")
            print("⚠️  Run the migration SQL file first!")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ DATABASE CONNECTION SUCCESSFUL!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nTroubleshooting:")
        print("1. Check if database file exists (SQLite)")
        print("2. Check database credentials (PostgreSQL)")
        print("3. Run migration SQL if tables don't exist")
        return False

if __name__ == "__main__":
    test_connection()
