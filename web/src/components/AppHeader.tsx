import { logout } from "@/app/actions/auth";

export function AppHeader({ username }: { username: string }) {
  return (
    <header className="sticky top-0 z-10 border-b border-border bg-background/80 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-3">
        <div className="flex items-center gap-3 font-semibold tracking-tight">
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-brand text-white">✦</span>
          ICSE Ace
        </div>
        <div className="flex items-center gap-3">
          <span className="hidden items-center gap-2 rounded-full border border-border bg-card py-1 pr-3 pl-1 text-sm sm:flex">
            <span className="grid h-7 w-7 place-items-center rounded-full bg-brand/15 font-semibold text-brand">
              {username.slice(0, 1).toUpperCase()}
            </span>
            {username}
          </span>
          <form action={logout}>
            <button className="rounded-xl border border-border px-3 py-1.5 text-sm font-medium transition hover:bg-card">
              Log out
            </button>
          </form>
        </div>
      </div>
    </header>
  );
}
