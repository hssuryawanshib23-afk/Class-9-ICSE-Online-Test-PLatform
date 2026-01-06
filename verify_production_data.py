"""
Verify production database has the data
"""
from db_connection import get_connection, get_placeholder

conn = get_connection()
cur = conn.cursor()

print("\n" + "="*60)
print("CHECKING PRODUCTION DATABASE")
print("="*60)

# Check chapters
cur.execute("SELECT subject, chapter_number, chapter_name FROM chapters ORDER BY subject, chapter_number")
chapters = cur.fetchall()

print(f"\nTotal chapters: {len(chapters)}")
print("\nChapters in database:")
for subject, ch_num, ch_name in chapters:
    print(f"  {subject} - Chapter {ch_num}: {ch_name}")

# Check concepts per subject
cur.execute("""
    SELECT ch.subject, COUNT(DISTINCT c.id) as concept_count
    FROM chapters ch
    LEFT JOIN concepts c ON ch.id = c.chapter_id
    GROUP BY ch.subject
""")
concept_counts = cur.fetchall()

print("\nConcepts per subject:")
for subject, count in concept_counts:
    print(f"  {subject}: {count} concepts")

# Check Chemistry specifically
placeholder = get_placeholder()
cur.execute(f"""
    SELECT ch.chapter_number, ch.chapter_name, COUNT(c.id) as concepts
    FROM chapters ch
    LEFT JOIN concepts c ON ch.id = c.chapter_id
    WHERE ch.subject = {placeholder}
    GROUP BY ch.chapter_number, ch.chapter_name
    ORDER BY ch.chapter_number
""", ("Chemistry",))

chem = cur.fetchall()
print(f"\nChemistry chapters: {len(chem)}")
for ch_num, ch_name, concepts in chem:
    print(f"  Chapter {ch_num}: {ch_name} ({concepts} concepts)")

conn.close()
print("\n" + "="*60)
