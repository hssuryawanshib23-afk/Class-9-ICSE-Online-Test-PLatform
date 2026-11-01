import "server-only";
import { query } from "@/lib/db";
import type { TestSession } from "@/lib/sessions";

export type ReviewOption = { letter: string; text: string; correct: boolean; picked: boolean };
export type ReviewItem = {
  n: number;
  text: string;
  difficulty: string | null;
  answered: boolean;
  ok: boolean;
  options: ReviewOption[];
};
export type DifficultyStat = { correct: number; total: number };
export type Breakdown = Record<"easy" | "medium" | "hard", DifficultyStat>;

const LETTERS = ["A", "B", "C", "D", "E", "F"];

export function gradeFor(p: number) {
  return p >= 90 ? "A+" : p >= 80 ? "A" : p >= 70 ? "B" : p >= 60 ? "C" : p >= 50 ? "D" : "F";
}

export function verdictFor(p: number) {
  if (p >= 90) return { emoji: "🏆", text: "Outstanding! You've mastered this topic!" };
  if (p >= 75) return { emoji: "🎉", text: "Excellent work! You have a strong understanding." };
  if (p >= 60) return { emoji: "👍", text: "Good job! A bit more practice will make you perfect." };
  if (p >= 40) return { emoji: "📚", text: "Keep practising! Review the concepts you missed." };
  return { emoji: "💪", text: "Don't give up! Focus on understanding the fundamentals." };
}

export function breakdownOf(items: ReviewItem[]): Breakdown {
  const b: Breakdown = { easy: { correct: 0, total: 0 }, medium: { correct: 0, total: 0 }, hard: { correct: 0, total: 0 } };
  for (const it of items) {
    const d = (it.difficulty ?? "medium").toLowerCase() as keyof Breakdown;
    if (!b[d]) continue;
    b[d].total++;
    if (it.ok) b[d].correct++;
  }
  return b;
}

/** Same thresholds as the Streamlit report, so students get consistent advice. */
export function insightsOf(b: Breakdown) {
  const strengths: string[] = [];
  const focus: string[] = [];
  const r = (d: DifficultyStat) => (d.total ? d.correct / d.total : null);
  const [e, m, h] = [r(b.easy), r(b.medium), r(b.hard)];
  if (e !== null && e >= 0.8) strengths.push("Strong grasp of fundamental concepts (easy questions).");
  if (m !== null && m >= 0.7) strengths.push("Good understanding of moderate-complexity topics.");
  if (h !== null && h >= 0.6) strengths.push("Excellent problem-solving on challenging questions.");
  if (e !== null && e < 0.6) focus.push("Strengthen the basics: revisit the fundamentals.");
  if (m !== null && m < 0.5) focus.push("More practice needed on moderate-difficulty topics.");
  if (h !== null && h < 0.4) focus.push("Work on advanced problem-solving techniques.");
  return { strengths, focus };
}

type OptionRow = { question_id: number; label: string; option_text: string; is_correct: number };
type QuestionRow = { id: number; question_text: string; difficulty: string | null };

async function loadQuestionData(ids: number[]) {
  const [qs, opts] = await Promise.all([
    query<QuestionRow>("SELECT id, question_text, difficulty FROM questions WHERE id = ANY($1)", [ids]),
    query<OptionRow>("SELECT question_id, label, option_text, is_correct FROM mcq_options WHERE question_id = ANY($1)", [ids]),
  ]);
  return {
    q: new Map(qs.map((r) => [r.id, r])),
    opt: new Map(opts.map((o) => [`${o.question_id}:${o.label.trim()}`, o])),
    byQuestion: opts.reduce((m, o) => m.set(o.question_id, [...(m.get(o.question_id) ?? []), o]), new Map<number, OptionRow[]>()),
  };
}

/** Review for a just-finished session: options appear in the order the student saw them. */
export async function reviewForSession(s: TestSession): Promise<ReviewItem[]> {
  const data = await loadQuestionData(s.questions.map((q) => q.id));
  return s.questions.map((q, i) => {
    const picked = s.answers[String(q.id)] ?? null;
    const options = q.options.map((label, n) => {
      const o = data.opt.get(`${q.id}:${label}`);
      return { letter: LETTERS[n], text: o?.option_text ?? "", correct: o?.is_correct === 1, picked: label === picked };
    });
    return {
      n: i + 1,
      text: data.q.get(q.id)?.question_text ?? "",
      difficulty: data.q.get(q.id)?.difficulty ?? null,
      answered: picked !== null,
      ok: options.some((o) => o.picked && o.correct),
      options,
    };
  });
}

export type HistoryRow = {
  type: "custom" | "admin";
  id: number;
  name: string;
  score: number;
  total: number;
  at: Date;
};

export async function getHistory(userId: number): Promise<HistoryRow[]> {
  const [custom, admin] = await Promise.all([
    query<HistoryRow>(
      `SELECT 'custom'::text AS type, id, 'Practice test'::text AS name, score, total_questions AS total,
              started_at AT TIME ZONE 'UTC' AS at
         FROM test_attempts WHERE student_id = $1`,
      [userId],
    ),
    query<HistoryRow>(
      `SELECT 'admin'::text AS type, a.attempt_id AS id, t.test_name AS name, a.score, a.total_questions AS total,
              a.attempted_at AT TIME ZONE 'UTC' AS at
         FROM admin_test_attempts a JOIN admin_tests t ON t.admin_test_id = a.admin_test_id
        WHERE a.user_id = $1`,
      [userId],
    ),
  ]);
  return [...custom, ...admin].sort((a, b) => b.at.getTime() - a.at.getTime());
}

/** Review of a past attempt. Returns null unless the attempt belongs to userId (or the caller is an admin). */
export async function getAttemptReview(
  type: "custom" | "admin",
  attemptId: number,
  viewer: { id: number; admin: boolean },
): Promise<{ name: string; owner: string; items: ReviewItem[] } | null> {
  type Resp = { question_id: number; picked: string | null };
  let name: string;
  let owner: string;
  let responses: Resp[];

  if (type === "custom") {
    const [a] = await query<{ student_id: number; username: string }>(
      "SELECT t.student_id, u.username FROM test_attempts t JOIN users u ON u.id = t.student_id WHERE t.id = $1",
      [attemptId],
    );
    if (!a || (a.student_id !== viewer.id && !viewer.admin)) return null;
    name = "Practice test";
    owner = a.username;
    responses = await query<Resp>(
      "SELECT question_id, selected_label AS picked FROM responses WHERE attempt_id = $1 ORDER BY id",
      [attemptId],
    );
  } else {
    const [a] = await query<{ user_id: number; username: string; test_name: string }>(
      `SELECT a.user_id, u.username, t.test_name FROM admin_test_attempts a
         JOIN users u ON u.id = a.user_id JOIN admin_tests t ON t.admin_test_id = a.admin_test_id
        WHERE a.attempt_id = $1`,
      [attemptId],
    );
    if (!a || (a.user_id !== viewer.id && !viewer.admin)) return null;
    name = a.test_name;
    owner = a.username;
    responses = await query<Resp>(
      "SELECT question_id, selected_answer AS picked FROM admin_test_responses WHERE attempt_id = $1 ORDER BY response_id",
      [attemptId],
    );
  }

  const data = await loadQuestionData(responses.map((r) => r.question_id));
  const items = responses.map((r, i) => {
    const picked = r.picked?.trim() || null;
    const options = (data.byQuestion.get(r.question_id) ?? [])
      .sort((x, y) => x.label.localeCompare(y.label))
      .map((o) => ({ letter: o.label.trim(), text: o.option_text, correct: o.is_correct === 1, picked: o.label.trim() === picked }));
    return {
      n: i + 1,
      text: data.q.get(r.question_id)?.question_text ?? "",
      difficulty: data.q.get(r.question_id)?.difficulty ?? null,
      answered: picked !== null,
      ok: options.some((o) => o.picked && o.correct),
      options,
    };
  });
  return { name, owner, items };
}
