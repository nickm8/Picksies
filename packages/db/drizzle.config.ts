import { defineConfig } from "drizzle-kit";

export default defineConfig({
  schema: "./src/index.ts",
  dialect: "sqlite",
  driver: "better-sqlite3",
  dbCredentials: {
    url: "sqlite.db",
  },
});