"""
Add email column to existing PostgreSQL database
Run this once to update the schema
"""
import psycopg2

print("\n" + "="*60)
print("PostgreSQL Email Column Migration")
print("="*60)
print("\nEnter your PostgreSQL connection details:")
print("(Find these in your Neon.tech dashboard)")
print()

host = input("Host: ").strip() or "ep-late-bonus-a12sc43w-pooler.ap-southeast-1.aws.neon.tech"
database = input("Database: ").strip() or "neondb"
user = input("User: ").strip() or "neondb_owner"
password = input("Password: ").strip()
port = input("Port (default 5432): ").strip() or "5432"

try:
    print("\nConnecting to PostgreSQL...")
    pg_conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password,
        port=port
    )
    pg_cur = pg_conn.cursor()
    
    print("Adding email column...")
    
    # Add email column (allow NULL initially)
    pg_cur.execute("""
        ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(255)
    """)
    
    # Set default emails for existing users
    pg_cur.execute("""
        UPDATE users 
        SET email = username || '@temporary.local' 
        WHERE email IS NULL
    """)
    
    # Make email NOT NULL
    pg_cur.execute("""
        ALTER TABLE users ALTER COLUMN email SET NOT NULL
    """)
    
    # Add UNIQUE constraint
    pg_cur.execute("""
        ALTER TABLE users ADD CONSTRAINT users_email_unique UNIQUE (email)
    """)
    
    pg_conn.commit()
    print("✅ Email column added successfully!")
    print("⚠️  Note: Existing users have temporary emails (username@temporary.local)")
    print("   Update them manually or ask users to re-register with real emails")
    
except Exception as e:
    print(f"❌ Error: {e}")
    if 'pg_conn' in locals():
        pg_conn.rollback()
        
finally:
    if 'pg_cur' in locals():
        pg_cur.close()
    if 'pg_conn' in locals():
        pg_conn.close()
