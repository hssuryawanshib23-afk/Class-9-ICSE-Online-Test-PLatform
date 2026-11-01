"use server";

import { randomInt } from "node:crypto";
import { headers } from "next/headers";
import { redirect } from "next/navigation";
import bcrypt from "bcryptjs";
import * as z from "zod";
import { BOARD_OPTIONS } from "@/lib/boards";
import { query } from "@/lib/db";
import { createSession, destroySession } from "@/lib/session";
import { clearFailures, isLocked, recordFailure } from "@/lib/throttle";
import { passwordRule } from "@/lib/validation";

export type FormState =
  | {
      errors?: Record<string, string[] | undefined>;
      message?: string;
      recoveryCode?: string;
      // Shown once to an admin after resetting a student's password.
      tempPassword?: string;
      // Echoed back so React 19's post-action form reset does not wipe what the user typed. Never the password.
      values?: Record<string, string>;
    }
  | undefined;

// A real bcrypt hash of a throwaway string, so a missing user costs the same time as a wrong password.
const DUMMY_HASH = "$2b$12$3/pCdBM0BKTvSRK5nhfILOzyju6ECl6/JAyPcKYEViwzaK257R/PS";

const SignupSchema = z.object({
  username: z
    .string()
    .trim()
    .min(3, "At least 3 characters")
    .max(30, "At most 30 characters")
    .regex(/^[A-Za-z0-9_.-]+$/, "Letters, numbers, . _ - only"),
  phone_number: z.string().trim().regex(/^[6-9]\d{9}$/, "Enter a 10-digit mobile number"),
  password: passwordRule,
  school_name: z.string().trim().min(1, "Enter your school").max(255),
  class_name: z.string().trim().min(1, "Enter your class").max(50),
  board_name: z.enum(BOARD_OPTIONS, { error: "Choose a board" }),
});

const LoginSchema = z.object({
  username: z.string().trim().min(1, "Enter your username").max(255),
  password: z.string().min(1, "Enter your password").max(200),
});

function echo(formData: FormData, names: string[]) {
  return Object.fromEntries(names.map((n) => [n, String(formData.get(n) ?? "")]));
}

async function clientIp() {
  const h = await headers();
  return (h.get("x-forwarded-for")?.split(",")[0] ?? h.get("x-real-ip") ?? "unknown").trim();
}

export async function signup(_prev: FormState, formData: FormData): Promise<FormState> {
  const parsed = SignupSchema.safeParse({
    username: formData.get("username"),
    phone_number: formData.get("phone_number"),
    password: formData.get("password"),
    school_name: formData.get("school_name"),
    class_name: formData.get("class_name"),
    board_name: formData.get("board_name"),
  });
  const values = echo(formData, ["username", "phone_number", "school_name", "class_name", "board_name"]);
  if (!parsed.success) return { errors: z.flattenError(parsed.error).fieldErrors, values };
  const d = parsed.data;

  const taken = await query(
    "SELECT 1 FROM users WHERE username = $1 OR phone_number = $2 LIMIT 1",
    [d.username, d.phone_number],
  );
  if (taken.length) {
    // Same message for either collision: do not reveal which one exists.
    return { message: "That username or phone number cannot be used. Try different details.", values };
  }

  const hash = await bcrypt.hash(d.password, 12);
  // users.recovery_code is varchar(8) in production, so keep 8 digits but draw them from a CSPRNG
  // (the Streamlit app used random.randint, which is not cryptographically secure).
  const recoveryCode = String(randomInt(0, 100_000_000)).padStart(8, "0");

  let rows: { id: number }[];
  try {
    rows = await query<{ id: number }>(
      `INSERT INTO users (username, phone_number, password_hash, role, school_name, class_name, board_name, recovery_code, created_at)
       VALUES ($1, $2, $3, 'student', $4, $5, $6, $7, CURRENT_TIMESTAMP) RETURNING id`,
      [d.username, d.phone_number, hash, d.school_name, d.class_name, d.board_name, recoveryCode],
    );
  } catch (err) {
    // Two signups with the same phone number racing past the check above.
    if ((err as { code?: string }).code === "23505") {
      return { message: "That username or phone number cannot be used. Try different details.", values };
    }
    throw err;
  }

  await createSession(rows[0].id);
  // Shown once on the dashboard; passed through the redirect would leak it into URLs/logs, so use a re-render.
  return { recoveryCode };
}

export async function login(_prev: FormState, formData: FormData): Promise<FormState> {
  const parsed = LoginSchema.safeParse({
    username: formData.get("username"),
    password: formData.get("password"),
  });
  const values = echo(formData, ["username"]);
  if (!parsed.success) return { errors: z.flattenError(parsed.error).fieldErrors, values };
  const { username, password } = parsed.data;

  const keys = [`u:${username.toLowerCase()}`, `ip:${await clientIp()}`];
  if (await isLocked(keys)) {
    return { message: "Too many attempts. Please wait 15 minutes and try again.", values };
  }

  const rows = await query<{ id: number; password_hash: string }>(
    "SELECT id, password_hash FROM users WHERE username = $1",
    [username],
  );
  const user = rows[0];
  const ok = await bcrypt.compare(password, user?.password_hash ?? DUMMY_HASH);

  if (!user || !ok) {
    await recordFailure(keys);
    return { message: "Incorrect username or password.", values };
  }

  await clearFailures([keys[0]]);
  await createSession(user.id);
  redirect("/dashboard");
}

export async function logout() {
  await destroySession();
  redirect("/login");
}
