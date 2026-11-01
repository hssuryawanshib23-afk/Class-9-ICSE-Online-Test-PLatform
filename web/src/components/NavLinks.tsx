"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export type NavItem = { href: string; label: string; icon: string };

/**
 * variant "top": links inside the header (tablet and desktop).
 * variant "bottom": a fixed tab bar for phones. It must be rendered OUTSIDE the header: the header uses
 * backdrop-filter, which makes `position: fixed` children position relative to the header instead of the screen.
 */
export function NavLinks({ items, variant }: { items: NavItem[]; variant: "top" | "bottom" }) {
  const path = usePathname();
  // Exact match for section roots like /admin, prefix match for everything beneath a section.
  const isActive = (href: string) => path === href || (href !== "/admin" && path.startsWith(href + "/"));

  if (variant === "top") {
    return (
      <nav className="hidden items-center gap-1 sm:flex" aria-label="Main">
        {items.map((l) => (
          <Link
            key={l.href}
            href={l.href}
            aria-current={isActive(l.href) ? "page" : undefined}
            className={`rounded-lg px-3 py-1.5 text-sm font-medium whitespace-nowrap transition ${
              isActive(l.href) ? "bg-brand/10 text-brand" : "text-muted hover:text-foreground"
            }`}
          >
            {l.label}
          </Link>
        ))}
      </nav>
    );
  }

  return (
    <nav
      aria-label="Main"
      className="fixed inset-x-0 bottom-0 z-20 grid border-t border-border bg-background pb-[env(safe-area-inset-bottom)] sm:hidden"
      style={{ gridTemplateColumns: `repeat(${items.length}, minmax(0, 1fr))` }}
    >
      {items.map((l) => (
        <Link
          key={l.href}
          href={l.href}
          aria-current={isActive(l.href) ? "page" : undefined}
          className={`flex flex-col items-center gap-0.5 py-2 text-[11px] font-medium transition ${
            isActive(l.href) ? "text-brand" : "text-muted"
          }`}
        >
          <span aria-hidden className="text-lg leading-none">{l.icon}</span>
          {l.label}
        </Link>
      ))}
    </nav>
  );
}
