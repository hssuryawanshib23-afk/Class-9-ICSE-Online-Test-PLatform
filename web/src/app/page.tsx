import { redirect } from "next/navigation";
import { isAdmin } from "@/lib/guards";
import { getSession } from "@/lib/session";

// Reads the session on every request, so it cannot be prerendered.
export const instant = false;

export default async function Home() {
  const user = await getSession();
  redirect(!user ? "/login" : isAdmin(user) ? "/admin" : "/dashboard");
}
