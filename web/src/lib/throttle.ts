import "server-only";
import { query } from "@/lib/db";

const WINDOW_MINUTES = 15;
const MAX_FAILURES = 5;

export async function isLocked(keys: string[]): Promise<boolean> {
  // Any single key (username or IP) at the limit locks the attempt.
  const rows = await query<{ n: string }>(
    `SELECT COUNT(*)::text AS n FROM login_attempts
      WHERE key = ANY($1) AND attempted_at > NOW() - make_interval(mins => $2)
      GROUP BY key ORDER BY COUNT(*) DESC LIMIT 1`,
    [keys, WINDOW_MINUTES],
  );
  return Number(rows[0]?.n ?? 0) >= MAX_FAILURES;
}

export async function recordFailure(keys: string[]) {
  for (const k of keys) {
    await query("INSERT INTO login_attempts (key) VALUES ($1)", [k]);
  }
}

export async function clearFailures(keys: string[]) {
  await query("DELETE FROM login_attempts WHERE key = ANY($1)", [keys]);
}
