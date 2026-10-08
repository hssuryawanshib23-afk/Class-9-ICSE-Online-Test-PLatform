"""
Test the EXACT query used by streamlit app for Chemistry
"""
from db_connection import get_connection, get_placeholder

subject = "Chemistry"

conn = get_connection()
cur = conn.cursor()
placeholder = get_placeholder()

print(f"\nTesting query for subject: {subject}")
print("="*60)

query = f'''
    SELECT ch.chapter_number, c.id, c.concept_name 
    FROM concepts c 
    JOIN chapters ch ON c.chapter_id = ch.id 
    WHERE ch.subject = {placeholder}
    ORDER BY ch.chapter_number, c.id
'''

print(f"Query: {query}")
print(f"Parameter: ('{subject}',)")
print("="*60)

cur.execute(query, (subject,))
rows = cur.fetchall()

print(f"\nTotal rows returned: {len(rows)}")

if rows:
    print("\nFirst 10 results:")
    for i, (ch_num, concept_id, concept_name) in enumerate(rows[:10], 1):
        print(f"  {i}. Chapter {ch_num} - Concept ID {concept_id}: {concept_name}")
    
    # Group by chapter
    concepts_by_chapter = {}
    for ch_num, concept_id, concept_name in rows:
        if ch_num not in concepts_by_chapter:
            concepts_by_chapter[ch_num] = []
        concepts_by_chapter[ch_num].append((concept_id, concept_name))
    
    print(f"\nChapters found: {sorted(concepts_by_chapter.keys())}")
    print("\nConcepts per chapter:")
    for ch_num in sorted(concepts_by_chapter.keys()):
        print(f"  Chapter {ch_num}: {len(concepts_by_chapter[ch_num])} concepts")
else:
    print("\n❌ NO RESULTS! This is the problem!")
    
    # Debug: check what subjects exist
    cur.execute("SELECT DISTINCT subject FROM chapters")
    subjects = cur.fetchall()
    print(f"\nSubjects in database: {[s[0] for s in subjects]}")
    
    # Check Chemistry specifically
    cur.execute(f"SELECT COUNT(*) FROM chapters WHERE subject = {placeholder}", (subject,))
    count = cur.fetchone()[0]
    print(f"Chemistry chapters in DB: {count}")

conn.close()
