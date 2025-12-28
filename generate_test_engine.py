import random
from db_connection import get_connection


def generate_test(chapters, difficulties, total_questions):
    """
    chapters: list[int]
    difficulties: list[str]  -> ["easy","medium","hard"]
    total_questions: int
    """

    conn = get_connection()
    cur = conn.cursor()

    ch_placeholders = ",".join(["%s"] * len(chapters))
    diff_placeholders = ",".join(["%s"] * len(difficulties))

    query = """
        SELECT q.id, q.question_text
        FROM questions q
        JOIN concepts c ON q.concept_id = c.id
        JOIN chapters ch ON c.chapter_id = ch.id
        WHERE ch.chapter_number IN ({})
          AND q.difficulty IN ({})
    """.format(ch_placeholders, diff_placeholders)

    cur.execute(query, (*chapters, *difficulties))
    rows = cur.fetchall()

    if len(rows) < total_questions:
        conn.close()
        return None  # caller must handle shortage

    random.shuffle(rows)
    selected = rows[:total_questions]

    questions = []
    for qid, qtext in selected:
        cur.execute(
            "SELECT label, option_text, is_correct FROM mcq_options WHERE question_id = %s",
            (qid,)
        )
        options = cur.fetchall()
        random.shuffle(options)

        questions.append({
            "id": qid,
            "text": qtext,
            "options": options
        })

    conn.close()
    return questions
