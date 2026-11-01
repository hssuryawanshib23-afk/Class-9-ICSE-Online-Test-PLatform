import { query } from "@/lib/db";

// TEMPORARY diagnostic for the first deploy: tells you WHICH part is misconfigured (env vars, database
// connection, missing tables) without exposing any secret. Delete this file once the site works.

const TABLES = ["users", "questions", "admin_tests", "login_attempts", "test_sessions"];

/** Keep the useful part of an error but never a host name, URL or credential. */
function safe(message: string) {
  return message
    .replace(/\b[a-z0-9.-]+\.(neon\.tech|aws\.neon\.tech|amazonaws\.com)\b/gi, "<host>")
    .replace(/\b[a-z]+:\/\/\S+/gi, "<url>")
    .slice(0, 200);
}

export async function GET() {
  const url = process.env.DATABASE_URL ?? "";
  const out: Record<string, unknown> = {
    env: {
      DATABASE_URL_set: url.length > 0,
      DATABASE_URL_looks_like_postgres: /^postgres(ql)?:\/\//.test(url),
      DATABASE_URL_has_channel_binding: /channel_binding/i.test(url),
      SESSION_SECRET_ok: (process.env.SESSION_SECRET?.length ?? 0) >= 32,
    },
  };

  try {
    await query("SELECT 1");
    out.database = "connected";
    const rows = await query<{ table_name: string }>(
      "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = ANY($1)",
      [TABLES],
    );
    const have = new Set(rows.map((r) => r.table_name));
    out.tables = Object.fromEntries(TABLES.map((t) => [t, have.has(t)]));
    out.missing_tables = TABLES.filter((t) => !have.has(t));
  } catch (err) {
    const e = err as { code?: string; message?: string };
    out.database = "FAILED";
    out.error = { code: e.code ?? null, message: safe(e.message ?? String(err)) };
  }

  return Response.json(out, { headers: { "Cache-Control": "no-store" } });
}
