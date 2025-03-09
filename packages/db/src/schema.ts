// SQLite types for our movie watchlist application
import { sqliteTable, text, integer, numeric } from 'drizzle-orm/sqlite-core';
import { relations } from 'drizzle-orm';
import { lifecycleDates } from './util/lifecycle-dates';

// Lists table with UUID as primary key (no user authentication)
export const lists = sqliteTable('lists', {
  id: text('id').primaryKey(), // UUID for the list
  name: text('name').notNull(),
  description: text('description'),
  lastActivityAt: text('last_activity_at').notNull().$defaultFn(() => new Date().toISOString()),
  createdByName: text('created_by_name'), // Optional display name for sharing context
  ...lifecycleDates,
});

// Movies table for storing movie metadata
export const movies = sqliteTable('movies', {
  id: text('id').primaryKey(), // Movie ID from Overseerr
  title: text('title').notNull(),
  overview: text('overview'),
  posterPath: text('poster_path'),
  backdropPath: text('backdrop_path'),
  releaseDate: text('release_date'),
  voteAverage: numeric('vote_average'),
  runtime: integer('runtime'),
  externalMovieId: integer('external_movie_id'), // TMDB ID
  ...lifecycleDates,
});

// Junction table for movies in lists with watched status
export const listMovies = sqliteTable('list_movies', {
  id: text('id').primaryKey(), // UUID for this relationship
  listId: text('list_id').notNull()
    .references(() => lists.id, { onDelete: 'cascade' }),
  movieId: text('movie_id').notNull()
    .references(() => movies.id, { onDelete: 'cascade' }),
  watched: integer('watched', { mode: 'boolean' }).default(false),
  addedAt: text('added_at').notNull().$defaultFn(() => new Date().toISOString()),
  watchedAt: text('watched_at'),
  addedByName: text('added_by_name'), // For attribution in shared lists
  ...lifecycleDates,
});

// Relations for better TypeScript type safety
export const listsRelations = relations(lists, ({ many }) => ({
  movies: many(listMovies),
}));

export const moviesRelations = relations(movies, ({ many }) => ({
  lists: many(listMovies),
}));

export const listMoviesRelations = relations(listMovies, ({ one }) => ({
  list: one(lists, {
    fields: [listMovies.listId],
    references: [lists.id],
  }),
  movie: one(movies, {
    fields: [listMovies.movieId],
    references: [movies.id],
  }),
}));