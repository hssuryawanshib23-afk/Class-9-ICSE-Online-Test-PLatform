import "server-only";
import { query } from "@/lib/db";
import { getHistory } from "@/lib/results";

export type SubjectSummary = { subject: string; chapters: number; questions: number };
export type StudentStats = {
  taken: number;
  average: number | null;
  best: number | null;
  recent: { id: number; type: "custom" | "admin"; name: string; score: number; total: number; at: Date }[];
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
  const all = await getHistory(userId);
  const pcts = all.filter((r) => r.total > 0).map((r) => (r.score * 100) / r.total);
  return {
    taken: all.length,
    average: pcts.length ? pcts.reduce((a, b) => a + b, 0) / pcts.length : null,
    best: pcts.length ? Math.max(...pcts) : null,
    recent: all.slice(0, 5).map((r) => ({ id: r.id, type: r.type, name: r.name, score: r.score, total: r.total, at: r.at })),
  };
}
