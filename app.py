from flask import Flask, render_template, request, redirect, session
import sqlite3

from auth import login, create_user
from generate_test_engine import generate_test

app = Flask(__name__)
app.secret_key = "supersecretkey"

DB_PATH = r"C:\Users\Dell\Desktop\Harsh\Projects\classplus chatbot\database\quiz.db"

# -------------------------
# AVALIABLE QUESTION CHECK
# -------------------------

def count_available_questions(chapters, difficulty):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    placeholders = ",".join("?" * len(chapters))

    query = f"""
        SELECT COUNT(DISTINCT q.id)
        FROM questions q
        JOIN concepts c ON q.concept_id = c.id
        JOIN chapters ch ON c.chapter_id = ch.id
        WHERE ch.chapter_number IN ({placeholders})
          AND q.difficulty = ?
    """

    cur.execute(query, (*chapters, difficulty))
    count = cur.fetchone()[0]

    conn.close()
    return count

# -------------------------
# HOME
# -------------------------
@app.route("/")
def home():
    if "user_id" not in session:
        return redirect("/login")

    if session["role"] == "admin":
        return redirect("/admin")

    return redirect("/test/setup")


# -------------------------
# AUTH
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        user = login(request.form["username"], request.form["password"])
        if user:
            session["user_id"] = user["user_id"]
            session["role"] = user["role"]
            return redirect("/")
        return "Invalid credentials"

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        try:
            user_id = create_user(
                request.form["username"],
                request.form["password"],
                "student"
            )

            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO students (user_id, name, class) VALUES (?,?,?)",
                (user_id, request.form["name"], request.form["class"])
            )
            conn.commit()
            conn.close()

            return redirect("/login")

        except Exception as e:
            return f"Signup failed: {e}"

    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# -------------------------
# TEST SETUP (STUDENT INPUT)
# -------------------------
@app.route("/test/setup", methods=["GET", "POST"])
def test_setup():
    if session.get("role") != "student":
        return redirect("/login")

    if request.method == "POST":
        chapters = request.form.getlist("chapters")
        if not chapters:
            return "Select at least one chapter"

        preset = request.form.get("preset")

        try:
            if preset == "50-50":
                before, after = 50, 50
            elif preset == "20-80":
                before, after = 20, 80
            elif preset == "30-70":
                before, after = 30, 70
            else:
                before = int(request.form.get("before", 0))
                after = int(request.form.get("after", 0))
        except ValueError:
            return "Invalid weightage values"

        if before + after > 100:
            return "Before + After weightage must not exceed 100"

        try:
            total = int(request.form["total"])
            time = int(request.form["time"])
        except ValueError:
            return "Invalid total questions or time"

        session["test_config"] = {
            "chapters": list(map(int, chapters)),
            "difficulty": request.form["difficulty"],
            "total": total,
            "time": time,
            "before": before,
            "after": after
        }

        return redirect("/test")

    return render_template("test_setup.html")


# -------------------------
# TEST GENERATION
# -------------------------
@app.route("/test")
def test():
    if session.get("role") != "student":
        return redirect("/login")

    cfg = session.get("test_config")
    if not cfg:
        return redirect("/test/setup")

    chapters = cfg["chapters"]
    difficulty = cfg["difficulty"]
    requested = cfg["total"]

    available = count_available_questions(chapters, difficulty)

    if available < requested:
        return render_template(
            "insufficient_questions.html",
            requested=requested,
            available=available,
            chapters=chapters,
            difficulty=difficulty
        )

    INPUT = {
        "chapters_before_mst": chapters,
        "chapters_after_mst": [],
        "weightage_before_mst": cfg["before"],
        "weightage_after_mst": cfg["after"],
        "total_questions": requested,
        "difficulty": difficulty,
        "time_minutes": cfg["time"]
    }

    questions = generate_test(INPUT)

    # HARD guarantee: trim or pad safely
    questions = questions[:requested]

    session["questions"] = questions

    return render_template(
        "test.html",
        questions=questions,
        time_minutes=cfg["time"]
    )


# -------------------------
# SUBMIT TEST
# -------------------------
@app.route("/submit", methods=["POST"])
def submit():
    if "user_id" not in session:
        return redirect("/login")

    questions = session.get("questions", [])
    if not questions:
        return redirect("/test")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    score = 0

    cur.execute(
        "INSERT INTO test_attempts (student_id, total_questions, score) VALUES (?,?,?)",
        (session["user_id"], len(questions), 0)
    )
    attempt_id = cur.lastrowid

    for q in questions:
        selected = request.form.get(str(q["question_id"]))
        correct = False

        for opt in q["options"]:
            if opt[0] == selected and opt[2]:
                correct = True
                score += 1

        cur.execute(
            """INSERT INTO responses
               (attempt_id, question_id, selected_label, is_correct)
               VALUES (?,?,?,?)""",
            (attempt_id, q["question_id"], selected, 1 if correct else 0)
        )

    cur.execute(
        "UPDATE test_attempts SET score=? WHERE id=?",
        (score, attempt_id)
    )

    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        score=score,
        total=len(questions)
    )


# -------------------------
# ADMIN DASHBOARD
# -------------------------
@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return "Unauthorized"

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT u.id, u.username
        FROM users u
        WHERE u.role = 'student'
        ORDER BY u.username
    """)
    students = cur.fetchall()

    reports = []

    for student_id, username in students:
        cur.execute("""
            SELECT ch.chapter_number,
                   COUNT(r.id),
                   SUM(r.is_correct)
            FROM responses r
            JOIN test_attempts t ON r.attempt_id = t.id
            JOIN questions q ON r.question_id = q.id
            JOIN concepts c ON q.concept_id = c.id
            JOIN chapters ch ON c.chapter_id = ch.id
            WHERE t.student_id = ?
            GROUP BY ch.chapter_number
            ORDER BY ch.chapter_number
        """, (student_id,))
        chapter_stats = cur.fetchall()

        cur.execute("""
            SELECT c.concept_name,
                   COUNT(r.id),
                   SUM(r.is_correct)
            FROM responses r
            JOIN test_attempts t ON r.attempt_id = t.id
            JOIN questions q ON r.question_id = q.id
            JOIN concepts c ON q.concept_id = c.id
            WHERE t.student_id = ?
            GROUP BY c.id
            HAVING (SUM(r.is_correct) * 1.0 / COUNT(r.id)) < 0.5
            ORDER BY (SUM(r.is_correct) * 1.0 / COUNT(r.id))
        """, (student_id,))
        weak_concepts = cur.fetchall()

        reports.append({
            "username": username,
            "chapter_stats": chapter_stats,
            "weak_concepts": weak_concepts
        })

    conn.close()

    return render_template(
        "admin.html",
        student_reports=reports
    )


# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    app.run(debug=False)
