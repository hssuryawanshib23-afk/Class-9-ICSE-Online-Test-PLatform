import { Pool, type QueryResultRow } from "pg";

const globalForPg = globalThis as unknown as { pgPool?: Pool };

function createPool() {
  const url = process.env.DATABASE_URL;
  if (!url) throw new Error("DATABASE_URL is not set");
  // Serverless: keep the pool tiny so we do not exhaust Neon's connection limit.
  return new Pool({ connectionString: url, max: 3, idleTimeoutMillis: 10_000 });
}

export function pool(): Pool {
  return (globalForPg.pgPool ??= createPool());
}

export async function query<T extends QueryResultRow = QueryResultRow>(
  text: string,
  params: unknown[] = [],
): Promise<T[]> {
  const res = await pool().query<T>(text, params);
  return res.rows;
}
