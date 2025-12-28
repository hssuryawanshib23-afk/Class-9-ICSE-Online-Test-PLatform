import os

BASE = os.getcwd()

folders = [
    "templates",
    "static",
]

files = {
    "app.py": """from flask import Flask, render_template, request, redirect, session
from auth import login, create_user
from generate_test_engine import generate_test
import sqlite3, random

app = Flask(__name__)
app.secret_key = "supersecretkey"

DB_PATH = r"C:\\Users\\Dell\\Desktop\\Harsh\\Projects\\classplus chatbot\\database\\quiz.db"

@app.route("/", methods=["GET"])
def home():
    if "user" in session:
        if session["role"] == "admin":
            return redirect("/admin")
        return redirect("/test")
    return redirect("/login")

@app.route("/login", methods=["GET","POST"])
def login_page():
    if request.method == "POST":
        user = login(request.form["username"], request.form["password"])
        if user:
            session["user"] = user["user_id"]
            session["role"] = user["role"]
            return redirect("/")
        return "Invalid credentials"
    return render_template("login.html")

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        uid = create_user(
            request.form["username"],
            request.form["password"],
            "student"
        )
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO students (user_id, name, class) VALUES (?,?,?)",
            (uid, request.form["name"], request.form["class"])
        )
        conn.commit()
        conn.close()
        return redirect("/login")
    return render_template("signup.html")

@app.route("/test")
def test():
    if "user" not in session:
        return redirect("/login")

    INPUT = {
        "chapters_before_mst": [2,3,4],
        "chapters_after_mst": [5,7,8,9,10],
        "weightage_before_mst": 40,
        "weightage_after_mst": 60,
        "total_questions": 10,
        "difficulty": "medium",
        "time_minutes": 60
    }

    questions = generate_test(INPUT)
    session["questions"] = questions
    return render_template("test.html", questions=questions)

@app.route("/submit", methods=["POST"])
def submit():
    questions = session.get("questions", [])
    score = 0

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO test_attempts (student_id, total_questions, score) VALUES (?,?,?)",
        (session["user"], len(questions), 0)
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
            "INSERT INTO responses (attempt_id, question_id, selected_label, is_correct) VALUES (?,?,?,?)",
            (attempt_id, q["question_id"], selected, 1 if correct else 0)
        )

    cur.execute(
        "UPDATE test_attempts SET score=? WHERE id=?",
        (score, attempt_id)
    )
    conn.commit()
    conn.close()

    return render_template("result.html", score=score, total=len(questions))

@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return "Unauthorized"

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(\"\"\"
        SELECT u.username, t.score, t.total_questions, t.started_at
        FROM test_attempts t
        JOIN students s ON t.student_id = s.user_id
        JOIN users u ON s.user_id = u.id
        ORDER BY t.started_at DESC
    \"\"\")
    rows = cur.fetchall()
    conn.close()
    return render_template("admin.html", rows=rows)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
""",

    "templates/login.html": """<h2>Login</h2>
<form method="post">
<input name="username" placeholder="Username"><br>
<input name="password" type="password" placeholder="Password"><br>
<button>Login</button>
</form>
<a href="/signup">Signup</a>
""",

    "templates/signup.html": """<h2>Signup</h2>
<form method="post">
<input name="username" placeholder="Username"><br>
<input name="password" type="password" placeholder="Password"><br>
<input name="name" placeholder="Name"><br>
<input name="class" placeholder="Class"><br>
<button>Create Account</button>
</form>
""",

    "templates/test.html": """<h2>Test</h2>
<form method="post" action="/submit">
{% for q in questions %}
<p>{{ loop.index }}. {{ q.question_text }}</p>
{% for opt in q.options %}
<input type="radio" name="{{ q.question_id }}" value="{{ opt[0] }}"> {{ opt[0] }}. {{ opt[1] }}<br>
{% endfor %}
<hr>
{% endfor %}
<button>Submit</button>
</form>
""",

    "templates/result.html": """<h2>Result</h2>
<p>Score: {{ score }} / {{ total }}</p>
<a href="/logout">Logout</a>
""",

    "templates/admin.html": """<h2>Admin Dashboard</h2>
<table border="1">
<tr><th>User</th><th>Score</th><th>Total</th><th>Time</th></tr>
{% for r in rows %}
<tr>
<td>{{ r[0] }}</td><td>{{ r[1] }}</td><td>{{ r[2] }}</td><td>{{ r[3] }}</td>
</tr>
{% endfor %}
</table>
"""
}

# Create folders
for f in folders:
    os.makedirs(f, exist_ok=True)

# Create files
for path, content in files.items():
    with open(path, "w", encoding="utf-8") as fp:
        fp.write(content)

print("✅ Flask app scaffold created")
