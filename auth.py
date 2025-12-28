import bcrypt
from db_connection import get_connection


def create_user(username, password, role="student"):
    conn = get_connection()
    cur = conn.cursor()

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    # Use %s for both SQLite and PostgreSQL compatibility
    cur.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, hashed, role)
    )

    user_id = cur.lastrowid
    conn.commit()
    conn.close()
    return user_id


def login(username, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, username, password_hash, role FROM users WHERE username = ?",
        (username,)
    )
    user = cur.fetchone()

    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user[2]):
        return {
            'id': user[0],
            'username': user[1],
            'role': user[3]
        }
    return None
