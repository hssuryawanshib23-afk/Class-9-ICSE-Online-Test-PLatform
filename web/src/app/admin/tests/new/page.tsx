import Link from "next/link";
import { AdminTestBuilder } from "@/components/AdminTestBuilder";
import { AppHeader } from "@/components/AppHeader";
import { getChapters, getSubjects } from "@/lib/catalog";
import { requireAdmin } from "@/lib/guards";

// Reads the session on every request, so it cannot be prerendered.
export const instant = false;

export default async function NewTestPage({ searchParams }: PageProps<"/admin/tests/new">) {
  const admin = await requireAdmin();
  const subjects = await getSubjects();
  const requested = (await searchParams).subject;
  const subject = subjects.find((s) => s === requested) ?? subjects[0];
  const chapters = subject ? await getChapters(subject) : [];

  return (
    <>
      <AppHeader username={admin.username} role={admin.role} />
      <main className="mx-auto w-full max-w-5xl px-6 py-10">
        <Link href="/admin/tests" className="text-sm font-medium text-brand">← All tests</Link>
        <h1 className="mt-3 text-3xl font-bold tracking-tight">Create a test</h1>
        <p className="mt-2 text-muted">Questions are chosen once, now, so every student gets the same ones (options are shuffled per student).</p>
        <div className="mt-6 flex flex-wrap gap-2" role="tablist" aria-label="Subject">
          {subjects.map((s) => (
            <Link
              key={s}
              href={`/admin/tests/new?subject=${encodeURIComponent(s)}`}
              role="tab"
              aria-selected={s === subject}
              className={`rounded-full border px-4 py-2 text-sm font-medium transition ${s === subject ? "border-brand bg-brand text-white" : "border-border bg-card hover:border-brand"}`}
            >
              {s}
            </Link>
          ))}
        </div>
        {chapters.length === 0 ? (
          <p className="mt-10 text-muted">No questions available yet.</p>
        ) : (
          <AdminTestBuilder key={subject} chapters={chapters} />
        )}
      </main>
    </>
  );
}
