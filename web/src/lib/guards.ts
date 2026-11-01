import "server-only";
import { redirect } from "next/navigation";
import { getSession, type SessionUser } from "@/lib/session";

import { BOARD_OPTIONS } from "@/lib/boards";

export const BOARDS = BOARD_OPTIONS;

export function isAdmin(user: Pick<SessionUser, "role">) {
  return user.role === "admin";
}

function profileComplete(u: SessionUser) {
  return Boolean(u.school_name?.trim() && u.class_name?.trim() && u.board_name?.trim());
}

/** Any logged-in user. */
export async function requireUser(): Promise<SessionUser> {
  const user = await getSession();
  if (!user) redirect("/login");
  return user;
}

/** Students only. Admins go to their own area; incomplete profiles are sent to finish it first. */
export async function requireStudent(): Promise<SessionUser> {
  const user = await requireUser();
  if (isAdmin(user)) redirect("/admin");
  if (!profileComplete(user)) redirect("/profile?setup=1");
  return user;
}

/** Admins only. Every admin page AND every admin action must call this: hiding links is not security. */
export async function requireAdmin(): Promise<SessionUser> {
  const user = await requireUser();
  if (!isAdmin(user)) redirect("/dashboard");
  return user;
}
