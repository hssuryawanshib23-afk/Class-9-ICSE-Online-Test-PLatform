"use client";

import Link from "next/link";
import { useActionState } from "react";
import { signup } from "@/app/actions/auth";
import { AuthShell, buttonCls, inputCls } from "@/components/AuthShell";

const FIELDS = [
  { name: "username", label: "Username", type: "text", auto: "username", required: true },
  { name: "phone_number", label: "Mobile number", type: "tel", auto: "tel-national", required: true },
  { name: "password", label: "Password", type: "password", auto: "new-password", required: true },
  { name: "school_name", label: "School (optional)", type: "text", auto: "organization", required: false },
] as const;

export default function SignupPage() {
  const [state, action, pending] = useActionState(signup, undefined);

  if (state?.recoveryCode) {
    return (
      <AuthShell title="You're in! 🎉" subtitle="Save this recovery code. It is the only way to reset your password.">
        <div className="rounded-2xl border-2 border-dashed border-accent bg-accent/10 p-6 text-center">
          <p className="font-mono text-3xl font-bold tracking-[.2em]">{state.recoveryCode}</p>
          <p className="mt-3 text-sm text-muted">Write it down or take a screenshot. We will not show it again.</p>
        </div>
        <Link href="/dashboard" className={`${buttonCls} mt-6 block text-center`}>I saved it, continue</Link>
      </AuthShell>
    );
  }

  return (
    <AuthShell title="Create your account" subtitle="It takes under a minute.">
      <form action={action} className="space-y-5" noValidate>
        {state?.message && (
          <p role="alert" className="rounded-xl border border-bad/30 bg-bad/10 px-4 py-3 text-sm text-bad">
            {state.message}
          </p>
        )}
        {FIELDS.map((f) => (
          <div key={f.name}>
            <label htmlFor={f.name} className="mb-1.5 block text-sm font-medium">{f.label}</label>
            <input id={f.name} name={f.name} type={f.type} autoComplete={f.auto} required={f.required} defaultValue={f.name === "password" ? undefined : state?.values?.[f.name]} className={inputCls} />
            {state?.errors?.[f.name] && <p className="mt-1 text-sm text-bad">{state.errors[f.name]![0]}</p>}
          </div>
        ))}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="class_name" className="mb-1.5 block text-sm font-medium">Class</label>
            <select id="class_name" name="class_name" defaultValue={state?.values?.class_name ?? "9"} className={inputCls}>
              <option value="9">9</option>
              <option value="10">10</option>
            </select>
          </div>
          <div>
            <label htmlFor="board_name" className="mb-1.5 block text-sm font-medium">Board</label>
            <select id="board_name" name="board_name" defaultValue={state?.values?.board_name ?? "ICSE"} className={inputCls}>
              <option value="ICSE">ICSE</option>
              <option value="CBSE">CBSE</option>
            </select>
          </div>
        </div>
        <button type="submit" disabled={pending} className={buttonCls}>
          {pending ? "Creating…" : "Create account"}
        </button>
        <p className="text-center text-sm text-muted">
          Already have an account? <Link href="/login" className="font-semibold text-brand">Log in</Link>
        </p>
      </form>
    </AuthShell>
  );
}
