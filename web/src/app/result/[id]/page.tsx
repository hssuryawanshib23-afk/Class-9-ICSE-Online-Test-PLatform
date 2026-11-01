import Link from "next/link";
import { redirect } from "next/navigation";
import { AppHeader } from "@/components/AppHeader";
import { tone } from "@/components/Bars";
import { ReviewList } from "@/components/ReviewList";
import { requireStudent } from "@/lib/guards";
import { breakdownOf, gradeFor, insightsOf, reviewForSession, verdictFor } from "@/lib/results";
import { loadSession } from "@/lib/sessions";

// Reads the session on every request, so it cannot be prerendered.
export const instant = false;

const DIFF_META = [
  { key: "easy", label: "🟢 Easy" },
  { key: "medium", label: "🟡 Medium" },
  { key: "hard", label: "🔴 Hard" },
] as const;

export default async function ResultPage({ params }: PageProps<"/result/[id]">) {
  const user = await requireStudent();

  const { id } = await params;
  const s = await loadSession(id, user.id);
  if (!s) redirect("/dashboard");
  if (!s.submitted_at) redirect(`/test/${s.id}`);

  const items = await reviewForSession(s);
  const total = s.total ?? items.length;
  const score = s.score ?? 0;
  const pct = total ? Math.round((score / total) * 100) : 0;
  const v = verdictFor(pct);
  const b = breakdownOf(items);
  const { strengths, focus } = insightsOf(b);
  const secs = Math.max(0, Math.round((s.submitted_at.getTime() - s.started_at.getTime()) / 1000));
  const wrong = items.filter((r) => !r.ok).length;

  return (
    <>
      <AppHeader username={user.username} role={user.role} />
      <main className="mx-auto w-full max-w-3xl px-6 py-10">
        <section className="rounded-3xl bg-gradient-to-br from-[#2a1a8f] via-brand to-brand-2 p-8 text-center text-white shadow-xl shadow-brand/20">
          <p className="text-5xl">{v.emoji}</p>
          <p className="mt-3 text-sm text-white/80">{v.text}</p>
          <p className="mt-2 text-6xl font-extrabold tracking-tight tabular-nums">
            {score}
            <span className="text-3xl font-semibold text-white/70">/{total}</span>
          </p>
          <p className="mt-1 text-xl font-semibold">{pct}%</p>
        </section>

        <section className="mt-4 grid grid-cols-3 gap-3">
          {[
            { k: "Grade", v: gradeFor(pct) },
            { k: "Time taken", v: `${Math.floor(secs / 60)}m ${secs % 60}s` },
            { k: "Accuracy", v: `${pct}%` },
          ].map((m) => (
            <div key={m.k} className="rounded-2xl border border-border bg-card p-4 text-center">
              <p className="text-xs text-muted">{m.k}</p>
              <p className="mt-1 text-2xl font-bold">{m.v}</p>
            </div>
          ))}
        </section>

        <div className="mt-6 flex flex-wrap gap-3">
          <Link href="/practice" className="rounded-xl bg-brand px-5 py-3 font-semibold text-white transition hover:brightness-110">
            Practice again
          </Link>
          <a href={`/result/${s.id}/pdf`} className="rounded-xl border border-border px-5 py-3 font-medium transition hover:bg-card">
            ⬇ Download PDF report
          </a>
          <Link href="/dashboard" className="rounded-xl border border-border px-5 py-3 font-medium transition hover:bg-card">
            Dashboard
          </Link>
        </div>

        <h2 className="mt-10 text-xl font-bold tracking-tight">Performance by difficulty</h2>
        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          {DIFF_META.map((d) => {
            const x = b[d.key];
            const p = x.total ? Math.round((x.correct / x.total) * 100) : 0;
            return (
              <div key={d.key} className="rounded-2xl border border-border bg-card p-4">
                <p className="text-sm font-medium">{d.label}</p>
                {x.total === 0 ? (
                  <p className="mt-2 text-sm text-muted">N/A</p>
                ) : (
                  <>
                    <p className="mt-1 text-2xl font-bold tabular-nums">
                      {x.correct}/{x.total} <span className="text-sm font-normal text-muted">{p}%</span>
                    </p>
                    <div className="mt-2 h-2 overflow-hidden rounded-full bg-border" role="img" aria-label={`${p}% correct`}>
                      <div className={`h-full rounded-full ${tone(p)}`} style={{ width: `${p}%` }} />
                    </div>
                  </>
                )}
              </div>
            );
          })}
        </div>

        {(strengths.length > 0 || focus.length > 0) && (
          <section className="mt-6 grid gap-3 sm:grid-cols-2">
            {strengths.length > 0 && (
              <div className="rounded-2xl border border-good/30 bg-good/5 p-5">
                <h3 className="font-semibold text-good">Strengths</h3>
                <ul className="mt-2 space-y-1 text-sm">{strengths.map((t) => <li key={t}>✓ {t}</li>)}</ul>
              </div>
            )}
            {focus.length > 0 && (
              <div className="rounded-2xl border border-bad/30 bg-bad/5 p-5">
                <h3 className="font-semibold text-bad">Focus on</h3>
                <ul className="mt-2 space-y-1 text-sm">{focus.map((t) => <li key={t}>⚠ {t}</li>)}</ul>
              </div>
            )}
          </section>
        )}

        <h2 className="mt-10 text-xl font-bold tracking-tight">
          Review <span className="text-sm font-normal text-muted">· {wrong} to learn from</span>
        </h2>
        <ReviewList items={items} />
      </main>
    </>
  );
}
