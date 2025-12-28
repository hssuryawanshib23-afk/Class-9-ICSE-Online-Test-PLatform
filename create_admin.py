from auth import create_user

try:
    uid = create_user("admin", "admin123", "admin")
    print("Admin created. User ID:", uid)
except Exception as e:
    print("Admin already exists or error:", e)
