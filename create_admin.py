"""
Create a new admin user in PostgreSQL database
Run this to create a fresh admin account
"""
import bcrypt
import psycopg2

# Your Neon.tech credentials
HOST = "ep-late-bonus-a12sc43w-pooler.ap-southeast-1.aws.neon.tech"
DATABASE = "neondb"
USER = "neondb_owner"
PASSWORD = "npg_N1WsLrbnM5iX"
PORT = "5432"

print("\n" + "="*60)
print("Create New Admin Account")
print("="*60)

admin_username = input("Admin Username: ").strip() or "admin"
admin_phone = input("Admin Phone (10 digits): ").strip() or "9999000001"
admin_password = input("Admin Password: ").strip() or "admin123"

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
    
    # Hash the password properly
    hashed = bcrypt.hashpw(admin_password.encode(), bcrypt.gensalt())
    
    print(f"Creating admin: {admin_username}")
    
    # Insert admin user
    pg_cur.execute("""
        INSERT INTO users (username, phone_number, password_hash, role)
        VALUES (%s, %s, %s, 'admin')
        RETURNING id
    """, (admin_username, admin_phone, hashed.decode('utf-8')))
    
    admin_id = pg_cur.fetchone()[0]
    
    pg_conn.commit()
    
    print(f"\n✅ Admin account created successfully!")
    print(f"   Username: {admin_username}")
    print(f"   Phone: {admin_phone}")
    print(f"   Password: {admin_password}")
    print(f"   ID: {admin_id}\n")
    
except Exception as e:
    print(f"\n❌ Error: {e}\n")
    if 'pg_conn' in locals():
        pg_conn.rollback()
        
finally:
    if 'pg_cur' in locals():
        pg_cur.close()
    if 'pg_conn' in locals():
        pg_conn.close()
