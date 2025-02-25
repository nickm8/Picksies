// Change from pg-specific types to SQLite types
import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core';
import { lifecycleDates } from './util/lifecycle-dates';

export const users = sqliteTable('users', {
  userId: text('user_id').primaryKey(),
  email: text('email').notNull(),
  ...lifecycleDates,
});

// Other tables similarly need to change from pgTable to sqliteTable