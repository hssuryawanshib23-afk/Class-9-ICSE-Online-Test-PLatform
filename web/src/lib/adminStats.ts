import "server-only";
import { query } from "@/lib/db";

/** Every answered question from both kinds of tests, one row each: (student, question, correct?). */
const ALL_RESPONSES = `
  SELECT ta.student_id AS uid, r.question_id, r.is_correct
    FROM responses r JOIN test_attempts ta ON ta.id = r.attempt_id
  UNION ALL
  SELECT a.user_id AS uid, r.question_id, r.is_correct
    FROM admin_test_responses r JOIN admin_test_attempts a ON a.attempt_id = r.attempt_id`;

/** Every finished test from both kinds of tests, one row each. */
const ALL_ATTEMPTS = `
  SELECT student_id AS uid, score, total_questions AS total, started_at AS at FROM test_attempts
  UNION ALL
  SELECT user_id AS uid, score, total_questions AS total, attempted_at AS at FROM admin_test_attempts`;

export type Overview = { students: number; tests: number; accuracy: number | null; answered: number };

export async function getOverview(): Promise<Overview> {
  const [o] = await query<Overview>(
    `SELECT (SELECT COUNT(*) FROM users WHERE role = 'student')::int AS students,
            (SELECT COUNT(*) FROM (${ALL_ATTEMPTS}) x)::int AS tests,
            (SELECT AVG(score * 100.0 / NULLIF(total, 0)) FROM (${ALL_ATTEMPTS}) x)::float8 AS accuracy,
            (SELECT COUNT(*) FROM (${ALL_RESPONSES}) y)::int AS answered`,
  );
  return o;
}

export type StudentPerf = {
  id: number;
  username: string;
  tests: number;
  avg: number;
  best: number;
  worst: number;
  last: Date | null;
};

export async function getStudentPerformance(): Promise<StudentPerf[]> {
  return query<StudentPerf>(
    `SELECT u.id, u.username, COUNT(*)::int AS tests,
            AVG(x.score * 100.0 / NULLIF(x.total, 0))::float8 AS avg,
            MAX(x.score * 100.0 / NULLIF(x.total, 0))::float8 AS best,
            MIN(x.score * 100.0 / NULLIF(x.total, 0))::float8 AS worst,
            MAX(x.at) AS last
       FROM users u JOIN (${ALL_ATTEMPTS}) x ON x.uid = u.id
      WHERE u.role = 'student'
      GROUP BY u.id, u.username
      ORDER BY avg DESC, u.username`,
  );
}

export type ChapterPerf = { subject: string; chapter: number; name: string | null; answered: number; correct: number; accuracy: number };

/** Grouped by subject AND chapter number (Streamlit grouped by number only, merging Physics and Chemistry). */
export async function getChapterPerformance(studentId?: number): Promise<ChapterPerf[]> {
  return query<ChapterPerf>(
    `SELECT COALESCE(ch.subject, 'Physics') AS subject, ch.chapter_number AS chapter, MAX(ch.chapter_name) AS name,
            COUNT(*)::int AS answered, SUM(r.is_correct)::int AS correct,
            ROUND(AVG(r.is_correct) * 100, 1)::float8 AS accuracy
       FROM (${ALL_RESPONSES}) r
       JOIN questions q ON q.id = r.question_id
       JOIN concepts c ON c.id = q.concept_id
       JOIN chapters ch ON ch.id = c.chapter_id
      WHERE ($1::int IS NULL OR r.uid = $1)
      GROUP BY 1, 2 ORDER BY 1, 2`,
    [studentId ?? null],
  );
}

export type DifficultyPerf = { difficulty: string; answered: number; correct: number; accuracy: number };

export async function getDifficultyPerformance(): Promise<DifficultyPerf[]> {
  return query<DifficultyPerf>(
    `SELECT q.difficulty, COUNT(*)::int AS answered, SUM(r.is_correct)::int AS correct,
            ROUND(AVG(r.is_correct) * 100, 1)::float8 AS accuracy
       FROM (${ALL_RESPONSES}) r JOIN questions q ON q.id = r.question_id
      GROUP BY q.difficulty
      ORDER BY CASE q.difficulty WHEN 'easy' THEN 1 WHEN 'medium' THEN 2 WHEN 'hard' THEN 3 ELSE 4 END`,
  );
}

export type ConceptPerf = { id: number; name: string; subject: string; chapter: number; answered: number; correct: number; accuracy: number };

/** Concepts with too few answers are noise, so they are ignored (minAnswers). */
export async function getConceptPerformance(minAnswers = 5): Promise<ConceptPerf[]> {
  return query<ConceptPerf>(
    `SELECT c.id, c.concept_name AS name, COALESCE(ch.subject, 'Physics') AS subject, ch.chapter_number AS chapter,
            COUNT(*)::int AS answered, SUM(r.is_correct)::int AS correct,
            ROUND(AVG(r.is_correct) * 100, 1)::float8 AS accuracy
       FROM (${ALL_RESPONSES}) r
       JOIN questions q ON q.id = r.question_id
       JOIN concepts c ON c.id = q.concept_id
       JOIN chapters ch ON ch.id = c.chapter_id
      GROUP BY c.id, c.concept_name, ch.subject, ch.chapter_number
     HAVING COUNT(*) >= $1
      ORDER BY accuracy ASC, answered DESC`,
    [minAnswers],
  );
}

export type ConceptStudent = { id: number; username: string; answered: number; correct: number; accuracy: number };

export async function getConceptStudents(conceptId: number): Promise<{ name: string; students: ConceptStudent[] } | null> {
  const [c] = await query<{ concept_name: string }>("SELECT concept_name FROM concepts WHERE id = $1", [conceptId]);
  if (!c) return null;
  const students = await query<ConceptStudent>(
    `SELECT u.id, u.username, COUNT(*)::int AS answered, SUM(r.is_correct)::int AS correct,
            ROUND(AVG(r.is_correct) * 100, 1)::float8 AS accuracy
       FROM (${ALL_RESPONSES}) r
       JOIN questions q ON q.id = r.question_id
       JOIN users u ON u.id = r.uid
      WHERE q.concept_id = $1
      GROUP BY u.id, u.username
      ORDER BY accuracy ASC, answered DESC`,
    [conceptId],
  );
  return { name: c.concept_name, students };
}
