import { drizzle } from 'drizzle-orm/better-sqlite3';
import Database from 'better-sqlite3';
import * as schema from './schema';

// Create function to get client (useful for testing)
export function createClient(path: string) {
  const sqlite = new Database(path);
  return drizzle(sqlite, { schema });
}

// Default export using sqlite.db in project root
export const db = createClient(process.env.DATABASE_URL || 'sqlite.db');