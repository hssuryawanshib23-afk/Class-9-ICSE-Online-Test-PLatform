from db_connection import get_connection

conn = get_connection()
cur = conn.cursor()

# Get all concepts
cur.execute('''
    SELECT ch.chapter_number, c.id, c.concept_name 
    FROM concepts c 
    JOIN chapters ch ON c.chapter_id = ch.id 
    ORDER BY ch.chapter_number, c.id
''')
rows = cur.fetchall()

for r in rows:
    print(f"Chapter {r[0]} - Concept ID {r[1]}: {r[2]}")

conn.close()
