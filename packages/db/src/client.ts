import { drizzle } from "drizzle-orm/bun-sqlite";
// @ts-ignore - Bun's SQLite types aren't recognized by TypeScript
import { Database } from "bun:sqlite";
import * as schema from './schema';
import { resolve } from "path";
import { fileURLToPath } from "url";

// Get the directory path for proper file resolution
const getDirPath = () => {
  try {
    // For ESM context
    // @ts-ignore - import.meta is available in ESM but TypeScript doesn't recognize it in CommonJS
    if (typeof import.meta !== 'undefined' && import.meta.url) {
      // @ts-ignore
      return fileURLToPath(new URL(".", import.meta.url));
    }
  } catch (e) {
    // For CommonJS context
    return process.cwd();
  }
  return process.cwd();
};

// Create function to get client (useful for testing)
export function createClient(path: string) {
  const dbPath = path.startsWith('/') ? path : resolve(getDirPath() || '.', '..', path);
  console.log(`Opening SQLite database at: ${dbPath}`);
  const sqlite = new Database(dbPath);
  return drizzle(sqlite, { schema });
}

// Default export using sqlite.db in project root
export const db = createClient(process.env.DATABASE_URL || 'sqlite.db');