import Link from "next/link";
import { redirect } from "next/navigation";
import { AppHeader } from "@/components/AppHeader";
import { DeleteStudentForm, ResetPasswordForm } from "@/components/AdminForms";
import { Bar, Stat } from "@/components/Bars";
import { getChapterPerformance } from "@/lib/adminStats";
import { query } from "@/lib/db";
import { requireAdmin } from "@/lib/guards";
import { getHistory } from "@/lib/results";

// Reads the session on every request, so it cannot be prerendered.
export const instant = false;

const fmt = new Intl.DateTimeFormat("en-IN", { day: "numeric", month: "short", year: "numeric", hour: "numeric", minute: "2-digit", timeZone: "Asia/Kolkata" });

export default async function AdminStudent({ params }: PageProps<"/admin/students/[id]">) {
  const admin = await requireAdmin();
  const id = Number((await params).id);
  if (!Number.isInteger(id)) redirect("/admin/students");

  const [u] = await query<{
    username: string; role: string; phone_number: string; school_name: string | null;
    class_name: string | null; board_name: string | null; created_at: Date | null;
  }>("SELECT username, role, phone_number, school_name, class_name, board_name, created_at FROM users WHERE id = $1", [id]);
  if (!u || u.role === "admin") redirect("/admin/students");

  const [history, chapters] = await Promise.all([getHistory(id), getChapterPerformance(id)]);
  const pcts = history.filter((h) => h.total).map((h) => (h.score * 100) / h.total);
  const avg = pcts.length ? pcts.reduce((a, b) => a + b, 0) / pcts.length : null;
  const byAccuracy = [...chapters].sort((a, b) => a.accuracy - b.accuracy);

  return (
    <>
      <AppHeader username={admin.username} role={admin.role} />
      <main className="mx-auto w-full max-w-4xl px-6 py-10">
        <Link href="/admin/students" className="text-sm font-medium text-brand">← All students</Link>
        <h1 className="mt-3 text-3xl font-bold tracking-tight">{u.username}</h1>
        <p className="mt-2 text-sm text-muted">
          📱 {u.phone_number} · {u.school_name || "No school"} · {[u.class_name, u.board_name].filter(Boolean).join(" · ") || "No class/board"}
          {u.created_at ? ` · joined ${fmt.format(u.created_at)}` : ""}
        </p>

        <section className="mt-6 grid gap-4 sm:grid-cols-3">
          <Stat label="Tests taken" value={String(history.length)} />
          <Stat label="Average" value={avg === null ? "—" : `${avg.toFixed(1)}%`} />
          <Stat label="Best" value={pcts.length ? `${Math.max(...pcts).toFixed(1)}%` : "—"} />
        </section>

        <div className="mt-10 grid gap-8 lg:grid-cols-[1.3fr_1fr]">
          <section>
            <h2 className="text-xl font-bold tracking-tight">Test history</h2>
            {history.length === 0 ? (
              <p className="mt-3 text-muted">No tests yet.</p>
            ) : (
              <ul className="mt-4 space-y-2">
                {history.map((h) => (
                  <li key={`${h.type}-${h.id}`}>
                    <Link href={`/admin/review/${h.type}/${h.id}`} className="flex items-center justify-between gap-3 rounded-xl border border-border bg-card px-4 py-3 text-sm transition hover:border-brand">
                      <span className="min-w-0">
                        <span className="block truncate font-medium">{h.name}</span>
                        <span className="text-xs text-muted">{fmt.format(h.at)}</span>
                      </span>
                      <span className="font-bold tabular-nums">{h.score}/{h.total}</span>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section>
            <h2 className="text-xl font-bold tracking-tight">By chapter</h2>
            {byAccuracy.length === 0 ? (
              <p className="mt-3 text-muted">No answers yet.</p>
            ) : (
              <ul className="mt-4 space-y-3 rounded-2xl border border-border bg-card p-4 text-sm">
                {byAccuracy.map((c) => (
                  <li key={`${c.subject}-${c.chapter}`}>
                    <div className="mb-1 flex justify-between"><span className="font-medium">{c.subject} · Ch {c.chapter}</span><span className="tabular-nums text-muted">{c.accuracy}% · {c.answered} Q</span></div>
                    <Bar value={c.accuracy} label={`${c.subject} chapter ${c.chapter}`} />
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>

        <section className="mt-12 space-y-4">
          <h2 className="text-xl font-bold tracking-tight">Manage account</h2>
          <ResetPasswordForm id={id} username={u.username} />
          <DeleteStudentForm id={id} username={u.username} />
        </section>
      </main>
    </>
  );
}
