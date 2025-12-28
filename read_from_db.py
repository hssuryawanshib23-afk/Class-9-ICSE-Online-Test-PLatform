import sqlite3

DB_PATH = r"C:\Users\Dell\Desktop\Harsh\Projects\classplus chatbot\database\quiz.db"

CHAPTER_NUMBER = 10
DIFFICULTY = "medium"        # easy | medium | hard
FORM = "trap"              # definition | identification | trap | application | comparison | reason

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT q.question_text, q.expected_answer, q.form, q.difficulty
        FROM questions q
        JOIN concepts c ON q.concept_id = c.id
        JOIN chapters ch ON c.chapter_id = ch.id
        WHERE ch.chapter_number = ?
          AND q.difficulty = ?
          AND q.form = ?
        ORDER BY RANDOM()
        LIMIT 5
    """, (CHAPTER_NUMBER, DIFFICULTY, FORM))

    rows = cursor.fetchall()

    print(
        f"\n📘 RANDOM {DIFFICULTY.upper()} / {FORM.upper()} QUESTIONS "
        f"FROM CHAPTER {CHAPTER_NUMBER}:\n"
    )

    for i, (question, answer, form, diff) in enumerate(rows, 1):
        print(f"{i}. ({diff}, {form}) {question}")
        print(f"   👉 Answer: {answer}\n")

    conn.close()

if __name__ == "__main__":
    main()
