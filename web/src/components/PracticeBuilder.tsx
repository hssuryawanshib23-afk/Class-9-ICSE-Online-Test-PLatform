"use client";

import { useActionState, useMemo, useState } from "react";
import { startCustomTest } from "@/app/actions/tests";
import { splitCounts } from "@/lib/difficulty";

export type ConceptData = { id: number; name: string; easy: number; medium: number; hard: number };
export type ChapterData = { number: number; name: string; concepts: ConceptData[] };

const field =
  "w-full rounded-xl border border-border bg-card px-3 py-2.5 text-base outline-none focus:border-brand focus:ring-4 focus:ring-brand/15";

export function PracticeBuilder({ chapters }: { chapters: ChapterData[] }) {
  const [state, action, pending] = useActionState(startCustomTest, undefined);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [open, setOpen] = useState<number | null>(chapters[0]?.number ?? null);
  const [total, setTotal] = useState(20);
  const [duration, setDuration] = useState(30);
  const [easy, setEasy] = useState(30);
  const [medium, setMedium] = useState(30);
  const hard = 100 - easy - medium;

  const avail = useMemo(() => {
    const a = { easy: 0, medium: 0, hard: 0 };
    for (const ch of chapters)
      for (const c of ch.concepts)
        if (selected.has(c.id)) {
          a.easy += c.easy;
          a.medium += c.medium;
          a.hard += c.hard;
        }
    return a;
  }, [chapters, selected]);

  const availableTotal = avail.easy + avail.medium + avail.hard;
  const need = splitCounts(total, easy, medium);
  const short = (["easy", "medium", "hard"] as const).filter((k) => need[k] > avail[k]);
  const problem =
    selected.size === 0
      ? "Select at least one concept."
      : hard < 34
        ? "Hard questions must be at least 34%."
        : total < 1 || total > availableTotal
          ? `Choose between 1 and ${availableTotal} questions.`
          : short.length
            ? `Not enough ${short.join(" / ")} questions for this mix. Lower the count or pick more concepts.`
            : null;

  function toggle(ids: number[], on: boolean) {
    setSelected((prev) => {
      const next = new Set(prev);
      for (const id of ids) {
        if (on) next.add(id);
        else next.delete(id);
      }
      return next;
    });
  }

  return (
    <form action={action} className="mt-8 grid gap-8 lg:grid-cols-[1.4fr_1fr]">
      <section aria-label="Concepts" className="space-y-3">
        {chapters.map((ch) => {
          const ids = ch.concepts.map((c) => c.id);
          const count = ids.filter((id) => selected.has(id)).length;
          const isOpen = open === ch.number;
          return (
            <div key={ch.number} className="overflow-hidden rounded-2xl border border-border bg-card">
              <button
                type="button"
                onClick={() => setOpen(isOpen ? null : ch.number)}
                aria-expanded={isOpen}
                className="flex w-full items-center justify-between gap-3 px-5 py-4 text-left"
              >
                <span>
                  <span className="text-sm text-muted">Chapter {ch.number}</span>
                  <span className="block font-semibold">{ch.name}</span>
                </span>
                <span className="flex items-center gap-3 text-sm">
                  {count > 0 && <span className="rounded-full bg-brand/10 px-2.5 py-0.5 font-medium text-brand">{count} selected</span>}
                  <span aria-hidden>{isOpen ? "−" : "+"}</span>
                </span>
              </button>
              {isOpen && (
                <div className="border-t border-border px-5 py-4">
                  <label className="mb-3 flex items-center gap-3 font-medium">
                    <input
                      type="checkbox"
                      className="h-4 w-4 accent-[var(--brand)]"
                      checked={count === ids.length}
                      onChange={(e) => toggle(ids, e.target.checked)}
                    />
                    Select all
                  </label>
                  <ul className="space-y-2">
                    {ch.concepts.map((c) => (
                      <li key={c.id}>
                        <label className="flex items-start gap-3">
                          <input
                            type="checkbox"
                            name="concept"
                            value={c.id}
                            className="mt-1 h-4 w-4 accent-[var(--brand)]"
                            checked={selected.has(c.id)}
                            onChange={(e) => toggle([c.id], e.target.checked)}
                          />
                          <span className="flex-1">{c.name}</span>
                          <span className="text-sm text-muted tabular-nums">{c.easy + c.medium + c.hard} Q</span>
                        </label>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          );
        })}
      </section>

      <aside className="h-fit space-y-5 rounded-2xl border border-border bg-card p-6 lg:sticky lg:top-20">
        <h2 className="text-lg font-bold">Test settings</h2>
        <p className="text-sm text-muted">
          {selected.size} concept{selected.size === 1 ? "" : "s"} · {availableTotal} questions available
        </p>

        <div className="grid grid-cols-2 gap-3">
          <label className="text-sm font-medium">
            Questions
            <input name="total" type="number" min={1} max={Math.max(availableTotal, 1)} value={total} onChange={(e) => setTotal(Number(e.target.value))} className={`${field} mt-1`} />
          </label>
          <label className="text-sm font-medium">
            Minutes
            <input name="duration" type="number" min={5} max={180} value={duration} onChange={(e) => setDuration(Number(e.target.value))} className={`${field} mt-1`} />
          </label>
        </div>

        <fieldset>
          <legend className="text-sm font-medium">Difficulty mix</legend>
          <div className="mt-2 grid grid-cols-3 gap-3">
            <label className="text-xs text-muted">
              🟢 Easy %
              <input name="easy" type="number" min={0} max={60} value={easy} onChange={(e) => setEasy(Number(e.target.value))} className={`${field} mt-1 text-foreground`} />
            </label>
            <label className="text-xs text-muted">
              🟡 Medium %
              <input name="medium" type="number" min={0} max={60} value={medium} onChange={(e) => setMedium(Number(e.target.value))} className={`${field} mt-1 text-foreground`} />
            </label>
            <label className="text-xs text-muted">
              🔴 Hard %
              <input name="hard" type="number" value={hard} readOnly className={`${field} mt-1 bg-background text-foreground`} />
            </label>
          </div>
          <p className="mt-2 text-xs text-muted">
            {need.easy} easy + {need.medium} medium + {need.hard} hard. At least 34% must be hard so practice stays challenging.
          </p>
        </fieldset>

        {(problem || state?.message) && (
          <p role="alert" className="rounded-xl border border-bad/30 bg-bad/10 px-4 py-3 text-sm text-bad">
            {state?.message ?? problem}
          </p>
        )}

        <button
          type="submit"
          disabled={pending || !!problem}
          className="w-full rounded-xl bg-brand px-4 py-3.5 font-semibold text-white shadow-lg shadow-brand/30 transition hover:brightness-110 disabled:opacity-50 disabled:shadow-none"
        >
          {pending ? "Preparing your test…" : "Start test"}
        </button>
      </aside>
    </form>
  );
}
