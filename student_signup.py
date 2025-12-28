from auth import create_user
import sqlite3

DB_PATH = r"C:\Users\Dell\Desktop\Harsh\Projects\classplus chatbot\database\quiz.db"

def signup_student(username, password, name, class_name):
    # create auth user
    user_id = create_user(username, password, "student")

    # create student profile
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO students (user_id, name, class) VALUES (?,?,?)",
        (user_id, name, class_name)
    )
    conn.commit()
    conn.close()
    return user_id

if __name__ == "__main__":
    uid = signup_student(
        username="student1",
        password="pass123",
        name="Student One",
        class_name="9-A"
    )
    print("Student created with user_id:", uid)
