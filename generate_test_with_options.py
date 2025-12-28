import sqlite3
import random
from collections import defaultdict

DB_PATH = r"C:\Users\Dell\Desktop\Harsh\Projects\classplus chatbot\database\quiz.db"

# =============================
# INPUT CONFIG (CHANGE THESE)
# =============================

INPUT = {
    "chapters_before_mst": [10],
    "chapters_after_mst": [2,10],

    "weightage_before_mst": 40,   # %
    "weightage_after_mst": 60,    # %

    "total_questions": 40,
    "difficulty": "hard",         # easy | medium | hard
    "time_minutes": 60
}

# =============================


def fetch_options(cur, question_id):
    cur.execute("""
        SELECT label, option_text, is_correct
        FROM mcq_options
        WHERE question_id = ?
    """, (question_id,))
    options = cur.fetchall()
    random.shuffle(options)
    return options


def pick_questions_for_chapters(cur, chapters, count, difficulty):
    """
    Picks 'count' questions from given chapters
    ensuring one question per concept
    """
    selected = []

    per_chapter = count // len(chapters)
    remainder = count % len(chapters)

    for i, chapter in enumerate(chapters):
        limit = per_chapter + (1 if i < remainder else 0)

        # get concepts for chapter
        cur.execute("""
            SELECT c.id
            FROM concepts c
            JOIN chapters ch ON c.chapter_id = ch.id
            WHERE ch.chapter_number = ?
        """, (chapter,))
        concept_ids = [r[0] for r in cur.fetchall()]
        random.shuffle(concept_ids)

        concept_ids = concept_ids[:limit]

        for cid in concept_ids:
            cur.execute("""
                SELECT id, question_text
                FROM questions
                WHERE concept_id = ?
                  AND difficulty = ?
                ORDER BY RANDOM()
                LIMIT 1
            """, (cid, difficulty))

            row = cur.fetchone()
            if not row:
                continue

            qid, qtext = row
            options = fetch_options(cur, qid)

            selected.append({
                "question_id": qid,
                "question": qtext,
                "options": options
            })

    return selected


def generate_test(input_cfg):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    total_q = input_cfg["total_questions"]

    before_count = (total_q * input_cfg["weightage_before_mst"]) // 100
    after_count = total_q - before_count

    test = []

    if input_cfg["chapters_before_mst"]:
        test.extend(
            pick_questions_for_chapters(
                cur,
                input_cfg["chapters_before_mst"],
                before_count,
                input_cfg["difficulty"]
            )
        )

    if input_cfg["chapters_after_mst"]:
        test.extend(
            pick_questions_for_chapters(
                cur,
                input_cfg["chapters_after_mst"],
                after_count,
                input_cfg["difficulty"]
            )
        )

    random.shuffle(test)
    conn.close()
    return test


def main():
    test = generate_test(INPUT)

    print("\n📝 GENERATED TEST\n")
    print(f"Total Questions: {len(test)}")
    print(f"Difficulty: {INPUT['difficulty']}")
    print(f"Time: {INPUT['time_minutes']} minutes\n")

    for i, q in enumerate(test, 1):
        print(f"{i}. {q['question']}")
        for label, text, _ in q["options"]:
            print(f"   {label}. {text}")
        print()


if __name__ == "__main__":
    main()
