import { Hono } from "hono";
import { zValidator } from "@hono/zod-validator";
import { OverseerrClient } from "./overseerr.client";
import { MovieService } from "../movies/movie.service";
import { 
  searchQuerySchema, 
  discoverQuerySchema,
  movieIdSchema
} from "./overseerr.types";

// Create a new Hono app for Overseerr routes
export const overseerrRoutes = new Hono()
  .get("/search", zValidator("query", searchQuerySchema), async (c) => {
    const { query, page } = c.req.valid("query");
    const overseerrClient = new OverseerrClient();
    
    try {
      const searchResults = await overseerrClient.searchMovies(query, page);
      return c.json(searchResults);
    } catch (error) {
      console.error("Error searching movies:", error);
      return c.json({ error: "Failed to search movies" }, 500);
    }
  })
  
  .get("/discover", zValidator("query", discoverQuerySchema), async (c) => {
    const params = c.req.valid("query");
    const overseerrClient = new OverseerrClient();
    
    try {
      const discoverResults = await overseerrClient.discoverMovies(params);
      return c.json(discoverResults);
    } catch (error) {
      console.error("Error discovering movies:", error);
      return c.json({ error: "Failed to discover movies" }, 500);
    }
  })
  
  .get("/movie/:id", zValidator("param", movieIdSchema), async (c) => {
    const { id } = c.req.valid("param");
    const overseerrClient = new OverseerrClient();
    const movieService = new MovieService();
    
    try {
      // Get movie details from Overseerr
      const movieDetails = await overseerrClient.getMovie(id);
      
      // Format movie data for our database
      const formattedMovie = overseerrClient.formatMovieData(movieDetails);
      
      // Save or update movie in our database
      await movieService.createOrUpdateMovie(formattedMovie);
      
      return c.json(movieDetails);
    } catch (error) {
      console.error(`Error fetching movie ${id}:`, error);
      return c.json({ error: "Failed to fetch movie details" }, 500);
    }
  })
  
  .get("/trending", async (c) => {
    const page = c.req.query("page") ? parseInt(c.req.query("page") || "1", 10) : 1;
    const timeWindow = (c.req.query("timeWindow") as "day" | "week" | undefined) ?? "week";
    const overseerrClient = new OverseerrClient();
    
    try {
      const trendingMovies = await overseerrClient.getTrendingMovies(page, timeWindow);
      return c.json(trendingMovies);
    } catch (error) {
      console.error("Error fetching trending movies:", error);
      return c.json({ error: "Failed to fetch trending movies" }, 500);
    }
  })
  
  .get("/popular", async (c) => {
    const page = c.req.query("page") ? parseInt(c.req.query("page") || "1", 10) : 1;
    const overseerrClient = new OverseerrClient();
    
    try {
      const popularMovies = await overseerrClient.getPopularMovies(page);
      return c.json(popularMovies);
    } catch (error) {
      console.error("Error fetching popular movies:", error);
      return c.json({ error: "Failed to fetch popular movies" }, 500);
    }
  });
