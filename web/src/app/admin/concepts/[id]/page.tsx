import Link from "next/link";
import { redirect } from "next/navigation";
import { AppHeader } from "@/components/AppHeader";
import { Bar } from "@/components/Bars";
import { getConceptStudents } from "@/lib/adminStats";
import { requireAdmin } from "@/lib/guards";

// Reads the session on every request, so it cannot be prerendered.
export const instant = false;

export default async function ConceptPage({ params }: PageProps<"/admin/concepts/[id]">) {
  const admin = await requireAdmin();
  const id = Number((await params).id);
  if (!Number.isInteger(id)) redirect("/admin");
  const data = await getConceptStudents(id);
  if (!data) redirect("/admin");

  return (
    <>
      <AppHeader username={admin.username} role={admin.role} />
      <main className="mx-auto w-full max-w-3xl px-6 py-10">
        <Link href="/admin" className="text-sm font-medium text-brand">← Overview</Link>
        <h1 className="mt-3 text-3xl font-bold tracking-tight">{data.name}</h1>
        <p className="mt-2 text-muted">Weakest students first.</p>
        {data.students.length === 0 ? (
          <p className="mt-8 text-muted">Nobody has answered questions on this concept yet.</p>
        ) : (
          <ul className="mt-6 space-y-3">
            {data.students.map((s) => (
              <li key={s.id} className="grid grid-cols-[1fr_8rem_6rem] items-center gap-4 rounded-2xl border border-border bg-card px-5 py-4 text-sm">
                <Link href={`/admin/students/${s.id}`} className="truncate font-medium text-brand hover:underline">{s.username}</Link>
                <Bar value={s.accuracy} label={s.username} />
                <span className="text-right tabular-nums">{s.accuracy}% <span className="text-muted">({s.correct}/{s.answered})</span></span>
              </li>
            ))}
          </ul>
        )}
      </main>
    </>
  );
}
