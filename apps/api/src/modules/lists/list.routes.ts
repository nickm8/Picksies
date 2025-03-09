import { Hono } from "hono";
import { zValidator } from "@hono/zod-validator";
import { ListService } from "./list.service";
import { 
  createListSchema, 
  updateListSchema, 
  addMovieToListSchema,
  updateMovieInListSchema
} from "./list.types";

// Create a new Hono app for list routes
export const listRoutes = new Hono()
  .get("/", async (c) => {
    const listService = new ListService();
    const lists = await listService.getLists();
    return c.json({ lists });
  })
  
  .get("/:id", async (c) => {
    const id = c.req.param("id");
    const listService = new ListService();
    
    const list = await listService.getListById(id);
    if (!list) {
      return c.json({ error: "List not found" }, 404);
    }
    
    return c.json({ list });
  })
  
  .post("/", zValidator("json", createListSchema), async (c) => {
    const data = c.req.valid("json");
    const listService = new ListService();
    
    const list = await listService.createList(data);
    return c.json({ list }, 201);
  })
  
  .put("/:id", zValidator("json", updateListSchema), async (c) => {
    const id = c.req.param("id");
    const data = c.req.valid("json");
    const listService = new ListService();
    
    const list = await listService.updateList(id, data);
    if (!list) {
      return c.json({ error: "List not found" }, 404);
    }
    
    return c.json({ list });
  })
  
  .delete("/:id", async (c) => {
    const id = c.req.param("id");
    const listService = new ListService();
    
    const list = await listService.deleteList(id);
    if (!list) {
      return c.json({ error: "List not found" }, 404);
    }
    
    return c.json({ success: true });
  })
  
  // Movie management within lists
  .get("/:id/movies", async (c) => {
    const id = c.req.param("id");
    const listService = new ListService();
    
    const list = await listService.getListById(id);
    if (!list) {
      return c.json({ error: "List not found" }, 404);
    }
    
    const moviesInList = await listService.getMoviesInList(id);
    return c.json({ movies: moviesInList });
  })
  
  .post("/:id/movies", zValidator("json", addMovieToListSchema), async (c) => {
    const id = c.req.param("id");
    const { movieId, addedByName } = c.req.valid("json");
    const listService = new ListService();
    
    const list = await listService.getListById(id);
    if (!list) {
      return c.json({ error: "List not found" }, 404);
    }
    
    const listMovie = await listService.addMovieToList(id, movieId, addedByName);
    return c.json({ listMovie }, 201);
  })
  
  .delete("/:id/movies/:movieId", async (c) => {
    const id = c.req.param("id");
    const movieId = c.req.param("movieId");
    const listService = new ListService();
    
    const list = await listService.getListById(id);
    if (!list) {
      return c.json({ error: "List not found" }, 404);
    }
    
    const removedMovie = await listService.removeMovieFromList(id, movieId);
    if (!removedMovie) {
      return c.json({ error: "Movie not found in list" }, 404);
    }
    
    return c.json({ success: true });
  })
  
  .patch("/:id/movies/:movieId", zValidator("json", updateMovieInListSchema), async (c) => {
    const id = c.req.param("id");
    const movieId = c.req.param("movieId");
    const data = c.req.valid("json");
    const listService = new ListService();
    
    const list = await listService.getListById(id);
    if (!list) {
      return c.json({ error: "List not found" }, 404);
    }
    
    const updatedMovie = await listService.updateMovieInList(id, movieId, data);
    if (!updatedMovie) {
      return c.json({ error: "Movie not found in list" }, 404);
    }
    
    return c.json({ listMovie: updatedMovie });
  });
