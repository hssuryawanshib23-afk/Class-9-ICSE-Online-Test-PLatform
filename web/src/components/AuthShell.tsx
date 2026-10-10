import type { ReactNode } from "react";

const CHIPS = [
  { q: "Speed = Distance ÷ ?", a: "Time", r: "-4deg", cls: "top-[20%] left-[8%]", delay: "0s" },
  { q: "SI unit of force", a: "Newton", r: "3deg", cls: "top-[34%] right-[9%]", delay: "-2s" },
  { q: "H₂O is a…", a: "Compound", r: "-2deg", cls: "top-[47%] left-[16%]", delay: "-4s" },
];

export function AuthShell({ title, subtitle, children }: { title: string; subtitle: string; children: ReactNode }) {
  return (
    <main className="grid min-h-dvh lg:grid-cols-[1.1fr_1fr]">
      <section className="relative hidden overflow-hidden bg-gradient-to-br from-[#2a1a8f] via-brand to-brand-2 p-12 text-white lg:flex lg:flex-col lg:justify-between">
        <div className="drift absolute -top-24 -right-24 h-96 w-96 rounded-full bg-accent/30 blur-3xl" />
        <div className="drift absolute -bottom-32 -left-16 h-96 w-96 rounded-full bg-white/20 blur-3xl" style={{ animationDelay: "-3s" }} />

        <div className="relative flex items-center gap-3 text-lg font-semibold tracking-tight">
          <span className="grid h-10 w-10 place-items-center rounded-xl bg-white text-xl text-brand">✦</span>
          ICSE Ace
        </div>

        {CHIPS.map((c) => (
          <div
            key={c.q}
            className={`float absolute ${c.cls} [@media(max-height:680px)]:hidden rounded-2xl border border-white/25 bg-white/15 px-5 py-3 shadow-xl backdrop-blur`}
            style={{ ["--r" as string]: c.r, animationDelay: c.delay }}
          >
            <p className="text-sm text-white/80">{c.q}</p>
            <p className="text-base font-semibold">{c.a}</p>
          </div>
        ))}

        <div className="relative max-w-md">
          <h2 className="text-4xl leading-tight font-bold tracking-tight">
            Practice smarter.<br />Score higher.
          </h2>
          <p className="mt-4 text-lg text-white/80">
            Chapter-wise Class 9 ICSE tests for Physics and Chemistry, with instant results and a leaderboard to chase.
          </p>
        </div>
      </section>

      <section className="flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          <div className="mb-8 flex items-center gap-3 text-lg font-semibold lg:hidden">
            <span className="grid h-9 w-9 place-items-center rounded-xl bg-brand text-white">✦</span>
            ICSE Ace
          </div>
          <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
          <p className="mt-2 text-muted">{subtitle}</p>
          <div className="mt-8">{children}</div>
        </div>
      </section>
    </main>
  );
}

export const inputCls =
  "w-full rounded-xl border border-border bg-card px-4 py-3 text-base outline-none transition focus:border-brand focus:ring-4 focus:ring-brand/15";
export const buttonCls =
  "w-full rounded-xl bg-brand px-4 py-3.5 text-base font-semibold text-white shadow-lg shadow-brand/30 transition hover:brightness-110 active:scale-[.99] disabled:opacity-60";
