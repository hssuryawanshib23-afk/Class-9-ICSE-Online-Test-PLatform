"""
Quick script to add a new admin user
Usage: python add_admin.py
"""
from auth import create_user

def add_admin():
    print("=== Add New Admin ===")
    username = input("Enter admin username: ").strip()
    password = input("Enter admin password: ").strip()
    
    if not username or not password:
        print("❌ Username and password cannot be empty!")
        return
    
    try:
        user_id = create_user(username, password, role="admin")
        print(f"✅ Admin '{username}' created successfully! (ID: {user_id})")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("(Username might already exist)")

if __name__ == "__main__":
    add_admin()
