import { z } from "zod";

// Schema for creating a new movie
export const createMovieSchema = z.object({
  id: z.string(),
  title: z.string().min(1, "Movie title is required"),
  overview: z.string().optional(),
  posterPath: z.string().optional(),
  backdropPath: z.string().optional(),
  releaseDate: z.string().optional(),
  voteAverage: z.string().optional(),
  runtime: z.number().optional(),
  externalMovieId: z.number().optional(),
});

// Schema for movie response
export const movieResponseSchema = z.object({
  id: z.string(),
  title: z.string(),
  overview: z.string().nullable(),
  posterPath: z.string().nullable(),
  backdropPath: z.string().nullable(),
  releaseDate: z.string().nullable(),
  voteAverage: z.string().nullable(),
  runtime: z.number().nullable(),
  externalMovieId: z.number().nullable(),
  createdAt: z.string(),
  updatedAt: z.string().nullable(),
});

// Types derived from schemas
export type CreateMovieInput = z.infer<typeof createMovieSchema>;
export type MovieResponse = z.infer<typeof movieResponseSchema>;
