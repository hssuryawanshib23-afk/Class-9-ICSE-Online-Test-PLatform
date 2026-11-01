"use client";

import { useCallback, useEffect, useRef, useState, useTransition } from "react";
import { autosaveAnswers, submitTest } from "@/app/actions/tests";

export type RunnerQuestion = { id: number; text: string; options: { label: string; text: string }[] };

const LETTERS = ["A", "B", "C", "D", "E", "F"];

function fmt(sec: number) {
  const m = Math.floor(sec / 60);
  return `${m}:${String(sec % 60).padStart(2, "0")}`;
}

export function TestRunner({
  sessionId,
  questions,
  initialAnswers,
  deadlineMs,
  serverNowMs,
}: {
  sessionId: string;
  questions: RunnerQuestion[];
  initialAnswers: Record<string, string>;
  deadlineMs: number;
  serverNowMs: number;
}) {
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>(initialAnswers);
  const [confirming, setConfirming] = useState(false);
  const [save, setSave] = useState<"saved" | "saving" | "offline">("saved");
  const [pending, startSubmit] = useTransition();

  // Server clock offset, so a wrong device clock cannot give extra (or fewer) minutes.
  const [offset] = useState(() => serverNowMs - Date.now());
  const remaining = () => Math.max(0, Math.round((deadlineMs - (Date.now() + offset)) / 1000));
  // Same value on server and browser for the first paint (no hydration mismatch); the interval corrects it.
  const [left, setLeft] = useState(() => Math.max(0, Math.round((deadlineMs - serverNowMs) / 1000)));

  const answersRef = useRef(answers);
  useEffect(() => {
    answersRef.current = answers;
  }, [answers]);
  const submitted = useRef(false);

  const doSubmit = useCallback(() => {
    if (submitted.current) return;
    submitted.current = true;
    startSubmit(() => submitTest(sessionId, answersRef.current));
  }, [sessionId]);

  useEffect(() => {
    const t = setInterval(() => {
      const r = remaining();
      setLeft(r);
      if (r === 0) doSubmit();
    }, 250);
    return () => clearInterval(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [doSubmit]);

  // Debounced autosave, so a closed tab or dead battery loses at most a second of answers.
  const first = useRef(true);
  useEffect(() => {
    if (first.current) {
      first.current = false;
      return;
    }
    setSave("saving");
    const t = setTimeout(async () => {
      try {
        const res = await autosaveAnswers(sessionId, answers);
        setSave(res.ok ? "saved" : "offline");
      } catch {
        setSave("offline");
      }
    }, 800);
    return () => clearTimeout(t);
  }, [answers, sessionId]);

  useEffect(() => {
    const warn = (e: BeforeUnloadEvent) => {
      if (!submitted.current) e.preventDefault();
    };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, []);

  const q = questions[index];
  const answered = questions.filter((x) => answers[String(x.id)]).length;
  const unanswered = questions.length - answered;

  function choose(label: string) {
    setAnswers((a) => ({ ...a, [String(q.id)]: label }));
  }

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (confirming || (e.target as HTMLElement).tagName === "INPUT") return;
      if (e.key === "ArrowRight") setIndex((i) => Math.min(i + 1, questions.length - 1));
      else if (e.key === "ArrowLeft") setIndex((i) => Math.max(i - 1, 0));
      else {
        const n = LETTERS.indexOf(e.key.toUpperCase());
        const opt = n >= 0 ? questions[index].options[n] : undefined;
        if (opt) setAnswers((a) => ({ ...a, [String(questions[index].id)]: opt.label }));
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [confirming, index, questions]);

  const low = left <= 60;

  return (
    <div className="min-h-dvh">
      <header className="sticky top-0 z-10 border-b border-border bg-background/90 backdrop-blur">
        <div className="mx-auto flex max-w-3xl items-center justify-between gap-4 px-6 py-3">
          <p className="text-sm font-medium">
            Question {index + 1} <span className="text-muted">of {questions.length}</span>
          </p>
          <div
            role="timer"
            aria-label="Time left"
            className={`rounded-full px-4 py-1.5 font-mono text-lg font-bold tabular-nums ${
              low ? "animate-pulse bg-bad text-white" : "bg-brand/10 text-brand"
            }`}
          >
            ⏱ {fmt(left)}
          </div>
          <p className="hidden text-xs text-muted sm:block" aria-live="polite">
            {save === "saving" ? "Saving…" : save === "offline" ? "⚠ Not saved, check connection" : "✓ Saved"}
          </p>
        </div>
        <div className="h-1 bg-border">
          <div className="h-full bg-brand transition-all" style={{ width: `${(answered / questions.length) * 100}%` }} />
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-6 py-8">
        <h1 className="text-xl leading-relaxed font-semibold whitespace-pre-wrap sm:text-2xl">{q.text}</h1>

        <div role="radiogroup" aria-label="Options" className="mt-6 space-y-3">
          {q.options.map((o, i) => {
            const on = answers[String(q.id)] === o.label;
            return (
              <button
                key={o.label}
                type="button"
                role="radio"
                aria-checked={on}
                onClick={() => choose(o.label)}
                className={`flex w-full items-start gap-4 rounded-2xl border-2 px-5 py-4 text-left transition ${
                  on ? "border-brand bg-brand/10" : "border-border bg-card hover:border-brand/50"
                }`}
              >
                <span
                  className={`grid h-8 w-8 shrink-0 place-items-center rounded-lg text-sm font-bold ${
                    on ? "bg-brand text-white" : "bg-border text-muted"
                  }`}
                >
                  {LETTERS[i]}
                </span>
                <span className="pt-0.5 whitespace-pre-wrap">{o.text}</span>
              </button>
            );
          })}
        </div>

        <div className="mt-8 flex items-center justify-between gap-3">
          <button
            type="button"
            disabled={index === 0}
            onClick={() => setIndex(index - 1)}
            className="rounded-xl border border-border px-5 py-3 font-medium transition hover:bg-card disabled:opacity-40"
          >
            ← Previous
          </button>
          {index < questions.length - 1 ? (
            <button
              type="button"
              onClick={() => setIndex(index + 1)}
              className="rounded-xl bg-brand px-5 py-3 font-semibold text-white transition hover:brightness-110"
            >
              Next →
            </button>
          ) : (
            <button
              type="button"
              onClick={() => (unanswered ? setConfirming(true) : doSubmit())}
              className="rounded-xl bg-good px-5 py-3 font-semibold text-white transition hover:brightness-110"
            >
              Submit test
            </button>
          )}
        </div>

        <nav aria-label="Question palette" className="mt-10 rounded-2xl border border-border bg-card p-5">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium">
              {answered}/{questions.length} answered
            </p>
            <button
              type="button"
              onClick={() => (unanswered ? setConfirming(true) : doSubmit())}
              className="text-sm font-semibold text-brand"
            >
              Submit now
            </button>
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            {questions.map((x, i) => {
              const done = !!answers[String(x.id)];
              return (
                <button
                  key={x.id}
                  type="button"
                  onClick={() => setIndex(i)}
                  aria-label={`Question ${i + 1}${done ? ", answered" : ", not answered"}`}
                  aria-current={i === index}
                  className={`h-9 w-9 rounded-lg text-sm font-medium transition ${
                    i === index
                      ? "bg-brand text-white ring-4 ring-brand/20"
                      : done
                        ? "bg-good/15 text-good"
                        : "bg-border text-muted hover:bg-brand/10"
                  }`}
                >
                  {i + 1}
                </button>
              );
            })}
          </div>
        </nav>
      </main>

      {confirming && (
        <div className="fixed inset-0 z-20 grid place-items-center bg-black/50 p-6" role="dialog" aria-modal="true" aria-label="Confirm submit">
          <div className="w-full max-w-sm rounded-2xl bg-card p-6 shadow-2xl">
            <h2 className="text-lg font-bold">Submit with unanswered questions?</h2>
            <p className="mt-2 text-sm text-muted">
              You have {unanswered} unanswered question{unanswered === 1 ? "" : "s"}. They will count as wrong.
            </p>
            <div className="mt-5 grid grid-cols-2 gap-3">
              <button type="button" onClick={() => setConfirming(false)} className="rounded-xl border border-border px-4 py-2.5 font-medium">
                Keep going
              </button>
              <button type="button" onClick={doSubmit} className="rounded-xl bg-brand px-4 py-2.5 font-semibold text-white">
                Submit
              </button>
            </div>
          </div>
        </div>
      )}

      {pending && (
        <div className="fixed inset-0 z-30 grid place-items-center bg-background/80 backdrop-blur" role="status">
          <p className="text-lg font-semibold">Submitting and marking your test…</p>
        </div>
      )}
    </div>
  );
}
