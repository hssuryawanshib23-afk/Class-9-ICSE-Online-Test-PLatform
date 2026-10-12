import "server-only";
import { query } from "@/lib/db";

export type SubjectSummary = { subject: string; chapters: number; questions: number };
export type StudentStats = {
  taken: number;
  average: number | null;
  best: number | null;
  recent: { id: number; score: number; total: number; at: Date }[];
};

export async function getSubjectSummaries(): Promise<SubjectSummary[]> {
  return query<SubjectSummary>(
    `SELECT COALESCE(ch.subject, 'Physics') AS subject,
            COUNT(DISTINCT ch.id)::int AS chapters,
            COUNT(q.id)::int AS questions
       FROM chapters ch
       LEFT JOIN concepts c ON c.chapter_id = ch.id
       LEFT JOIN questions q ON q.concept_id = c.id
      GROUP BY 1 ORDER BY 1`,
  );
}

export async function getStudentStats(userId: number): Promise<StudentStats> {
  const [agg] = await query<{ taken: number; average: number | null; best: number | null }>(
    `SELECT COUNT(*)::int AS taken,
            AVG(score * 100.0 / NULLIF(total_questions, 0))::float8 AS average,
            MAX(score * 100.0 / NULLIF(total_questions, 0))::float8 AS best
       FROM test_attempts WHERE student_id = $1`,
    [userId],
  );
  const recent = await query<{ id: number; score: number; total: number; at: Date }>(
    `SELECT id, score, total_questions AS total, started_at AT TIME ZONE 'UTC' AS at
       FROM test_attempts WHERE student_id = $1
      ORDER BY started_at DESC LIMIT 5`,
    [userId],
  );
  return { taken: agg.taken, average: agg.average, best: agg.best, recent };
}
