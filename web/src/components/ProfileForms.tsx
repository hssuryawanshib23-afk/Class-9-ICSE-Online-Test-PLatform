"use client";

import { useActionState, useState } from "react";
import { changePassword, regenerateRecoveryCode, updateProfile } from "@/app/actions/account";
import { buttonCls, inputCls } from "@/components/AuthShell";
import { PasswordField } from "@/components/PasswordField";
import { BOARD_OPTIONS } from "@/lib/boards";

const card = "rounded-2xl border border-border bg-card p-6";
const ok = "rounded-xl border border-good/30 bg-good/10 px-4 py-3 text-sm text-good";
const err = "mt-1 text-sm text-bad";

export function ProfileForm({ school, className, board }: { school: string; className: string; board: string }) {
  const [state, action, pending] = useActionState(updateProfile, undefined);
  return (
    <form action={action} className={`${card} space-y-4`}>
      <h2 className="text-lg font-bold">Edit profile</h2>
      {state?.message && <p role="status" className={ok}>{state.message}</p>}
      <div>
        <label htmlFor="school_name" className="mb-1.5 block text-sm font-medium">School</label>
        <input id="school_name" name="school_name" defaultValue={school} className={inputCls} />
        {state?.errors?.school_name && <p className={err}>{state.errors.school_name[0]}</p>}
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="class_name" className="mb-1.5 block text-sm font-medium">Class</label>
          <input id="class_name" name="class_name" defaultValue={className} placeholder="e.g. 9" className={inputCls} />
          {state?.errors?.class_name && <p className={err}>{state.errors.class_name[0]}</p>}
        </div>
        <div>
          <label htmlFor="board_name" className="mb-1.5 block text-sm font-medium">Board</label>
          <select id="board_name" name="board_name" defaultValue={board} className={inputCls}>
            <option value="" disabled>Choose…</option>
            {BOARD_OPTIONS.map((b) => <option key={b} value={b}>{b}</option>)}
          </select>
          {state?.errors?.board_name && <p className={err}>{state.errors.board_name[0]}</p>}
        </div>
      </div>
      <button disabled={pending} className={buttonCls}>{pending ? "Saving…" : "Save profile"}</button>
    </form>
  );
}

export function PasswordForm() {
  const [state, action, pending] = useActionState(changePassword, undefined);
  return (
    <form action={action} className={`${card} space-y-4`} key={state?.message}>
      <h2 className="text-lg font-bold">Change password</h2>
      {state?.message && <p role={state.errors ? "alert" : "status"} className={state.errors ? "text-sm text-bad" : ok}>{state.message}</p>}
      {/* Controlled password fields keep what was typed when the server rejects one of them. */}
      <PasswordField name="current" label="Current password" autoComplete="current-password" error={state?.errors?.current?.[0]} />
      <PasswordField name="next" label="New password" autoComplete="new-password" showStrength error={state?.errors?.next?.[0]} />
      <PasswordField name="confirm" label="Confirm new password" autoComplete="new-password" error={state?.errors?.confirm?.[0]} />
      <button disabled={pending} className={buttonCls}>{pending ? "Updating…" : "Change password"}</button>
    </form>
  );
}

export function RecoveryCard({ code }: { code: string | null }) {
  const [shown, setShown] = useState(false);
  const [state, action, pending] = useActionState(regenerateRecoveryCode, undefined);
  const current = state?.recoveryCode ?? code;
  return (
    <section className={card} aria-label="Recovery code">
      <h2 className="text-lg font-bold">Recovery code</h2>
      <p className="mt-1 text-sm text-muted">Needed to reset your password if you forget it. Keep it private.</p>
      <div className="mt-4 flex items-center justify-between rounded-xl border-2 border-dashed border-accent bg-accent/10 px-5 py-4">
        <span className="font-mono text-2xl font-bold tracking-[.25em]">{current ? (shown || state?.recoveryCode ? current : "••••••••") : "Not set"}</span>
        {current && !state?.recoveryCode && (
          <button type="button" onClick={() => setShown((s) => !s)} className="text-sm font-semibold text-brand">
            {shown ? "Hide" : "Show"}
          </button>
        )}
      </div>
      {state?.message && <p role="status" className={`${ok} mt-3`}>{state.message}</p>}
      <details className="mt-4">
        <summary className="cursor-pointer text-sm font-medium text-brand">Generate a new code</summary>
        <form action={action} className="mt-3 space-y-3">
          <p className="text-sm text-muted">The old code stops working immediately.</p>
          <input name="current" type="password" placeholder="Your password" autoComplete="current-password" className={inputCls} />
          {state?.errors?.current && <p className={err}>{state.errors.current[0]}</p>}
          <button disabled={pending} className="rounded-xl border border-border px-4 py-2.5 text-sm font-semibold transition hover:bg-background">
            {pending ? "Generating…" : "Generate new code"}
          </button>
        </form>
      </details>
    </section>
  );
}
