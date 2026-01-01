import streamlit as st
import time

from auth import login, create_user
from generate_test_engine import (
    generate_test, 
    generate_test_with_difficulty_cap,
    create_admin_test,
    get_admin_test_questions,
    get_available_admin_tests
)
from db_connection import get_connection, get_placeholder, USE_POSTGRES

st.set_page_config("Class 9 ICSE Test Platform", layout="wide")



def admin_page():
    st.title("📊 Admin Dashboard")
    
    # Create tabs for different admin functions
    tab1, tab2, tab3 = st.tabs(["📈 Statistics", "📝 Create Test", "🗂️ Manage Tests"])
    
    with tab1:
        show_admin_statistics()
    
    with tab2:
        create_test_interface()
    
    with tab3:
        manage_tests_interface()


def show_admin_statistics():
    """Display admin statistics (original admin_page content)"""

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
                "Last Test": str(r[6])[:10] if r[6] else "N/A"
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
        placeholder = get_placeholder()
        cur.execute(f"""
            SELECT 
                t.id,
                t.started_at,
                t.total_questions,
                t.score,
                ROUND(t.score*1.0/t.total_questions*100, 2) AS accuracy
            FROM test_attempts t
            WHERE t.student_id = {placeholder}
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
                        "Date": str(t[1])[:16] if t[1] else "N/A",
                        "Questions": t[2],
                        "Score": f"{t[3]}/{t[2]}",
                        "Accuracy": f"{t[4]}%"
                    })
                st.dataframe(history_display, use_container_width=True)
        
        with col2:
            st.markdown(f"**📊 Chapter Performance for {selected_student}**")
            cur.execute(f"""
                SELECT 
                    ch.chapter_number,
                    ROUND(AVG(r.is_correct)*100, 2) AS accuracy,
                    COUNT(r.id) AS questions_attempted
                FROM responses r
                JOIN test_attempts t ON r.attempt_id = t.id
                JOIN questions q ON r.question_id = q.id
                JOIN concepts c ON q.concept_id = c.id
                JOIN chapters ch ON c.chapter_id = ch.id
                WHERE t.student_id = {placeholder}
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
        HAVING COUNT(r.id) > 0
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
        placeholder = get_placeholder()
        cur.execute(f"""
            SELECT 
                u.username,
                COUNT(r.id) AS attempts,
                SUM(r.is_correct) AS correct,
                ROUND(AVG(r.is_correct)*100, 2) AS accuracy
            FROM responses r
            JOIN test_attempts t ON r.attempt_id = t.id
            JOIN users u ON t.student_id = u.id
            JOIN questions q ON r.question_id = q.id
            WHERE q.concept_id = {placeholder}
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


def create_test_interface():
    """Admin interface to create tests with full control"""
    st.subheader("📝 Create New Test")
    st.markdown("Create a test that will be visible to all students")
    
    # Test metadata
    test_name = st.text_input("Test Name", placeholder="e.g., Chapter 2-5 Practice Test")
    
    # Chapter selection
    chapters = st.multiselect(
        "Select Chapters",
        [2, 3, 4, 5, 7, 8, 9, 10],
        help="Choose which chapters to include"
    )
    
    # Difficulty distribution
    st.markdown("### ⚡ Difficulty Distribution")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        easy_pct = st.number_input("🟢 Easy %", 0, 100, 30, step=5)
    with col2:
        medium_pct = st.number_input("🟡 Medium %", 0, 100, 30, step=5)
    with col3:
        hard_pct = st.number_input("🔴 Hard %", 0, 100, 40, step=5)
    
    total_pct = easy_pct + medium_pct + hard_pct
    if total_pct != 100:
        st.error(f"❌ Total percentage must equal 100% (currently {total_pct}%)")
    else:
        st.success(f"✅ Distribution: {easy_pct}% Easy, {medium_pct}% Medium, {hard_pct}% Hard")
    
    # Test parameters
    col1, col2 = st.columns(2)
    with col1:
        total_questions = st.number_input("Total Questions", 5, 100, 30, help="Total number of questions in the test")
    with col2:
        duration = st.number_input("Duration (minutes)", 5, 180, 60, help="Time limit for the test")
    
    # Show breakdown
    if total_questions > 0:
        easy_count = round(total_questions * easy_pct / 100)
        medium_count = round(total_questions * medium_pct / 100)
        hard_count = total_questions - easy_count - medium_count
        
        st.info(f"📊 Question Breakdown: {easy_count} Easy + {medium_count} Medium + {hard_count} Hard = {total_questions} Total")
    
    # Create test button
    if st.button("🚀 Create Test", type="primary", disabled=(total_pct != 100 or not chapters or not test_name)):
        with st.spinner("Creating test..."):
            try:
                admin_test_id = create_admin_test(
                    test_name=test_name,
                    chapters=chapters,
                    total_questions=total_questions,
                    duration_minutes=duration,
                    easy_pct=easy_pct,
                    medium_pct=medium_pct,
                    hard_pct=hard_pct,
                    created_by_user_id=st.session_state.user['id']
                )
                
                if admin_test_id:
                    st.success(f"✅ Test '{test_name}' created successfully! (ID: {admin_test_id})")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Not enough questions available with the selected criteria. Try adjusting difficulty percentages or chapters.")
            except Exception as e:
                st.error(f"❌ Error creating test: {e}")


def manage_tests_interface():
    """Interface to view and manage existing admin tests"""
    st.subheader("🗂️ Manage Tests")
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Get all admin tests
    cur.execute("""
        SELECT 
            at.admin_test_id, at.test_name, at.total_questions,
            at.duration_minutes, at.easy_percentage, at.medium_percentage,
            at.hard_percentage, at.chapters, at.is_active, u.username,
            at.created_at,
            COUNT(DISTINCT ata.attempt_id) as attempts_count,
            ROUND(AVG(ata.score * 1.0 / ata.total_questions) * 100, 2) as avg_score
        FROM admin_tests at
        JOIN users u ON at.created_by = u.id
        LEFT JOIN admin_test_attempts ata ON at.admin_test_id = ata.admin_test_id
        GROUP BY at.admin_test_id, at.test_name, at.total_questions,
                 at.duration_minutes, at.easy_percentage, at.medium_percentage,
                 at.hard_percentage, at.chapters, at.is_active, u.username, at.created_at
        ORDER BY at.created_at DESC
    """)
    
    tests = cur.fetchall()
    
    if not tests:
        st.info("No tests created yet. Create your first test in the 'Create Test' tab!")
        conn.close()
        return
    
    # Display tests
    for test in tests:
        test_id, name, total_q, duration, easy, med, hard, chapters, is_active, creator, created_at, attempts, avg_score = test
        
        with st.expander(f"{'✅' if is_active else '❌'} {name} ({total_q} questions, {duration} min)"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Chapters:** {chapters}")
                st.markdown(f"**Difficulty:** 🟢 {easy}% Easy, 🟡 {med}% Medium, 🔴 {hard}% Hard")
                st.markdown(f"**Created by:** {creator} on {str(created_at)[:16]}")
                st.markdown(f"**Attempts:** {attempts} | **Avg Score:** {avg_score or 0}%")
            
            with col2:
                # Toggle active/inactive
                placeholder = get_placeholder()
                active_val = "false" if USE_POSTGRES else "0"
                inactive_val = "true" if USE_POSTGRES else "1"
                
                if is_active:
                    if st.button(f"🚫 Deactivate", key=f"deactivate_{test_id}"):
                        cur.execute(f"UPDATE admin_tests SET is_active = {active_val} WHERE admin_test_id = {placeholder}", (test_id,))
                        conn.commit()
                        st.success("Test deactivated")
                        time.sleep(0.5)
                        st.rerun()
                else:
                    if st.button(f"✅ Activate", key=f"activate_{test_id}"):
                        cur.execute(f"UPDATE admin_tests SET is_active = {inactive_val} WHERE admin_test_id = {placeholder}", (test_id,))
                        conn.commit()
                        st.success("Test activated")
                        time.sleep(0.5)
                        st.rerun()
                
                # Delete test
                if st.button(f"🗑️ Delete", key=f"delete_{test_id}", type="secondary"):
                    cur.execute(f"DELETE FROM admin_tests WHERE admin_test_id = {placeholder}", (test_id,))
                    conn.commit()
                    st.warning("Test deleted")
                    time.sleep(0.5)
                    st.rerun()
            
            # Results section
            st.markdown("---")
            st.markdown("### 📊 Test Results")
            
            # Use checkbox instead of button to avoid nesting issues
            if st.checkbox(f"Show Detailed Results", key=f"results_{test_id}"):
                show_test_results(test_id, name, total_q)
    
    conn.close()


def show_test_results(test_id, test_name, total_questions):
    """Show detailed results for a specific test"""
    
    conn = get_connection()
    cur = conn.cursor()
    placeholder = get_placeholder()
    
    # Get all students and their attempts
    cur.execute(f"""
        SELECT 
            u.id, u.username,
            ata.attempt_id, ata.score, ata.percentage, ata.attempted_at
        FROM users u
        LEFT JOIN admin_test_attempts ata ON u.id = ata.user_id AND ata.admin_test_id = {placeholder}
        WHERE u.role = 'student'
        ORDER BY ata.attempted_at DESC, u.username
    """, (test_id,))
    
    results = cur.fetchall()
    
    if not results:
        st.info("No students in the system yet.")
        conn.close()
        return
    
    # Separate attempted and not attempted
    attempted = [r for r in results if r[2] is not None]
    not_attempted = [r for r in results if r[2] is None]
    
    # Show stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📝 Total Students", len(results))
    with col2:
        st.metric("✅ Attempted", len(attempted))
    with col3:
        st.metric("⏳ Pending", len(not_attempted))
    
    # Attempted students table - use containers instead of expanders
    if attempted:
        st.markdown("#### ✅ Students Who Attempted")
        
        for user_id, username, attempt_id, score, percentage, attempted_at in attempted:
            # Use container with custom styling instead of expander
            emoji = '🌟' if percentage >= 80 else '✅' if percentage >= 60 else '⚠️'
            
            with st.container():
                st.markdown(f"**{emoji} {username} - {percentage}% ({score}/{total_questions})**")
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown(f"**Score:** {score}/{total_questions}")
                    st.markdown(f"**Percentage:** {percentage}%")
                    st.markdown(f"**Attempted:** {str(attempted_at)[:16]}")
                
                with col2:
                    # Get weak concepts/chapters
                    cur.execute(f"""
                        SELECT 
                            ch.chapter_number,
                            COUNT(r.response_id) as total,
                            SUM(r.is_correct) as correct,
                            ROUND(AVG(r.is_correct) * 100, 1) as accuracy
                        FROM admin_test_responses r
                        JOIN questions q ON r.question_id = q.id
                        JOIN concepts c ON q.concept_id = c.id
                        JOIN chapters ch ON c.chapter_id = ch.id
                        WHERE r.attempt_id = {placeholder}
                        GROUP BY ch.chapter_number
                        HAVING AVG(r.is_correct) * 100 < 60
                        ORDER BY AVG(r.is_correct) ASC
                    """, (attempt_id,))
                    
                    weak_chapters = cur.fetchall()
                    
                    if weak_chapters:
                        st.markdown("**⚠️ Needs Improvement:**")
                        for ch_num, total, correct, acc in weak_chapters:
                            st.markdown(f"- Chapter {ch_num}: {acc}% ({correct}/{total} correct)")
                    else:
                        st.markdown("**🎉 Strong performance across all chapters!**")
                
                st.markdown("---")  # Separator between students
    
    # Not attempted students
    if not_attempted:
        st.markdown("#### ⏳ Students Who Haven't Attempted")
        not_attempted_names = [r[1] for r in not_attempted]
        st.markdown(", ".join(not_attempted_names))
    
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
    
    placeholder = get_placeholder()

    for d in difficulties:
        ch_p = ",".join([placeholder] * len(chapters))
        cur.execute(
            """
            SELECT COUNT(*)
            FROM questions q
            JOIN concepts c ON q.concept_id=c.id
            JOIN chapters ch ON c.chapter_id=ch.id
            WHERE ch.chapter_number IN ({})
              AND q.difficulty = {}
            """.format(ch_p, placeholder),
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
            st.error("❌ Invalid username or password")

def signup_page():
    st.title("Signup")

    u = st.text_input("Username", key="signup_username")
    p = st.text_input("Phone Number (10 digits - used to prevent duplicate accounts)", key="signup_phone", max_chars=10)
    pw = st.text_input("Password", type="password", key="signup_password")

    if st.button("Create account", key="signup_btn"):
        if not u or not p or not pw:
            st.error("❌ All fields are required!")
            return
        
        if not p.isdigit() or len(p) != 10:
            st.error("❌ Please enter a valid 10-digit phone number")
            return
        
        user_id = create_user(u, p, pw, "student")
        if user_id:
            st.success("✅ Account created! Please login.")
        else:
            st.error("❌ This phone number is already registered. Please use a different number or login.")

# ================= SETUP =================
def setup_page():
    st.title("Test Setup")
    
    # Add tabs for custom test and admin tests
    tab1, tab2 = st.tabs(["🎯 Create Custom Test", "📋 Take Admin Test"])
    
    with tab1:
        custom_test_setup()
    
    with tab2:
        admin_test_selection()


def custom_test_setup():
    """Original test setup - now with difficulty caps"""
    st.subheader("Create Your Custom Test")
    st.info("⚠️ Note: To ensure balanced learning, you must select at least 40% hard, 30% medium, and 30% easy questions.")

    chapters = st.multiselect(
        "Chapters",
        [2,3,4,5,7,8,9,10],
        key="setup_chapters"
    )

    # Difficulty selection with percentage display
    st.markdown("### ⚡ Select Difficulty Levels")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        include_easy = st.checkbox("🟢 Easy", value=True, key="include_easy")
    with col2:
        include_medium = st.checkbox("🟡 Medium", value=True, key="include_medium")
    with col3:
        include_hard = st.checkbox("🔴 Hard", value=True, key="include_hard")
    
    # Build difficulties list
    selected_difficulties = []
    if include_easy:
        selected_difficulties.append("easy")
    if include_medium:
        selected_difficulties.append("medium")
    if include_hard:
        selected_difficulties.append("hard")

    if not chapters or not selected_difficulties:
        st.warning("Select chapters and at least one difficulty level")
        return

    available = get_available_count(chapters, selected_difficulties)
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
    
    # Apply mandatory difficulty distribution (40% hard, 30% medium, 30% easy)
    st.markdown("### 📊 Mandatory Difficulty Distribution")
    st.warning("Tests will automatically include: 40% Hard, 30% Medium, 30% Easy questions")
    
    easy_count = round(total * 0.30)
    medium_count = round(total * 0.30)
    hard_count = total - easy_count - medium_count
    
    st.info(f"Your test will have: {easy_count} Easy + {medium_count} Medium + {hard_count} Hard = {total} Total")

    if st.button("Start Test", key="start_test_btn"):
        # Use new function with difficulty caps
        questions = generate_test_with_difficulty_cap(
            chapters=chapters,
            total_questions=total,
            easy_pct=30,
            medium_pct=30,
            hard_pct=40
        )
        
        if questions is None:
            st.error("Not enough questions available with the required difficulty distribution.")
            return

        st.session_state.test = questions
        st.session_state.test_type = "custom"  # Track test type
        st.session_state.start_time = time.time()
        st.session_state.answers = {}
        st.session_state.duration = duration * 60
        st.session_state.page = "test"
        st.rerun()


def admin_test_selection():
    """Show available admin tests for students to take"""
    st.subheader("📋 Available Admin Tests")
    st.markdown("Take tests created by your instructors")
    
    tests = get_available_admin_tests()
    
    if not tests:
        st.info("No tests available at the moment. Check back later!")
        return
    
    # Display available tests
    for test in tests:
        test_id, name, total_q, duration, easy, med, hard, creator, created_at = test
        
        with st.expander(f"📝 {name}"):
            st.markdown(f"**Questions:** {total_q} | **Duration:** {duration} minutes")
            st.markdown(f"**Difficulty:** 🟢 {easy}% Easy, 🟡 {med}% Medium, 🔴 {hard}% Hard")
            st.markdown(f"**Created by:** {creator} on {str(created_at)[:10]}")
            
            # Check if student has already attempted
            conn = get_connection()
            cur = conn.cursor()
            placeholder = get_placeholder()
            cur.execute(f"""
                SELECT COUNT(*) FROM admin_test_attempts
                WHERE admin_test_id = {placeholder} AND user_id = {placeholder}
            """, (test_id, st.session_state.user['id']))
            attempts_count = cur.fetchone()[0]
            conn.close()
            
            col1, col2 = st.columns([3, 1])
            with col1:
                if attempts_count > 0:
                    st.info(f"✅ You've attempted this test {attempts_count} time(s)")
            with col2:
                if st.button(f"Start Test", key=f"start_admin_test_{test_id}", type="primary"):
                    # Load admin test
                    questions = get_admin_test_questions(test_id)
                    
                    st.session_state.test = questions
                    st.session_state.test_type = "admin"  # Track test type
                    st.session_state.admin_test_id = test_id  # Store admin test ID
                    st.session_state.start_time = time.time()
                    st.session_state.answers = {}
                    st.session_state.duration = duration * 60
                    st.session_state.page = "test"
                    st.rerun()


# ================= OLD SETUP (REMOVED) =================
# Keeping this comment for reference - old setup_page() moved to custom_test_setup()

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
        # Show difficulty badge
        difficulty = q.get('difficulty', 'medium')
        if difficulty == 'easy':
            badge = "🟢 Easy"
            badge_color = "#90EE90"
        elif difficulty == 'hard':
            badge = "🔴 Hard"
            badge_color = "#FFB6C6"
        else:
            badge = "🟡 Medium"
            badge_color = "#FFE4A0"
        
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
            <span style="background-color: {badge_color}; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;">{badge}</span>
            <span style="font-size: 16px; font-weight: bold;">Q{i}. {q['text']}</span>
        </div>
        """, unsafe_allow_html=True)

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
    test_type = st.session_state.get("test_type", "custom")
    
    if test_type == "admin":
        # Save admin test attempt
        save_admin_test_attempt(score, len(st.session_state.test))
    else:
        # Save regular test attempt
        save_test_attempt(score, len(st.session_state.test))
    
    st.session_state.page = "result"
    st.rerun()


def save_admin_test_attempt(score, total_questions):
    """Save admin test attempt and responses to database"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        admin_test_id = st.session_state.get("admin_test_id")
        user_id = st.session_state.user['id']
        
        placeholder = get_placeholder()
        timestamp = "NOW()" if USE_POSTGRES else "CURRENT_TIMESTAMP"
        
        # Insert admin test attempt with correct column names
        if USE_POSTGRES:
            cur.execute(f"""
                INSERT INTO admin_test_attempts (admin_test_id, user_id, score, total_questions, percentage, attempted_at)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {timestamp})
                RETURNING attempt_id
            """, (admin_test_id, user_id, score, total_questions, round(score * 100.0 / total_questions, 2)))
            attempt_id = cur.fetchone()[0]
        else:
            cur.execute(f"""
                INSERT INTO admin_test_attempts (admin_test_id, user_id, score, total_questions, percentage, attempted_at)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {timestamp})
            """, (admin_test_id, user_id, score, total_questions, round(score * 100.0 / total_questions, 2)))
            attempt_id = cur.lastrowid
        
        # Insert individual responses
        for q in st.session_state.test:
            qid = q["id"]
            selected_label = st.session_state.answers.get(qid)
            
            # Check if answer is correct
            is_correct = 0
            if selected_label:
                for opt in q["options"]:
                    if opt[0] == selected_label and opt[2]:
                        is_correct = 1
                        break
            
            cur.execute(f"""
                INSERT INTO admin_test_responses (attempt_id, question_id, selected_answer, is_correct)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})
            """, (attempt_id, qid, selected_label, is_correct))
        
        conn.commit()
        
    except Exception as e:
        st.error(f"❌ Database error: {e}")
        conn.rollback()
        
    finally:
        conn.close()


def save_test_attempt(score, total_questions):
    """Save test attempt and responses to database"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        placeholder = get_placeholder()
        timestamp = "NOW()" if USE_POSTGRES else "CURRENT_TIMESTAMP"
        
        # Get user_id from username
        cur.execute(
            f"SELECT id FROM users WHERE username = {placeholder}",
            (st.session_state.user['username'],)
        )
        user_id_result = cur.fetchone()
        
        if not user_id_result:
            st.error(f"❌ User not found in database!")
            return
        
        user_id = user_id_result[0]
        
        # Check if student record exists (CRITICAL FIX!)
        cur.execute(
            f"SELECT user_id FROM students WHERE user_id = {placeholder}",
            (user_id,)
        )
        student_check = cur.fetchone()
        
        # Create student record if it doesn't exist
        if not student_check:
            cur.execute(
                f"INSERT INTO students (user_id, name, class) VALUES ({placeholder}, {placeholder}, {placeholder})",
                (user_id, st.session_state.user['username'], '9')
            )
            conn.commit()
        
        # Insert test attempt with correct column order
        if USE_POSTGRES:
            cur.execute(f"""
                INSERT INTO test_attempts (student_id, total_questions, score, started_at)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {timestamp})
                RETURNING id
            """, (user_id, total_questions, score))
            attempt_id = cur.fetchone()[0]
        else:
            cur.execute(f"""
                INSERT INTO test_attempts (student_id, total_questions, score, started_at)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {timestamp})
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
            
            cur.execute(f"""
                INSERT INTO responses (attempt_id, question_id, selected_label, is_correct)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})
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

