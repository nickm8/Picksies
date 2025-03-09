// @ts-ignore - Bun's SQLite types aren't recognized by TypeScript
import { drizzle } from "drizzle-orm/bun-sqlite";
// @ts-ignore
import { migrate } from "drizzle-orm/bun-sqlite/migrator";
// @ts-ignore
import { Database } from "bun:sqlite";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

// Export all schema entities
export * from "./schema";

// Helper function to get directory path that works in both ESM and CommonJS
const getDirPath = () => {
  try {
    // For ESM context
    // @ts-ignore - import.meta is available in ESM but TypeScript doesn't recognize it in CommonJS
    if (typeof import.meta !== 'undefined' && import.meta.url) {
      // @ts-ignore
      return dirname(fileURLToPath(import.meta.url));
    }
  } catch (e) {
    // Fallback for CommonJS
    console.log("Using CommonJS path resolution");
  }
  
  // Default to current directory if all else fails
  return process.cwd();
};

// Get database path
const DB_PATH = process.env.DATABASE_URL || resolve(getDirPath(), "../sqlite.db");

// Create SQLite database connection
const sqlite = new Database(DB_PATH);
export const db = drizzle(sqlite);

// Function to run migrations
export const runMigrations = async () => {
  try {
    const migrationsPath = resolve(getDirPath(), "../migrations");
    console.log(`Running migrations from ${migrationsPath}`);
    console.log(`Using database at ${DB_PATH}`);
    
    await migrate(db, { 
      migrationsFolder: migrationsPath 
    });
    console.log("Migrations completed successfully.");
    return true;
  } catch (error) {
    console.error("Migration error:", error);
    return false;
  }
};
