import Link from "next/link";
import { setTestActive } from "@/app/actions/admin";
import { AppHeader } from "@/components/AppHeader";
import { query } from "@/lib/db";
import { requireAdmin } from "@/lib/guards";

// Reads the session on every request, so it cannot be prerendered.
export const instant = false;

type T = {
  admin_test_id: number;
  test_name: string;
  total_questions: number;
  duration_minutes: number;
  easy_percentage: number;
  medium_percentage: number;
  hard_percentage: number;
  is_active: boolean | null;
  allow_retake: boolean | null;
  creator: string | null;
  created_at: Date;
  attempts: number;
  avg: number | null;
};

const dateFmt = new Intl.DateTimeFormat("en-IN", { day: "numeric", month: "short", year: "numeric", timeZone: "Asia/Kolkata" });

export default async function AdminTests() {
  const admin = await requireAdmin();
  const tests = await query<T>(
    `SELECT t.admin_test_id, t.test_name, t.total_questions, t.duration_minutes,
            t.easy_percentage, t.medium_percentage, t.hard_percentage, t.is_active, t.allow_retake,
            u.username AS creator, t.created_at,
            COUNT(a.attempt_id)::int AS attempts,
            AVG(a.score * 100.0 / NULLIF(a.total_questions, 0))::float8 AS avg
       FROM admin_tests t
       LEFT JOIN users u ON u.id = t.created_by
       LEFT JOIN admin_test_attempts a ON a.admin_test_id = t.admin_test_id
      GROUP BY t.admin_test_id, u.username
      ORDER BY t.created_at DESC`,
  );

  return (
    <>
      <AppHeader username={admin.username} role={admin.role} />
      <main className="mx-auto w-full max-w-5xl px-6 py-10">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-sm font-medium text-brand">Admin</p>
            <h1 className="mt-1 text-3xl font-bold tracking-tight">Tests</h1>
          </div>
          <Link href="/admin/tests/new" className="rounded-xl bg-brand px-5 py-3 font-semibold text-white shadow-lg shadow-brand/30 transition hover:brightness-110">
            + Create test
          </Link>
        </div>

        {tests.length === 0 ? (
          <div className="mt-10 rounded-2xl border border-dashed border-border bg-card p-10 text-center">
            <p className="text-4xl">🗂️</p>
            <p className="mt-3 font-semibold">No tests yet</p>
            <p className="mt-1 text-sm text-muted">Create your first test for students to take.</p>
          </div>
        ) : (
          <ul className="mt-8 space-y-4">
            {tests.map((t) => {
              const active = t.is_active !== false;
              return (
                <li key={t.admin_test_id} className="rounded-2xl border border-border bg-card p-6">
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div className="min-w-0">
                      <h2 className="text-lg font-bold">
                        {t.test_name}
                        <span className={`ml-3 rounded-full px-2.5 py-0.5 text-xs font-medium ${active ? "bg-good/10 text-good" : "bg-border text-muted"}`}>
                          {active ? "Active" : "Inactive"}
                        </span>
                      </h2>
                      <p className="mt-1 text-sm text-muted">
                        {t.total_questions} questions · {t.duration_minutes} min · 🟢 {t.easy_percentage}% 🟡 {t.medium_percentage}% 🔴 {t.hard_percentage}%
                        {t.allow_retake ? " · retakes allowed" : ""}
                      </p>
                      <p className="mt-1 text-sm text-muted">
                        {t.creator ? `By ${t.creator} · ` : ""}{dateFmt.format(t.created_at)} · {t.attempts} attempt{t.attempts === 1 ? "" : "s"}
                        {t.avg !== null ? ` · avg ${t.avg.toFixed(1)}%` : ""}
                      </p>
                    </div>
                    <div className="flex shrink-0 gap-2">
                      <Link href={`/admin/tests/${t.admin_test_id}`} className="rounded-xl bg-brand px-4 py-2.5 text-sm font-semibold text-white transition hover:brightness-110">Results</Link>
                      <form action={setTestActive}>
                        <input type="hidden" name="admin_test_id" value={t.admin_test_id} />
                        <input type="hidden" name="active" value={String(!active)} />
                        <button className="rounded-xl border border-border px-4 py-2.5 text-sm font-semibold transition hover:bg-background">
                          {active ? "Deactivate" : "Activate"}
                        </button>
                      </form>
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </main>
    </>
  );
}
