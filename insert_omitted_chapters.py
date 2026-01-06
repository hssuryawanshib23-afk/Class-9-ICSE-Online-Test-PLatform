"""
═══════════════════════════════════════════════════════════════
INSERT OMITTED PHYSICS CHAPTERS (1 & 6) INTO DATABASE
Run this after completing database migrations
═══════════════════════════════════════════════════════════════
"""

import json
import os
from db_connection import get_connection, get_placeholder, USE_POSTGRES

# Paths to omitted chapter files
CHAPTER_1_FILE = r"Question\Physics\chapter_1_omitted.json"
CHAPTER_6_FILE = r"Question\Physics\chapter_6_omitted.json"

def insert_chapter_data(json_file_path, subject="Physics"):
    """Insert chapter, concepts, and questions from JSON file"""
    print(f"\n📖 Processing: {json_file_path}")
    
    # Load JSON
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    chapter_info = data['chapter']
    chapter_number = chapter_info['chapter_number']
    chapter_name = chapter_info.get('chapter_name', f'Chapter {chapter_number}')
    
    print(f"   Subject: {subject}")
    print(f"   Chapter: {chapter_number} - {chapter_name}")
    
    conn = get_connection()
    cur = conn.cursor()
    placeholder = get_placeholder()
    
    try:
        # Check if chapter already exists
        cur.execute(f"""
            SELECT id FROM chapters 
            WHERE subject = {placeholder} AND chapter_number = {placeholder}
        """, (subject, chapter_number))
        
        existing = cur.fetchone()
        if existing:
            print(f"   ⚠️  Chapter {chapter_number} already exists. Skipping...")
            conn.close()
            return
        
        # Insert chapter with chapter_name
        if USE_POSTGRES:
            cur.execute(f"""
                INSERT INTO chapters (subject, chapter_number, chapter_name) 
                VALUES ({placeholder}, {placeholder}, {placeholder}) 
                RETURNING id
            """, (subject, chapter_number, chapter_name))
            chapter_id = cur.fetchone()[0]
        else:
            cur.execute(f"""
                INSERT INTO chapters (subject, chapter_number, chapter_name) 
                VALUES ({placeholder}, {placeholder}, {placeholder})
            """, (subject, chapter_number, chapter_name))
            chapter_id = cur.lastrowid
        
        print(f"   ✓ Created chapter (ID: {chapter_id})")
        
        # Insert concepts and questions
        concepts = data['concepts']
        total_questions = 0
        
        for concept in concepts:
            concept_name = concept['concept_name']
            concept_type = concept.get('concept_type', 'general')  # Default to 'general' if missing
            
            # Insert concept with concept_type
            if USE_POSTGRES:
                cur.execute(f"""
                    INSERT INTO concepts (chapter_id, concept_name, concept_type) 
                    VALUES ({placeholder}, {placeholder}, {placeholder}) 
                    RETURNING id
                """, (chapter_id, concept_name, concept_type))
                concept_id = cur.fetchone()[0]
            else:
                cur.execute(f"""
                    INSERT INTO concepts (chapter_id, concept_name, concept_type) 
                    VALUES ({placeholder}, {placeholder}, {placeholder})
                """, (chapter_id, concept_name, concept_type))
                concept_id = cur.lastrowid
            
            # Insert questions
            questions = concept['questions']
            for q in questions:
                # Insert question with all required fields
                if USE_POSTGRES:
                    cur.execute(f"""
                        INSERT INTO questions (concept_id, difficulty, question_text, form, thinking_type, correct_label, key_concept) 
                        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}) 
                        RETURNING id
                    """, (concept_id, q['difficulty'], q['question_text'], q['form'], q['thinking_type'], q['correct_label'], q['key_concept']))
                    question_id = cur.fetchone()[0]
                else:
                    cur.execute(f"""
                        INSERT INTO questions (concept_id, difficulty, question_text, form, thinking_type, correct_label, key_concept) 
                        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                    """, (concept_id, q['difficulty'], q['question_text'], q['form'], q['thinking_type'], q['correct_label'], q['key_concept']))
                    question_id = cur.lastrowid
                
                # Insert MCQ options
                for opt in q['options']:
                    is_correct = 1 if opt['is_correct'] else 0
                    cur.execute(f"""
                        INSERT INTO mcq_options (question_id, label, option_text, is_correct) 
                        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})
                    """, (question_id, opt['label'], opt['text'], is_correct))
                
                total_questions += 1
        
        conn.commit()
        print(f"   ✓ Inserted {len(concepts)} concepts")
        print(f"   ✓ Inserted {total_questions} questions")
        print(f"   🎉 Chapter {chapter_number} successfully added!")
        
    except Exception as e:
        conn.rollback()
        print(f"   ❌ Error: {e}")
        raise
    finally:
        conn.close()


def main():
    print("═" * 63)
    print("  INSERTING OMITTED PHYSICS CHAPTERS (1 & 6)")
    print("═" * 63)
    
    # Check if files exist
    if not os.path.exists(CHAPTER_1_FILE):
        print(f"❌ File not found: {CHAPTER_1_FILE}")
        return
    
    if not os.path.exists(CHAPTER_6_FILE):
        print(f"❌ File not found: {CHAPTER_6_FILE}")
        return
    
    # Insert Chapter 1
    insert_chapter_data(CHAPTER_1_FILE, subject="Physics")
    
    # Insert Chapter 6
    insert_chapter_data(CHAPTER_6_FILE, subject="Physics")
    
    print("\n═" * 63)
    print("  ✅ ALL OMITTED CHAPTERS INSERTED SUCCESSFULLY!")
    print("═" * 63)
    print("\nNext steps:")
    print("1. Update CHAPTER_NAMES in streamlit_app.py to include chapters 1 & 6")
    print("2. Test the app to ensure chapters appear correctly")
    print()


if __name__ == "__main__":
    main()
