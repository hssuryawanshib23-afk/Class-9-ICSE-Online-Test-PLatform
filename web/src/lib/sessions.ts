import "server-only";
import { query, withTx } from "@/lib/db";
import type { SessionQuestion } from "@/lib/testEngine";

/** Seconds after the deadline during which a late submit is still accepted (network lag). */
export const GRACE_SECONDS = 30;

export type TestSession = {
  id: string;
  user_id: number;
  kind: "custom" | "admin";
  admin_test_id: number | null;
  questions: SessionQuestion[];
  answers: Record<string, string>;
  duration_seconds: number;
  started_at: Date;
  submitted_at: Date | null;
  attempt_id: number | null;
  score: number | null;
  total: number | null;
};

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

/** Loads a session only if it belongs to userId. Anything else looks like "not found". */
export async function loadSession(id: string, userId: number): Promise<TestSession | null> {
  if (!UUID.test(id)) return null;
  const rows = await query<TestSession>(
    "SELECT * FROM test_sessions WHERE id = $1 AND user_id = $2",
    [id, userId],
  );
  return rows[0] ?? null;
}

/** Current server time in ms. A function so server components can read the clock without an impure render call. */
export function nowMs() {
  return Date.now();
}

export function deadlineMs(s: Pick<TestSession, "started_at" | "duration_seconds">) {
  return s.started_at.getTime() + s.duration_seconds * 1000;
}

export function isPastGrace(s: Pick<TestSession, "started_at" | "duration_seconds">, now = Date.now()) {
  return now > deadlineMs(s) + GRACE_SECONDS * 1000;
}

/** Keeps only answers for questions in this session whose label is one of that question's options. */
export function sanitizeAnswers(
  questions: SessionQuestion[],
  raw: Record<string, unknown>,
): Record<string, string> {
  const out: Record<string, string> = {};
  for (const q of questions) {
    const v = raw[String(q.id)];
    if (typeof v === "string" && q.options.includes(v)) out[String(q.id)] = v;
  }
  return out;
}

/** Autosave. Ignored once the test is submitted or the grace period has passed. */
export async function saveAnswers(id: string, userId: number, raw: Record<string, unknown>) {
  const s = await loadSession(id, userId);
  if (!s || s.submitted_at || isPastGrace(s)) return false;
  await query("UPDATE test_sessions SET answers = $1::jsonb WHERE id = $2 AND submitted_at IS NULL", [
    JSON.stringify(sanitizeAnswers(s.questions, raw)),
    id,
  ]);
  return true;
}

/**
 * Grades on the server and writes the attempt in the same shape the Streamlit app reads
 * (test_attempts/responses or admin_test_attempts/admin_test_responses). Idempotent: a second
 * call on a submitted session just returns it, so a double click cannot create two attempts.
 */
export async function finalizeSession(
  id: string,
  userId: number,
  submittedAnswers?: Record<string, unknown>,
): Promise<void> {
  await withTx(async (db) => {
    const found = await db.query<TestSession>(
      "SELECT * FROM test_sessions WHERE id = $1 AND user_id = $2 FOR UPDATE",
      [id, userId],
    );
    const s = found.rows[0];
    if (!s || s.submitted_at) return;

    // Within the deadline (+grace) trust what the browser sent last; afterwards use what was autosaved.
    const answers =
      submittedAnswers && !isPastGrace(s)
        ? sanitizeAnswers(s.questions, submittedAnswers)
        : sanitizeAnswers(s.questions, s.answers);

    const qids = s.questions.map((q) => q.id);
    const correctRows = await db.query<{ question_id: number; label: string }>(
      "SELECT question_id, label FROM mcq_options WHERE question_id = ANY($1) AND is_correct = 1",
      [qids],
    );
    const correct = new Map<number, Set<string>>();
    for (const r of correctRows.rows) {
      const set = correct.get(r.question_id) ?? new Set<string>();
      set.add(r.label.trim());
      correct.set(r.question_id, set);
    }

    const picked = qids.map((qid) => answers[String(qid)] ?? null);
    const flags = qids.map((qid, i) => (picked[i] && correct.get(qid)?.has(picked[i]!) ? 1 : 0));
    const score = flags.reduce<number>((a, b) => a + b, 0);
    const total = qids.length;

    let attemptId: number;
    if (s.kind === "admin") {
      const a = await db.query<{ attempt_id: number }>(
        `INSERT INTO admin_test_attempts (admin_test_id, user_id, score, total_questions, percentage, attempted_at)
         VALUES ($1, $2, $3, $4, $5, NOW()) RETURNING attempt_id`,
        [s.admin_test_id, userId, score, total, total ? Math.round((score * 10000) / total) / 100 : 0],
      );
      attemptId = a.rows[0].attempt_id;
      await db.query(
        `INSERT INTO admin_test_responses (attempt_id, question_id, selected_answer, is_correct)
         SELECT $1, * FROM unnest($2::int[], $3::text[], $4::int[])`,
        [attemptId, qids, picked, flags],
      );
    } else {
      // Streamlit creates the students row lazily; do the same so its history pages keep working.
      await db.query(
        `INSERT INTO students (user_id, name, class)
         SELECT id, username, '9' FROM users WHERE id = $1
         ON CONFLICT (user_id) DO NOTHING`,
        [userId],
      );
      const a = await db.query<{ id: number }>(
        `INSERT INTO test_attempts (student_id, total_questions, score, started_at)
         VALUES ($1, $2, $3, NOW()) RETURNING id`,
        [userId, total, score],
      );
      attemptId = a.rows[0].id;
      await db.query(
        `INSERT INTO responses (attempt_id, question_id, selected_label, is_correct)
         SELECT $1, * FROM unnest($2::int[], $3::text[], $4::int[])`,
        [attemptId, qids, picked, flags],
      );
    }

    await db.query(
      `UPDATE test_sessions
          SET answers = $1::jsonb, submitted_at = NOW(), attempt_id = $2, score = $3, total = $4
        WHERE id = $5`,
      [JSON.stringify(answers), attemptId, score, total, id],
    );
  });
}
