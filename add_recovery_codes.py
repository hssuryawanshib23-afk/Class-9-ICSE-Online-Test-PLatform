"""
Add recovery_code column and generate unique codes for all users
"""
from db_connection import get_connection
import random

def generate_numeric_code():
    """Generate 8-digit unique numeric code"""
    return str(random.randint(10000000, 99999999))

def add_recovery_codes():
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Check if column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'recovery_code'
        """)
        
        if not cur.fetchone():
            print("Adding recovery_code column...")
            cur.execute("""
                ALTER TABLE users 
                ADD COLUMN recovery_code VARCHAR(8)
            """)
            conn.commit()
            print("✅ recovery_code column added!")
        
        # Get all users without recovery codes
        cur.execute("""
            SELECT id, username 
            FROM users 
            WHERE recovery_code IS NULL
        """)
        
        users = cur.fetchall()
        print(f"\nGenerating codes for {len(users)} users...")
        
        for user_id, username in users:
            code = generate_numeric_code()
            cur.execute("""
                UPDATE users 
                SET recovery_code = %s 
                WHERE id = %s
            """, (code, user_id))
            print(f"✓ {username}: {code}")
        
        conn.commit()
        print(f"\n✅ Generated {len(users)} recovery codes!")
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        conn.close()

if __name__ == "__main__":
    add_recovery_codes()
