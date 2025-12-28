import json
import os
import sqlite3

JSON_DIR = r"C:\Users\Dell\Desktop\Harsh\Projects\classplus chatbot\Question"
DB_PATH  = r"C:\Users\Dell\Desktop\Harsh\Projects\classplus chatbot\database\quiz.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for filename in os.listdir(JSON_DIR):
        if not filename.endswith(".json"):
            continue

        print(f"📥 Ingesting {filename}")
        with open(os.path.join(JSON_DIR, filename), "r", encoding="utf-8") as f:
            data = json.load(f)

        ch = data["chapter"]

        # ----- chapter -----
        cur.execute("""
            INSERT OR IGNORE INTO chapters(subject, chapter_number, chapter_name)
            VALUES (?,?,?)
        """, (ch["subject"], ch["chapter_number"], ch["chapter_name"]))

        cur.execute("""
            SELECT id FROM chapters
            WHERE subject=? AND chapter_number=?
        """, (ch["subject"], ch["chapter_number"]))
        chapter_id = cur.fetchone()[0]

        for concept in data["concepts"]:
            # ----- concept -----
            cur.execute("""
                INSERT OR IGNORE INTO concepts(chapter_id, concept_name, concept_type)
                VALUES (?,?,?)
            """, (chapter_id, concept["concept_name"], concept["concept_type"]))

            cur.execute("""
                SELECT id FROM concepts
                WHERE chapter_id=? AND concept_name=?
            """, (chapter_id, concept["concept_name"]))
            concept_id = cur.fetchone()[0]

            for q in concept["questions"]:
                # ----- question -----
                cur.execute("""
                    INSERT INTO questions(
                        concept_id, form, difficulty, thinking_type,
                        question_text, correct_label, key_concept
                    ) VALUES (?,?,?,?,?,?,?)
                """, (
                    concept_id,
                    q["form"],
                    q["difficulty"],
                    q["thinking_type"],
                    q["question_text"],
                    q["correct_label"],
                    q["key_concept"]
                ))
                question_id = cur.lastrowid

                # ----- options -----
                for opt in q["options"]:
                    cur.execute("""
                        INSERT INTO mcq_options(
                            question_id, label, option_text, is_correct
                        ) VALUES (?,?,?,?)
                    """, (
                        question_id,
                        opt["label"],
                        opt["text"],
                        1 if opt["is_correct"] else 0
                    ))

    conn.commit()
    conn.close()
    print("🎉 FRESH DATABASE INGESTION COMPLETE")

if __name__ == "__main__":
    main()
