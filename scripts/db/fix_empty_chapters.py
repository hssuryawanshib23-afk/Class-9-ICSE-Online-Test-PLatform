"""
Delete empty Chemistry chapters and Physics chapters 1 & 6, then re-insert with full data
"""
from db_connection import get_connection, get_placeholder

conn = get_connection()
cur = conn.cursor()
placeholder = get_placeholder()

print("\n" + "="*60)
print("FIXING EMPTY CHAPTERS")
print("="*60)

# Check which chapters have no concepts
cur.execute("""
    SELECT ch.id, ch.subject, ch.chapter_number, ch.chapter_name, COUNT(c.id) as concept_count
    FROM chapters ch
    LEFT JOIN concepts c ON ch.id = c.chapter_id
    GROUP BY ch.id, ch.subject, ch.chapter_number, ch.chapter_name
    HAVING COUNT(c.id) = 0
    ORDER BY ch.subject, ch.chapter_number
""")

empty_chapters = cur.fetchall()

if empty_chapters:
    print(f"\nFound {len(empty_chapters)} empty chapters:")
    for ch_id, subject, ch_num, ch_name, count in empty_chapters:
        print(f"  ID {ch_id}: {subject} Chapter {ch_num} - {ch_name or 'No name'} ({count} concepts)")
    
    # Delete these empty chapters
    print("\nDeleting empty chapters...")
    for ch_id, subject, ch_num, ch_name, count in empty_chapters:
        cur.execute(f"DELETE FROM chapters WHERE id = {placeholder}", (ch_id,))
        print(f"  ✓ Deleted {subject} Chapter {ch_num}")
    
    conn.commit()
    print("\n✅ Empty chapters deleted!")
else:
    print("\nNo empty chapters found.")

conn.close()
print("="*60)
