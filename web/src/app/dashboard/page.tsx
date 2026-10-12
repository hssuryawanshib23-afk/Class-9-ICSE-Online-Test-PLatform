import { redirect } from "next/navigation";
import { AppHeader } from "@/components/AppHeader";
import { getSession } from "@/lib/session";
import { getStudentStats, getSubjectSummaries, type StudentStats, type SubjectSummary } from "@/lib/stats";

// Reads the session on every request, so it cannot be prerendered.
export const instant = false;

const SUBJECT_STYLE: Record<string, { icon: string; grad: string }> = {
  Physics: { icon: "⚛", grad: "from-[#4338ca] to-[#7c3aed]" },
  Chemistry: { icon: "⚗", grad: "from-[#0e7490] to-[#16a34a]" },
};

const dateFmt = new Intl.DateTimeFormat("en-IN", {
  day: "numeric", month: "short", hour: "numeric", minute: "2-digit", timeZone: "Asia/Kolkata",
});

function pct(n: number | null) {
  return n === null ? "—" : `${Math.round(n)}%`;
}

function scoreColor(p: number) {
  return p >= 75 ? "bg-good" : p >= 40 ? "bg-accent" : "bg-bad";
}

export default async function DashboardPage() {
  const user = await getSession();
  if (!user) redirect("/login");

  let stats: StudentStats | null = null;
  let subjects: SubjectSummary[] = [];
  try {
    [stats, subjects] = await Promise.all([getStudentStats(user.id), getSubjectSummaries()]);
  } catch (err) {
    console.error("dashboard stats failed", err);
  }

  return (
    <>
      <AppHeader username={user.username} />
      <main className="mx-auto w-full max-w-5xl px-6 py-10">
        <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#2a1a8f] via-brand to-brand-2 p-8 text-white shadow-xl shadow-brand/20 sm:p-10">
          <div className="drift absolute -top-16 -right-10 h-64 w-64 rounded-full bg-accent/30 blur-3xl" />
          <p className="relative text-sm font-medium text-white/80">Welcome back</p>
          <h1 className="relative mt-1 text-3xl font-bold tracking-tight sm:text-4xl">Hi, {user.username} 👋</h1>
          <p className="relative mt-2 max-w-lg text-white/80">
            {stats && stats.taken > 0
              ? `You have completed ${stats.taken} test${stats.taken === 1 ? "" : "s"}. Keep the streak going.`
              : "Your first practice test is the best way to find out where you stand."}
          </p>
        </section>

        {!stats && (
          <p role="status" className="mt-6 rounded-xl border border-accent/40 bg-accent/10 px-4 py-3 text-sm">
            Some of your stats are unavailable right now. Please refresh in a moment.
          </p>
        )}

        <section className="mt-8 grid gap-4 sm:grid-cols-3">
          {[
            { label: "Tests taken", value: stats ? String(stats.taken) : "—" },
            { label: "Average score", value: pct(stats?.average ?? null) },
            { label: "Best score", value: pct(stats?.best ?? null) },
          ].map((s) => (
            <div key={s.label} className="rounded-2xl border border-border bg-card p-5">
              <p className="text-sm text-muted">{s.label}</p>
              <p className="mt-1 text-3xl font-bold tracking-tight">{s.value}</p>
            </div>
          ))}
        </section>

        <h2 className="mt-12 text-xl font-bold tracking-tight">Subjects</h2>
        <section className="mt-4 grid gap-4 sm:grid-cols-2">
          {subjects.length === 0 && <p className="text-muted">No subjects available yet.</p>}
          {subjects.map((s) => {
            const style = SUBJECT_STYLE[s.subject] ?? SUBJECT_STYLE.Physics;
            return (
              <article key={s.subject} className={`rounded-2xl bg-gradient-to-br ${style.grad} p-6 text-white shadow-lg`}>
                <div className="flex items-start justify-between gap-3">
                  <span className="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-white/20 text-2xl">{style.icon}</span>
                  <span className="rounded-full bg-white/20 px-3 py-1 text-right text-xs font-medium">Practice opening soon</span>
                </div>
                <h3 className="mt-5 text-2xl font-bold">{s.subject}</h3>
                <p className="mt-1 text-white/80">
                  {s.chapters} chapters · {s.questions.toLocaleString("en-IN")} questions
                </p>
              </article>
            );
          })}
        </section>

        <h2 className="mt-12 text-xl font-bold tracking-tight">Recent tests</h2>
        <section className="mt-4">
          {!stats || stats.recent.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-border bg-card p-10 text-center">
              <p className="text-4xl">📝</p>
              <p className="mt-3 font-semibold">No tests yet</p>
              <p className="mt-1 text-sm text-muted">Your results will appear here after your first test.</p>
            </div>
          ) : (
            <ul className="divide-y divide-border overflow-hidden rounded-2xl border border-border bg-card">
              {stats.recent.map((r) => {
                const p = r.total ? (r.score / r.total) * 100 : 0;
                return (
                  <li key={r.id} className="flex items-center gap-4 px-5 py-4">
                    <div className="min-w-0 flex-1">
                      <p className="text-sm text-muted">{dateFmt.format(r.at)}</p>
                      <div className="mt-2 h-2 overflow-hidden rounded-full bg-border">
                        <div className={`h-full rounded-full ${scoreColor(p)}`} style={{ width: `${p}%` }} />
                      </div>
                    </div>
                    <p className="w-28 shrink-0 text-right font-semibold tabular-nums">
                      {r.score}/{r.total}
                      <span className="ml-2 text-sm font-normal text-muted">{Math.round(p)}%</span>
                    </p>
                  </li>
                );
              })}
            </ul>
          )}
        </section>
      </main>
    </>
  );
}
