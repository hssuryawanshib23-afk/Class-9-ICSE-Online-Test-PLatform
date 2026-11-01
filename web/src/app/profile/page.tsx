import { redirect } from "next/navigation";
import { AppHeader } from "@/components/AppHeader";
import { PasswordForm, ProfileForm, RecoveryCard } from "@/components/ProfileForms";
import { query } from "@/lib/db";
import { isAdmin, requireUser } from "@/lib/guards";

// Reads the session on every request, so it cannot be prerendered.
export const instant = false;

const fmt = new Intl.DateTimeFormat("en-IN", { day: "numeric", month: "long", year: "numeric", timeZone: "Asia/Kolkata" });

export default async function ProfilePage({ searchParams }: PageProps<"/profile">) {
  const user = await requireUser();
  if (isAdmin(user)) redirect("/admin/settings");
  const setup = (await searchParams).setup === "1";

  const [p] = await query<{
    phone_number: string;
    school_name: string | null;
    class_name: string | null;
    board_name: string | null;
    recovery_code: string | null;
    created_at: Date | null;
  }>(
    "SELECT phone_number, school_name, class_name, board_name, recovery_code, created_at FROM users WHERE id = $1",
    [user.id],
  );

  return (
    <>
      <AppHeader username={user.username} role={user.role} />
      <main className="mx-auto w-full max-w-3xl px-6 py-10">
        {setup && (
          <p role="status" className="mb-6 rounded-2xl border border-accent/40 bg-accent/10 px-5 py-4 text-sm">
            <strong>One last step.</strong> Please add your school, class and board to start taking tests.
          </p>
        )}
        <section className="flex items-center gap-5">
          <span className="grid h-20 w-20 place-items-center rounded-full bg-gradient-to-br from-brand to-brand-2 text-3xl font-bold text-white">
            {user.username.slice(0, 1).toUpperCase()}
          </span>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">{user.username}</h1>
            <p className="text-sm text-muted">📱 {p.phone_number}</p>
            {p.created_at && <p className="text-sm text-muted">Joined {fmt.format(p.created_at)}</p>}
          </div>
        </section>

        <div className="mt-8 space-y-6">
          <ProfileForm school={p.school_name ?? ""} className={p.class_name ?? ""} board={p.board_name ?? ""} />
          <RecoveryCard code={p.recovery_code} />
          <PasswordForm />
        </div>
      </main>
    </>
  );
}
