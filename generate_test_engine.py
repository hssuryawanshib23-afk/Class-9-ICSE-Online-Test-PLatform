import random
from db_connection import get_connection, get_placeholder, adapt_query, get_last_insert_id, USE_POSTGRES


def generate_test_from_concepts(concept_ids, total_questions, easy_pct=30, medium_pct=30, hard_pct=40):
    """
    Generate a test with specific difficulty distribution from selected concepts.
    
    Args:
        concept_ids: list[int] - Concept IDs to include
        total_questions: int - Total number of questions
        easy_pct: int - Percentage of easy questions (default 30%)
        medium_pct: int - Percentage of medium questions (default 30%)
        hard_pct: int - Percentage of hard questions (default 40%)
    
    Returns:
        list of question dicts or None if insufficient questions
    """
    if easy_pct + medium_pct + hard_pct != 100:
        raise ValueError("Percentages must add up to 100")
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Calculate required questions per difficulty
    easy_count = round(total_questions * easy_pct / 100)
    medium_count = round(total_questions * medium_pct / 100)
    hard_count = total_questions - easy_count - medium_count  # Ensure exact total
    
    # Use appropriate placeholder for database type
    placeholder = get_placeholder()
    concept_placeholders = ",".join([placeholder] * len(concept_ids))
    
    selected_questions = []
    
    # Fetch questions for each difficulty level
    for difficulty, count in [("easy", easy_count), ("medium", medium_count), ("hard", hard_count)]:
        if count == 0:
            continue
            
        query = """
            SELECT q.id, q.question_text, q.difficulty
            FROM questions q
            WHERE q.concept_id IN ({})
              AND q.difficulty = {}
        """.format(concept_placeholders, placeholder)
        
        cur.execute(query, (*concept_ids, difficulty))
        rows = cur.fetchall()
        
        if len(rows) < count:
            conn.close()
            return None  # Not enough questions of this difficulty
        
        random.shuffle(rows)
        selected_questions.extend(rows[:count])
    
    # Shuffle all selected questions
    random.shuffle(selected_questions)
    
    # Build final question list with options
    questions = []
    for qid, qtext, difficulty in selected_questions:
        cur.execute(
            "SELECT label, option_text, is_correct FROM mcq_options WHERE question_id = {}".format(placeholder),
            (qid,)
        )
        options = cur.fetchall()
        random.shuffle(options)
        
        questions.append({
            "id": qid,
            "text": qtext,
            "difficulty": difficulty,
            "options": options
        })
    
    conn.close()
    return questions


def generate_test_with_difficulty_cap(chapters, total_questions, easy_pct=30, medium_pct=30, hard_pct=40, subject="Physics"):
    """
    Generate a test with specific difficulty distribution.
    
    Args:
        chapters: list[int] - Chapter numbers to include
        total_questions: int - Total number of questions
        easy_pct: int - Percentage of easy questions (default 30%)
        medium_pct: int - Percentage of medium questions (default 30%)
        hard_pct: int - Percentage of hard questions (default 40%)
        subject: str - Subject name (default "Physics")
    
    Returns:
        list of question dicts or None if insufficient questions
    """
    if easy_pct + medium_pct + hard_pct != 100:
        raise ValueError("Percentages must add up to 100")
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Calculate required questions per difficulty
    easy_count = round(total_questions * easy_pct / 100)
    medium_count = round(total_questions * medium_pct / 100)
    hard_count = total_questions - easy_count - medium_count  # Ensure exact total
    
    # Use appropriate placeholder for database type
    placeholder = get_placeholder()
    ch_placeholders = ",".join([placeholder] * len(chapters))
    
    selected_questions = []
    
    # Fetch questions for each difficulty level
    for difficulty, count in [("easy", easy_count), ("medium", medium_count), ("hard", hard_count)]:
        if count == 0:
            continue
            
        query = """
            SELECT q.id, q.question_text, q.difficulty
            FROM questions q
            JOIN concepts c ON q.concept_id = c.id
            JOIN chapters ch ON c.chapter_id = ch.id
            WHERE ch.chapter_number IN ({})
              AND ch.subject = {}
              AND q.difficulty = {}
        """.format(ch_placeholders, placeholder, placeholder)
        
        cur.execute(query, (*chapters, subject, difficulty))
        rows = cur.fetchall()
        
        if len(rows) < count:
            conn.close()
            return None  # Not enough questions of this difficulty
        
        random.shuffle(rows)
        selected_questions.extend(rows[:count])
    
    # Shuffle all selected questions
    random.shuffle(selected_questions)
    
    # Build final question list with options
    questions = []
    for qid, qtext, difficulty in selected_questions:
        cur.execute(
            "SELECT label, option_text, is_correct FROM mcq_options WHERE question_id = {}".format(placeholder),
            (qid,)
        )
        options = cur.fetchall()
        random.shuffle(options)
        
        questions.append({
            "id": qid,
            "text": qtext,
            "difficulty": difficulty,
            "options": options
        })
    
    conn.close()
    return questions


def generate_test(chapters, difficulties, total_questions):
    """
    LEGACY: Generate test with selected difficulties (no percentage control).
    Kept for backward compatibility.
    
    chapters: list[int]
    difficulties: list[str]  -> ["easy","medium","hard"]
    total_questions: int
    """

    conn = get_connection()
    cur = conn.cursor()

    placeholder = get_placeholder()
    ch_placeholders = ",".join([placeholder] * len(chapters))
    diff_placeholders = ",".join([placeholder] * len(difficulties))

    query = """
        SELECT q.id, q.question_text
        FROM questions q
        JOIN concepts c ON q.concept_id = c.id
        JOIN chapters ch ON c.chapter_id = ch.id
        WHERE ch.chapter_number IN ({})
          AND q.difficulty IN ({})
    """.format(ch_placeholders, diff_placeholders)

    cur.execute(query, (*chapters, *difficulties))
    rows = cur.fetchall()

    if len(rows) < total_questions:
        conn.close()
        return None  # caller must handle shortage

    random.shuffle(rows)
    selected = rows[:total_questions]

    questions = []
    for qid, qtext in selected:
        cur.execute(
            "SELECT label, option_text, is_correct FROM mcq_options WHERE question_id = {}".format(placeholder),
            (qid,)
        )
        options = cur.fetchall()
        random.shuffle(options)

        questions.append({
            "id": qid,
            "text": qtext,
            "options": options
        })

    conn.close()
    return questions


def create_admin_test(test_name, chapters, total_questions, duration_minutes, 
                      easy_pct, medium_pct, hard_pct, created_by_user_id, subject="Physics", concept_ids=None, allow_retake=False):
    """
    Create an admin test with pre-generated questions.
    
    Args:
        test_name: str - Name of the test
        chapters: list[int] - Chapter numbers (used if concept_ids is None)
        total_questions: int - Total questions
        duration_minutes: int - Test duration
        easy_pct, medium_pct, hard_pct: int - Difficulty percentages
        created_by_user_id: int - Admin user ID
        subject: str - Subject name (default "Physics")
        concept_ids: list[int] - Specific concept IDs (overrides chapters if provided)
        allow_retake: bool - Allow students to take the test multiple times (default False)
    
    Returns:
        int - admin_test_id or None if failed
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Generate questions with difficulty distribution
        if concept_ids:
            # Use concept-based generation
            questions = generate_test_from_concepts(
                concept_ids, total_questions, easy_pct, medium_pct, hard_pct
            )
        else:
            # Use chapter-based generation
            questions = generate_test_with_difficulty_cap(
                chapters, total_questions, easy_pct, medium_pct, hard_pct, subject
            )
        
        if questions is None:
            conn.close()
            return None
        
        # Store chapters as comma-separated string
        chapters_str = ",".join(map(str, chapters))
        
        placeholder = get_placeholder()
        
        # Insert admin test - database agnostic
        if USE_POSTGRES:
            # PostgreSQL with RETURNING
            query = """
                INSERT INTO admin_tests 
                (test_name, created_by, total_questions, duration_minutes,
                 easy_percentage, medium_percentage, hard_percentage, chapters, is_active, allow_retake)
                VALUES ({}, {}, {}, {}, {}, {}, {}, {}, true, {})
                RETURNING admin_test_id
            """.format(*([placeholder] * 9))
            
            cur.execute(query, (test_name, created_by_user_id, total_questions, duration_minutes,
                  easy_pct, medium_pct, hard_pct, chapters_str, allow_retake))
            admin_test_id = cur.fetchone()[0]
        else:
            # SQLite without RETURNING
            query = """
                INSERT INTO admin_tests 
                (test_name, created_by, total_questions, duration_minutes,
                 easy_percentage, medium_percentage, hard_percentage, chapters, is_active, allow_retake)
                VALUES ({}, {}, {}, {}, {}, {}, {}, {}, 1, {})
            """.format(*([placeholder] * 9))
            
            cur.execute(query, (test_name, created_by_user_id, total_questions, duration_minutes,
                  easy_pct, medium_pct, hard_pct, chapters_str, 1 if allow_retake else 0))
            admin_test_id = cur.lastrowid
        
        # Link questions to this test
        for order, q in enumerate(questions, 1):
            query = """
                INSERT INTO admin_test_questions (admin_test_id, question_id, question_order)
                VALUES ({}, {}, {})
            """.format(placeholder, placeholder, placeholder)
            cur.execute(query, (admin_test_id, q["id"], order))
        
        conn.commit()
        conn.close()
        return admin_test_id
        
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e


def get_admin_test_questions(admin_test_id):
    """
    Retrieve all questions for an admin test in correct order.
    
    Returns:
        list of question dicts with options
    """
    conn = get_connection()
    cur = conn.cursor()
    
    placeholder = get_placeholder()
    
    # Get questions in order
    query = """
        SELECT q.id, q.question_text, q.difficulty
        FROM admin_test_questions atq
        JOIN questions q ON atq.question_id = q.id
        WHERE atq.admin_test_id = {}
        ORDER BY atq.question_order
    """.format(placeholder)
    
    cur.execute(query, (admin_test_id,))
    
    question_rows = cur.fetchall()
    
    questions = []
    for qid, qtext, difficulty in question_rows:
        cur.execute(
            "SELECT label, option_text, is_correct FROM mcq_options WHERE question_id = {}".format(placeholder),
            (qid,)
        )
        options = cur.fetchall()
        random.shuffle(options)  # Shuffle options for each student
        
        questions.append({
            "id": qid,
            "text": qtext,
            "difficulty": difficulty,
            "options": options
        })
    
    conn.close()
    return questions


def get_available_admin_tests():
    """Get all active admin tests."""
    conn = get_connection()
    cur = conn.cursor()
    
    # Database-agnostic query for boolean/integer is_active
    if USE_POSTGRES:
        active_check = "at.is_active = true"
    else:
        active_check = "at.is_active = 1"
    
    query = """
        SELECT 
            at.admin_test_id, at.test_name, at.total_questions,
            at.duration_minutes, at.easy_percentage, at.medium_percentage,
            at.hard_percentage, u.username, at.created_at
        FROM admin_tests at
        JOIN users u ON at.created_by = u.id
        WHERE {}
        ORDER BY at.created_at DESC
    """.format(active_check)
    
    cur.execute(query)
    
    tests = cur.fetchall()
    conn.close()
    return tests
