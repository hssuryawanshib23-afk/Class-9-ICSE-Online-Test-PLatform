import { redirect } from "next/navigation";
import { logout } from "@/app/actions/auth";
import { getSession } from "@/lib/session";

// Reads the session on every request, so it cannot be prerendered.
export const instant = false;

export default async function DashboardPage() {
  const user = await getSession();
  if (!user) redirect("/login");

  return (
    <main className="mx-auto max-w-3xl px-6 py-16">
      <p className="text-sm font-medium text-brand">Dashboard</p>
      <h1 className="mt-1 text-4xl font-bold tracking-tight">Hi, {user.username} 👋</h1>
      <p className="mt-3 text-muted">
        Signed in as <span className="font-medium text-foreground">{user.role}</span>. Tests are coming next.
      </p>
      <form action={logout} className="mt-8">
        <button className="rounded-xl border border-border px-4 py-2 text-sm font-medium hover:bg-card">Log out</button>
      </form>
    </main>
  );
}
