"use client";

import Link from "next/link";
import { useActionState } from "react";
import { login } from "@/app/actions/auth";
import { AuthShell, buttonCls, inputCls } from "@/components/AuthShell";

export default function LoginPage() {
  const [state, action, pending] = useActionState(login, undefined);

  return (
    <AuthShell title="Welcome back" subtitle="Log in to continue your practice.">
      <form action={action} className="space-y-5" noValidate>
        {state?.message && (
          <p role="alert" className="rounded-xl border border-bad/30 bg-bad/10 px-4 py-3 text-sm text-bad">
            {state.message}
          </p>
        )}
        <div>
          <label htmlFor="username" className="mb-1.5 block text-sm font-medium">Username</label>
          <input id="username" name="username" autoComplete="username" defaultValue={state?.values?.username} className={inputCls} />
          {state?.errors?.username && <p className="mt-1 text-sm text-bad">{state.errors.username[0]}</p>}
        </div>
        <div>
          <label htmlFor="password" className="mb-1.5 block text-sm font-medium">Password</label>
          <input id="password" name="password" type="password" autoComplete="current-password" className={inputCls} />
          {state?.errors?.password && <p className="mt-1 text-sm text-bad">{state.errors.password[0]}</p>}
        </div>
        <button type="submit" disabled={pending} className={buttonCls}>
          {pending ? "Logging in…" : "Log in"}
        </button>
        <p className="text-center text-sm text-muted">
          New here? <Link href="/signup" className="font-semibold text-brand">Create an account</Link>
        </p>
      </form>
    </AuthShell>
  );
}
