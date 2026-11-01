"use client";

import Link from "next/link";
import { useActionState } from "react";
import { resetPassword } from "@/app/actions/account";
import { AuthShell, buttonCls, inputCls } from "@/components/AuthShell";
import { PasswordField } from "@/components/PasswordField";

export default function ForgotPasswordPage() {
  const [state, action, pending] = useActionState(resetPassword, undefined);

  if (state?.recoveryCode) {
    return (
      <AuthShell title="Password reset 🎉" subtitle="Save your NEW recovery code. The old one no longer works.">
        <div className="rounded-2xl border-2 border-dashed border-accent bg-accent/10 p-6 text-center">
          <p className="font-mono text-3xl font-bold tracking-[.2em]">{state.recoveryCode}</p>
          <p className="mt-3 text-sm text-muted">Write it down or take a screenshot. We will not show it again.</p>
        </div>
        <Link href="/login" className={`${buttonCls} mt-6 block text-center`}>Back to login</Link>
      </AuthShell>
    );
  }

  return (
    <AuthShell title="Reset your password" subtitle="Enter your username and the 8-digit recovery code from signup.">
      <form action={action} className="space-y-5" noValidate>
        {state?.message && (
          <p role="alert" className="rounded-xl border border-bad/30 bg-bad/10 px-4 py-3 text-sm text-bad">{state.message}</p>
        )}
        <div>
          <label htmlFor="username" className="mb-1.5 block text-sm font-medium">Username</label>
          <input id="username" name="username" autoComplete="username" defaultValue={state?.values?.username} className={inputCls} />
          {state?.errors?.username && <p className="mt-1 text-sm text-bad">{state.errors.username[0]}</p>}
        </div>
        <div>
          <label htmlFor="code" className="mb-1.5 block text-sm font-medium">Recovery code</label>
          <input id="code" name="code" inputMode="numeric" maxLength={8} autoComplete="one-time-code" className={`${inputCls} font-mono tracking-widest`} />
          {state?.errors?.code && <p className="mt-1 text-sm text-bad">{state.errors.code[0]}</p>}
        </div>
        <PasswordField name="next" label="New password" autoComplete="new-password" showStrength error={state?.errors?.next?.[0]} />
        <PasswordField name="confirm" label="Confirm new password" autoComplete="new-password" error={state?.errors?.confirm?.[0]} />
        <button type="submit" disabled={pending} className={buttonCls}>{pending ? "Resetting…" : "Reset password"}</button>
        <p className="text-center text-sm text-muted">
          Lost your code? Ask your teacher to reset your password.
          <br />
          <Link href="/login" className="font-semibold text-brand">Back to login</Link>
        </p>
      </form>
    </AuthShell>
  );
}
