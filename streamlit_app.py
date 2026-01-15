import streamlit as st
import time
from datetime import datetime
import pytz

from auth import login, create_user
from generate_test_engine import (
    generate_test, 
    generate_test_with_difficulty_cap,
    generate_test_from_concepts,
    create_admin_test,
    get_admin_test_questions,
    get_available_admin_tests
)
from db_connection import get_connection, get_placeholder, USE_POSTGRES

st.set_page_config("Class 9 ICSE Test Platform", layout="wide")

# Chapter name mappings - Physics and Chemistry
CHAPTER_NAMES = {
    "Biology": {
        1: "Introducing Biology (Scope and Branches)",
        2: "Cell - The Unit of Life",
        3: "Tissues: Plant and Animal Tissues",
        4: "The Flower",
        5: "Pollination and Fertilization",
        6: "Seed: Structure and Germination",
        7: "Respiration in Plants",
        8: "Five Kingdom Classification",
        9: "Economic Importance of Bacteria and Fungi",
        10: "Nutrition",
        11: "Digestive System",
        12: "Skeleton, Movement and Locomotion",
        13: "Skin: The Jack of All Trades",
        14: "The Respiratory System",
        15: "Hygiene: A Key to Healthy Life",
        16: "Diseases: Cause and Control",
        17: "Aids to Health",
        18: "Health Organizations",
        19: "Waste Generation and Management"
    },
    "Physics": {
        1: "Measurements and Experimentation",
        2: "Motion in One Dimension",
        3: "Laws of Motion",
        4: "Pressure in Fluids",
        5: "Upthrust in Fluids and Archimedes' Principle",
        6: "Heat and Energy",
        7: "Reflection of Light",
        8: "Propagation of Sound Waves",
        9: "Current Electricity",
        10: "Magnetism"
    },
    "Chemistry": {
        1: "The Language of Chemistry",
        2: "Chemical Changes and Reactions",
        3: "Water",
        4: "Atomic Structure and Chemical Bonding",
        5: "The Periodic Table",
        6: "Study of the First Element - Hydrogen",
        7: "Study of Gas Laws",
        8: "Atmospheric Pollution",
        9: "Practical Work"
    }
}

def get_concepts_by_chapter(subject="Physics"):
    """Get all concepts grouped by chapter for a specific subject"""
    conn = get_connection()
    cur = conn.cursor()
    placeholder = get_placeholder()
    cur.execute(f'''
        SELECT ch.chapter_number, c.id, c.concept_name 
        FROM concepts c 
        JOIN chapters ch ON c.chapter_id = ch.id 
        WHERE ch.subject = {placeholder}
        ORDER BY ch.chapter_number, c.id
    ''', (subject,))
    rows = cur.fetchall()
    conn.close()
    
    concepts_by_chapter = {}
    for ch_num, concept_id, concept_name in rows:
        if ch_num not in concepts_by_chapter:
            concepts_by_chapter[ch_num] = []
        concepts_by_chapter[ch_num].append((concept_id, concept_name))
    return concepts_by_chapter

def format_timestamp(timestamp):
    """Convert timestamp to IST timezone"""
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except:
            timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    if timestamp.tzinfo is None:
        timestamp = pytz.UTC.localize(timestamp)
    ist = pytz.timezone('Asia/Kolkata')
    return timestamp.astimezone(ist).strftime('%Y-%m-%d %I:%M %p IST')



def admin_page():
    st.title("📊 Admin Dashboard")
    
    # Create tabs for different admin functions
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📈 Statistics", "📝 Create Test", "🗂️ Manage Tests", "👥 Students", "🏆 Leaderboard", "🔐 Settings"])
    
    with tab1:
        show_admin_statistics()
    
    with tab2:
        create_test_interface()
    
    with tab3:
        manage_tests_interface()
    
    with tab4:
        show_students_list()
    
    with tab5:
        leaderboard_page()
    
    with tab6:
        admin_settings()


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
    
    # Subject selection
    subject = st.selectbox(
        "Select Subject",
        ["Biology", "Physics", "Chemistry"],
        help="Choose the subject for this test"
    )
    
    # Selection mode: Chapters or Concepts
    selection_mode = st.radio(
        "📌 Selection Mode",
        ["Select by Chapters", "Select by Concepts"],
        help="Choose entire chapters or specific concepts"
    )
    
    selected_concept_ids = []
    chapters = []
    
    if selection_mode == "Select by Chapters":
        # Chapter selection based on subject
        available_chapters = list(CHAPTER_NAMES[subject].keys())
        chapters = st.multiselect(
            "Select Chapters",
            available_chapters,
            help="Choose which chapters to include",
            format_func=lambda x: f"Chapter {x}: {CHAPTER_NAMES[subject][x]}"
        )
        
        # Get all concept IDs from selected chapters
        if chapters:
            conn = get_connection()
            cur = conn.cursor()
            placeholder = get_placeholder()
            chapter_placeholders = ",".join([placeholder] * len(chapters))
            cur.execute(f"""
                SELECT c.id
                FROM concepts c
                JOIN chapters ch ON c.chapter_id = ch.id
                WHERE ch.chapter_number IN ({chapter_placeholders})
                AND ch.subject = {placeholder}
            """, tuple(chapters) + (subject,))
            selected_concept_ids = [row[0] for row in cur.fetchall()]
            conn.close()
    
    else:  # Select by Concepts
        # Get concepts grouped by chapter for selected subject
        concepts_by_chapter = get_concepts_by_chapter(subject)
        
        if not concepts_by_chapter:
            st.error(f"⚠️ No concepts found for {subject}. Database connection issue!")
        else:
            st.info(f"✓ Found {len(concepts_by_chapter)} chapters for {subject}")
        
        # Create expandable sections for each chapter
        st.markdown("### 📚 Select Concepts to Include")
        
        for ch_num in sorted(concepts_by_chapter.keys()):
            chapter_name = CHAPTER_NAMES.get(subject, {}).get(ch_num, f'Chapter {ch_num}')
            with st.expander(f"📖 Chapter {ch_num}: {chapter_name}"):
                concepts = concepts_by_chapter[ch_num]
                select_all = st.checkbox(f"Select All from Chapter {ch_num}", key=f"admin_select_all_ch{ch_num}")
                
                # If select all is checked, add all concepts from this chapter
                if select_all:
                    for concept_id, concept_name in concepts:
                        selected_concept_ids.append(concept_id)
                        st.checkbox(concept_name, value=True, disabled=True, key=f"admin_concept_{concept_id}")
                else:
                    # Otherwise, show individual checkboxes
                    for concept_id, concept_name in concepts:
                        if st.checkbox(concept_name, value=False, key=f"admin_concept_{concept_id}"):
                            selected_concept_ids.append(concept_id)
    
    # Validation for concepts
    if not selected_concept_ids:
        st.info("📚 Please select at least one chapter or concept to create a test")
        return
    
    # Get available questions for selected concepts
    conn = get_connection()
    cur = conn.cursor()
    placeholder = get_placeholder()
    concept_placeholders = ",".join([placeholder] * len(selected_concept_ids))
    cur.execute(f"""
        SELECT COUNT(*)
        FROM questions
        WHERE concept_id IN ({concept_placeholders})
    """, tuple(selected_concept_ids))
    available_questions = cur.fetchone()[0]
    conn.close()
    
    st.info(f"📊 Available questions from selection: {available_questions}")
    
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
        total_questions = st.number_input(
            "Total Questions", 
            5, 
            min(100, available_questions), 
            min(30, available_questions), 
            help="Total number of questions in the test"
        )
    with col2:
        duration = st.number_input("Duration (minutes)", 5, 180, 60, help="Time limit for the test")
    
    if available_questions == 0:
        st.warning("⚠️ No questions available for selected concepts/chapters")
        if subject == "Biology":
            st.info("💡 Biology questions may not be loaded yet. Run: `python insert_all_chapters.py`")
        return
    
    # Show breakdown
    if total_questions > 0:
        easy_count = round(total_questions * easy_pct / 100)
        medium_count = round(total_questions * medium_pct / 100)
        hard_count = total_questions - easy_count - medium_count
        
        st.info(f"📊 Question Breakdown: {easy_count} Easy + {medium_count} Medium + {hard_count} Hard = {total_questions} Total")
    
    # Create test button
    if st.button("🚀 Create Test", type="primary", disabled=(total_pct != 100 or not selected_concept_ids or not test_name)):
        with st.spinner("Creating test..."):
            try:
                admin_test_id = create_admin_test(
                    test_name=test_name,
                    chapters=chapters if selection_mode == "Select by Chapters" else [],
                    total_questions=total_questions,
                    duration_minutes=duration,
                    easy_pct=easy_pct,
                    medium_pct=medium_pct,
                    hard_pct=hard_pct,
                    created_by_user_id=st.session_state.user['id'],
                    subject=subject,
                    concept_ids=selected_concept_ids
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
                st.markdown(f"**Created by:** {creator} on {format_timestamp(created_at)}")
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
                    st.markdown(f"**Attempted:** {format_timestamp(attempted_at)}")
                
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
                
                # Add button to view full test details
                if st.button(f"👁️ View Full Test Details", key=f"view_test_{attempt_id}"):
                    show_student_test_details(attempt_id, username, test_id, total_questions)
                
                st.markdown("---")  # Separator between students
    
    # Not attempted students
    if not_attempted:
        st.markdown("#### ⏳ Students Who Haven't Attempted")
        not_attempted_names = [r[1] for r in not_attempted]
        st.markdown(", ".join(not_attempted_names))
    
    conn.close()


def show_student_test_details(attempt_id, username, test_id, total_questions):
    """Show detailed question-by-question review for a student's test attempt"""
    st.markdown(f"### 📝 Full Test Review: {username}")
    
    conn = get_connection()
    cur = conn.cursor()
    placeholder = get_placeholder()
    
    # Get all questions with student's answers
    cur.execute(f"""
        SELECT 
            q.id, q.question_text, q.difficulty,
            r.selected_answer, r.is_correct,
            atq.question_order
        FROM admin_test_questions atq
        JOIN questions q ON atq.question_id = q.id
        JOIN admin_test_responses r ON r.question_id = q.id AND r.attempt_id = {placeholder}
        WHERE atq.admin_test_id = {placeholder}
        ORDER BY atq.question_order
    """, (attempt_id, test_id))
    
    results = cur.fetchall()
    
    for qid, qtext, difficulty, selected_answer, is_correct, order in results:
        # Get options for this question
        cur.execute(f"""
            SELECT label, option_text, is_correct
            FROM mcq_options
            WHERE question_id = {placeholder}
            ORDER BY label
        """, (qid,))
        
        options = cur.fetchall()
        
        # Display question with result
        result_emoji = "✅" if is_correct else "❌"
        diff_badge = "🟢" if difficulty == "easy" else "🔴" if difficulty == "hard" else "🟡"
        
        with st.container():
            st.markdown(f"#### {result_emoji} Q{order}. {diff_badge} {difficulty.title()}")
            st.markdown(f"**{qtext}**")
            
            # Show options with indicators
            for label, opt_text, is_correct_opt in options:
                if label == selected_answer and is_correct_opt:
                    st.success(f"✅ **{label}. {opt_text}** ← Student's answer (Correct!)")
                elif label == selected_answer and not is_correct_opt:
                    st.error(f"❌ **{label}. {opt_text}** ← Student's answer (Incorrect)")
                elif is_correct_opt:
                    st.info(f"✓ **{label}. {opt_text}** ← Correct answer")
                else:
                    st.markdown(f"{label}. {opt_text}")
            
            st.markdown("---")
    
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

def show_students_list():
    """Display list of all students with their info"""
    st.subheader("👥 Registered Students")
    
    conn = get_connection()
    cur = conn.cursor()
    placeholder = get_placeholder()
    
    try:
        cur.execute(f"""
            SELECT id, username, phone_number, school_name, class_name, board_name, recovery_code, created_at 
            FROM users 
            WHERE role = {placeholder}
            ORDER BY created_at DESC
        """, ('student',))
        students = cur.fetchall()
        
        if not students:
            st.info("No students registered yet.")
            return
        
        st.success(f"Total Students: {len(students)}")
        
        # Display as detailed cards
        st.markdown("---")
        for student_id, username, phone, school, class_name, board, recovery_code, created_at in students:
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**👤 {username}**")
                st.caption(f"🏫 {school or 'N/A'} | 📚 Class {class_name or 'N/A'} | 📋 {board or 'N/A'}")
            with col2:
                st.write(f"📱 {phone}")
                st.write(f"🔑 Recovery: `{recovery_code or 'N/A'}`")
                if created_at:
                    st.caption(f"📅 Registered: {format_timestamp(created_at)}")
            with col3:
                if st.button("🗑️ Delete", key=f"delete_student_{student_id}", type="secondary"):
                    st.session_state[f'confirm_delete_{student_id}'] = True
                    st.rerun()
            
            # Show confirmation dialog if delete was clicked
            if st.session_state.get(f'confirm_delete_{student_id}', False):
                with st.container():
                    st.warning(f"⚠️ Are you sure you want to delete **{username}**? This will permanently remove:")
                    st.markdown("""
                    - Their account and login credentials
                    - All test attempts and results
                    - All test responses
                    - This action CANNOT be undone!
                    """)
                    
                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button("✅ Yes, Delete Permanently", key=f"confirm_yes_{student_id}", type="primary"):
                            delete_student(student_id, username)
                            del st.session_state[f'confirm_delete_{student_id}']
                            st.rerun()
                    with col_no:
                        if st.button("❌ No, Cancel", key=f"confirm_no_{student_id}"):
                            del st.session_state[f'confirm_delete_{student_id}']
                            st.rerun()
            
            st.divider()
    
    except Exception as e:
        st.error(f"Error loading students: {str(e)}")
    finally:
        conn.close()

def delete_student(student_id, username):
    """Delete a student and all their associated data"""
    conn = get_connection()
    cur = conn.cursor()
    placeholder = get_placeholder()
    
    try:
        # Delete from users table (CASCADE should handle related records)
        # But we'll explicitly delete to be safe
        
        # Delete test responses (custom tests)
        cur.execute(f"""
            DELETE FROM responses 
            WHERE attempt_id IN (
                SELECT id FROM test_attempts WHERE student_id = {placeholder}
            )
        """, (student_id,))
        
        # Delete test attempts (custom tests)
        cur.execute(f"DELETE FROM test_attempts WHERE student_id = {placeholder}", (student_id,))
        
        # Delete admin test responses
        cur.execute(f"""
            DELETE FROM admin_test_responses 
            WHERE attempt_id IN (
                SELECT attempt_id FROM admin_test_attempts WHERE user_id = {placeholder}
            )
        """, (student_id,))
        
        # Delete admin test attempts
        cur.execute(f"DELETE FROM admin_test_attempts WHERE user_id = {placeholder}", (student_id,))
        
        # Finally, delete the user account
        cur.execute(f"DELETE FROM users WHERE id = {placeholder}", (student_id,))
        
        conn.commit()
        st.success(f"✅ Successfully deleted student **{username}** and all their data!")
        time.sleep(2)
        
    except Exception as e:
        conn.rollback()
        st.error(f"❌ Error deleting student: {str(e)}")
    finally:
        conn.close()

def admin_settings():
    """Admin settings page for changing credentials"""
    st.subheader("🔐 Admin Settings")
    
    st.markdown("### Change Admin Password")
    
    current_user = st.session_state.user
    admin_username = current_user['username']
    
    with st.form("change_password_form"):
        st.write(f"Logged in as: **{admin_username}**")
        new_password = st.text_input("New Password", type="password", key="new_admin_pwd")
        confirm_password = st.text_input("Confirm New Password", type="password", key="confirm_admin_pwd")
        
        if st.form_submit_button("Update Password"):
            if not new_password:
                st.error("Password cannot be empty!")
            elif new_password != confirm_password:
                st.error("Passwords do not match!")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters long!")
            else:
                # Update password
                import bcrypt
                conn = get_connection()
                cur = conn.cursor()
                placeholder = get_placeholder()
                
                hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
                cur.execute(
                    f"UPDATE users SET password_hash = {placeholder} WHERE username = {placeholder}",
                    (hashed.decode('utf-8'), admin_username)
                )
                conn.commit()
                conn.close()
                
                st.success("✅ Password updated successfully! Please log in again with your new password.")
                st.info("Logging out in 3 seconds...")
                time.sleep(3)
                st.session_state.clear()
                st.session_state.page = "login"
                st.rerun()

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

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login", key="login_btn", use_container_width=True):
            user = login(u, p)
            if user:
                st.session_state.user = user
                st.session_state.page = "setup"
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
    
    with col2:
        if st.button("🔑 Forgot Password?", key="forgot_password_btn", use_container_width=True):
            st.session_state.page = "forgot_password"
            st.rerun()


def forgot_password_page():
    """Handle password reset with phone number OR recovery code verification"""
    st.title("🔑 Reset Password")
    st.markdown("Verify your identity to reset your password")
    
    # Step 1: Choose verification method
    if not st.session_state.get("pwd_reset_verified", False):
        st.markdown("### Step 1: Verify Your Identity")
        
        verification_method = st.radio(
            "Choose verification method:",
            ["Phone Number", "Recovery Code"],
            key="verification_method"
        )
        
        username = st.text_input("Enter your Username", key="reset_username_input")
        
        if verification_method == "Phone Number":
            verifier = st.text_input("Enter your Registered Phone Number", key="reset_phone_input", max_chars=10)
            verify_label = "Phone Number"
        else:
            verifier = st.text_input("Enter your 8-digit Recovery Code", key="reset_code_input", max_chars=8)
            verify_label = "Recovery Code"
        
        if st.button("Verify", key="verify_btn", type="primary"):
            if not username or not verifier:
                st.error("❌ Please fill in both fields")
                return
            
            # Verify username and phone/code match
            conn = get_connection()
            cur = conn.cursor()
            placeholder = get_placeholder()
            
            if verification_method == "Phone Number":
                if not verifier.isdigit() or len(verifier) != 10:
                    st.error("❌ Please enter a valid 10-digit phone number")
                    return
                
                cur.execute(f"""
                    SELECT id, username 
                    FROM users 
                    WHERE username = {placeholder} AND phone_number = {placeholder}
                """, (username, verifier))
            else:
                if not verifier.isdigit() or len(verifier) != 8:
                    st.error("❌ Recovery code must be 8 digits")
                    return
                
                cur.execute(f"""
                    SELECT id, username 
                    FROM users 
                    WHERE username = {placeholder} AND recovery_code = {placeholder}
                """, (username, verifier))
            
            result = cur.fetchone()
            conn.close()
            
            if result:
                st.session_state.pwd_reset_verified = True
                st.session_state.pwd_reset_user_id = result[0]
                st.session_state.pwd_reset_username = result[1]
                st.success(f"✅ Identity verified using {verify_label}! Now set your new password.")
                st.rerun()
            else:
                st.error(f"❌ Username and {verify_label} don't match. Please check and try again.")
        
        if st.button("← Back to Login", key="back_to_login"):
            st.session_state.page = "login"
            st.rerun()
    
    # Step 2: Set new password
    else:
        st.markdown(f"### Step 2: Set New Password for **{st.session_state.pwd_reset_username}**")
        new_password = st.text_input("New Password", type="password", key="new_password")
        confirm_password = st.text_input("Confirm New Password", type="password", key="confirm_password")
        
        if st.button("Reset Password", key="reset_password_btn", type="primary"):
            if not new_password or not confirm_password:
                st.error("❌ Please fill in both password fields")
                return
            
            if new_password != confirm_password:
                st.error("❌ Passwords don't match!")
                return
            
            if len(new_password) < 4:
                st.error("❌ Password must be at least 4 characters long")
                return
            
            # Update password in database
            import bcrypt
            hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode('utf-8')
            
            conn = get_connection()
            cur = conn.cursor()
            placeholder = get_placeholder()
            
            try:
                cur.execute(f"""
                    UPDATE users 
                    SET password_hash = {placeholder}
                    WHERE id = {placeholder}
                """, (hashed_password, st.session_state.pwd_reset_user_id))
                
                conn.commit()
                conn.close()
                
                # Clear reset session variables
                st.session_state.pwd_reset_verified = False
                st.session_state.pwd_reset_user_id = None
                st.session_state.pwd_reset_username = None
                
                st.success("✅ Password reset successful! Please login with your new password.")
                st.balloons()
                time.sleep(2)
                st.session_state.page = "login"
                st.rerun()
                
            except Exception as e:
                conn.rollback()
                conn.close()
                st.error(f"❌ Error resetting password: {e}")
        
        if st.button("← Cancel", key="cancel_reset"):
            st.session_state.pwd_reset_verified = False
            st.session_state.pwd_reset_user_id = None
            st.session_state.pwd_reset_username = None
            st.session_state.page = "login"
            st.rerun()

def signup_page():
    st.title("Signup")

    u = st.text_input("Username", key="signup_username")
    p = st.text_input("Phone Number (10 digits - used to prevent duplicate accounts)", key="signup_phone", max_chars=10)
    pw = st.text_input("Password", type="password", key="signup_password")
    
    # New mandatory fields
    school = st.text_input("School Name *", key="signup_school")
    class_name = st.text_input("Class *", key="signup_class", placeholder="e.g., 9th, 10th")
    board = st.selectbox("Board *", ["ICSE", "CBSE", "State Board", "Other"], key="signup_board")

    if st.button("Create account", key="signup_btn"):
        if not u or not p or not pw or not school or not class_name or not board:
            st.error("❌ All fields are required!")
            return
        
        if not p.isdigit() or len(p) != 10:
            st.error("❌ Please enter a valid 10-digit phone number")
            return
        
        result = create_user(u, p, pw, "student", school, class_name, board)
        if result and isinstance(result, dict):
            st.success("✅ Account created successfully!")
            st.balloons()
            
            # Show recovery code prominently
            st.warning("⚠️ **IMPORTANT: Save Your Recovery Code**")
            st.info(f"🔑 **Your Recovery Code: `{result['recovery_code']}`**")
            st.markdown("""
            **You'll need this code to reset your password if you forget it.**
            - Take a screenshot or write it down
            - You can view it anytime in your profile after login
            """)
            
            if st.button("Continue to Login", key="continue_login"):
                st.rerun()
        else:
            st.error("❌ This phone number is already registered. Please use a different number or login.")

def show_student_history():
    """Display all past test attempts for the current student"""
    st.subheader("📜 Your Test History")
    
    user = st.session_state.get("user")
    if not user:
        st.error("Please log in to view test history")
        return
    
    user_id = user['id']
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Get both custom and admin test attempts
        placeholder = get_placeholder()
        
        # Get custom test attempts
        custom_query = f"""
            SELECT 
                'Custom Test' as test_name,
                ta.score,
                ta.total_questions,
                ta.started_at,
                ta.id,
                'custom' as test_type
            FROM test_attempts ta
            WHERE ta.student_id = {placeholder}
            ORDER BY ta.started_at DESC
        """
        cursor.execute(custom_query, (user_id,))
        custom_results = cursor.fetchall()
        
        # Get admin test attempts
        admin_query = f"""
            SELECT 
                at.test_name,
                ata.score,
                ata.total_questions,
                ata.attempted_at as timestamp,
                ata.attempt_id,
                'admin' as test_type
            FROM admin_test_attempts ata
            JOIN admin_tests at ON ata.admin_test_id = at.admin_test_id
            WHERE ata.user_id = {placeholder}
            ORDER BY ata.attempted_at DESC
        """
        cursor.execute(admin_query, (user_id,))
        admin_results = cursor.fetchall()
        
        # Combine and sort by timestamp
        all_results = []
        for row in custom_results:
            all_results.append({
                'test_name': row[0],
                'score': row[1],
                'total': row[2],
                'timestamp': row[3],
                'attempt_id': row[4],
                'test_type': row[5]
            })
        
        for row in admin_results:
            all_results.append({
                'test_name': row[0],
                'score': row[1],
                'total': row[2],
                'timestamp': row[3],
                'attempt_id': row[4],
                'test_type': row[5]
            })
        
        # Sort by timestamp descending
        all_results.sort(key=lambda x: x['timestamp'], reverse=True)
        
        if not all_results:
            st.info("📭 No test history yet. Take a test to see your results here!")
            return
        
        st.success(f"Found {len(all_results)} test attempt(s)")
        
        # Display each test result
        for result in all_results:
            percentage = (result['score'] / result['total']) * 100
            
            # Color coding based on percentage
            if percentage >= 80:
                emoji = "🌟"
                color = "green"
            elif percentage >= 60:
                emoji = "👍"
                color = "blue"
            else:
                emoji = "📚"
                color = "orange"
            
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"### {emoji} {result['test_name']}")
                    st.caption(f"📅 {format_timestamp(result['timestamp'])}")
                
                with col2:
                    st.metric("Score", f"{result['score']}/{result['total']}", f"{percentage:.1f}%")
                
                with col3:
                    if st.button("👁️ View Details", key=f"view_{result['test_type']}_{result['attempt_id']}"):
                        # Store in session state to view details
                        st.session_state.view_history_attempt = result['attempt_id']
                        st.session_state.view_history_type = result['test_type']
                        st.rerun()
                
                st.divider()
        
        # Check if we need to show details for a specific attempt
        if hasattr(st.session_state, 'view_history_attempt') and st.session_state.view_history_attempt:
            show_history_test_details(
                st.session_state.view_history_attempt,
                st.session_state.view_history_type
            )
            if st.button("← Back to History"):
                del st.session_state.view_history_attempt
                del st.session_state.view_history_type
                st.rerun()
    
    except Exception as e:
        st.error(f"Error loading test history: {str(e)}")
    finally:
        conn.close()


def show_history_test_details(attempt_id, test_type):
    """Show detailed Q&A review for a past test attempt"""
    st.subheader("📖 Test Review")
    
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = get_placeholder()
    
    try:
        if test_type == 'custom':
            # Get custom test responses
            query = f"""
                SELECT 
                    q.question_text,
                    r.selected_label, r.is_correct, q.difficulty, q.id
                FROM responses r
                JOIN questions q ON r.question_id = q.id
                WHERE r.attempt_id = {placeholder}
                ORDER BY r.id
            """
        else:
            # Get admin test responses
            query = f"""
                SELECT 
                    q.question_text,
                    atr.selected_answer, atr.is_correct, q.difficulty, q.id
                FROM admin_test_responses atr
                JOIN questions q ON atr.question_id = q.id
                WHERE atr.attempt_id = {placeholder}
                ORDER BY atr.response_id
            """
        
        cursor.execute(query, (attempt_id,))
        responses = cursor.fetchall()
        
        correct_count = sum(1 for r in responses if r[2])
        total = len(responses)
        
        st.info(f"Score: {correct_count}/{total} ({(correct_count/total)*100:.1f}%)")
        
        for i, r in enumerate(responses, 1):
            question_text, selected, is_correct, difficulty, question_id = r
            
            # Get options for this question
            option_query = f"""
                SELECT label, option_text, is_correct
                FROM mcq_options
                WHERE question_id = {placeholder}
                ORDER BY label
            """
            cursor.execute(option_query, (question_id,))
            options = cursor.fetchall()
            
            # Find correct answer
            correct_answer = next((opt[0] for opt in options if opt[2] == 1), None)
            
            # Show difficulty badge
            if difficulty == 'easy':
                badge = "🟢 Easy"
                badge_color = "#90EE90"
            elif difficulty == 'hard':
                badge = "🔴 Hard"
                badge_color = "#FFB6C6"
            else:
                badge = "🟡 Medium"
                badge_color = "#FFE4A0"
            
            # Color based on correctness
            if is_correct:
                result_emoji = "✅"
                border_color = "#90EE90"
            else:
                result_emoji = "❌"
                border_color = "#FFB6C6"
            
            with st.container():
                st.markdown(f"""
                <div style="border-left: 4px solid {border_color}; padding-left: 15px; margin-bottom: 20px;">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                        <span style="background-color: {badge_color}; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;">{badge}</span>
                        <span style="font-size: 20px;">{result_emoji}</span>
                    </div>
                    <p style="font-size: 16px; font-weight: bold; margin: 10px 0;">Q{i}. {question_text}</p>
                </div>
                """, unsafe_allow_html=True)
                
                for opt in options:
                    label, option_text, is_correct_opt = opt
                    if label == correct_answer:
                        st.success(f"**{label}. {option_text}** ✓ (Correct Answer)")
                    elif label == selected and not is_correct:
                        st.error(f"**{label}. {option_text}** ✗ (Your Answer)")
                    else:
                        st.write(f"{label}. {option_text}")
                
                st.divider()
    
    except Exception as e:
        st.error(f"Error loading test details: {str(e)}")
    finally:
        conn.close()


# ================= SETUP =================
def student_profile_page():
    """Student profile with recovery code and editable fields"""
    st.subheader("👤 My Profile")
    
    user_id = st.session_state.user['id']
    conn = get_connection()
    cur = conn.cursor()
    placeholder = get_placeholder()
    
    # Get current user data
    cur.execute(f"""
        SELECT username, phone_number, school_name, class_name, board_name, recovery_code, created_at
        FROM users
        WHERE id = {placeholder}
    """, (user_id,))
    
    username, phone, school, class_name, board, recovery_code, created_at = cur.fetchone()
    conn.close()
    
    # Profile display with default avatar
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Default avatar
        st.markdown("""
        <div style='text-align: center;'>
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        width: 120px; height: 120px; border-radius: 50%; 
                        display: flex; align-items: center; justify-content: center;
                        font-size: 48px; color: white; font-weight: bold;
                        margin: 0 auto;'>
                {}
            </div>
        </div>
        """.format(username[0].upper()), unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"### {username}")
        st.caption(f"📱 {phone}")
        st.caption(f"📅 Joined: {format_timestamp(created_at)}")
    
    st.markdown("---")
    
    # Recovery Code Section
    st.markdown("### 🔑 Recovery Code")
    st.info(f"**Your Recovery Code: `{recovery_code}`**")
    st.caption("Use this code to reset your password if you forget it. Keep it safe!")
    
    st.markdown("---")
    
    # Editable Profile Fields
    st.markdown("### ✏️ Edit Profile")
    
    with st.form("profile_edit_form"):
        new_school = st.text_input("School Name", value=school)
        new_class = st.text_input("Class", value=class_name)
        new_board = st.selectbox("Board", ["ICSE", "CBSE", "State Board", "Other"], 
                                  index=["ICSE", "CBSE", "State Board", "Other"].index(board) if board in ["ICSE", "CBSE", "State Board", "Other"] else 0)
        
        if st.form_submit_button("💾 Update Profile", type="primary"):
            conn = get_connection()
            cur = conn.cursor()
            
            try:
                cur.execute(f"""
                    UPDATE users
                    SET school_name = {placeholder}, class_name = {placeholder}, board_name = {placeholder}
                    WHERE id = {placeholder}
                """, (new_school, new_class, new_board, user_id))
                
                conn.commit()
                conn.close()
                st.success("✅ Profile updated successfully!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                conn.rollback()
                conn.close()
                st.error(f"❌ Error updating profile: {e}")


def leaderboard_page():
    """Leaderboard showing student rankings based on accuracy and performance"""
    st.subheader("🏆 Leaderboard")
    
    # Filter options
    col1, col2 = st.columns([1, 3])
    
    with col1:
        board_filter = st.selectbox(
            "Filter by Board",
            ["All Boards", "ICSE", "CBSE", "State Board", "Other"],
            key="leaderboard_board_filter"
        )
    
    with col2:
        st.caption("📊 Rankings based on: Accuracy, Tests Attempted, and Difficulty Level")
    
    conn = get_connection()
    cur = conn.cursor()
    placeholder = get_placeholder()
    
    try:
        # Build query based on filter
        if board_filter == "All Boards":
            board_condition = ""
            board_params = ()
        else:
            board_condition = f"AND u.board_name = {placeholder}"
            board_params = (board_filter,)
        
        # Get leaderboard data
        query = f"""
            WITH user_stats AS (
                SELECT 
                    u.id,
                    u.username,
                    u.school_name,
                    u.class_name,
                    u.board_name,
                    COUNT(DISTINCT ta.id) as custom_tests,
                    COUNT(DISTINCT ata.attempt_id) as admin_tests,
                    COALESCE(SUM(ta.score), 0) as custom_score,
                    COALESCE(SUM(ta.total_questions), 0) as custom_total,
                    COALESCE(SUM(ata.score), 0) as admin_score,
                    COALESCE(SUM(ata.total_questions), 0) as admin_total,
                    COUNT(DISTINCT CASE WHEN q.difficulty = 'hard' AND r.is_correct = 1 THEN r.id END) as hard_correct
                FROM users u
                LEFT JOIN test_attempts ta ON u.id = ta.student_id
                LEFT JOIN admin_test_attempts ata ON u.id = ata.user_id
                LEFT JOIN responses r ON ta.id = r.attempt_id
                LEFT JOIN questions q ON r.question_id = q.id
                WHERE u.role = 'student' {board_condition}
                GROUP BY u.id, u.username, u.school_name, u.class_name, u.board_name
            )
            SELECT 
                username,
                school_name,
                class_name,
                board_name,
                (custom_tests + admin_tests) as total_tests,
                ROUND(
                    CASE 
                        WHEN (custom_total + admin_total) > 0 
                        THEN ((custom_score + admin_score) * 100.0 / (custom_total + admin_total))
                        ELSE 0 
                    END, 2
                ) as overall_accuracy,
                hard_correct
            FROM user_stats
            WHERE (custom_tests + admin_tests) > 0
            ORDER BY hard_correct DESC, overall_accuracy DESC, total_tests DESC
            LIMIT 50
        """
        
        cur.execute(query, board_params)
        results = cur.fetchall()
        conn.close()
        
        if not results:
            st.info("No test data available yet. Be the first to take a test!")
            return
        
        st.success(f"Showing Top {len(results)} Students" + (f" - {board_filter}" if board_filter != "All Boards" else ""))
        
        # Display leaderboard
        for rank, (username, school, class_name, board, total_tests, accuracy, hard_correct) in enumerate(results, 1):
            # Medal for top 3
            if rank == 1:
                medal = "🥇"
                color = "#FFD700"
            elif rank == 2:
                medal = "🥈"
                color = "#C0C0C0"
            elif rank == 3:
                medal = "🥉"
                color = "#CD7F32"
            else:
                medal = f"#{rank}"
                color = "#555555"
            
            with st.container():
                col1, col2, col3, col4 = st.columns([1, 4, 2, 2])
                
                with col1:
                    st.markdown(f"<h2 style='color: {color}; margin: 0;'>{medal}</h2>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"**{username}**")
                
                with col3:
                    st.metric("Accuracy", f"{accuracy}%")
                    st.caption(f"📝 {total_tests} tests")
                
                with col4:
                    st.metric("Hard Qs", f"{hard_correct}")
                    st.caption("✅ Correct")
                
                st.markdown("---")
    
    except Exception as e:
        st.error(f"❌ Error loading leaderboard: {e}")
        conn.close()


def setup_page():
    st.title("Student Dashboard")
    
    # Check if student needs to complete their profile
    if check_and_prompt_profile_completion():
        return  # Stop here until profile is completed
    
    # Add tabs for custom test, admin tests, history, profile, and leaderboard
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Create Custom Test", "📋 Take Admin Test", "📊 My Test History", "👤 My Profile", "🏆 Leaderboard"])
    
    with tab1:
        custom_test_setup()
    
    with tab2:
        admin_test_selection()
    
    with tab3:
        show_student_history()
    
    with tab4:
        student_profile_page()
    
    with tab5:
        leaderboard_page()


def check_and_prompt_profile_completion():
    """Check if student has completed their profile. Returns True if profile incomplete."""
    user_id = st.session_state.user['id']
    
    conn = get_connection()
    cur = conn.cursor()
    placeholder = get_placeholder()
    
    # Check if school_name, class_name, board_name are filled
    cur.execute(f"""
        SELECT school_name, class_name, board_name
        FROM users
        WHERE id = {placeholder}
    """, (user_id,))
    
    row = cur.fetchone()
    conn.close()
    
    # Check if any field is NULL or empty
    if not row or not all(row):
        st.warning("⚠️ **Please complete your profile before accessing the test platform**")
        
        with st.form("complete_profile_form"):
            st.markdown("### 🎓 Complete Your Profile")
            
            school = st.text_input(
                "School Name *",
                value=row[0] if row and row[0] else "",
                placeholder="e.g., Delhi Public School"
            )
            
            class_name = st.text_input(
                "Class *",
                value=row[1] if row and row[1] else "",
                placeholder="e.g., 9"
            )
            
            board = st.selectbox(
                "Board *",
                ["", "ICSE", "CBSE", "State Board", "Other"],
                index=0 if not row or not row[2] else ["", "ICSE", "CBSE", "State Board", "Other"].index(row[2]) if row[2] in ["ICSE", "CBSE", "State Board", "Other"] else 0
            )
            
            submitted = st.form_submit_button("✅ Save & Continue", type="primary")
            
            if submitted:
                if not school or not class_name or not board:
                    st.error("❌ Please fill in all fields")
                else:
                    # Update profile
                    conn = get_connection()
                    cur = conn.cursor()
                    
                    cur.execute(f"""
                        UPDATE users
                        SET school_name = {placeholder}, class_name = {placeholder}, board_name = {placeholder}
                        WHERE id = {placeholder}
                    """, (school, class_name, board, user_id))
                    
                    conn.commit()
                    conn.close()
                    
                    st.success("✅ Profile completed successfully!")
                    time.sleep(1)
                    st.rerun()
        
        return True  # Profile incomplete
    
    return False  # Profile is complete


def custom_test_setup():
    """Test setup with concept-based selection and flexible difficulty distribution (minimum 34% hard)"""
    st.subheader("Create Your Custom Test")
    st.warning("⚠️ **Important:** You MUST include at least 34% Hard questions to ensure effective learning. This prevents gaming the system with only easy questions.")

    # Subject selection
    subject = st.selectbox(
        "📚 Select Subject",
        ["Biology", "Physics", "Chemistry"],
        help="Choose which subject you want to practice"
    )
    
    # Get concepts grouped by chapter for selected subject
    concepts_by_chapter = get_concepts_by_chapter(subject)
    
    # DEBUG: Show what was fetched
    if not concepts_by_chapter:
        st.error(f"⚠️ No concepts found for {subject}. Database connection issue!")
    else:
        st.info(f"✓ Found {len(concepts_by_chapter)} chapters for {subject}")
    
    # Create expandable sections for each chapter
    st.markdown("### 📚 Select Concepts to Include")
    selected_concept_ids = []
    
    for ch_num in sorted(concepts_by_chapter.keys()):
        chapter_name = CHAPTER_NAMES.get(subject, {}).get(ch_num, f'Chapter {ch_num}')
        with st.expander(f"📖 Chapter {ch_num}: {chapter_name}"):
            concepts = concepts_by_chapter[ch_num]
            select_all = st.checkbox(f"Select All from Chapter {ch_num}", key=f"select_all_ch{ch_num}")
            
            # If select all is checked, add all concepts from this chapter
            if select_all:
                for concept_id, concept_name in concepts:
                    selected_concept_ids.append(concept_id)
                    st.checkbox(concept_name, value=True, disabled=True, key=f"concept_{concept_id}")
            else:
                # Otherwise, show individual checkboxes
                for concept_id, concept_name in concepts:
                    if st.checkbox(concept_name, value=False, key=f"concept_{concept_id}"):
                        selected_concept_ids.append(concept_id)
    
    # All difficulties are always selected (no checkboxes)
    selected_difficulties = ["easy", "medium", "hard"]

    if not selected_concept_ids:
        st.info("📚 Please select at least one concept to create a test")
        return

    # Get available questions for selected concepts
    conn = get_connection()
    cur = conn.cursor()
    placeholder = get_placeholder()
    concept_placeholders = ",".join([placeholder] * len(selected_concept_ids))
    
    cur.execute(f"""
        SELECT COUNT(*)
        FROM questions
        WHERE concept_id IN ({concept_placeholders})
    """, tuple(selected_concept_ids))
    available = cur.fetchone()[0]
    conn.close()
    
    st.info(f"Available questions: {available}")

    if available == 0:
        st.warning("No questions available for selected concepts")
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
    
    # Difficulty distribution with constraints
    st.markdown("### ⚡ Difficulty Distribution")
    st.caption("Choose your difficulty mix (Hard must be at least 34%)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        easy_pct = st.slider("🟢 Easy %", 0, 60, 30, step=1, key="easy_slider")
    with col2:
        medium_pct = st.slider("🟡 Medium %", 0, 60, 30, step=1, key="medium_slider")
    with col3:
        hard_pct = st.slider("🔴 Hard %", 34, 100, 40, step=1, key="hard_slider")
    
    total_pct = easy_pct + medium_pct + hard_pct
    
    # Validation
    if total_pct != 100:
        st.error(f"❌ Total percentage must equal 100% (currently {total_pct}%)")
        return
    
    if hard_pct < 34:
        st.error(f"❌ Hard questions must be at least 34% (currently {hard_pct}%)")
        return
    
    # Show breakdown
    st.success(f"✅ Distribution: {easy_pct}% Easy, {medium_pct}% Medium, {hard_pct}% Hard")
    
    easy_count = round(total * easy_pct / 100)
    medium_count = round(total * medium_pct / 100)
    hard_count = total - easy_count - medium_count
    
    st.info(f"📊 Your test will have: {easy_count} Easy + {medium_count} Medium + {hard_count} Hard = {total} Total")

    # Validation warnings
    can_start = True
    if total_pct != 100:
        st.error(f"❌ Total percentage must equal 100% (currently {total_pct}%)")
        can_start = False
    if hard_pct < 34:
        st.error(f"❌ Hard questions must be at least 34% (currently {hard_pct}%)")
        can_start = False
    
    if st.button("Start Test", key="start_test_btn", type="primary", disabled=not can_start):
        # Use new function with custom difficulty distribution for concepts
        questions = generate_test_from_concepts(
            concept_ids=selected_concept_ids,
            total_questions=total,
            easy_pct=easy_pct,
            medium_pct=medium_pct,
            hard_pct=hard_pct
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
            st.markdown(f"**Created by:** {creator} on {format_timestamp(created_at)}")
            
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
    # Scroll to top when test starts
    st.markdown('<script>window.scrollTo(0, 0);</script>', unsafe_allow_html=True)
    
    st.title("Test")

    elapsed = int(time.time() - st.session_state.start_time)
    remaining = st.session_state.duration - elapsed

    if remaining <= 0:
        submit_test(auto=True)
        return

    st.warning(f"⏳ Time left: {remaining//60}:{remaining%60:02d}")

    # Initialize current page
    if "current_page" not in st.session_state:
        st.session_state.current_page = 0
    
    # Pagination settings
    questions_per_page = 5
    total_questions = len(st.session_state.test)
    total_pages = (total_questions + questions_per_page - 1) // questions_per_page
    
    # Calculate question range for current page
    start_idx = st.session_state.current_page * questions_per_page
    end_idx = min(start_idx + questions_per_page, total_questions)
    
    # Page indicator
    st.info(f"📄 Page {st.session_state.current_page + 1} of {total_pages} | Questions {start_idx + 1}-{end_idx} of {total_questions}")
    
    # Display questions for current page
    for i in range(start_idx, end_idx):
        q = st.session_state.test[i]
        # Don't show difficulty during test
        st.markdown(f"**Q{i+1}. {q['text']}**")

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
        st.markdown("---")
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.session_state.current_page > 0:
            if st.button("⬅️ Previous", use_container_width=True):
                st.session_state.current_page -= 1
                st.rerun()
    
    with col2:
        # Show answered status
        answered = sum(1 for q in st.session_state.test if st.session_state.answers.get(q["id"]))
        st.info(f"📝 Answered: {answered}/{total_questions}")
    
    with col3:
        if st.session_state.current_page < total_pages - 1:
            if st.button("Next ➡️", use_container_width=True):
                st.session_state.current_page += 1
                st.rerun()
    
    # Submit button (show on last page or always)
    st.markdown("---")
    
    # Check for unanswered questions
    unanswered = []
    for i, q in enumerate(st.session_state.test, 1):
        if not st.session_state.answers.get(q["id"]):
            unanswered.append(i)

    if st.button("📤 Submit Test", key="submit_test_btn", type="primary", use_container_width=True):
        if unanswered:
            st.session_state.show_submit_confirmation = True
            st.session_state.unanswered_questions = unanswered
            st.rerun()
        else:
            submit_test(auto=False)
    
    # Show confirmation dialog if there are unanswered questions
    if st.session_state.get("show_submit_confirmation", False):
        with st.container():
            st.warning("⚠️ You have unanswered questions!")
            st.markdown(f"**Unanswered Questions:** {', '.join([f'Q{q}' for q in st.session_state.unanswered_questions])}")
            st.info("You can scroll up to answer them or submit anyway.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📝 Go Back to Review", key="review_btn", use_container_width=True):
                    st.session_state.show_submit_confirmation = False
                    st.rerun()
            with col2:
                if st.button("✅ Submit Anyway", key="submit_anyway_btn", type="primary", use_container_width=True):
                    st.session_state.show_submit_confirmation = False
                    submit_test(auto=False)
                    st.rerun()

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
    st.title("Test Results")
    
    score = st.session_state.score
    total = len(st.session_state.test)
    percentage = round((score / total) * 100, 2)
    
    # Overall score display
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📝 Score", f"{score}/{total}")
    with col2:
        st.metric("📊 Percentage", f"{percentage}%")
    with col3:
        emoji = "🌟" if percentage >= 80 else "✅" if percentage >= 60 else "⚠️" if percentage >= 40 else "❌"
        st.metric("Grade", emoji)
    
    st.markdown("---")
    
    # Detailed question breakdown
    st.subheader("📋 Question-by-Question Review")
    
    for i, q in enumerate(st.session_state.test, 1):
        qid = q["id"]
        selected = st.session_state.answers.get(qid)
        
        # Find correct answer
        correct_option = None
        is_correct = False
        
        for opt in q["options"]:
            if opt[2]:  # is_correct flag
                correct_option = opt
            if opt[0] == selected and opt[2]:
                is_correct = True
        
        # Display question with result indicator
        result_emoji = "✅" if is_correct else "❌"
        difficulty = q.get('difficulty', 'medium')
        diff_badge = "🟢" if difficulty == "easy" else "🔴" if difficulty == "hard" else "🟡"
        
        with st.container():
            st.markdown(f"### {result_emoji} Question {i} {diff_badge} {difficulty.title()}")
            st.markdown(f"**{q['text']}**")
            
            # Show all options with indicators
            for opt in q["options"]:
                label, text, is_correct_opt = opt
                
                if label == selected and is_correct_opt:
                    # Correct answer selected
                    st.success(f"✅ **{label}. {text}** ← Your answer (Correct!)")
                elif label == selected and not is_correct_opt:
                    # Wrong answer selected
                    st.error(f"❌ **{label}. {text}** ← Your answer (Incorrect)")
                elif is_correct_opt:
                    # Show correct answer
                    st.info(f"✓ **{label}. {text}** ← Correct answer")
                else:
                    # Other options
                    st.markdown(f"{label}. {text}")
            
            st.markdown("---")
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Take Another Test", key="new_test_btn", type="primary"):
            st.session_state.page = "setup"
            st.rerun()
    with col2:
        if st.button("🏠 Back to Dashboard", key="back_dashboard_btn"):
            st.session_state.page = "setup"
            st.rerun()

# ================= ROUTER =================
if st.session_state.user is None:
    # Check if on forgot password page
    if st.session_state.get("page") == "forgot_password":
        forgot_password_page()
    else:
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

