import { redirect } from "next/navigation";
import { TestRunner, type RunnerQuestion } from "@/components/TestRunner";
import { query } from "@/lib/db";
import { requireStudent } from "@/lib/guards";
import { deadlineMs, finalizeSession, isPastGrace, loadSession, nowMs } from "@/lib/sessions";

// Reads the session on every request, so it cannot be prerendered.
export const instant = false;

export default async function TestPage({ params }: PageProps<"/test/[id]">) {
  const user = await requireStudent();

  const { id } = await params;
  const s = await loadSession(id, user.id);
  if (!s) redirect("/dashboard");
  if (s.submitted_at) redirect(`/result/${s.id}`);

  // Closed while the student was away: grade what was autosaved.
  if (isPastGrace(s)) {
    await finalizeSession(s.id, user.id);
    redirect(`/result/${s.id}`);
  }

  const ids = s.questions.map((q) => q.id);
  const [texts, opts] = await Promise.all([
    query<{ id: number; question_text: string }>("SELECT id, question_text FROM questions WHERE id = ANY($1)", [ids]),
    // is_correct is deliberately not selected: correct answers never reach the browser during a test.
    query<{ question_id: number; label: string; option_text: string }>(
      "SELECT question_id, label, option_text FROM mcq_options WHERE question_id = ANY($1)",
      [ids],
    ),
  ]);
  const textOf = new Map(texts.map((r) => [r.id, r.question_text]));
  const optText = new Map(opts.map((o) => [`${o.question_id}:${o.label.trim()}`, o.option_text]));

  const questions: RunnerQuestion[] = s.questions.map((q) => ({
    id: q.id,
    text: textOf.get(q.id) ?? "",
    options: q.options.map((label) => ({ label, text: optText.get(`${q.id}:${label}`) ?? "" })),
  }));

  return (
    <TestRunner
      sessionId={s.id}
      questions={questions}
      initialAnswers={s.answers}
      deadlineMs={deadlineMs(s)}
      serverNowMs={nowMs()}
    />
  );
}
