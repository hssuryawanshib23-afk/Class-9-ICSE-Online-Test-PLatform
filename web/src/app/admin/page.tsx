import Link from "next/link";
import { AppHeader } from "@/components/AppHeader";
import { Bar, Stat } from "@/components/Bars";
import {
  getChapterPerformance,
  getConceptPerformance,
  getDifficultyPerformance,
  getOverview,
  getStudentPerformance,
} from "@/lib/adminStats";
import { requireAdmin } from "@/lib/guards";

// Reads the session on every request, so it cannot be prerendered.
export const instant = false;

const dateFmt = new Intl.DateTimeFormat("en-IN", { day: "numeric", month: "short", timeZone: "Asia/Kolkata" });
const status = (p: number) => (p >= 80 ? "🔥" : p >= 60 ? "✅" : p >= 40 ? "⚠️" : "🚨");

export default async function AdminOverview() {
  const admin = await requireAdmin();
  const [o, students, chapters, difficulty, concepts] = await Promise.all([
    getOverview(),
    getStudentPerformance(),
    getChapterPerformance(),
    getDifficultyPerformance(),
    getConceptPerformance(),
  ]);

  const weakChapters = chapters.filter((c) => c.accuracy < 50);
  const topChapters = [...chapters].filter((c) => c.accuracy >= 70).sort((a, b) => b.accuracy - a.accuracy).slice(0, 3);
  const weakConcepts = concepts.slice(0, 5);
  const strongConcepts = [...concepts].sort((a, b) => b.accuracy - a.accuracy).slice(0, 5);

  return (
    <>
      <AppHeader username={admin.username} role={admin.role} />
      <main className="mx-auto w-full max-w-5xl px-6 py-10">
        <p className="text-sm font-medium text-brand">Admin</p>
        <h1 className="mt-1 text-3xl font-bold tracking-tight">Overview</h1>

        <section className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Stat label="Students" value={String(o.students)} />
          <Stat label="Tests taken" value={String(o.tests)} hint="Practice + teacher tests" />
          <Stat label="Average accuracy" value={o.accuracy === null ? "—" : `${Math.round(o.accuracy * 10) / 10}%`} />
          <Stat label="Questions answered" value={o.answered.toLocaleString("en-IN")} />
        </section>

        <h2 className="mt-12 text-xl font-bold tracking-tight">Student performance</h2>
        {students.length === 0 ? (
          <p className="mt-3 text-muted">No test data yet.</p>
        ) : (
          <div className="mt-4 overflow-x-auto rounded-2xl border border-border bg-card">
            <table className="w-full min-w-[560px] text-left text-sm">
              <thead className="border-b border-border text-muted">
                <tr>
                  {["", "Student", "Tests", "Avg", "Best", "Worst", "Last test"].map((h) => (
                    <th key={h} className="px-4 py-3 font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {students.map((s) => (
                  <tr key={s.id} className="hover:bg-background">
                    <td className="px-4 py-3">{status(s.avg)}</td>
                    <td className="px-4 py-3 font-medium"><Link href={`/admin/students/${s.id}`} className="text-brand hover:underline">{s.username}</Link></td>
                    <td className="px-4 py-3 tabular-nums">{s.tests}</td>
                    <td className="px-4 py-3 tabular-nums">{s.avg.toFixed(1)}%</td>
                    <td className="px-4 py-3 tabular-nums">{s.best.toFixed(1)}%</td>
                    <td className="px-4 py-3 tabular-nums">{s.worst.toFixed(1)}%</td>
                    <td className="px-4 py-3 text-muted">{s.last ? dateFmt.format(s.last) : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <h2 className="mt-12 text-xl font-bold tracking-tight">Chapter-wise accuracy</h2>
        {chapters.length === 0 ? (
          <p className="mt-3 text-muted">No answers recorded yet.</p>
        ) : (
          <ul className="mt-4 space-y-3 rounded-2xl border border-border bg-card p-5">
            {chapters.map((c) => (
              <li key={`${c.subject}-${c.chapter}`} className="grid grid-cols-[9rem_1fr_7rem] items-center gap-4 text-sm">
                <span className="truncate font-medium">{c.subject} · Ch {c.chapter}</span>
                <Bar value={c.accuracy} label={`${c.subject} chapter ${c.chapter}`} />
                <span className="text-right tabular-nums text-muted">{c.accuracy}% · {c.correct}/{c.answered}</span>
              </li>
            ))}
          </ul>
        )}

        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          <section className="rounded-2xl border border-bad/30 bg-bad/5 p-5">
            <h3 className="font-semibold text-bad">Weak chapters (below 50%)</h3>
            {weakChapters.length === 0 ? (
              <p className="mt-2 text-sm text-muted">None. 🎉</p>
            ) : (
              <ul className="mt-2 space-y-1 text-sm">
                {weakChapters.map((c) => <li key={`${c.subject}-${c.chapter}`}><strong>{c.subject} Ch {c.chapter}</strong>: {c.accuracy}% ({c.correct}/{c.answered})</li>)}
              </ul>
            )}
          </section>
          <section className="rounded-2xl border border-good/30 bg-good/5 p-5">
            <h3 className="font-semibold text-good">Top chapters</h3>
            {topChapters.length === 0 ? (
              <p className="mt-2 text-sm text-muted">No chapter above 70% yet.</p>
            ) : (
              <ul className="mt-2 space-y-1 text-sm">
                {topChapters.map((c) => <li key={`${c.subject}-${c.chapter}`}><strong>{c.subject} Ch {c.chapter}</strong>: {c.accuracy}% ({c.correct}/{c.answered})</li>)}
              </ul>
            )}
          </section>
        </div>

        <h2 className="mt-12 text-xl font-bold tracking-tight">Difficulty</h2>
        <div className="mt-4 grid gap-4 sm:grid-cols-3">
          {difficulty.map((d) => (
            <div key={d.difficulty} className="rounded-2xl border border-border bg-card p-5">
              <p className="text-sm font-medium">{d.difficulty === "easy" ? "🟢 Easy" : d.difficulty === "hard" ? "🔴 Hard" : "🟡 Medium"}</p>
              <p className="mt-1 text-3xl font-bold tabular-nums">{d.accuracy}%</p>
              <p className="mb-2 text-xs text-muted">{d.correct}/{d.answered} correct</p>
              <Bar value={d.accuracy} label={d.difficulty} />
            </div>
          ))}
        </div>

        <h2 className="mt-12 text-xl font-bold tracking-tight">Concepts</h2>
        <p className="mt-1 text-sm text-muted">Based on concepts with at least 5 answers. Click one to see which students struggle with it.</p>
        {concepts.length === 0 ? (
          <p className="mt-3 text-muted">Not enough answers yet.</p>
        ) : (
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            {[
              { title: "Needs attention", list: weakConcepts, cls: "border-bad/30 bg-bad/5", head: "text-bad" },
              { title: "Strongest", list: strongConcepts, cls: "border-good/30 bg-good/5", head: "text-good" },
            ].map((g) => (
              <section key={g.title} className={`rounded-2xl border p-5 ${g.cls}`}>
                <h3 className={`font-semibold ${g.head}`}>{g.title}</h3>
                <ul className="mt-2 space-y-2 text-sm">
                  {g.list.map((c) => (
                    <li key={c.id}>
                      <Link href={`/admin/concepts/${c.id}`} className="font-medium hover:underline">{c.name}</Link>
                      <span className="block text-muted">{c.subject} Ch {c.chapter} · {c.accuracy}% ({c.correct}/{c.answered})</span>
                    </li>
                  ))}
                </ul>
              </section>
            ))}
          </div>
        )}
      </main>
    </>
  );
}
