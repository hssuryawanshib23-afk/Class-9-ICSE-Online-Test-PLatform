"use client";

import { useState } from "react";

export type ConceptData = { id: number; name: string; easy: number; medium: number; hard: number };
export type ChapterData = { number: number; name: string; concepts: ConceptData[] };

/** Accordion of chapters with per-concept checkboxes. Selected concepts are submitted as `concept` fields. */
export function ConceptPicker({
  chapters,
  selected,
  onToggle,
}: {
  chapters: ChapterData[];
  selected: Set<number>;
  onToggle: (ids: number[], on: boolean) => void;
}) {
  const [open, setOpen] = useState<number | null>(chapters[0]?.number ?? null);

  return (
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
                    onChange={(e) => onToggle(ids, e.target.checked)}
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
                          onChange={(e) => onToggle([c.id], e.target.checked)}
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
  );
}

/** Per-difficulty availability for the current selection. */
export function availability(chapters: ChapterData[], selected: Set<number>) {
  const a = { easy: 0, medium: 0, hard: 0 };
  for (const ch of chapters)
    for (const c of ch.concepts)
      if (selected.has(c.id)) {
        a.easy += c.easy;
        a.medium += c.medium;
        a.hard += c.hard;
      }
  return a;
}
