import Link from "next/link";
import { redirect } from "next/navigation";
import { AppHeader } from "@/components/AppHeader";
import { query } from "@/lib/db";
import { getSession } from "@/lib/session";
import { loadSession } from "@/lib/sessions";

// Reads the session on every request, so it cannot be prerendered.
export const instant = false;

const LETTERS = ["A", "B", "C", "D", "E", "F"];

function verdict(p: number) {
  if (p >= 90) return { emoji: "🏆", text: "Outstanding!" };
  if (p >= 75) return { emoji: "🎉", text: "Great work!" };
  if (p >= 50) return { emoji: "👍", text: "Good effort, keep going." };
  return { emoji: "💪", text: "Review the answers below and try again." };
}

export default async function ResultPage({ params }: PageProps<"/result/[id]">) {
  const user = await getSession();
  if (!user) redirect("/login");

  const { id } = await params;
  const s = await loadSession(id, user.id);
  if (!s) redirect("/dashboard");
  if (!s.submitted_at) redirect(`/test/${s.id}`);

  const ids = s.questions.map((q) => q.id);
  const [texts, opts] = await Promise.all([
    query<{ id: number; question_text: string; difficulty: string }>(
      "SELECT id, question_text, difficulty FROM questions WHERE id = ANY($1)",
      [ids],
    ),
    query<{ question_id: number; label: string; option_text: string; is_correct: number }>(
      "SELECT question_id, label, option_text, is_correct FROM mcq_options WHERE question_id = ANY($1)",
      [ids],
    ),
  ]);
  const qInfo = new Map(texts.map((r) => [r.id, r]));
  const optInfo = new Map(opts.map((o) => [`${o.question_id}:${o.label.trim()}`, o]));

  const total = s.total ?? s.questions.length;
  const score = s.score ?? 0;
  const pct = total ? Math.round((score / total) * 100) : 0;
  const v = verdict(pct);

  const review = s.questions.map((q, i) => {
    const picked = s.answers[String(q.id)] ?? null;
    const options = q.options.map((label, n) => {
      const o = optInfo.get(`${q.id}:${label}`);
      return { letter: LETTERS[n], label, text: o?.option_text ?? "", correct: o?.is_correct === 1 };
    });
    const ok = options.some((o) => o.label === picked && o.correct);
    return { n: i + 1, text: qInfo.get(q.id)?.question_text ?? "", difficulty: qInfo.get(q.id)?.difficulty, picked, options, ok };
  });
  const wrong = review.filter((r) => !r.ok).length;

  return (
    <>
      <AppHeader username={user.username} />
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

        <div className="mt-6 flex flex-wrap gap-3">
          <Link href="/practice" className="rounded-xl bg-brand px-5 py-3 font-semibold text-white transition hover:brightness-110">
            Practice again
          </Link>
          <Link href="/dashboard" className="rounded-xl border border-border px-5 py-3 font-medium transition hover:bg-card">
            Dashboard
          </Link>
        </div>

        <h2 className="mt-10 text-xl font-bold tracking-tight">
          Review <span className="text-sm font-normal text-muted">· {wrong} to learn from</span>
        </h2>
        <ol className="mt-4 space-y-4">
          {review.map((r) => (
            <li key={r.n}>
              <details open={!r.ok} className="rounded-2xl border border-border bg-card p-5">
                <summary className="flex cursor-pointer items-start gap-3">
                  <span className={`mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-full text-sm font-bold text-white ${r.ok ? "bg-good" : "bg-bad"}`}>
                    {r.ok ? "✓" : "✗"}
                  </span>
                  <span className="font-medium whitespace-pre-wrap">
                    {r.n}. {r.text}
                  </span>
                </summary>
                <ul className="mt-4 space-y-2">
                  {r.options.map((o) => {
                    const chosen = o.label === r.picked;
                    const cls = o.correct
                      ? "border-good bg-good/10"
                      : chosen
                        ? "border-bad bg-bad/10"
                        : "border-border";
                    return (
                      <li key={o.label} className={`flex items-start gap-3 rounded-xl border-2 px-4 py-3 ${cls}`}>
                        <span className="font-bold">{o.letter}.</span>
                        <span className="flex-1 whitespace-pre-wrap">{o.text}</span>
                        {o.correct && <span className="text-xs font-semibold text-good">Correct answer</span>}
                        {chosen && !o.correct && <span className="text-xs font-semibold text-bad">Your answer</span>}
                      </li>
                    );
                  })}
                </ul>
                {!r.picked && <p className="mt-3 text-sm text-muted">You did not answer this question.</p>}
              </details>
            </li>
          ))}
        </ol>
      </main>
    </>
  );
}
