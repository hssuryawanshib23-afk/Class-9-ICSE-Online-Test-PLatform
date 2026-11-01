"use client";

import { useActionState, useMemo, useState } from "react";
import { createAdminTest } from "@/app/actions/admin";
import { availability, ConceptPicker, type ChapterData } from "@/components/ConceptPicker";
import { splitCounts } from "@/lib/difficulty";

const field =
  "w-full rounded-xl border border-border bg-card px-3 py-2.5 text-base outline-none focus:border-brand focus:ring-4 focus:ring-brand/15";

export function AdminTestBuilder({ chapters }: { chapters: ChapterData[] }) {
  const [state, action, pending] = useActionState(createAdminTest, undefined);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [name, setName] = useState("");
  const [total, setTotal] = useState(20);
  const [duration, setDuration] = useState(30);
  const [easy, setEasy] = useState(30);
  const [medium, setMedium] = useState(30);
  const [hard, setHard] = useState(40);

  const avail = useMemo(() => availability(chapters, selected), [chapters, selected]);
  const availableTotal = avail.easy + avail.medium + avail.hard;
  const need = splitCounts(total, easy, medium);
  const short = (["easy", "medium", "hard"] as const).filter((k) => need[k] > avail[k]);
  const problem = !name.trim()
    ? "Give the test a name."
    : selected.size === 0
      ? "Select at least one concept."
      : easy + medium + hard !== 100
        ? `Difficulty must add up to 100% (now ${easy + medium + hard}%).`
        : total < 5 || total > Math.min(100, availableTotal)
          ? `Choose between 5 and ${Math.min(100, availableTotal)} questions.`
          : short.length
            ? `Not enough ${short.join(" / ")} questions for this mix.`
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

  const num = (v: string) => (v === "" ? 0 : Number(v));

  return (
    <form action={action} className="mt-8 grid gap-8 lg:grid-cols-[1.4fr_1fr]">
      <ConceptPicker chapters={chapters} selected={selected} onToggle={toggle} />

      <aside className="h-fit space-y-5 rounded-2xl border border-border bg-card p-6 lg:sticky lg:top-20">
        <h2 className="text-lg font-bold">Test settings</h2>
        <label className="block text-sm font-medium">
          Test name
          <input name="name" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Chapters 2–5 practice test" maxLength={255} className={`${field} mt-1`} />
        </label>
        <p className="text-sm text-muted">
          {selected.size} concept{selected.size === 1 ? "" : "s"} · {availableTotal} questions available
        </p>
        <div className="grid grid-cols-2 gap-3">
          <label className="text-sm font-medium">
            Questions
            <input name="total" type="number" min={5} max={100} value={total} onChange={(e) => setTotal(num(e.target.value))} className={`${field} mt-1`} />
          </label>
          <label className="text-sm font-medium">
            Minutes
            <input name="duration" type="number" min={5} max={180} value={duration} onChange={(e) => setDuration(num(e.target.value))} className={`${field} mt-1`} />
          </label>
        </div>
        <fieldset>
          <legend className="text-sm font-medium">Difficulty mix (must total 100%)</legend>
          <div className="mt-2 grid grid-cols-3 gap-3">
            {(
              [
                ["easy", "🟢 Easy %", easy, setEasy],
                ["medium", "🟡 Medium %", medium, setMedium],
                ["hard", "🔴 Hard %", hard, setHard],
              ] as const
            ).map(([n, label, v, set]) => (
              <label key={n} className="text-xs text-muted">
                {label}
                <input name={n} type="number" min={0} max={100} value={v} onChange={(e) => set(num(e.target.value))} className={`${field} mt-1 text-foreground`} />
              </label>
            ))}
          </div>
          <p className="mt-2 text-xs text-muted">
            {need.easy} easy + {need.medium} medium + {need.hard} hard
          </p>
        </fieldset>
        <label className="flex items-center gap-3 text-sm font-medium">
          <input type="checkbox" name="allow_retake" className="h-4 w-4 accent-[var(--brand)]" />
          Allow students to retake this test
        </label>

        {(problem || state?.message) && (
          <p role="alert" className="rounded-xl border border-bad/30 bg-bad/10 px-4 py-3 text-sm text-bad">
            {state?.message ?? problem}
          </p>
        )}
        <button
          disabled={pending || !!problem}
          className="w-full rounded-xl bg-brand px-4 py-3.5 font-semibold text-white shadow-lg shadow-brand/30 transition hover:brightness-110 disabled:opacity-50 disabled:shadow-none"
        >
          {pending ? "Creating…" : "Create test"}
        </button>
      </aside>
    </form>
  );
}
