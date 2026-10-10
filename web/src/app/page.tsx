import { redirect } from "next/navigation";
import { getSession } from "@/lib/session";

// Reads the session on every request, so it cannot be prerendered.
export const instant = false;

export default async function Home() {
  redirect((await getSession()) ? "/dashboard" : "/login");
}
