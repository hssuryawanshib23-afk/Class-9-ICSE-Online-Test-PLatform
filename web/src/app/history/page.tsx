import Link from "next/link";
import { AppHeader } from "@/components/AppHeader";
import { requireStudent } from "@/lib/guards";
import { getHistory } from "@/lib/results";

// Reads the session on every request, so it cannot be prerendered.
export const instant = false;

const fmt = new Intl.DateTimeFormat("en-IN", {
  day: "numeric", month: "short", year: "numeric", hour: "numeric", minute: "2-digit", timeZone: "Asia/Kolkata",
});

export default async function HistoryPage() {
  const user = await requireStudent();
  const rows = await getHistory(user.id);

  return (
    <>
      <AppHeader username={user.username} role={user.role} />
      <main className="mx-auto w-full max-w-3xl px-6 py-10">
        <p className="text-sm font-medium text-brand">History</p>
        <h1 className="mt-1 text-3xl font-bold tracking-tight">Your test history</h1>
        <p className="mt-2 text-muted">{rows.length ? `${rows.length} test${rows.length === 1 ? "" : "s"} so far.` : ""}</p>

        {rows.length === 0 ? (
          <div className="mt-10 rounded-2xl border border-dashed border-border bg-card p-10 text-center">
            <p className="text-4xl">📭</p>
            <p className="mt-3 font-semibold">No tests yet</p>
            <p className="mt-1 text-sm text-muted">Take a test and your results will show up here.</p>
            <Link href="/practice" className="mt-5 inline-block rounded-xl bg-brand px-5 py-3 font-semibold text-white">Start practising</Link>
          </div>
        ) : (
          <ul className="mt-6 space-y-3">
            {rows.map((r) => {
              const p = r.total ? (r.score / r.total) * 100 : 0;
              const tone = p >= 80 ? "text-good" : p >= 60 ? "text-brand" : "text-accent";
              return (
                <li key={`${r.type}-${r.id}`}>
                  <Link
                    href={`/history/${r.type}/${r.id}`}
                    className="flex items-center gap-4 rounded-2xl border border-border bg-card px-5 py-4 transition hover:border-brand"
                  >
                    <div className="min-w-0 flex-1">
                      <p className="truncate font-semibold">
                        {r.name}
                        {r.type === "admin" && <span className="ml-2 rounded-full bg-brand/10 px-2 py-0.5 text-xs font-medium text-brand">Teacher test</span>}
                      </p>
                      <p className="text-sm text-muted">{fmt.format(r.at)}</p>
                    </div>
                    <p className={`text-right text-xl font-bold tabular-nums ${tone}`}>
                      {r.score}/{r.total}
                      <span className="block text-xs font-normal text-muted">{Math.round(p)}%</span>
                    </p>
                    <span aria-hidden className="text-muted">›</span>
                  </Link>
                </li>
              );
            })}
          </ul>
        )}
      </main>
    </>
  );
}
