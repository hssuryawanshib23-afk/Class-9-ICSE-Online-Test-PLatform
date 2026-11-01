import Link from "next/link";
import { redirect } from "next/navigation";
import { AppHeader } from "@/components/AppHeader";
import { ReviewList } from "@/components/ReviewList";
import { requireStudent } from "@/lib/guards";
import { getAttemptReview } from "@/lib/results";

// Reads the session on every request, so it cannot be prerendered.
export const instant = false;

export default async function HistoryDetail({ params }: PageProps<"/history/[type]/[id]">) {
  const user = await requireStudent();
  const { type, id } = await params;
  const attemptId = Number(id);
  if ((type !== "custom" && type !== "admin") || !Number.isInteger(attemptId)) redirect("/history");

  // Ownership is checked inside: someone else's attempt id looks exactly like a missing one.
  const review = await getAttemptReview(type, attemptId, { id: user.id, admin: false });
  if (!review) redirect("/history");

  const correct = review.items.filter((i) => i.ok).length;
  const total = review.items.length;

  return (
    <>
      <AppHeader username={user.username} role={user.role} />
      <main className="mx-auto w-full max-w-3xl px-6 py-10">
        <Link href="/history" className="text-sm font-medium text-brand">← Back to history</Link>
        <h1 className="mt-3 text-3xl font-bold tracking-tight">{review.name}</h1>
        <p className="mt-2 text-lg">
          Score <span className="font-bold">{correct}/{total}</span>
          <span className="text-muted"> · {total ? Math.round((correct / total) * 100) : 0}%</span>
        </p>
        <ReviewList items={review.items} />
      </main>
    </>
  );
}
