"use client";

import { useActionState, useMemo, useState } from "react";
import { startCustomTest } from "@/app/actions/tests";
import { availability, ConceptPicker, type ChapterData } from "@/components/ConceptPicker";
import { splitCounts } from "@/lib/difficulty";

export type { ChapterData } from "@/components/ConceptPicker";

const field =
  "w-full rounded-xl border border-border bg-card px-3 py-2.5 text-base outline-none focus:border-brand focus:ring-4 focus:ring-brand/15";

export function PracticeBuilder({ chapters }: { chapters: ChapterData[] }) {
  const [state, action, pending] = useActionState(startCustomTest, undefined);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [total, setTotal] = useState(20);
  const [duration, setDuration] = useState(30);
  const [easy, setEasy] = useState(30);
  const [medium, setMedium] = useState(30);
  const hard = 100 - easy - medium;

  const avail = useMemo(() => availability(chapters, selected), [chapters, selected]);

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
      <ConceptPicker chapters={chapters} selected={selected} onToggle={toggle} />

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
