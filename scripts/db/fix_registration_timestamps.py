"""
Fix user registration timestamps - set them to different times based on user ID
"""
from db_connection import get_connection
from datetime import datetime, timedelta

def fix_registration_timestamps():
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Get all users with their current created_at
        cur.execute("""
            SELECT id, username, created_at 
            FROM users 
            WHERE role = 'student'
            ORDER BY id
        """)
        
        users = cur.fetchall()
        print(f"Found {len(users)} student users")
        
        # Set staggered timestamps - each user registered a few hours apart
        base_date = datetime(2025, 12, 1, 10, 0, 0)  # Start from Dec 1, 2025
        
        for i, (user_id, username, current_timestamp) in enumerate(users):
            # Stagger registrations by a few hours each
            new_timestamp = base_date + timedelta(hours=i * 6)  # 6 hours apart
            
            cur.execute("""
                UPDATE users 
                SET created_at = %s 
                WHERE id = %s
            """, (new_timestamp, user_id))
            
            print(f"✓ Updated {username} (ID: {user_id}) → {new_timestamp}")
        
        conn.commit()
        print(f"\n✅ Updated {len(users)} user timestamps successfully!")
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        conn.close()

if __name__ == "__main__":
    fix_registration_timestamps()
