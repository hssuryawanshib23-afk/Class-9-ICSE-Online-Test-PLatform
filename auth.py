import bcrypt
from db_connection import get_connection


def create_user(username, email, password, role="student"):
    conn = get_connection()
    cur = conn.cursor()
    
    # Check if email already exists
    cur.execute(
        "SELECT id FROM users WHERE email = %s",
        (email,)
    )
    if cur.fetchone():
        conn.close()
        return None  # Email already exists

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    # Use RETURNING for PostgreSQL compatibility
    cur.execute(
        "INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s) RETURNING id",
        (username, email, hashed, role)
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
        # Handle both bytes and string password hashes
        stored_hash = user[2]
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode('utf-8')
        
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return {
                'id': user[0],
                'username': user[1],
                'role': user[3]
            }
    return None
