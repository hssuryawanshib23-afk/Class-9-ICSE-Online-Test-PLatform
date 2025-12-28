import bcrypt
from db_connection import get_connection


def create_user(username, phone_number, password, role="student"):
    conn = get_connection()
    cur = conn.cursor()
    
    # Check if phone number already exists
    cur.execute(
        "SELECT id FROM users WHERE phone_number = %s",
        (phone_number,)
    )
    if cur.fetchone():
        conn.close()
        return None  # Phone number already exists

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    # Use RETURNING for PostgreSQL compatibility
    # Decode hash to string for PostgreSQL storage
    cur.execute(
        "INSERT INTO users (username, phone_number, password_hash, role) VALUES (%s, %s, %s, %s) RETURNING id",
        (username, phone_number, hashed.decode('utf-8'), role)
    )

    user_id = cur.fetchone()[0]
    conn.commit()
    conn.close()
    return user_id


def login(username, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, username, password_hash, role FROM users WHERE username = %s",
        (username,)
    )
    user = cur.fetchone()

    conn.close()

    if user:
        # DEBUG: Print user info
        print(f"DEBUG: User found: id={user[0]}, username={user[1]}, role={user[3]}")
        print(f"DEBUG: Stored hash type: {type(user[2])}")
        print(f"DEBUG: Stored hash length: {len(user[2]) if user[2] else 0}")
        print(f"DEBUG: First 20 chars of hash: {str(user[2])[:20]}")
        
        # Handle both bytes and string password hashes
        stored_hash = user[2]
        if isinstance(stored_hash, str):
            print(f"DEBUG: Converting string hash to bytes")
            stored_hash = stored_hash.encode('utf-8')
        
        try:
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                print(f"DEBUG: Password match successful!")
                return {
                    'id': user[0],
                    'username': user[1],
                    'role': user[3]
                }
            else:
                print(f"DEBUG: Password mismatch")
        except Exception as e:
            print(f"DEBUG: bcrypt error: {e}")
    else:
        print(f"DEBUG: No user found with username: {username}")
    
    return None
