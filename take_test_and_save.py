import random
import sqlite3
from auth import login
from generate_test_engine import generate_test

DB_PATH = r"C:\Users\Dell\Desktop\Harsh\Projects\classplus chatbot\database\quiz.db"

INPUT = {
    "chapters_before_mst": [2,3,4],
    "chapters_after_mst": [5,7,8,9,10],
    "weightage_before_mst": 40,
    "weightage_after_mst": 60,
    "total_questions": 10,
    "difficulty": "medium",
    "time_minutes": 60
}

def save_attempt(student_user_id, responses):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    score = sum(1 for r in responses if r["is_correct"])

    cur.execute(
        "INSERT INTO test_attempts (student_id, total_questions, score) VALUES (?,?,?)",
        (student_user_id, len(responses), score)
    )
    attempt_id = cur.lastrowid

    for r in responses:
        cur.execute(
            "INSERT INTO responses (attempt_id, question_id, selected_label, is_correct) VALUES (?,?,?,?)",
            (attempt_id, r["question_id"], r["selected"], 1 if r["is_correct"] else 0)
        )

    conn.commit()
    conn.close()
    return attempt_id, score

if __name__ == "__main__":
    auth = login("student1", "pass123")
    assert auth and auth["role"] == "student"

    test = generate_test(INPUT)

    # simulate answers
    responses = []
    for q in test:
        choice = random.choice(q["options"])
        responses.append({
            "question_id": q["question_id"],
            "selected": choice[0],
            "is_correct": choice[2]
        })

    attempt_id, score = save_attempt(auth["user_id"], responses)
    print(f"Attempt saved. ID={attempt_id}, Score={score}/{len(responses)}")
