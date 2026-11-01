import type { ReviewItem } from "@/lib/results";

const DIFF = { easy: "🟢 Easy", medium: "🟡 Medium", hard: "🔴 Hard" } as const;

export function ReviewList({ items, viewer = "You" }: { items: ReviewItem[]; viewer?: string }) {
  return (
    <ol className="mt-4 space-y-4">
      {items.map((r) => (
        <li key={r.n}>
          <details open={!r.ok} className="rounded-2xl border border-border bg-card p-5">
            <summary className="flex cursor-pointer items-start gap-3">
              <span
                className={`mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-full text-sm font-bold text-white ${r.ok ? "bg-good" : "bg-bad"}`}
                aria-label={r.ok ? "Correct" : "Incorrect"}
              >
                {r.ok ? "✓" : "✗"}
              </span>
              <span className="flex-1 font-medium whitespace-pre-wrap">
                {r.n}. {r.text}
              </span>
              {r.difficulty && (
                <span className="shrink-0 rounded-full bg-border px-2.5 py-0.5 text-xs">
                  {DIFF[r.difficulty.toLowerCase() as keyof typeof DIFF] ?? r.difficulty}
                </span>
              )}
            </summary>
            <ul className="mt-4 space-y-2">
              {r.options.map((o) => {
                const cls = o.correct ? "border-good bg-good/10" : o.picked ? "border-bad bg-bad/10" : "border-border";
                return (
                  <li key={o.letter} className={`flex items-start gap-3 rounded-xl border-2 px-4 py-3 ${cls}`}>
                    <span className="font-bold">{o.letter}.</span>
                    <span className="flex-1 whitespace-pre-wrap">{o.text}</span>
                    {o.correct && <span className="text-xs font-semibold text-good">Correct answer</span>}
                    {o.picked && !o.correct && <span className="text-xs font-semibold text-bad">{viewer === "You" ? "Your answer" : `${viewer}'s answer`}</span>}
                  </li>
                );
              })}
            </ul>
            {!r.answered && <p className="mt-3 text-sm text-muted">Not answered.</p>}
          </details>
        </li>
      ))}
    </ol>
  );
}
