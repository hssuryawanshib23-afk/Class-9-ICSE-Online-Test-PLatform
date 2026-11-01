/** Accuracy bar used across the admin analytics. Colour thresholds match the Streamlit dashboard (70 / 50). */
export function tone(p: number) {
  return p >= 70 ? "bg-good" : p >= 50 ? "bg-accent" : "bg-bad";
}

export function Bar({ value, label }: { value: number; label: string }) {
  return (
    <div className="h-2.5 overflow-hidden rounded-full bg-border" role="img" aria-label={`${label}: ${value}%`}>
      <div className={`h-full rounded-full ${tone(value)}`} style={{ width: `${Math.min(100, Math.max(0, value))}%` }} />
    </div>
  );
}

export function Stat({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="rounded-2xl border border-border bg-card p-5">
      <p className="text-sm text-muted">{label}</p>
      <p className="mt-1 text-3xl font-bold tracking-tight tabular-nums">{value}</p>
      {hint && <p className="mt-1 text-xs text-muted">{hint}</p>}
    </div>
  );
}
