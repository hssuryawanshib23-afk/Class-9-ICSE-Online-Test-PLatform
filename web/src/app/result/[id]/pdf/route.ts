import { requireStudent } from "@/lib/guards";
import { buildReport } from "@/lib/pdfReport";
import { reviewForSession } from "@/lib/results";
import { loadSession } from "@/lib/sessions";

export async function GET(_req: Request, ctx: RouteContext<"/result/[id]/pdf">) {
  const user = await requireStudent();
  const { id } = await ctx.params;
  const s = await loadSession(id, user.id);
  if (!s || !s.submitted_at) return new Response("Not found", { status: 404 });

  const items = await reviewForSession(s);
  const bytes = await buildReport({
    title: s.kind === "admin" ? "Teacher test" : "Practice test",
    student: user.username,
    score: s.score ?? 0,
    total: s.total ?? items.length,
    seconds: Math.max(0, Math.round((s.submitted_at.getTime() - s.started_at.getTime()) / 1000)),
    items,
    date: s.submitted_at,
  });

  return new Response(Buffer.from(bytes), {
    headers: {
      "Content-Type": "application/pdf",
      "Content-Disposition": `attachment; filename="test-report-${id.slice(0, 8)}.pdf"`,
      "Cache-Control": "private, no-store",
    },
  });
}
