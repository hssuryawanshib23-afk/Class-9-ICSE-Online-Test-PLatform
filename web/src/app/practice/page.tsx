import Link from "next/link";
import { redirect } from "next/navigation";
import { AppHeader } from "@/components/AppHeader";
import { PracticeBuilder, type ChapterData } from "@/components/PracticeBuilder";
import { query } from "@/lib/db";
import { getSession } from "@/lib/session";

// Reads the session on every request, so it cannot be prerendered.
export const instant = false;

type Row = {
  chapter_number: number;
  chapter_name: string | null;
  concept_id: number;
  concept_name: string;
  easy: number;
  medium: number;
  hard: number;
};

export default async function PracticePage({ searchParams }: PageProps<"/practice">) {
  const user = await getSession();
  if (!user) redirect("/login");

  const subjects = (
    await query<{ subject: string }>(
      `SELECT DISTINCT COALESCE(ch.subject, 'Physics') AS subject
         FROM chapters ch JOIN concepts c ON c.chapter_id = ch.id JOIN questions q ON q.concept_id = c.id
        ORDER BY 1`,
    )
  ).map((r) => r.subject);

  const requested = (await searchParams).subject;
  const subject = subjects.find((s) => s === requested) ?? subjects[0];

  let chapters: ChapterData[] = [];
  if (subject) {
    const rows = await query<Row>(
      `SELECT ch.chapter_number, ch.chapter_name, c.id AS concept_id, c.concept_name,
              COUNT(q.id) FILTER (WHERE q.difficulty = 'easy')::int AS easy,
              COUNT(q.id) FILTER (WHERE q.difficulty = 'medium')::int AS medium,
              COUNT(q.id) FILTER (WHERE q.difficulty = 'hard')::int AS hard
         FROM chapters ch
         JOIN concepts c ON c.chapter_id = ch.id
         LEFT JOIN questions q ON q.concept_id = c.id
        WHERE COALESCE(ch.subject, 'Physics') = $1
        GROUP BY ch.chapter_number, ch.chapter_name, c.id, c.concept_name
        ORDER BY ch.chapter_number, c.id`,
      [subject],
    );
    const byChapter = new Map<number, ChapterData>();
    for (const r of rows) {
      const ch = byChapter.get(r.chapter_number) ?? {
        number: r.chapter_number,
        name: r.chapter_name || `Chapter ${r.chapter_number}`,
        concepts: [],
      };
      if (r.easy + r.medium + r.hard > 0) {
        ch.concepts.push({ id: r.concept_id, name: r.concept_name, easy: r.easy, medium: r.medium, hard: r.hard });
      }
      byChapter.set(r.chapter_number, ch);
    }
    chapters = [...byChapter.values()].filter((c) => c.concepts.length > 0);
  }

  return (
    <>
      <AppHeader username={user.username} />
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
