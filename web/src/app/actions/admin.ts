"use server";

import { randomInt } from "node:crypto";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import bcrypt from "bcryptjs";
import * as z from "zod";
import type { FormState } from "@/app/actions/auth";
import { query, withTx } from "@/lib/db";
import { requireAdmin } from "@/lib/guards";
import { clearFailures } from "@/lib/throttle";
import { generateFromConcepts } from "@/lib/testEngine";

const CreateSchema = z
  .object({
    name: z.string().trim().min(1, "Give the test a name").max(255),
    concepts: z.array(z.coerce.number().int().positive()).min(1, "Pick at least one concept").max(2000),
    total: z.coerce.number().int().min(5, "At least 5 questions").max(100, "At most 100 questions"),
    duration: z.coerce.number().int().min(5).max(180),
    easy: z.coerce.number().int().min(0).max(100),
    medium: z.coerce.number().int().min(0).max(100),
    hard: z.coerce.number().int().min(0).max(100),
  })
  .refine((d) => d.easy + d.medium + d.hard === 100, { message: "Difficulty must add up to 100%" });

export async function createAdminTest(_prev: FormState, formData: FormData): Promise<FormState> {
  const admin = await requireAdmin();
  const parsed = CreateSchema.safeParse({
    name: formData.get("name"),
    concepts: formData.getAll("concept"),
    total: formData.get("total"),
    duration: formData.get("duration"),
    easy: formData.get("easy"),
    medium: formData.get("medium"),
    hard: formData.get("hard"),
  });
  if (!parsed.success) return { message: parsed.error.issues[0]?.message ?? "Please check the form." };
  const d = parsed.data;
  const retake = formData.get("allow_retake") === "on";
  const conceptIds = [...new Set(d.concepts)];

  const questions = await generateFromConcepts(conceptIds, d.total, d.easy, d.medium);
  if (!questions) {
    return { message: "Not enough questions for that difficulty mix. Lower the count, change the mix or pick more concepts." };
  }

  const chapters = await query<{ n: number }>(
    `SELECT DISTINCT ch.chapter_number AS n FROM concepts c JOIN chapters ch ON ch.id = c.chapter_id
      WHERE c.id = ANY($1) ORDER BY 1`,
    [conceptIds],
  );

  await withTx(async (db) => {
    const t = await db.query<{ admin_test_id: number }>(
      `INSERT INTO admin_tests (test_name, created_by, total_questions, duration_minutes,
                                easy_percentage, medium_percentage, hard_percentage, chapters, is_active, allow_retake)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, true, $9) RETURNING admin_test_id`,
      [d.name, admin.id, d.total, d.duration, d.easy, d.medium, d.hard, chapters.map((c) => c.n).join(","), retake],
    );
    await db.query(
      `INSERT INTO admin_test_questions (admin_test_id, question_id, question_order)
       SELECT $1, * FROM unnest($2::int[], $3::int[])`,
      [t.rows[0].admin_test_id, questions.map((q) => q.id), questions.map((_, i) => i + 1)],
    );
  });

  revalidatePath("/admin/tests");
  redirect("/admin/tests");
}

export async function setTestActive(formData: FormData) {
  await requireAdmin();
  const id = Number(formData.get("admin_test_id"));
  if (!Number.isInteger(id)) return;
  await query("UPDATE admin_tests SET is_active = $1 WHERE admin_test_id = $2", [formData.get("active") === "true", id]);
  revalidatePath("/admin/tests");
}

/** Deleting a test also deletes every student's attempt at it (database cascade), so the name must be typed. */
export async function deleteAdminTest(_prev: FormState, formData: FormData): Promise<FormState> {
  await requireAdmin();
  const id = Number(formData.get("admin_test_id"));
  if (!Number.isInteger(id)) return { message: "Invalid test." };
  const [t] = await query<{ test_name: string }>("SELECT test_name FROM admin_tests WHERE admin_test_id = $1", [id]);
  if (!t) return { message: "That test no longer exists." };
  if (String(formData.get("confirm") ?? "").trim() !== t.test_name) {
    return { message: "Type the test name exactly to confirm." };
  }
  await withTx(async (db) => {
    await db.query("DELETE FROM test_sessions WHERE kind = 'admin' AND admin_test_id = $1", [id]);
    await db.query("DELETE FROM admin_tests WHERE admin_test_id = $1", [id]);
  });
  revalidatePath("/admin/tests");
  redirect("/admin/tests");
}

export async function deleteStudent(_prev: FormState, formData: FormData): Promise<FormState> {
  const admin = await requireAdmin();
  const id = Number(formData.get("student_id"));
  if (!Number.isInteger(id)) return { message: "Invalid student." };
  const [u] = await query<{ username: string; role: string }>("SELECT username, role FROM users WHERE id = $1", [id]);
  // Never delete an admin (their tests would cascade-delete everyone's results) or yourself.
  if (!u || u.role === "admin" || id === admin.id) return { message: "This account cannot be deleted here." };
  if (String(formData.get("confirm") ?? "").trim() !== u.username) {
    return { message: "Type the username exactly to confirm." };
  }
  await withTx(async (db) => {
    await db.query("DELETE FROM test_sessions WHERE user_id = $1", [id]);
    await db.query("DELETE FROM users WHERE id = $1 AND role <> 'admin'", [id]); // attempts/responses cascade
  });
  revalidatePath("/admin/students");
  redirect("/admin/students");
}

// No 0/O/1/l/I so a password read out over the phone is unambiguous.
const ALPHABET = "abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789";

function tempPassword() {
  for (;;) {
    const p = Array.from({ length: 10 }, () => ALPHABET[randomInt(ALPHABET.length)]).join("");
    if (/[a-z]/.test(p) && /[A-Z]/.test(p) && /\d/.test(p)) return p;
  }
}

/** For students who lost their recovery code. The temporary password is shown once, here, and never stored. */
export async function resetStudentPassword(_prev: FormState, formData: FormData): Promise<FormState> {
  await requireAdmin();
  const id = Number(formData.get("student_id"));
  if (!Number.isInteger(id)) return { message: "Invalid student." };
  const [u] = await query<{ username: string; role: string }>("SELECT username, role FROM users WHERE id = $1", [id]);
  if (!u || u.role === "admin") return { message: "This account cannot be reset here." };

  const pw = tempPassword();
  await query("UPDATE users SET password_hash = $1 WHERE id = $2", [await bcrypt.hash(pw, 12), id]);
  await clearFailures([`u:${u.username.toLowerCase()}`, `pw:${id}`]);
  return { tempPassword: pw, message: `Password for ${u.username} was reset. Share this temporary password and ask them to change it from their profile.` };
}
