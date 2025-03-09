import { db } from "@repo/db";
import { movies } from "@repo/db/src/schema";
import { eq } from "drizzle-orm";
import { CreateMovieInput } from "./movie.types";

/**
 * Service for managing movies
 */
export class MovieService {
  /**
   * Create a new movie or update if it already exists
   */
  async createOrUpdateMovie(data: CreateMovieInput) {
    // Check if the movie already exists
    const existingMovie = await this.getMovieById(data.id);
    
    if (existingMovie) {
      // Update the existing movie
      const [updatedMovie] = await db
        .update(movies)
        .set({
          ...data,
          updatedAt: new Date().toISOString(),
        })
        .where(eq(movies.id, data.id))
        .returning();
      
      return updatedMovie;
    } else {
      // Create a new movie
      const [newMovie] = await db
        .insert(movies)
        .values({
          ...data,
        })
        .returning();
      
      return newMovie;
    }
  }
  
  /**
   * Get all movies
   */
  async getMovies() {
    return db.query.movies.findMany({
      orderBy: (movies, { desc }) => [desc(movies.createdAt)],
    });
  }
  
  /**
   * Get a movie by ID
   */
  async getMovieById(id: string) {
    return db.query.movies.findFirst({
      where: eq(movies.id, id),
    });
  }
  
  /**
   * Delete a movie
   */
  async deleteMovie(id: string) {
    const [deletedMovie] = await db
      .delete(movies)
      .where(eq(movies.id, id))
      .returning();
    
    return deletedMovie;
  }
}
