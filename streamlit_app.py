import streamlit as st
import time

from auth import login, create_user
from generate_test_engine import generate_test
from db_connection import get_connection

st.set_page_config("Class 9 ICSE Test Platform", layout="wide")



def admin_page():
    st.title("📊 Admin Dashboard")

    conn = get_connection()
    cur = conn.cursor()

    # ---------------- GLOBAL STATS ----------------
    st.subheader("📈 Overall Statistics")

    cur.execute(
        "SELECT COUNT(*) FROM users WHERE role='student'"
    )
    total_students = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM test_attempts"
    )
    total_tests = cur.fetchone()[0]

    cur.execute(
        "SELECT AVG(score*1.0/total_questions) FROM test_attempts"
    )
    avg_score = cur.fetchone()[0]
    
    cur.execute(
        "SELECT COUNT(*) FROM responses"
    )
    total_questions_answered = cur.fetchone()[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 Total Students", total_students)
    col2.metric("📝 Total Tests", total_tests)
    col3.metric("✅ Avg Accuracy", f"{round((avg_score or 0)*100, 2)}%")
    col4.metric("❓ Questions Answered", total_questions_answered)

    st.divider()

    # ---------------- STUDENT-WISE DETAILED ----------------
    st.subheader("👨‍🎓 Student Performance Analysis")

    cur.execute("""
        SELECT 
            u.id,
            u.username,
            COUNT(t.id) AS tests_taken,
            ROUND(AVG(t.score*1.0/t.total_questions)*100, 2) AS avg_accuracy,
            MAX(t.score*1.0/t.total_questions)*100 AS best_score,
            MIN(t.score*1.0/t.total_questions)*100 AS worst_score,
            MAX(t.started_at) AS last_test_date
        FROM users u
        JOIN test_attempts t ON u.id = t.student_id
        WHERE u.role='student'
        GROUP BY u.id, u.username
        ORDER BY avg_accuracy DESC
    """)
    student_data = cur.fetchall()

    if student_data:
        # Display summary table
        student_summary = []
        for r in student_data:
            status = "🔥" if r[3] >= 80 else "✅" if r[3] >= 60 else "⚠️" if r[3] >= 40 else "🚨"
            student_summary.append({
                "Status": status,
                "Student": r[1],
                "Tests": r[2],
                "Avg %": f"{r[3]:.1f}",
                "Best %": f"{r[4]:.1f}",
                "Worst %": f"{r[5]:.1f}",
                "Last Test": r[6][:10] if r[6] else "N/A"
            })
        
        st.dataframe(student_summary, use_container_width=True)

        # Individual student drill-down
        st.markdown("---")
        st.subheader("🔍 Individual Student Deep Dive")
        
        selected_student = st.selectbox(
            "Select a student to view details:",
            options=[r[1] for r in student_data],
            index=0
        )
        
        # Get selected student's user_id
        student_id = next(r[0] for r in student_data if r[1] == selected_student)
        
        # Student's test history
        cur.execute("""
            SELECT 
                t.id,
                t.started_at,
                t.total_questions,
                t.score,
                ROUND(t.score*1.0/t.total_questions*100, 2) AS accuracy
            FROM test_attempts t
            WHERE t.student_id = %s
            ORDER BY t.started_at DESC
        """, (student_id,))
        test_history = cur.fetchall()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"**📋 Test History for {selected_student}**")
            if test_history:
                history_display = []
                for idx, t in enumerate(test_history, 1):
                    history_display.append({
                        "Test #": idx,
                        "Date": t[1][:16] if t[1] else "N/A",
                        "Questions": t[2],
                        "Score": f"{t[3]}/{t[2]}",
                        "Accuracy": f"{t[4]}%"
                    })
                st.dataframe(history_display, use_container_width=True)
        
        with col2:
            st.markdown(f"**📊 Chapter Performance for {selected_student}**")
            cur.execute("""
                SELECT 
                    ch.chapter_number,
                    ROUND(AVG(r.is_correct)*100, 2) AS accuracy,
                    COUNT(r.id) AS questions_attempted
                FROM responses r
                JOIN test_attempts t ON r.attempt_id = t.id
                JOIN questions q ON r.question_id = q.id
                JOIN concepts c ON q.concept_id = c.id
                JOIN chapters ch ON c.chapter_id = ch.id
                WHERE t.student_id = %s
                GROUP BY ch.chapter_number
                ORDER BY accuracy ASC
            """, (student_id,))
            student_chapters = cur.fetchall()
            
            if student_chapters:
                for ch in student_chapters:
                    emoji = "✅" if ch[1] >= 70 else "⚠️" if ch[1] >= 50 else "❌"
                    st.write(f"{emoji} Ch {ch[0]}: {ch[1]}% ({ch[2]} Qs)")
            else:
                st.info("No chapter data")

    else:
        st.info("No student test data yet.")

    st.divider()

    # ---------------- CHAPTER-WISE ANALYSIS ----------------
    st.subheader("📚 Chapter-wise Performance")

    cur.execute("""
        SELECT 
            ch.chapter_number,
            ROUND(AVG(r.is_correct)*100, 2) AS accuracy,
            COUNT(r.id) AS total_attempts,
            SUM(r.is_correct) AS correct_answers
        FROM responses r
        JOIN questions q ON r.question_id = q.id
        JOIN concepts c ON q.concept_id = c.id
        JOIN chapters ch ON c.chapter_id = ch.id
        GROUP BY ch.chapter_number
        ORDER BY ch.chapter_number
    """)
    chapter_df = cur.fetchall()

    if chapter_df:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.bar_chart(
                {f"Chapter {r[0]}": r[1] for r in chapter_df}
            )
        
        with col2:
            st.markdown("**📊 Chapter Stats**")
            for ch in chapter_df:
                status = "🟢" if ch[1] >= 70 else "🟡" if ch[1] >= 50 else "🔴"
                st.write(f"{status} **Ch {ch[0]}**: {ch[1]}% | {ch[3]}/{ch[2]} correct")
    else:
        st.info("No chapter data yet.")

    # ---------------- WEAK AREAS & RECOMMENDATIONS ----------------
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚨 Weak Chapters (<50%)")
        weak = [r for r in chapter_df if r[1] < 50]
        if weak:
            for ch in weak:
                st.error(f"**Chapter {ch[0]}**: {ch[1]}% accuracy ({ch[3]}/{ch[2]} correct)")
        else:
            st.success("✅ No weak chapters detected!")
    
    with col2:
        st.subheader("🏆 Top Performing Chapters")
        top = sorted([r for r in chapter_df if r[1] >= 70], key=lambda x: x[1], reverse=True)[:3]
        if top:
            for ch in top:
                st.success(f"**Chapter {ch[0]}**: {ch[1]}% accuracy ({ch[3]}/{ch[2]} correct)")
        else:
            st.info("No chapters with ≥70% yet")

    # ---------------- DIFFICULTY ANALYSIS ----------------
    st.divider()
    st.subheader("⚡ Difficulty Level Analysis")
    
    cur.execute("""
        SELECT 
            q.difficulty,
            COUNT(r.id) AS attempts,
            SUM(r.is_correct) AS correct,
            ROUND(AVG(r.is_correct)*100, 2) AS accuracy
        FROM responses r
        JOIN questions q ON r.question_id = q.id
        GROUP BY q.difficulty
        ORDER BY 
            CASE q.difficulty
                WHEN 'easy' THEN 1
                WHEN 'medium' THEN 2
                WHEN 'hard' THEN 3
            END
    """)
    difficulty_stats = cur.fetchall()
    
    if difficulty_stats:
        col1, col2, col3 = st.columns(3)
        for idx, diff in enumerate(difficulty_stats):
            with [col1, col2, col3][idx]:
                emoji = "🟢" if diff[0] == "easy" else "🟡" if diff[0] == "medium" else "🔴"
                st.metric(
                    f"{emoji} {diff[0].upper()}",
                    f"{diff[3]}%",
                    f"{diff[2]}/{diff[1]} correct"
                )

    # ---------------- CONCEPT-LEVEL ANALYSIS ----------------
    st.divider()
    st.subheader("🧠 Concept-Level Performance Analysis")
    
    # Get all concept stats
    cur.execute("""
        SELECT 
            c.id,
            c.concept_name,
            ch.chapter_number,
            COUNT(r.id) AS total_attempts,
            SUM(r.is_correct) AS correct_answers,
            ROUND(AVG(r.is_correct)*100, 2) AS accuracy
        FROM concepts c
        JOIN chapters ch ON c.chapter_id = ch.id
        LEFT JOIN questions q ON q.concept_id = c.id
        LEFT JOIN responses r ON r.question_id = q.id
        GROUP BY c.id, c.concept_name, ch.chapter_number
        HAVING total_attempts > 0
        ORDER BY accuracy ASC
    """)
    concept_stats = cur.fetchall()
    
    if concept_stats:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🚨 Struggling Concepts (Bottom 5)")
            weak_concepts = concept_stats[:5]
            for concept in weak_concepts:
                accuracy_color = "🔴" if concept[5] < 40 else "🟠"
                st.error(f"{accuracy_color} **{concept[1]}** (Ch {concept[2]})\n- Accuracy: {concept[5]}% ({concept[4]}/{concept[3]} correct)")
        
        with col2:
            st.markdown("### 🏆 Winning Concepts (Top 5)")
            strong_concepts = sorted(concept_stats, key=lambda x: x[5], reverse=True)[:5]
            for concept in strong_concepts:
                accuracy_color = "🟢" if concept[5] >= 80 else "🟡"
                st.success(f"{accuracy_color} **{concept[1]}** (Ch {concept[2]})\n- Accuracy: {concept[5]}% ({concept[4]}/{concept[3]} correct)")
        
        # Concept drill-down
        st.markdown("---")
        st.subheader("🔬 Concept Deep Dive: Student-Level Analysis")
        
        # Create a nice dropdown with concept names
        concept_options = {f"{c[1]} (Ch {c[2]}) - {c[5]}%": c[0] for c in concept_stats}
        selected_concept_display = st.selectbox(
            "Select a concept to see which students struggle:",
            options=list(concept_options.keys())
        )
        
        selected_concept_id = concept_options[selected_concept_display]
        
        # Get student performance for this concept
        cur.execute("""
            SELECT 
                u.username,
                COUNT(r.id) AS attempts,
                SUM(r.is_correct) AS correct,
                ROUND(AVG(r.is_correct)*100, 2) AS accuracy
            FROM responses r
            JOIN test_attempts t ON r.attempt_id = t.id
            JOIN users u ON t.student_id = u.id
            JOIN questions q ON r.question_id = q.id
            WHERE q.concept_id = %s
            GROUP BY u.username
            ORDER BY accuracy ASC, attempts DESC
        """, (selected_concept_id,))
        student_concept_performance = cur.fetchall()
        
        if student_concept_performance:
            st.markdown(f"**📊 Student Performance on: {selected_concept_display.split(' (Ch')[0]}**")
            
            # Separate into struggling and performing well
            struggling = [s for s in student_concept_performance if s[3] < 50]
            doing_well = [s for s in student_concept_performance if s[3] >= 70]
            
            col1, col2 = st.columns(2)
            
            with col1:
                if struggling:
                    st.markdown("**🚨 Students Struggling (<50%)**")
                    for student in struggling:
                        st.warning(f"• **{student[0]}**: {student[3]}% ({student[2]}/{student[1]} correct)")
                else:
                    st.success("✅ No students struggling with this concept!")
            
            with col2:
                if doing_well:
                    st.markdown("**🌟 Students Excelling (≥70%)**")
                    for student in doing_well:
                        st.success(f"• **{student[0]}**: {student[3]}% ({student[2]}/{student[1]} correct)")
                else:
                    st.info("No students excelling yet")
            
            # Full table view
            st.markdown("**📋 Complete Student List**")
            performance_table = []
            for s in student_concept_performance:
                status = "🔥" if s[3] >= 80 else "✅" if s[3] >= 60 else "⚠️" if s[3] >= 40 else "🚨"
                performance_table.append({
                    "Status": status,
                    "Student": s[0],
                    "Attempts": s[1],
                    "Correct": s[2],
                    "Accuracy": f"{s[3]}%"
                })
            st.dataframe(performance_table, use_container_width=True)
        else:
            st.info("No student data for this concept yet")
    else:
        st.info("No concept data available yet")

    conn.close()



# ================= SESSION =================
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.page = "login"
    st.session_state.test = None
    st.session_state.start_time = None
    st.session_state.answers = {}
    st.session_state.duration = None
    st.session_state.score = None

# ================= HELPERS =================
def get_available_count(chapters, difficulties):
    conn = get_connection()
    cur = conn.cursor()
    total = 0

    for d in difficulties:
        ch_p = ",".join("%s" * len(chapters))
        cur.execute(
            f"""
            SELECT COUNT(*)
            FROM questions q
            JOIN concepts c ON q.concept_id=c.id
            JOIN chapters ch ON c.chapter_id=ch.id
            WHERE ch.chapter_number IN ({ch_p})
              AND q.difficulty = %s
            """,
            (*chapters, d)
        )
        result = cur.fetchone()
        total += result[0]

    conn.close()
    return total

def logout():
    st.session_state.clear()
    st.session_state.page = "login"
    st.rerun()

# ================= SIDEBAR =================
if st.session_state.user:
    with st.sidebar:
        st.markdown(f"**Logged in as:** `{st.session_state.user['role']}`")
        if st.button("Logout", key="logout_btn"):
            logout()

# ================= AUTH =================
def login_page():
    st.title("Login")

    u = st.text_input("Username", key="login_username")
    p = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_btn"):
        user = login(u, p)
        if user:
            st.session_state.user = user
            st.session_state.page = "setup"
            st.rerun()
        else:
            st.error("Invalid credentials")

def signup_page():
    st.title("Signup")

    u = st.text_input("Username", key="signup_username")
    p = st.text_input("Password", type="password", key="signup_password")

    if st.button("Create account", key="signup_btn"):
        create_user(u, p, "student")
        st.success("Account created. Please login.")

# ================= SETUP =================
def setup_page():
    st.title("Test Setup")

    chapters = st.multiselect(
        "Chapters",
        [2,3,4,5,7,8,9,10],
        key="setup_chapters"
    )

    difficulties = st.multiselect(
        "Difficulty",
        ["easy","medium","hard"],
        default=["easy","medium","hard"],
        key="setup_difficulty"
    )

    st.subheader("Weightage")
    pre = st.number_input("Pre-MST (%)", 0, 100, 50, key="premst")
    post = st.number_input("Post-MST (%)", 0, 100, 50, key="postmst")

    if pre + post != 100:
        st.error("Pre-MST + Post-MST must equal 100%")
        return

    if not chapters or not difficulties:
        st.warning("Select chapters and difficulty")
        return

    available = get_available_count(chapters, difficulties)
    st.info(f"Available questions: {available}")

    if available == 0:
        return

    total = st.number_input(
        "Number of questions",
        min_value=1,
        max_value=available,
        value=min(30, available),
        key="total_questions"
    )

    duration = st.number_input(
        "Time (minutes)",
        5, 180, 60,
        key="test_duration"
    )

    if st.button("Start Test", key="start_test_btn"):
        questions = generate_test(chapters, difficulties, total)
        if questions is None:
            st.error("Not enough questions")
            return

        st.session_state.test = questions
        st.session_state.start_time = time.time()
        st.session_state.answers = {}
        st.session_state.duration = duration * 60
        st.session_state.page = "test"
        st.rerun()

# ================= TEST =================
def test_page():
    st.title("Test")

    elapsed = int(time.time() - st.session_state.start_time)
    remaining = st.session_state.duration - elapsed

    if remaining <= 0:
        submit_test(auto=True)
        return

    st.warning(f"⏳ Time left: {remaining//60}:{remaining%60:02d}")

    for i, q in enumerate(st.session_state.test, 1):
        st.markdown(f"**Q{i}. {q['text']}**")

        labels = [o[0] for o in q["options"]]
        label_map = {o[0]: o[1] for o in q["options"]}

        choice = st.radio(
            "",
            labels,
            index=None,
            format_func=lambda x: f"{x}. {label_map[x]}",
            key=f"q_{q['id']}"
        )
        st.session_state.answers[q["id"]] = choice

    if st.button("Submit Test", key="submit_test_btn"):
        submit_test(auto=False)

    # heartbeat rerun (Streamlit limitation)
    time.sleep(0.5)
    st.rerun()

def submit_test(auto=False):
    score = 0
    for q in st.session_state.test:
        qid = q["id"]
        sel = st.session_state.answers.get(qid)
        for opt in q["options"]:
            if opt[0] == sel and opt[2]:
                score += 1

    st.session_state.score = score
    
    # ===== SAVE TO DATABASE =====
    save_test_attempt(score, len(st.session_state.test))
    
    st.session_state.page = "result"
    st.rerun()

def save_test_attempt(score, total_questions):
    """Save test attempt and responses to database"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Enable foreign keys
    cur.execute("PRAGMA foreign_keys = ON")
    
    try:
        # Get user_id from username
        cur.execute(
            "SELECT id FROM users WHERE username = %s",
            (st.session_state.user['username'],)
        )
        user_id_result = cur.fetchone()
        
        if not user_id_result:
            st.error(f"❌ User not found in database!")
            return
        
        user_id = user_id_result[0]
        
        # Check if student record exists (CRITICAL FIX!)
        cur.execute(
            "SELECT user_id FROM students WHERE user_id = %s",
            (user_id,)
        )
        student_check = cur.fetchone()
        
        # Create student record if it doesn't exist
        if not student_check:
            cur.execute(
                "INSERT INTO students (user_id, name, class) VALUES (%s, %s, %s)",
                (user_id, st.session_state.user['username'], '9')
            )
            conn.commit()
        
        # Insert test attempt with correct column order
        cur.execute("""
            INSERT INTO test_attempts (student_id, total_questions, score, started_at)
            VALUES (%s, %s, %s, datetime('now'))
        """, (user_id, total_questions, score))
        
        attempt_id = cur.lastrowid
        
        # Insert individual responses
        for q in st.session_state.test:
            qid = q["id"]
            selected_label = st.session_state.answers.get(qid)
            
            # Check if answer is correct (use 1/0 for SQLite)
            is_correct = 0
            if selected_label:
                for opt in q["options"]:
                    if opt[0] == selected_label and opt[2]:
                        is_correct = 1
                        break
            
            cur.execute("""
                INSERT INTO responses (attempt_id, question_id, selected_label, is_correct)
                VALUES (%s, %s, %s, %s)
            """, (attempt_id, qid, selected_label, is_correct))
        
        conn.commit()
        
    except Exception as e:
        st.error(f"❌ Database error: {e}")
        conn.rollback()
        
    finally:
        conn.close()

# ================= RESULT =================
def result_page():
    st.title("Result")
    st.success(f"Score: {st.session_state.score} / {len(st.session_state.test)}")

    if st.button("Take another test", key="new_test_btn"):
        st.session_state.page = "setup"
        st.rerun()

# ================= ROUTER =================
if st.session_state.user is None:
    t1, t2 = st.tabs(["Login", "Signup"])
    with t1:
        login_page()
    with t2:
        signup_page()
else:
    if st.session_state.user["role"] == "admin":
        admin_page()
    else:
        if st.session_state.page == "setup":
            setup_page()
        elif st.session_state.page == "test":
            test_page()
        elif st.session_state.page == "result":
            result_page()

