import bcrypt
from db_connection import get_connection, get_placeholder, get_last_insert_id, USE_POSTGRES


def create_user(username, phone_number, password, role="student"):
    conn = get_connection()
    cur = conn.cursor()
    placeholder = get_placeholder()
    
    # Check if phone number already exists
    cur.execute(
        f"SELECT id FROM users WHERE phone_number = {placeholder}",
        (phone_number,)
    )
    if cur.fetchone():
        conn.close()
        return None  # Phone number already exists

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    # Handle RETURNING for PostgreSQL vs lastrowid for SQLite
    # Decode hash to string for storage
    if USE_POSTGRES:
        cur.execute(
            f"INSERT INTO users (username, phone_number, password_hash, role) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}) RETURNING id",
            (username, phone_number, hashed.decode('utf-8'), role)
        )
        user_id = cur.fetchone()[0]
    else:
        cur.execute(
            f"INSERT INTO users (username, phone_number, password_hash, role) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})",
            (username, phone_number, hashed.decode('utf-8'), role)
        )
        user_id = cur.lastrowid

    conn.commit()
    conn.close()
    return user_id


def login(username, password):
    conn = get_connection()
    cur = conn.cursor()
    placeholder = get_placeholder()

    cur.execute(
        f"SELECT id, username, password_hash, role FROM users WHERE username = {placeholder}",
        (username,)
    )
    user = cur.fetchone()

    conn.close()

    if user:
        # Handle both bytes and string password hashes
        stored_hash = user[2]
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode('utf-8')
        
        try:
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                return {
                    'id': user[0],
                    'username': user[1],
                    'role': user[3]
                }
        except Exception as e:
            print(f"bcrypt error: {e}")
    
    return None
