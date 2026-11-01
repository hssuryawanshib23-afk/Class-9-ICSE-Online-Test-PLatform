import { startAdminTest } from "@/app/actions/tests";
import { AppHeader } from "@/components/AppHeader";
import { query } from "@/lib/db";
import { requireStudent } from "@/lib/guards";

// Reads the session on every request, so it cannot be prerendered.
export const instant = false;

type AdminTest = {
  admin_test_id: number;
  test_name: string;
  total_questions: number;
  duration_minutes: number;
  easy_percentage: number;
  medium_percentage: number;
  hard_percentage: number;
  allow_retake: boolean | null;
  creator: string | null;
  created_at: Date;
  attempts: number;
};

const dateFmt = new Intl.DateTimeFormat("en-IN", { day: "numeric", month: "short", year: "numeric", timeZone: "Asia/Kolkata" });

export default async function TestsPage() {
  const user = await requireStudent();

  const tests = await query<AdminTest>(
    `SELECT t.admin_test_id, t.test_name, t.total_questions, t.duration_minutes,
            t.easy_percentage, t.medium_percentage, t.hard_percentage, t.allow_retake,
            u.username AS creator, t.created_at,
            (SELECT COUNT(*)::int FROM admin_test_attempts a
              WHERE a.admin_test_id = t.admin_test_id AND a.user_id = $1) AS attempts
       FROM admin_tests t LEFT JOIN users u ON u.id = t.created_by
      WHERE t.is_active = true
      ORDER BY t.created_at DESC`,
    [user.id],
  );

  return (
    <>
      <AppHeader username={user.username} role={user.role} />
      <main className="mx-auto w-full max-w-5xl px-6 py-10">
        <p className="text-sm font-medium text-brand">Tests</p>
        <h1 className="mt-1 text-3xl font-bold tracking-tight">Tests from your teachers</h1>
        <p className="mt-2 text-muted">Ready-made tests. Your timer starts the moment you press Start.</p>

        {tests.length === 0 ? (
          <div className="mt-10 rounded-2xl border border-dashed border-border bg-card p-10 text-center">
            <p className="text-4xl">📋</p>
            <p className="mt-3 font-semibold">No tests right now</p>
            <p className="mt-1 text-sm text-muted">Check back later, or build your own on the Practice page.</p>
          </div>
        ) : (
          <ul className="mt-8 grid gap-4 sm:grid-cols-2">
            {tests.map((t) => {
              const done = t.attempts > 0;
              const locked = done && !t.allow_retake;
              return (
                <li key={t.admin_test_id} className="flex flex-col rounded-2xl border border-border bg-card p-6">
                  <div className="flex items-start justify-between gap-3">
                    <h2 className="text-lg font-bold">{t.test_name}</h2>
                    {done && (
                      <span className="shrink-0 rounded-full bg-good/10 px-2.5 py-0.5 text-xs font-medium text-good">
                        {locked ? "Completed" : `Taken ${t.attempts}×`}
                      </span>
                    )}
                  </div>
                  <p className="mt-2 text-sm text-muted">
                    {t.total_questions} questions · {t.duration_minutes} min
                  </p>
                  <p className="mt-1 text-sm text-muted">
                    🟢 {t.easy_percentage}% · 🟡 {t.medium_percentage}% · 🔴 {t.hard_percentage}%
                  </p>
                  <p className="mt-1 text-xs text-muted">
                    {t.creator ? `By ${t.creator} · ` : ""}
                    {dateFmt.format(t.created_at)}
                  </p>
                  <form action={startAdminTest} className="mt-5">
                    <input type="hidden" name="admin_test_id" value={t.admin_test_id} />
                    <button
                      disabled={locked}
                      className="w-full rounded-xl bg-brand px-4 py-3 font-semibold text-white transition hover:brightness-110 disabled:bg-border disabled:text-muted"
                    >
                      {locked ? "Already completed" : done ? "Retake" : "Start test"}
                    </button>
                  </form>
                </li>
              );
            })}
          </ul>
        )}
      </main>
    </>
  );
}
