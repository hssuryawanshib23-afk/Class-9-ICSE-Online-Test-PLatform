"use client";

import { useState } from "react";
import { inputCls } from "@/components/AuthShell";

function strength(pw: string) {
  let s = 0;
  if (pw.length >= 8) s++;
  if (pw.length >= 12) s++;
  if (/[A-Z]/.test(pw) && /[a-z]/.test(pw)) s++;
  if (/\d/.test(pw)) s++;
  if (/[^A-Za-z0-9]/.test(pw)) s++;
  return Math.min(s, 4);
}

const LABELS = ["Too short", "Weak", "Okay", "Good", "Strong"];
const COLORS = ["bg-border", "bg-bad", "bg-accent", "bg-good", "bg-good"];

export function PasswordField({
  name = "password",
  label = "Password",
  autoComplete,
  showStrength = false,
  error,
}: {
  name?: string;
  label?: string;
  autoComplete: string;
  showStrength?: boolean;
  error?: string;
}) {
  const [visible, setVisible] = useState(false);
  const [value, setValue] = useState("");
  const s = strength(value);

  return (
    <div>
      <label htmlFor={name} className="mb-1.5 block text-sm font-medium">{label}</label>
      <div className="relative">
        <input
          id={name}
          name={name}
          type={visible ? "text" : "password"}
          autoComplete={autoComplete}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          className={`${inputCls} pr-16`}
        />
        <button
          type="button"
          onClick={() => setVisible((v) => !v)}
          aria-pressed={visible}
          className="absolute inset-y-0 right-3 my-auto h-8 rounded-lg px-2 text-sm font-medium text-brand"
        >
          {visible ? "Hide" : "Show"}
        </button>
      </div>
      {showStrength && value && (
        <div className="mt-2" aria-live="polite">
          <div className="flex gap-1.5">
            {[1, 2, 3, 4].map((i) => (
              <span key={i} className={`h-1.5 flex-1 rounded-full transition-colors ${i <= s ? COLORS[s] : "bg-border"}`} />
            ))}
          </div>
          <p className="mt-1 text-xs text-muted">{LABELS[s]}</p>
        </div>
      )}
      {error && <p className="mt-1 text-sm text-bad">{error}</p>}
    </div>
  );
}
