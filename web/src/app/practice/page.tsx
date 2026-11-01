import Link from "next/link";
import { AppHeader } from "@/components/AppHeader";
import { PracticeBuilder } from "@/components/PracticeBuilder";
import { getChapters, getSubjects } from "@/lib/catalog";
import { requireStudent } from "@/lib/guards";

// Reads the session on every request, so it cannot be prerendered.
export const instant = false;

export default async function PracticePage({ searchParams }: PageProps<"/practice">) {
  const user = await requireStudent();

  const subjects = await getSubjects();
  const requested = (await searchParams).subject;
  const subject = subjects.find((s) => s === requested) ?? subjects[0];
  const chapters = subject ? await getChapters(subject) : [];

  return (
    <>
      <AppHeader username={user.username} role={user.role} />
      <main className="mx-auto w-full max-w-5xl px-6 py-10">
        <p className="text-sm font-medium text-brand">Practice</p>
        <h1 className="mt-1 text-3xl font-bold tracking-tight">Build your test</h1>
        <p className="mt-2 text-muted">Pick the concepts you want to practise, then set how long and how hard.</p>

        <div className="mt-6 flex flex-wrap gap-2" role="tablist" aria-label="Subject">
          {subjects.map((s) => (
            <Link
              key={s}
              href={`/practice?subject=${encodeURIComponent(s)}`}
              role="tab"
              aria-selected={s === subject}
              className={`rounded-full border px-4 py-2 text-sm font-medium transition ${
                s === subject ? "border-brand bg-brand text-white" : "border-border bg-card hover:border-brand"
              }`}
            >
              {s}
            </Link>
          ))}
        </div>

        {chapters.length === 0 ? (
          <p className="mt-10 text-muted">No questions available for this subject yet.</p>
        ) : (
          <PracticeBuilder key={subject} chapters={chapters} />
        )}
      </main>
    </>
  );
}
