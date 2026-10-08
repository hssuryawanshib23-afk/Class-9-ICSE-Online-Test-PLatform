"""
═══════════════════════════════════════════════════════════════
CENTRALIZED CHAPTER INSERTION SCRIPT
Automatically inserts ALL chapters from Question folder
Supports: Biology, Chemistry, Physics
═══════════════════════════════════════════════════════════════
"""

import json
import os
from db_connection import get_connection, get_placeholder, USE_POSTGRES

# Base path to Question folder
QUESTION_BASE_PATH = r"Question"

def insert_chapter_data(json_file_path, subject):
    """Insert chapter, concepts, and questions from JSON file"""
    print(f"\n📖 Processing: {os.path.basename(json_file_path)}")
    
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
            return {"status": "skipped", "chapter": chapter_number}
        
        # Insert chapter
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
            concept_type = concept.get('concept_type', 'general')
            
            # Insert concept
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
                # Insert question
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
        
        return {"status": "success", "chapter": chapter_number, "concepts": len(concepts), "questions": total_questions}
        
    except Exception as e:
        conn.rollback()
        print(f"   ❌ Error: {e}")
        return {"status": "error", "chapter": chapter_number, "error": str(e)}
    finally:
        conn.close()


def process_subject(subject_name):
    """Process all chapters for a given subject"""
    print(f"\n{'='*63}")
    print(f"  PROCESSING {subject_name.upper()}")
    print(f"{'='*63}")
    
    subject_folder = os.path.join(QUESTION_BASE_PATH, subject_name)
    
    if not os.path.exists(subject_folder):
        print(f"⚠️  Folder not found: {subject_folder}")
        return {"success": 0, "skipped": 0, "errors": 0}
    
    # Get all JSON files
    files = sorted([f for f in os.listdir(subject_folder) if f.endswith(".json")])
    
    if not files:
        print(f"⚠️  No JSON files found in {subject_folder}")
        return {"success": 0, "skipped": 0, "errors": 0}
    
    print(f"\nFound {len(files)} chapter files")
    
    results = {"success": 0, "skipped": 0, "errors": 0, "total_concepts": 0, "total_questions": 0}
    
    for idx, file in enumerate(files, 1):
        file_path = os.path.join(subject_folder, file)
        print(f"\n[{idx}/{len(files)}]", end=" ")
        
        result = insert_chapter_data(file_path, subject_name)
        
        if result["status"] == "success":
            results["success"] += 1
            results["total_concepts"] += result["concepts"]
            results["total_questions"] += result["questions"]
        elif result["status"] == "skipped":
            results["skipped"] += 1
        else:
            results["errors"] += 1
    
    return results


def main():
    print("═" * 63)
    print("  CENTRALIZED CHAPTER INSERTION")
    print("  Auto-detect and insert all subjects")
    print("═" * 63)
    
    # Define subjects to process
    subjects = ["Biology", "Chemistry", "Physics"]
    
    overall_stats = {}
    
    for subject in subjects:
        stats = process_subject(subject)
        overall_stats[subject] = stats
    
    # Final summary
    print("\n" + "═" * 63)
    print("  OVERALL SUMMARY")
    print("═" * 63)
    
    grand_total_success = 0
    grand_total_questions = 0
    grand_total_concepts = 0
    
    for subject, stats in overall_stats.items():
        print(f"\n📚 {subject}:")
        print(f"   ✅ Inserted: {stats['success']} chapters")
        print(f"   ⚠️  Skipped: {stats['skipped']} chapters")
        print(f"   ❌ Errors: {stats['errors']} chapters")
        print(f"   📊 Concepts: {stats['total_concepts']}")
        print(f"   ❓ Questions: {stats['total_questions']}")
        
        grand_total_success += stats['success']
        grand_total_questions += stats['total_questions']
        grand_total_concepts += stats['total_concepts']
    
    print("\n" + "═" * 63)
    print(f"🎉 Grand Total:")
    print(f"   Chapters Inserted: {grand_total_success}")
    print(f"   Total Concepts: {grand_total_concepts}")
    print(f"   Total Questions: {grand_total_questions}")
    print("═" * 63)
    
    print("\n✨ Database insertion complete!")
    print("\n📝 Next steps:")
    print("   1. Verify: python verify_production_data.py")
    print("   2. Test the app with new Biology chapters")


if __name__ == "__main__":
    main()
