"""
Fix Chemistry Chapter 5 Concept 9 Question 4 answer.
Changes correct answer from C (Chlorine) to D (Argon).
"""
import json
from db_connection import get_connection

def fix_ch5_q4():
    """Update the specific question in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # First, find the question by its text to get the ID
        cursor.execute("""
            SELECT q.id, q.question_text, q.correct_label 
            FROM questions q
            WHERE q.question_text = 'In the third period, which element is likely to have the smallest atomic size?'
        """)
        
        result = cursor.fetchone()
        if not result:
            print("❌ Question not found!")
            return
        
        question_id = result[0]
        print(f"✓ Found question with ID: {question_id}")
        print(f"  Current correct_label: {result[2]}")
        
        # Step 1: Update the correct_label in questions table
        cursor.execute("""
            UPDATE questions 
            SET correct_label = 'D',
                key_concept = 'Noble gases (Group 18) have the smallest atomic size in a period due to maximum effective nuclear charge.'
            WHERE id = %s
        """, (question_id,))
        print(f"✓ Updated correct_label to 'D' for question ID {question_id}")
        
        # Step 2: Update is_correct in mcq_options table - set C to false
        cursor.execute("""
            UPDATE mcq_options 
            SET is_correct = 0
            WHERE question_id = %s AND label = 'C'
        """, (question_id,))
        print(f"✓ Set option C (Chlorine) as incorrect")
        
        # Step 3: Update is_correct in mcq_options table - set D to true
        cursor.execute("""
            UPDATE mcq_options 
            SET is_correct = 1
            WHERE question_id = %s AND label = 'D'
        """, (question_id,))
        print(f"✓ Set option D (Argon) as correct")
        
        # Commit the changes
        conn.commit()
        
        # Verify the changes
        cursor.execute("""
            SELECT q.id, q.question_text, q.correct_label, q.key_concept,
                   o.label, o.option_text, o.is_correct
            FROM questions q
            JOIN mcq_options o ON q.id = o.question_id
            WHERE q.id = %s
            ORDER BY o.label
        """, (question_id,))
        
        print("\n✓ Verification - Updated question details:")
        results = cursor.fetchall()
        if results:
            print(f"Question ID: {results[0][0]}")
            print(f"Question: {results[0][1]}")
            print(f"Correct Label: {results[0][2]}")
            print(f"Key Concept: {results[0][3]}")
            print("\nOptions:")
            for row in results:
                correct_marker = "✓ CORRECT" if row[6] else ""
                print(f"  {row[4]}: {row[5]} {correct_marker}")
        
        print("\n✅ Successfully fixed CH5_C9_Q4 answer!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_ch5_q4()
