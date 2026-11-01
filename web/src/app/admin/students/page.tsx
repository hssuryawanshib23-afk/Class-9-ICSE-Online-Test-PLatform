import Link from "next/link";
import { AppHeader } from "@/components/AppHeader";
import { query } from "@/lib/db";
import { requireAdmin } from "@/lib/guards";

// Reads the session on every request, so it cannot be prerendered.
export const instant = false;

type S = {
  id: number;
  username: string;
  phone_number: string;
  school_name: string | null;
  class_name: string | null;
  board_name: string | null;
  created_at: Date | null;
  tests: number;
  avg: number | null;
};

const dateFmt = new Intl.DateTimeFormat("en-IN", { day: "numeric", month: "short", year: "numeric", timeZone: "Asia/Kolkata" });

export default async function AdminStudents({ searchParams }: PageProps<"/admin/students">) {
  const admin = await requireAdmin();
  const q = String((await searchParams).q ?? "").trim().slice(0, 100);

  const students = await query<S>(
    `SELECT u.id, u.username, u.phone_number, u.school_name, u.class_name, u.board_name, u.created_at,
            COALESCE(t.tests, 0)::int AS tests, t.avg::float8 AS avg
       FROM users u
       LEFT JOIN LATERAL (
         SELECT COUNT(*) AS tests, AVG(score * 100.0 / NULLIF(total, 0)) AS avg FROM (
           SELECT score, total_questions AS total FROM test_attempts WHERE student_id = u.id
           UNION ALL
           SELECT score, total_questions FROM admin_test_attempts WHERE user_id = u.id
         ) x
       ) t ON true
      WHERE u.role = 'student'
        AND ($1 = '' OR u.username ILIKE '%' || $1 || '%' OR u.school_name ILIKE '%' || $1 || '%' OR u.phone_number LIKE '%' || $1 || '%')
      ORDER BY u.created_at DESC NULLS LAST, u.id DESC
      LIMIT 500`,
    [q],
  );

  return (
    <>
      <AppHeader username={admin.username} role={admin.role} />
      <main className="mx-auto w-full max-w-5xl px-6 py-10">
        <p className="text-sm font-medium text-brand">Admin</p>
        <h1 className="mt-1 text-3xl font-bold tracking-tight">Students</h1>

        <form className="mt-6 flex gap-3" role="search">
          <input
            name="q"
            defaultValue={q}
            placeholder="Search by username, school or phone"
            className="w-full max-w-md rounded-xl border border-border bg-card px-4 py-3 outline-none focus:border-brand focus:ring-4 focus:ring-brand/15"
            aria-label="Search students"
          />
          <button className="rounded-xl bg-brand px-5 py-3 font-semibold text-white">Search</button>
        </form>
        <p className="mt-3 text-sm text-muted">{students.length} student{students.length === 1 ? "" : "s"}{q ? ` matching “${q}”` : ""}</p>

        {students.length === 0 ? (
          <p className="mt-8 text-muted">No students found.</p>
        ) : (
          <div className="mt-4 overflow-x-auto rounded-2xl border border-border bg-card">
            <table className="w-full min-w-[640px] text-left text-sm">
              <thead className="border-b border-border text-muted">
                <tr>{["Student", "School", "Class · Board", "Tests", "Avg", "Joined"].map((h) => <th key={h} className="px-4 py-3 font-medium">{h}</th>)}</tr>
              </thead>
              <tbody className="divide-y divide-border">
                {students.map((s) => (
                  <tr key={s.id} className="hover:bg-background">
                    <td className="px-4 py-3">
                      <Link href={`/admin/students/${s.id}`} className="font-medium text-brand hover:underline">{s.username}</Link>
                      <span className="block text-xs text-muted">{s.phone_number}</span>
                    </td>
                    <td className="px-4 py-3">{s.school_name || "—"}</td>
                    <td className="px-4 py-3">{[s.class_name, s.board_name].filter(Boolean).join(" · ") || "—"}</td>
                    <td className="px-4 py-3 tabular-nums">{s.tests}</td>
                    <td className="px-4 py-3 tabular-nums">{s.avg === null ? "—" : `${s.avg.toFixed(1)}%`}</td>
                    <td className="px-4 py-3 text-muted">{s.created_at ? dateFmt.format(s.created_at) : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </>
  );
}
