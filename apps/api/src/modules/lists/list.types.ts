import { z } from "zod";

// Schema for creating a new list
export const createListSchema = z.object({
  name: z.string().min(1, "List name is required"),
  description: z.string().optional(),
  createdByName: z.string().optional(),
});

// Schema for updating an existing list
export const updateListSchema = z.object({
  name: z.string().min(1, "List name is required").optional(),
  description: z.string().optional(),
});

// Schema for list response
export const listResponseSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  description: z.string().nullable(),
  createdByName: z.string().nullable(),
  createdAt: z.string(),
  updatedAt: z.string(),
  lastActivityAt: z.string(),
});

// Schema for adding a movie to a list
export const addMovieToListSchema = z.object({
  movieId: z.string(),
  addedByName: z.string().optional(),
});

// Schema for updating a movie in a list
export const updateMovieInListSchema = z.object({
  watched: z.boolean().optional(),
});

// Types derived from schemas
export type CreateListInput = z.infer<typeof createListSchema>;
export type UpdateListInput = z.infer<typeof updateListSchema>;
export type ListResponse = z.infer<typeof listResponseSchema>;
export type AddMovieToListInput = z.infer<typeof addMovieToListSchema>;
export type UpdateMovieInListInput = z.infer<typeof updateMovieInListSchema>;
