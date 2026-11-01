import Link from "next/link";
import { redirect } from "next/navigation";
import { AppHeader } from "@/components/AppHeader";
import { DeleteTestForm } from "@/components/AdminForms";
import { Stat } from "@/components/Bars";
import { query } from "@/lib/db";
import { requireAdmin } from "@/lib/guards";

// Reads the session on every request, so it cannot be prerendered.
export const instant = false;

const dateFmt = new Intl.DateTimeFormat("en-IN", { day: "numeric", month: "short", hour: "numeric", minute: "2-digit", timeZone: "Asia/Kolkata" });

type Row = { user_id: number; username: string; attempt_id: number | null; score: number | null; total: number | null; percentage: number | null; at: Date | null };
type Weak = { attempt_id: number; subject: string; chapter: number; answered: number; accuracy: number };

export default async function AdminTestResults({ params }: PageProps<"/admin/tests/[id]">) {
  const admin = await requireAdmin();
  const id = Number((await params).id);
  if (!Number.isInteger(id)) redirect("/admin/tests");

  const [t] = await query<{ test_name: string; total_questions: number; duration_minutes: number }>(
    "SELECT test_name, total_questions, duration_minutes FROM admin_tests WHERE admin_test_id = $1",
    [id],
  );
  if (!t) redirect("/admin/tests");

  // Latest attempt per student (retakes can create several).
  const rows = await query<Row>(
    `SELECT u.id AS user_id, u.username, a.attempt_id, a.score, a.total_questions AS total,
            a.percentage::float8 AS percentage, a.attempted_at AS at
       FROM users u
       LEFT JOIN LATERAL (
         SELECT * FROM admin_test_attempts WHERE admin_test_id = $1 AND user_id = u.id ORDER BY attempted_at DESC LIMIT 1
       ) a ON true
      WHERE u.role = 'student'
      ORDER BY a.attempted_at DESC NULLS LAST, u.username`,
    [id],
  );
  const attempted = rows.filter((r) => r.attempt_id !== null);
  const pending = rows.filter((r) => r.attempt_id === null);

  const weak = attempted.length
    ? await query<Weak>(
        `SELECT r.attempt_id, COALESCE(ch.subject, 'Physics') AS subject, ch.chapter_number AS chapter,
                COUNT(*)::int AS answered, ROUND(AVG(r.is_correct) * 100, 0)::float8 AS accuracy
           FROM admin_test_responses r
           JOIN questions q ON q.id = r.question_id
           JOIN concepts c ON c.id = q.concept_id
           JOIN chapters ch ON ch.id = c.chapter_id
          WHERE r.attempt_id = ANY($1)
          GROUP BY r.attempt_id, ch.subject, ch.chapter_number
         HAVING AVG(r.is_correct) * 100 < 60
          ORDER BY accuracy`,
        [attempted.map((r) => r.attempt_id)],
      )
    : [];
  const [{ n }] = await query<{ n: number }>("SELECT COUNT(*)::int AS n FROM admin_test_attempts WHERE admin_test_id = $1", [id]);

  return (
    <>
      <AppHeader username={admin.username} role={admin.role} />
      <main className="mx-auto w-full max-w-5xl px-6 py-10">
        <Link href="/admin/tests" className="text-sm font-medium text-brand">← All tests</Link>
        <h1 className="mt-3 text-3xl font-bold tracking-tight">{t.test_name}</h1>
        <p className="mt-2 text-muted">{t.total_questions} questions · {t.duration_minutes} min</p>

        <section className="mt-6 grid gap-4 sm:grid-cols-3">
          <Stat label="Students" value={String(rows.length)} />
          <Stat label="Attempted" value={String(attempted.length)} />
          <Stat label="Pending" value={String(pending.length)} />
        </section>

        <h2 className="mt-10 text-xl font-bold tracking-tight">Results</h2>
        {attempted.length === 0 ? (
          <p className="mt-3 text-muted">Nobody has taken this test yet.</p>
        ) : (
          <ul className="mt-4 space-y-3">
            {attempted.map((r) => {
              const p = r.percentage ?? 0;
              const w = weak.filter((x) => x.attempt_id === r.attempt_id);
              return (
                <li key={r.user_id} className="rounded-2xl border border-border bg-card p-5">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <Link href={`/admin/students/${r.user_id}`} className="font-semibold text-brand hover:underline">{r.username}</Link>
                      <p className="text-sm text-muted">{r.at ? dateFmt.format(r.at) : ""}</p>
                    </div>
                    <p className="text-xl font-bold tabular-nums">
                      {r.score}/{r.total} <span className="text-sm font-normal text-muted">{p.toFixed(1)}%</span>
                      <span className="ml-2">{p >= 80 ? "🌟" : p >= 60 ? "✅" : "⚠️"}</span>
                    </p>
                  </div>
                  {w.length > 0 && (
                    <p className="mt-2 text-sm text-bad">
                      Weak: {w.map((x) => `${x.subject} Ch ${x.chapter} (${x.accuracy}%)`).join(", ")}
                    </p>
                  )}
                  <Link href={`/admin/review/admin/${r.attempt_id}`} className="mt-3 inline-block text-sm font-medium text-brand hover:underline">View answers →</Link>
                </li>
              );
            })}
          </ul>
        )}

        {pending.length > 0 && (
          <section className="mt-8">
            <h2 className="text-xl font-bold tracking-tight">Not attempted</h2>
            <p className="mt-3 text-sm text-muted">{pending.map((r) => r.username).join(", ")}</p>
          </section>
        )}

        <div className="mt-12"><DeleteTestForm id={id} name={t.test_name} attempts={n} /></div>
      </main>
    </>
  );
}
