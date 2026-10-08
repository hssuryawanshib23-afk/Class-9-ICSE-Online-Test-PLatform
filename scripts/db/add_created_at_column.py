"""
Add created_at column to users table if it doesn't exist
"""
from db_connection import get_connection

def add_created_at_column():
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Check if column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'created_at'
        """)
        
        if cur.fetchone():
            print("✓ created_at column already exists")
        else:
            print("Adding created_at column to users table...")
            cur.execute("""
                ALTER TABLE users 
                ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """)
            conn.commit()
            print("✅ created_at column added successfully!")
        
        # Update existing rows without created_at to have a timestamp
        cur.execute("""
            UPDATE users 
            SET created_at = CURRENT_TIMESTAMP 
            WHERE created_at IS NULL
        """)
        updated = cur.rowcount
        if updated > 0:
            conn.commit()
            print(f"✅ Updated {updated} existing users with current timestamp")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        conn.close()

if __name__ == "__main__":
    add_created_at_column()
