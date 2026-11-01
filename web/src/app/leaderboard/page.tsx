import Link from "next/link";
import { AppHeader } from "@/components/AppHeader";
import { query } from "@/lib/db";
import { BOARDS, requireUser } from "@/lib/guards";

// Reads the session on every request, so it cannot be prerendered.
export const instant = false;

type Row = { username: string; total_tests: number; accuracy: number; hard_correct: number };

const MEDAL = ["🥇", "🥈", "🥉"];

export default async function LeaderboardPage({ searchParams }: PageProps<"/leaderboard">) {
  const user = await requireUser();
  const requested = (await searchParams).board;
  const board = BOARDS.find((b) => b === requested) ?? null;

  // Totals are computed per table first and joined once. The Streamlit query joined attempts,
  // admin attempts and responses together, which multiplied rows and inflated every score.
  const rows = await query<Row>(
    `WITH c AS (
       SELECT student_id AS uid, COUNT(*) AS tests, SUM(score) AS s, SUM(total_questions) AS t
         FROM test_attempts GROUP BY student_id
     ), a AS (
       SELECT user_id AS uid, COUNT(*) AS tests, SUM(score) AS s, SUM(total_questions) AS t
         FROM admin_test_attempts GROUP BY user_id
     ), h AS (
       SELECT uid, SUM(n) AS hard FROM (
         SELECT ta.student_id AS uid, COUNT(*) AS n
           FROM responses r JOIN test_attempts ta ON ta.id = r.attempt_id JOIN questions q ON q.id = r.question_id
          WHERE q.difficulty = 'hard' AND r.is_correct = 1 GROUP BY ta.student_id
         UNION ALL
         SELECT ata.user_id, COUNT(*)
           FROM admin_test_responses r JOIN admin_test_attempts ata ON ata.attempt_id = r.attempt_id JOIN questions q ON q.id = r.question_id
          WHERE q.difficulty = 'hard' AND r.is_correct = 1 GROUP BY ata.user_id
       ) x GROUP BY uid
     )
     SELECT u.username,
            (COALESCE(c.tests, 0) + COALESCE(a.tests, 0))::int AS total_tests,
            COALESCE(ROUND((COALESCE(c.s, 0) + COALESCE(a.s, 0)) * 100.0 / NULLIF(COALESCE(c.t, 0) + COALESCE(a.t, 0), 0), 2), 0)::float8 AS accuracy,
            COALESCE(h.hard, 0)::int AS hard_correct
       FROM users u
       LEFT JOIN c ON c.uid = u.id LEFT JOIN a ON a.uid = u.id LEFT JOIN h ON h.uid = u.id
      WHERE u.role = 'student' AND ($1::text IS NULL OR u.board_name = $1)
        AND COALESCE(c.tests, 0) + COALESCE(a.tests, 0) > 0
      ORDER BY hard_correct DESC, accuracy DESC, total_tests DESC, u.username
      LIMIT 50`,
    [board],
  );

  return (
    <>
      <AppHeader username={user.username} role={user.role} />
      <main className="mx-auto w-full max-w-3xl px-6 py-10">
        <p className="text-sm font-medium text-brand">Leaderboard</p>
        <h1 className="mt-1 text-3xl font-bold tracking-tight">Top students</h1>
        <p className="mt-2 text-muted">Ranked by hard questions answered correctly, then accuracy, then tests taken.</p>

        <div className="mt-6 flex flex-wrap gap-2" role="tablist" aria-label="Board">
          {[null, ...BOARDS].map((b) => (
            <Link
              key={b ?? "all"}
              href={b ? `/leaderboard?board=${encodeURIComponent(b)}` : "/leaderboard"}
              role="tab"
              aria-selected={b === board}
              className={`rounded-full border px-4 py-2 text-sm font-medium transition ${
                b === board ? "border-brand bg-brand text-white" : "border-border bg-card hover:border-brand"
              }`}
            >
              {b ?? "All boards"}
            </Link>
          ))}
        </div>

        {rows.length === 0 ? (
          <p className="mt-10 text-muted">No results yet. Be the first to take a test!</p>
        ) : (
          <ol className="mt-6 space-y-3">
            {rows.map((r, i) => {
              const me = r.username === user.username;
              return (
                <li
                  key={`${r.username}-${i}`}
                  className={`flex items-center gap-4 rounded-2xl border px-5 py-4 ${
                    me ? "border-brand bg-brand/5" : "border-border bg-card"
                  } ${i < 3 ? "shadow-md" : ""}`}
                >
                  <span className="w-10 text-center text-2xl font-bold" aria-label={`Rank ${i + 1}`}>
                    {MEDAL[i] ?? `#${i + 1}`}
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-semibold">
                      {r.username} {me && <span className="ml-1 text-xs font-medium text-brand">(you)</span>}
                    </p>
                    <p className="text-sm text-muted">{r.total_tests} test{r.total_tests === 1 ? "" : "s"}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold tabular-nums">{r.accuracy}%</p>
                    <p className="text-xs text-muted">accuracy</p>
                  </div>
                  <div className="w-16 text-right">
                    <p className="font-bold tabular-nums">{r.hard_correct}</p>
                    <p className="text-xs text-muted">hard ✓</p>
                  </div>
                </li>
              );
            })}
          </ol>
        )}
      </main>
    </>
  );
}
