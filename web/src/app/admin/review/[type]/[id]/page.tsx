import { redirect } from "next/navigation";
import { AppHeader } from "@/components/AppHeader";
import { ReviewList } from "@/components/ReviewList";
import { requireAdmin } from "@/lib/guards";
import { getAttemptReview } from "@/lib/results";

// Reads the session on every request, so it cannot be prerendered.
export const instant = false;

export default async function AdminReview({ params }: PageProps<"/admin/review/[type]/[id]">) {
  const admin = await requireAdmin();
  const { type, id } = await params;
  const attemptId = Number(id);
  if ((type !== "custom" && type !== "admin") || !Number.isInteger(attemptId)) redirect("/admin");

  const review = await getAttemptReview(type, attemptId, { id: admin.id, admin: true });
  if (!review) redirect("/admin");
  const correct = review.items.filter((i) => i.ok).length;

  return (
    <>
      <AppHeader username={admin.username} role={admin.role} />
      <main className="mx-auto w-full max-w-3xl px-6 py-10">
        <h1 className="text-3xl font-bold tracking-tight">{review.owner}: {review.name}</h1>
        <p className="mt-2 text-lg">
          Score <span className="font-bold">{correct}/{review.items.length}</span>
          <span className="text-muted"> · {review.items.length ? Math.round((correct / review.items.length) * 100) : 0}%</span>
        </p>
        <ReviewList items={review.items} viewer={review.owner} />
      </main>
    </>
  );
}
