"""
FORCE RE-INSERT: Delete existing chapters and re-insert with full data
RUN THIS ON PRODUCTION
"""
from db_connection import get_connection, get_placeholder

conn = get_connection()
cur = conn.cursor()
placeholder = get_placeholder()

print("\n" + "="*60)
print("FORCE DELETE & RE-INSERT")
print("="*60)

# Delete Physics chapters 1 and 6
chapters_to_delete = [
    ("Physics", 1),
    ("Physics", 6),
    ("Chemistry", 1),
    ("Chemistry", 2),
    ("Chemistry", 3),
    ("Chemistry", 4),
    ("Chemistry", 5),
    ("Chemistry", 6),
    ("Chemistry", 7),
    ("Chemistry", 8),
    ("Chemistry", 9)
]

for subject, ch_num in chapters_to_delete:
    cur.execute(f"""
        DELETE FROM chapters 
        WHERE subject = {placeholder} AND chapter_number = {placeholder}
    """, (subject, ch_num))
    print(f"✓ Deleted {subject} Chapter {ch_num}")

conn.commit()
conn.close()

print("\n✅ All target chapters deleted!")
print("\nNow run:")
print("  python insert_omitted_chapters.py")
print("  python insert_chemistry_chapters.py")
print("="*60)
