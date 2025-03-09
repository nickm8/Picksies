import { z } from "zod";

// Schema for search query
export const searchQuerySchema = z.object({
  query: z.string().min(1, "Search query is required"),
  page: z.string().optional().transform(val => val ? parseInt(val, 10) : 1),
});

// Schema for discover query
export const discoverQuerySchema = z.object({
  page: z.string().optional().transform(val => val ? parseInt(val, 10) : 1),
  genre: z.string().optional().transform(val => val ? parseInt(val, 10) : undefined),
  sortBy: z.string().optional(),
  primaryReleaseDateGte: z.string().optional(),
  primaryReleaseDateLte: z.string().optional(),
  voteAverageGte: z.string().optional().transform(val => val ? parseFloat(val) : undefined),
  voteAverageLte: z.string().optional().transform(val => val ? parseFloat(val) : undefined),
  language: z.string().optional(),
});

// Schema for movie ID parameter
export const movieIdSchema = z.object({
  id: z.string().transform(val => parseInt(val, 10)),
});

// Types derived from schemas
export type SearchQueryInput = z.infer<typeof searchQuerySchema>;
export type DiscoverQueryInput = z.infer<typeof discoverQuerySchema>;
export type MovieIdParam = z.infer<typeof movieIdSchema>;
