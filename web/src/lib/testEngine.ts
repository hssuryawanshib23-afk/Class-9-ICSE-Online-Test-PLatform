import "server-only";
import { randomInt } from "node:crypto";
import { query } from "@/lib/db";
import { splitCounts } from "@/lib/difficulty";

export type Difficulty = "easy" | "medium" | "hard";

/** Fisher–Yates with a CSPRNG, so question and option order cannot be predicted. */
export function shuffle<T>(items: readonly T[]): T[] {
  const a = [...items];
  for (let i = a.length - 1; i > 0; i--) {
    const j = randomInt(0, i + 1);
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

export type SessionQuestion = { id: number; options: string[] };

/**
 * Port of generate_test_from_concepts: picks questions per difficulty from the chosen concepts.
 * Returns null when any difficulty bucket does not have enough questions.
 */
export async function generateFromConcepts(
  conceptIds: number[],
  total: number,
  easyPct: number,
  mediumPct: number,
): Promise<SessionQuestion[] | null> {
  const counts = splitCounts(total, easyPct, mediumPct);
  const picked: number[] = [];

  for (const difficulty of ["easy", "medium", "hard"] as const) {
    const need = counts[difficulty];
    if (need === 0) continue;
    const rows = await query<{ id: number }>(
      "SELECT id FROM questions WHERE concept_id = ANY($1) AND difficulty = $2",
      [conceptIds, difficulty],
    );
    if (rows.length < need) return null;
    picked.push(...shuffle(rows.map((r) => r.id)).slice(0, need));
  }

  return withOptionOrder(shuffle(picked));
}

/** Attaches a random option display order to each question id. */
export async function withOptionOrder(questionIds: number[]): Promise<SessionQuestion[]> {
  if (questionIds.length === 0) return [];
  const rows = await query<{ question_id: number; label: string }>(
    "SELECT question_id, label FROM mcq_options WHERE question_id = ANY($1)",
    [questionIds],
  );
  const byQuestion = new Map<number, string[]>();
  for (const r of rows) {
    const list = byQuestion.get(r.question_id) ?? [];
    list.push(r.label.trim());
    byQuestion.set(r.question_id, list);
  }
  return questionIds.map((id) => ({ id, options: shuffle(byQuestion.get(id) ?? []) }));
}
