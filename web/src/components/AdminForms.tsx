"use client";

import { useActionState } from "react";
import { deleteAdminTest, deleteStudent, resetStudentPassword } from "@/app/actions/admin";

const input = "w-full rounded-xl border border-border bg-card px-3 py-2.5 outline-none focus:border-bad focus:ring-4 focus:ring-bad/15";
const bad = "rounded-xl bg-bad px-4 py-2.5 text-sm font-semibold text-white transition hover:brightness-110 disabled:opacity-50";

export function DeleteTestForm({ id, name, attempts }: { id: number; name: string; attempts: number }) {
  const [state, action, pending] = useActionState(deleteAdminTest, undefined);
  return (
    <details className="rounded-xl border border-bad/30 p-4">
      <summary className="cursor-pointer text-sm font-semibold text-bad">Delete this test…</summary>
      <form action={action} className="mt-3 space-y-3">
        <input type="hidden" name="admin_test_id" value={id} />
        <p className="text-sm">
          This permanently deletes the test{attempts > 0 ? <> and <strong>{attempts} student result{attempts === 1 ? "" : "s"}</strong></> : ""}. Consider
          deactivating it instead. Type <strong>{name}</strong> to confirm.
        </p>
        <input name="confirm" autoComplete="off" className={input} aria-label="Type the test name to confirm" />
        {state?.message && <p role="alert" className="text-sm text-bad">{state.message}</p>}
        <button disabled={pending} className={bad}>{pending ? "Deleting…" : "Delete permanently"}</button>
      </form>
    </details>
  );
}

export function DeleteStudentForm({ id, username }: { id: number; username: string }) {
  const [state, action, pending] = useActionState(deleteStudent, undefined);
  return (
    <details className="rounded-xl border border-bad/30 p-4">
      <summary className="cursor-pointer text-sm font-semibold text-bad">Delete this student…</summary>
      <form action={action} className="mt-3 space-y-3">
        <input type="hidden" name="student_id" value={id} />
        <p className="text-sm">
          Permanently removes the account, all test attempts and all responses. This cannot be undone. Type <strong>{username}</strong> to confirm.
        </p>
        <input name="confirm" autoComplete="off" className={input} aria-label="Type the username to confirm" />
        {state?.message && <p role="alert" className="text-sm text-bad">{state.message}</p>}
        <button disabled={pending} className={bad}>{pending ? "Deleting…" : "Delete permanently"}</button>
      </form>
    </details>
  );
}

export function ResetPasswordForm({ id, username }: { id: number; username: string }) {
  const [state, action, pending] = useActionState(resetStudentPassword, undefined);
  return (
    <div className="rounded-xl border border-border p-4">
      <p className="text-sm font-semibold">Reset password</p>
      <p className="mt-1 text-sm text-muted">For students who lost their recovery code. Creates a temporary password for {username}.</p>
      {state?.tempPassword ? (
        <div className="mt-3 rounded-xl border-2 border-dashed border-accent bg-accent/10 p-4" role="status">
          <p className="text-sm">{state.message}</p>
          <p className="mt-2 font-mono text-2xl font-bold tracking-wider select-all">{state.tempPassword}</p>
          <p className="mt-2 text-xs text-muted">Shown once. It is not stored anywhere.</p>
        </div>
      ) : (
        <form action={action} className="mt-3">
          <input type="hidden" name="student_id" value={id} />
          {state?.message && <p role="alert" className="mb-2 text-sm text-bad">{state.message}</p>}
          <button disabled={pending} className="rounded-xl border border-border px-4 py-2.5 text-sm font-semibold transition hover:bg-background">
            {pending ? "Resetting…" : "Generate temporary password"}
          </button>
        </form>
      )}
    </div>
  );
}
