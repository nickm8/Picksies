import { db } from "@repo/db";
import { lists, listMovies, movies } from "@repo/db/src/schema";
import { eq, and } from "drizzle-orm";
import { v4 as uuidv4 } from "uuid";
import { CreateListInput, UpdateListInput, UpdateMovieInListInput } from "./list.types";

/**
 * Service for managing watchlists
 */
export class ListService {
  /**
   * Create a new watchlist
   */
  async createList(data: CreateListInput) {
    const id = uuidv4();
    const now = new Date().toISOString();
    
    const [list] = await db.insert(lists).values({
      id,
      name: data.name,
      description: data.description || null,
      createdByName: data.createdByName || null,
      lastActivityAt: now,
    }).returning();
    
    return list;
  }
  
  /**
   * Get all watchlists
   */
  async getLists() {
    return db.query.lists.findMany({
      orderBy: (lists, { desc }) => [desc(lists.lastActivityAt)],
    });
  }
  
  /**
   * Get a watchlist by ID
   */
  async getListById(id: string) {
    return db.query.lists.findFirst({
      where: eq(lists.id, id),
    });
  }
  
  /**
   * Update a watchlist
   */
  async updateList(id: string, data: UpdateListInput) {
    const [updatedList] = await db
      .update(lists)
      .set({
        ...data,
        updatedAt: new Date().toISOString(),
        lastActivityAt: new Date().toISOString(),
      })
      .where(eq(lists.id, id))
      .returning();
    
    return updatedList;
  }
  
  /**
   * Delete a watchlist
   */
  async deleteList(id: string) {
    const [deletedList] = await db
      .delete(lists)
      .where(eq(lists.id, id))
      .returning();
    
    return deletedList;
  }
  
  /**
   * Get all movies in a watchlist
   */
  async getMoviesInList(listId: string) {
    return db.query.listMovies.findMany({
      where: eq(listMovies.listId, listId),
      with: {
        movie: true,
      },
      orderBy: (listMovies, { desc }) => [desc(listMovies.addedAt)],
    });
  }
  
  /**
   * Add a movie to a watchlist
   */
  async addMovieToList(listId: string, movieId: string, addedByName?: string) {
    const id = uuidv4();
    const now = new Date().toISOString();
    
    // Update list's lastActivityAt
    await db
      .update(lists)
      .set({
        lastActivityAt: now,
      })
      .where(eq(lists.id, listId));
    
    const [listMovie] = await db
      .insert(listMovies)
      .values({
        id,
        listId,
        movieId,
        addedByName: addedByName || null,
        addedAt: now,
      })
      .returning();
    
    return listMovie;
  }
  
  /**
   * Remove a movie from a watchlist
   */
  async removeMovieFromList(listId: string, movieId: string) {
    const now = new Date().toISOString();
    
    // Update list's lastActivityAt
    await db
      .update(lists)
      .set({
        lastActivityAt: now,
      })
      .where(eq(lists.id, listId));
    
    const [removedMovie] = await db
      .delete(listMovies)
      .where(
        and(
          eq(listMovies.listId, listId),
          eq(listMovies.movieId, movieId)
        )
      )
      .returning();
    
    return removedMovie;
  }
  
  /**
   * Update a movie in a watchlist (e.g., mark as watched)
   */
  async updateMovieInList(listId: string, movieId: string, data: UpdateMovieInListInput) {
    const now = new Date().toISOString();
    const updateData: any = { ...data, updatedAt: now };
    
    // If marking as watched, set the watchedAt timestamp
    if (data.watched === true) {
      updateData.watchedAt = now;
    } else if (data.watched === false) {
      updateData.watchedAt = null;
    }
    
    // Update list's lastActivityAt
    await db
      .update(lists)
      .set({
        lastActivityAt: now,
      })
      .where(eq(lists.id, listId));
    
    const [updatedMovie] = await db
      .update(listMovies)
      .set(updateData)
      .where(
        and(
          eq(listMovies.listId, listId),
          eq(listMovies.movieId, movieId)
        )
      )
      .returning();
    
    return updatedMovie;
  }
}
