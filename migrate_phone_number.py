"""
Add phone_number column to existing PostgreSQL database
Run this once to update the schema on Neon.tech
"""
import psycopg2

# Your Neon.tech credentials
HOST = "ep-late-bonus-a12sc43w-pooler.ap-southeast-1.aws.neon.tech"
DATABASE = "neondb"
USER = "neondb_owner"
PASSWORD = "npg_N1WsLrbnM5iX"
PORT = "5432"

print("\n" + "="*60)
print("PostgreSQL Phone Number Column Migration")
print("="*60)

try:
    print("\nConnecting to PostgreSQL...")
    pg_conn = psycopg2.connect(
        host=HOST,
        database=DATABASE,
        user=USER,
        password=PASSWORD,
        port=PORT
    )
    pg_cur = pg_conn.cursor()
    
    print("Adding phone_number column...")
    
    # Add phone_number column (allow NULL initially)
    pg_cur.execute("""
        ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_number VARCHAR(15)
    """)
    
    # Set default phone numbers for existing users (9999 + padded user_id)
    pg_cur.execute("""
        UPDATE users 
        SET phone_number = '9999' || LPAD(id::text, 6, '0')
        WHERE phone_number IS NULL
    """)
    
    # Make phone_number NOT NULL
    pg_cur.execute("""
        ALTER TABLE users ALTER COLUMN phone_number SET NOT NULL
    """)
    
    # Add UNIQUE constraint (check if it exists first)
    pg_cur.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'users_phone_number_unique'
            ) THEN
                ALTER TABLE users ADD CONSTRAINT users_phone_number_unique UNIQUE (phone_number);
            END IF;
        END $$
    """)
    
    pg_conn.commit()
    print("\n✅ Phone number column added successfully!")
    print("⚠️  Note: Existing users have temporary phone numbers (9999XXXXXX)")
    print("   Update them manually or ask users to re-register with real phone numbers\n")
    
except Exception as e:
    print(f"\n❌ Error: {e}\n")
    if 'pg_conn' in locals():
        pg_conn.rollback()
        
finally:
    if 'pg_cur' in locals():
        pg_cur.close()
    if 'pg_conn' in locals():
        pg_conn.close()
