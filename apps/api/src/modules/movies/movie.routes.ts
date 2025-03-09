import { Hono } from "hono";
import { zValidator } from "@hono/zod-validator";
import { MovieService } from "./movie.service";
import { createMovieSchema } from "./movie.types";

// Create a new Hono app for movie routes
export const movieRoutes = new Hono()
  .get("/", async (c) => {
    const movieService = new MovieService();
    const movies = await movieService.getMovies();
    return c.json({ movies });
  })
  
  .get("/:id", async (c) => {
    const id = c.req.param("id");
    const movieService = new MovieService();
    
    const movie = await movieService.getMovieById(id);
    if (!movie) {
      return c.json({ error: "Movie not found" }, 404);
    }
    
    return c.json({ movie });
  })
  
  .post("/", zValidator("json", createMovieSchema), async (c) => {
    const data = c.req.valid("json");
    const movieService = new MovieService();
    
    const movie = await movieService.createOrUpdateMovie(data);
    return c.json({ movie }, 201);
  })
  
  .delete("/:id", async (c) => {
    const id = c.req.param("id");
    const movieService = new MovieService();
    
    const movie = await movieService.deleteMovie(id);
    if (!movie) {
      return c.json({ error: "Movie not found" }, 404);
    }
    
    return c.json({ success: true });
  });
