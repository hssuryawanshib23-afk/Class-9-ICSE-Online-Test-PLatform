"use server";

import { redirect } from "next/navigation";
import * as z from "zod";
import { query } from "@/lib/db";
import { requireStudent } from "@/lib/guards";
import { getSession } from "@/lib/session";
import { deadlineMs, finalizeSession, loadSession, saveAnswers } from "@/lib/sessions";
import { generateFromConcepts, withOptionOrder } from "@/lib/testEngine";

export type StartState = { message?: string; values?: Record<string, string> } | undefined;

const CustomSchema = z
  .object({
    concepts: z.array(z.coerce.number().int().positive()).min(1, "Pick at least one concept").max(1000),
    total: z.coerce.number().int().min(1).max(200),
    duration: z.coerce.number().int().min(5).max(180),
    easy: z.coerce.number().int().min(0).max(60),
    medium: z.coerce.number().int().min(0).max(60),
    hard: z.coerce.number().int().min(34).max(100),
  })
  .refine((d) => d.easy + d.medium + d.hard === 100, { message: "Difficulty must add up to 100%" });

export async function startCustomTest(_prev: StartState, formData: FormData): Promise<StartState> {
  const user = await requireStudent();

  const parsed = CustomSchema.safeParse({
    concepts: formData.getAll("concept"),
    total: formData.get("total"),
    duration: formData.get("duration"),
    easy: formData.get("easy"),
    medium: formData.get("medium"),
    hard: formData.get("hard"),
  });
  if (!parsed.success) {
    return { message: parsed.error.issues[0]?.message ?? "Please check your selections." };
  }
  const d = parsed.data;

  const questions = await generateFromConcepts([...new Set(d.concepts)], d.total, d.easy, d.medium);
  if (!questions) {
    return { message: "Not enough questions for that difficulty mix. Try fewer questions or select more concepts." };
  }

  const rows = await query<{ id: string }>(
    `INSERT INTO test_sessions (user_id, kind, questions, duration_seconds)
     VALUES ($1, 'custom', $2::jsonb, $3) RETURNING id`,
    [user.id, JSON.stringify(questions), d.duration * 60],
  );
  redirect(`/test/${rows[0].id}`);
}

export async function startAdminTest(formData: FormData) {
  const user = await requireStudent();
  const adminTestId = Number(formData.get("admin_test_id"));
  if (!Number.isInteger(adminTestId)) redirect("/tests");

  const [t] = await query<{ duration_minutes: number; allow_retake: boolean | null }>(
    "SELECT duration_minutes, allow_retake FROM admin_tests WHERE admin_test_id = $1 AND is_active = true",
    [adminTestId],
  );
  if (!t) redirect("/tests");

  // Resume a test already in progress instead of starting a fresh clock.
  const open = await query<{ id: string; started_at: Date; duration_seconds: number }>(
    `SELECT id, started_at, duration_seconds FROM test_sessions
      WHERE user_id = $1 AND kind = 'admin' AND admin_test_id = $2 AND submitted_at IS NULL
      ORDER BY started_at DESC LIMIT 1`,
    [user.id, adminTestId],
  );
  if (open[0] && Date.now() < deadlineMs(open[0])) redirect(`/test/${open[0].id}`);

  if (!t.allow_retake) {
    const [done] = await query<{ n: number }>(
      "SELECT COUNT(*)::int AS n FROM admin_test_attempts WHERE admin_test_id = $1 AND user_id = $2",
      [adminTestId, user.id],
    );
    if (done.n > 0) redirect("/tests");
  }

  const ordered = await query<{ question_id: number }>(
    "SELECT question_id FROM admin_test_questions WHERE admin_test_id = $1 ORDER BY question_order",
    [adminTestId],
  );
  const questions = await withOptionOrder(ordered.map((r) => r.question_id));
  if (questions.length === 0) redirect("/tests");

  const rows = await query<{ id: string }>(
    `INSERT INTO test_sessions (user_id, kind, admin_test_id, questions, duration_seconds)
     VALUES ($1, 'admin', $2, $3::jsonb, $4) RETURNING id`,
    [user.id, adminTestId, JSON.stringify(questions), t.duration_minutes * 60],
  );
  redirect(`/test/${rows[0].id}`);
}

export async function autosaveAnswers(sessionId: string, answers: Record<string, string>) {
  const user = await getSession();
  if (!user) return { ok: false as const };
  return { ok: await saveAnswers(sessionId, user.id, answers) };
}

export async function submitTest(sessionId: string, answers: Record<string, string>) {
  const user = await requireStudent();
  const s = await loadSession(sessionId, user.id);
  if (!s) redirect("/dashboard");
  await finalizeSession(sessionId, user.id, answers);
  redirect(`/result/${sessionId}`);
}
