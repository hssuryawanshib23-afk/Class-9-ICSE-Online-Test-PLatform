"""
Script to fix the two questions with incorrect answers
Run this locally (SQLite) and on Neon.tech (PostgreSQL)
"""

from db_connection import get_connection

def fix_questions():
    conn = get_connection()
    cur = conn.cursor()
    
    print("Fixing questions with incorrect answers...")
    
    # Fix 1: Chapter 2, Concept 4 (Distance and Displacement), Question 4
    # Find the question by searching for the concept and question text
    cur.execute("""
        SELECT q.id, q.question_text 
        FROM questions q
        JOIN concepts c ON q.concept_id = c.id
        JOIN chapters ch ON c.chapter_id = ch.id
        WHERE ch.chapter_number = 2 
        AND c.concept_name LIKE '%Distance%Displacement%'
        ORDER BY q.id
    """)
    
    questions_ch2 = cur.fetchall()
    if len(questions_ch2) >= 4:
        question_id_1 = questions_ch2[3][0]  # 4th question (index 3)
        print(f"\nChapter 2, Concept 4, Question 4:")
        print(f"  Question ID: {question_id_1}")
        print(f"  Text: {questions_ch2[3][1][:80]}...")
        
        # Update: Set D to incorrect, C to correct
        cur.execute("""
            UPDATE mcq_options 
            SET is_correct = 0 
            WHERE question_id = ? AND label = 'D'
        """, (question_id_1,))
        
        cur.execute("""
            UPDATE mcq_options 
            SET is_correct = 1 
            WHERE question_id = ? AND label = 'C'
        """, (question_id_1,))
        
        print("  ✅ Fixed: Changed correct answer from D to C")
    
    # Fix 2: Chapter 4, Concept 2 (Pressure), Question 3
    cur.execute("""
        SELECT q.id, q.question_text 
        FROM questions q
        JOIN concepts c ON q.concept_id = c.id
        JOIN chapters ch ON c.chapter_id = ch.id
        WHERE ch.chapter_number = 4 
        AND c.concept_name LIKE '%Pressure%'
        ORDER BY q.id
    """)
    
    questions_ch4 = cur.fetchall()
    if len(questions_ch4) >= 3:
        question_id_2 = questions_ch4[2][0]  # 3rd question (index 2)
        print(f"\nChapter 4, Concept 2, Question 3:")
        print(f"  Question ID: {question_id_2}")
        print(f"  Text: {questions_ch4[2][1][:80]}...")
        
        # Set all to incorrect first, then C to correct
        cur.execute("""
            UPDATE mcq_options 
            SET is_correct = 0 
            WHERE question_id = ?
        """, (question_id_2,))
        
        cur.execute("""
            UPDATE mcq_options 
            SET is_correct = 1 
            WHERE question_id = ? AND label = 'C'
        """, (question_id_2,))
        
        print("  ✅ Fixed: Set correct answer to C")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*50)
    print("✅ All fixes applied successfully!")
    print("="*50)
    print("\nFor Neon.tech (PostgreSQL):")
    print("Run the same script with USE_POSTGRES=true environment variable")
    print("Or apply the SQL updates manually in the SQL Editor")

if __name__ == "__main__":
    fix_questions()
