"use server";

import { randomInt, timingSafeEqual } from "node:crypto";
import { headers } from "next/headers";
import { revalidatePath } from "next/cache";
import bcrypt from "bcryptjs";
import * as z from "zod";
import { query } from "@/lib/db";
import { BOARDS, requireUser } from "@/lib/guards";
import { clearFailures, isLocked, recordFailure } from "@/lib/throttle";
import { passwordRule } from "@/lib/validation";
import type { FormState } from "@/app/actions/auth";

// Same trick as login: a real hash so a missing user takes as long as a wrong code.
const DUMMY_HASH = "$2b$12$ugo/qh.VPgwHCVCbcK6pBOvdypcGl5Pqn8b2cCpRE6lHSJMPkUwbC";

function newRecoveryCode() {
  // users.recovery_code is varchar(8) in production: 8 digits from a CSPRNG.
  return String(randomInt(0, 100_000_000)).padStart(8, "0");
}

function same(a: string, b: string) {
  const x = Buffer.from(a);
  const y = Buffer.from(b);
  return x.length === y.length && timingSafeEqual(x, y);
}

async function clientIp() {
  const h = await headers();
  return (h.get("x-forwarded-for")?.split(",")[0] ?? h.get("x-real-ip") ?? "unknown").trim();
}

const ProfileSchema = z.object({
  school_name: z.string().trim().min(1, "Enter your school").max(255),
  class_name: z.string().trim().min(1, "Enter your class").max(50),
  board_name: z.enum(BOARDS, { error: "Choose a board" }),
});

export async function updateProfile(_prev: FormState, formData: FormData): Promise<FormState> {
  const user = await requireUser();
  const parsed = ProfileSchema.safeParse({
    school_name: formData.get("school_name"),
    class_name: formData.get("class_name"),
    board_name: formData.get("board_name"),
  });
  if (!parsed.success) return { errors: z.flattenError(parsed.error).fieldErrors };
  const d = parsed.data;
  await query("UPDATE users SET school_name = $1, class_name = $2, board_name = $3 WHERE id = $4", [
    d.school_name,
    d.class_name,
    d.board_name,
    user.id,
  ]);
  revalidatePath("/", "layout");
  return { message: "Profile saved." };
}

const ChangeSchema = z
  .object({
    current: z.string().min(1, "Enter your current password").max(200),
    next: passwordRule,
    confirm: z.string(),
  })
  .refine((d) => d.next === d.confirm, { path: ["confirm"], message: "Passwords do not match" });

async function checkCurrentPassword(userId: number, password: string) {
  const keys = [`pw:${userId}`];
  if (await isLocked(keys)) return "locked" as const;
  const [row] = await query<{ password_hash: string }>("SELECT password_hash FROM users WHERE id = $1", [userId]);
  if (!row || !(await bcrypt.compare(password, row.password_hash))) {
    await recordFailure(keys);
    return "wrong" as const;
  }
  await clearFailures(keys);
  return "ok" as const;
}

export async function changePassword(_prev: FormState, formData: FormData): Promise<FormState> {
  const user = await requireUser();
  const parsed = ChangeSchema.safeParse({
    current: formData.get("current"),
    next: formData.get("next"),
    confirm: formData.get("confirm"),
  });
  if (!parsed.success) return { errors: z.flattenError(parsed.error).fieldErrors };

  const check = await checkCurrentPassword(user.id, parsed.data.current);
  if (check === "locked") return { message: "Too many attempts. Please wait 15 minutes." };
  if (check === "wrong") return { errors: { current: ["Current password is incorrect"] } };

  await query("UPDATE users SET password_hash = $1 WHERE id = $2", [await bcrypt.hash(parsed.data.next, 12), user.id]);
  return { message: "Password changed." };
}

export async function regenerateRecoveryCode(_prev: FormState, formData: FormData): Promise<FormState> {
  const user = await requireUser();
  const check = await checkCurrentPassword(user.id, String(formData.get("current") ?? ""));
  if (check === "locked") return { message: "Too many attempts. Please wait 15 minutes." };
  if (check === "wrong") return { errors: { current: ["Password is incorrect"] } };

  const code = newRecoveryCode();
  await query("UPDATE users SET recovery_code = $1 WHERE id = $2", [code, user.id]);
  return { recoveryCode: code, message: "New recovery code created. The old one no longer works." };
}

const ResetSchema = z
  .object({
    username: z.string().trim().min(1, "Enter your username").max(255),
    code: z.string().trim().regex(/^\d{8}$/, "Recovery code is 8 digits"),
    next: passwordRule,
    confirm: z.string(),
  })
  .refine((d) => d.next === d.confirm, { path: ["confirm"], message: "Passwords do not match" });

/**
 * Reset with username + recovery code only. Phone number is deliberately NOT accepted: it is not a
 * secret (classmates know it), so it would let anyone take over an account.
 */
export async function resetPassword(_prev: FormState, formData: FormData): Promise<FormState> {
  const parsed = ResetSchema.safeParse({
    username: formData.get("username"),
    code: formData.get("code"),
    next: formData.get("next"),
    confirm: formData.get("confirm"),
  });
  const values = { username: String(formData.get("username") ?? "") };
  if (!parsed.success) return { errors: z.flattenError(parsed.error).fieldErrors, values };
  const { username, code, next } = parsed.data;

  const keys = [`reset:u:${username.toLowerCase()}`, `reset:ip:${await clientIp()}`];
  if (await isLocked(keys)) {
    return { message: "Too many attempts. Please wait 15 minutes, or ask your teacher to reset your password.", values };
  }

  const rows = await query<{ id: number; recovery_code: string | null; role: string }>(
    "SELECT id, recovery_code, role FROM users WHERE username = $1",
    [username],
  );
  // Several accounts can share a username in production (no unique constraint): accept whichever matches.
  const user = rows.find((r) => r.recovery_code && same(r.recovery_code, code));
  await bcrypt.compare(code, DUMMY_HASH); // keep timing similar whether or not the user exists

  // Admin accounts are never reset through this public form.
  if (!user || user.role === "admin") {
    await recordFailure(keys);
    return { message: "Username and recovery code do not match.", values };
  }

  const fresh = newRecoveryCode();
  await query("UPDATE users SET password_hash = $1, recovery_code = $2 WHERE id = $3", [
    await bcrypt.hash(next, 12),
    fresh,
    user.id,
  ]);
  await clearFailures(keys);
  return { recoveryCode: fresh, message: "Password reset. Here is your NEW recovery code." };
}
