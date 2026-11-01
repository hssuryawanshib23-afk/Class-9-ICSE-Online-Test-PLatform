import Link from "next/link";
import { logout } from "@/app/actions/auth";
import { NavLinks, type NavItem } from "@/components/NavLinks";

const STUDENT_NAV: NavItem[] = [
  { href: "/dashboard", label: "Home", icon: "🏠" },
  { href: "/practice", label: "Practice", icon: "✏️" },
  { href: "/tests", label: "Tests", icon: "📋" },
  { href: "/history", label: "History", icon: "🕘" },
  { href: "/leaderboard", label: "Ranks", icon: "🏆" },
];

const ADMIN_NAV: NavItem[] = [
  { href: "/admin", label: "Overview", icon: "📊" },
  { href: "/admin/tests", label: "Tests", icon: "🗂️" },
  { href: "/admin/students", label: "Students", icon: "👥" },
  { href: "/leaderboard", label: "Ranks", icon: "🏆" },
  { href: "/admin/settings", label: "Settings", icon: "⚙️" },
];

export function AppHeader({ username, role = "student" }: { username: string; role?: string }) {
  const admin = role === "admin";
  const items = admin ? ADMIN_NAV : STUDENT_NAV;
  return (
    <>
    <header className="sticky top-0 z-10 border-b border-border bg-background/80 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-6 py-3">
        <div className="flex min-w-0 items-center gap-6">
          <Link href={admin ? "/admin" : "/dashboard"} className="flex shrink-0 items-center gap-3 font-semibold tracking-tight">
            <span className="grid h-9 w-9 place-items-center rounded-xl bg-brand text-white">✦</span>
            <span className="hidden lg:inline">ICSE Ace{admin ? " · Admin" : ""}</span>
          </Link>
          <NavLinks items={items} variant="top" />
        </div>
        <div className="flex shrink-0 items-center gap-3">
          {admin ? (
            <span className="hidden rounded-full bg-accent/20 px-3 py-1 text-sm font-medium sm:block">{username}</span>
          ) : (
            <Link
              href="/profile"
              className="hidden items-center gap-2 rounded-full border border-border bg-card py-1 pr-3 pl-1 text-sm transition hover:border-brand sm:flex"
            >
              <span className="grid h-7 w-7 place-items-center rounded-full bg-brand/15 font-semibold text-brand">
                {username.slice(0, 1).toUpperCase()}
              </span>
              {username}
            </Link>
          )}
          <form action={logout}>
            <button className="rounded-xl border border-border px-3 py-1.5 text-sm font-medium transition hover:bg-card">Log out</button>
          </form>
        </div>
      </div>
    </header>
    <NavLinks items={items} variant="bottom" />
    </>
  );
}
