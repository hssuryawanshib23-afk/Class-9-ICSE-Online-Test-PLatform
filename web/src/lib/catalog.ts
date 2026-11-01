import "server-only";
import { query } from "@/lib/db";
import type { ChapterData } from "@/components/ConceptPicker";

export async function getSubjects(): Promise<string[]> {
  return (
    await query<{ subject: string }>(
      `SELECT DISTINCT COALESCE(ch.subject, 'Physics') AS subject
         FROM chapters ch JOIN concepts c ON c.chapter_id = ch.id JOIN questions q ON q.concept_id = c.id
        ORDER BY 1`,
    )
  ).map((r) => r.subject);
}

/** Chapters → concepts with per-difficulty question counts, for one subject. Concepts without questions are dropped. */
export async function getChapters(subject: string): Promise<ChapterData[]> {
  const rows = await query<{
    chapter_number: number;
    chapter_name: string | null;
    concept_id: number;
    concept_name: string;
    easy: number;
    medium: number;
    hard: number;
  }>(
    `SELECT ch.chapter_number, ch.chapter_name, c.id AS concept_id, c.concept_name,
            COUNT(q.id) FILTER (WHERE q.difficulty = 'easy')::int AS easy,
            COUNT(q.id) FILTER (WHERE q.difficulty = 'medium')::int AS medium,
            COUNT(q.id) FILTER (WHERE q.difficulty = 'hard')::int AS hard
       FROM chapters ch
       JOIN concepts c ON c.chapter_id = ch.id
       LEFT JOIN questions q ON q.concept_id = c.id
      WHERE COALESCE(ch.subject, 'Physics') = $1
      GROUP BY ch.chapter_number, ch.chapter_name, c.id, c.concept_name
      ORDER BY ch.chapter_number, c.id`,
    [subject],
  );
  const byChapter = new Map<number, ChapterData>();
  for (const r of rows) {
    const ch = byChapter.get(r.chapter_number) ?? { number: r.chapter_number, name: r.chapter_name || `Chapter ${r.chapter_number}`, concepts: [] };
    if (r.easy + r.medium + r.hard > 0) ch.concepts.push({ id: r.concept_id, name: r.concept_name, easy: r.easy, medium: r.medium, hard: r.hard });
    byChapter.set(r.chapter_number, ch);
  }
  return [...byChapter.values()].filter((c) => c.concepts.length > 0);
}
