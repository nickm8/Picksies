import { runMigrations } from "./index";

/**
 * Script to run database migrations
 * This can be used as a standalone script or imported and called from the API
 */
async function main() {
  try {
    const success = await runMigrations();
    // Check if migrations were successful
    if (success === true) {
      console.log("✅ Database migrations completed successfully");
      // Only exit if running as a script, not when imported
      if (typeof process !== 'undefined' && process.exit) {
        process.exit(0);
      }
    } else {
      console.error("❌ Migrations failed");
      if (typeof process !== 'undefined' && process.exit) {
        process.exit(1);
      }
    }
  } catch (error) {
    console.error("❌ Error running migrations:", error);
    if (typeof process !== 'undefined' && process.exit) {
      process.exit(1);
    }
  }
}

// Run as standalone script if called directly
// This works in CommonJS
if (typeof require !== 'undefined' && require.main === module) {
  main();
}

// This works in ESM with Bun
try {
  // We need to check if we're in an ESM context where import.meta is available
  // @ts-ignore - TypeScript doesn't recognize this pattern in CommonJS
  if (typeof process !== 'undefined') {
    // Need to use a different approach to avoid TypeScript errors
    // This code will only execute in ESM environments where import.meta exists
    const isBunEnv = process.versions && process.versions.bun;
    
    if (isBunEnv) {
      // In Bun environment, we can safely run the migrations
      main();
    }
  }
} catch (e) {
  // Ignore any errors in CommonJS context
  console.log("Not in ESM context, skipping auto-run");
}

export default main;
