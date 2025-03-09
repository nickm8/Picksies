import { Hono } from "hono";
import { cors } from "hono/cors";
import { logger } from "hono/logger";

// Import our routes
import { listRoutes } from "@/modules/lists/list.routes";
import { movieRoutes } from "@/modules/movies/movie.routes";
import { overseerrRoutes } from "@/modules/overseerr/overseerr.routes";

// Import database and migrations
import { db, runMigrations } from "@repo/db";

// Run migrations when the server starts
(async () => {
  try {
    console.log("Running database migrations...");
    const migrationSuccess = await runMigrations();
    if (migrationSuccess) {
      console.log("✅ Database migrations applied successfully");
    } else {
      console.error("⚠️ Database migrations failed, but server will continue");
    }
    console.log("Database connected successfully");
  } catch (error) {
    console.error("❌ Error during database initialization:", error);
    // Continue running the server even if migrations fail
  }
})();

const app = new Hono();

app.use("*", logger());

app.use(
  "*",
  cors({
    origin: ["http://localhost:3000"],
    allowMethods: ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allowHeaders: ["Content-Type", "Authorization"],
    exposeHeaders: ["Content-Length"],
    maxAge: 600,
    credentials: true,
  }),
);

app.get("/health", (c) => {
  return c.text("OK");
});

const routes = app
  .basePath("/api")
  .route("/lists", listRoutes)
  .route("/movies", movieRoutes)
  .route("/overseerr", overseerrRoutes);

export type AppType = typeof routes;

export default {
  port: 3004,
  fetch: app.fetch,
  idleTimeout: 30,
};
