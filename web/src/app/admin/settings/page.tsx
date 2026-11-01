import { AppHeader } from "@/components/AppHeader";
import { PasswordForm } from "@/components/ProfileForms";
import { requireAdmin } from "@/lib/guards";

// Reads the session on every request, so it cannot be prerendered.
export const instant = false;

export default async function AdminSettings() {
  const admin = await requireAdmin();
  return (
    <>
      <AppHeader username={admin.username} role={admin.role} />
      <main className="mx-auto w-full max-w-xl px-6 py-10">
        <p className="text-sm font-medium text-brand">Admin</p>
        <h1 className="mt-1 text-3xl font-bold tracking-tight">Settings</h1>
        <p className="mt-2 text-muted">
          Signed in as <strong className="text-foreground">{admin.username}</strong>.
        </p>
        <div className="mt-8"><PasswordForm /></div>
      </main>
    </>
  );
}
