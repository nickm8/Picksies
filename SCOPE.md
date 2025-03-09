# Movie Watchlist Application Scope

## Core Features

### Access & Authentication

- UUID-based shareable links with no traditional login required
- Optional display name for user attribution on suggestions/comments
- Backend validation of list access:
  ```typescript
  app.get("/list/:listId", async (c) => {
    const listId = c.req.param('listId')
    if (!isValidUUID(listId)) {
      return c.json({ error: "Invalid list ID" }, 400)
    }
    // List retrieval logic
  })
  ```

### Watchlist Management

- Dual-list system ("To Watch" / "Watched")
- Automated list transitions when marking movies as watched
- New additions default to "To Watch" category
- Full CRUD operations for movie list management

### Search & Discovery

curl --location --globoff '{{overseer_url}}/api/v1/search?query=The%20Order&page=1' \
--header 'Accept: application/json'

```yaml
/discover/movies:
  get:
    summary: Discover movies
    description: Returns a list of movies in a JSON object.
    tags:
      - search
    parameters:
      - in: query
        name: page
        schema:
          type: number
          example: 1
        default: 1
      - in: query
        name: language
        schema:
          type: string
          example: en
      - in: query
        name: genre
        schema:
          type: string
          example: 18
      - in: query
        name: studio
        schema:
          type: number
          example: 1
      - in: query
        name: keywords
        schema:
          type: string
          example: 1,2
      - in: query
        name: sortBy
        schema:
          type: string
          example: popularity.desc
      - in: query
        name: primaryReleaseDateGte
        schema:
          type: string
          example: 2022-01-01
      - in: query
        name: primaryReleaseDateLte
        schema:
          type: string
          example: 2023-01-01
      - in: query
        name: withRuntimeGte
        schema:
          type: number
          example: 60
      - in: query
        name: withRuntimeLte
        schema:
          type: number
          example: 120
      - in: query
        name: voteAverageGte
        schema:
          type: number
          example: 7
      - in: query
        name: voteAverageLte
        schema:
          type: number
          example: 10
      - in: query
        name: voteCountGte
        schema:
          type: number
          example: 7
      - in: query
        name: voteCountLte
        schema:
          type: number
          example: 10
      - in: query
        name: watchRegion
        schema:
          type: string
          example: US
      - in: query
        name: watchProviders
        schema:
          type: string
          example: 8|9
    responses:
      "200":
        description: Results
        content:
          application/json:
            schema:
              type: object
              properties:
                page:
                  type: number
                  example: 1
                totalPages:
                  type: number
                  example: 20
                totalResults:
                  type: number
                  example: 200
                results:
                  type: array
                  items:
                    $ref: "#/components/schemas/MovieResult"
```

- Comprehensive Overseerr API integration using `/discover/movies` endpoint
- Multi-filter search capabilities with the following parameters:
  ```tsx
  const filters = {
    genre: "action",
    year: "2020-2024",
    rating: "7+",
  };
  ```
- Advanced filtering options including:
  - Genre filtering
  - Release date ranges (primaryReleaseDateGte/Lte)
  - Runtime ranges (withRuntimeGte/Lte)
  - Rating thresholds (voteAverageGte/Lte)
  - Streaming availability (watchRegion, watchProviders)

### UI & Real-time Updates

- Poster-heavy visual design with clean list views
- Dark mode default theme
- Responsive grid layout for all device sizes
- Real-time updates via polling (3-second interval)
- Optimistic UI updates for immediate feedback

## Technical Architecture

### Backend Stack

| Component     | Technology        | Implementation Details                   |
| ------------- | ----------------- | ---------------------------------------- |
| API Framework | Hono              | Type-safe API development                |
| Database      | SQLite + Drizzle  | Lightweight ORM with TypeScript support  |
| API Client    | fetch             | Native fetch for Overseerr communication |
| Auth          | UUID4             | Link-based access control                |

### Frontend Stack

- **Core Framework**: React 18 with TypeScript, built using Vite
- **State Management**:
  - Zustand for global application state
  - React Query for API data caching and fetching:
  ```tsx
  const { data } = useQuery({
    queryKey: ["movies", listId],
    queryFn: fetchMovies,
    refetchInterval: 3000, // 3-second polling interval
  });
  ```
- **Styling**: Tailwind CSS with shadcn/ui components for accessibility and consistent design
- **Data Visualization**: Poster-grid layout with responsive design

## API Integration

### Overseerr Integration

- Utilizing the following Overseerr endpoints:
  - `/discover/movies` - Main discovery endpoint with filtering
  - Movie search for quick title lookup
- Key parameters to implement from the Overseerr API:
  - genre: Filter by genre ID
  - primaryReleaseDateGte/Lte: Date range filtering
  - withRuntimeGte/Lte: Movie length filtering
  - voteAverageGte/Lte: Rating filtering
  - watchRegion/watchProviders: Availability filtering

## Data Model

### Movie Entity

```typescript
interface Movie {
  id: number;             // Primary key
  tmdbId: number;         // TMDB ID for the movie
  title: string;          // Movie title
  posterPath: string;     // Relative path to poster image
  releaseDate: string;    // ISO date format
  overview: string;       // Movie description
  runtime: number;        // Movie runtime in minutes
  voteAverage: number;    // Rating from 0-10
  genres: number[];       // Array of genre IDs
  listId: string;         // UUID of the list this movie belongs to
  status: "toWatch" | "watched"; // Current status
  addedAt: string;        // ISO date of when movie was added
  watchedAt: string | null; // ISO date of when marked as watched (if applicable)
  addedBy: string | null; // Optional user name who added the movie
}
```

### List Entity

```typescript
interface List {
  id: string;              // UUID for the list
  name: string;            // Custom list name
  createdAt: string;       // ISO date
  lastUpdatedAt: string;   // ISO date of last list modification
  movies: Movie[];         // Movies in this list
}
```

## API Endpoints

### List Management

```typescript
app.get("/lists/:listId", async (c) => { /* ... */ })
app.post("/lists", async (c) => { /* ... */ })
app.delete("/lists/:listId", async (c) => { /* ... */ })
```

### Movie Management

```typescript
app.get("/lists/:listId/movies", async (c) => { /* ... */ })
app.post("/lists/:listId/movies", async (c) => { /* ... */ })
app.patch("/lists/:listId/movies/:movieId", async (c) => { /* ... */ })
app.delete("/lists/:listId/movies/:movieId", async (c) => { /* ... */ })
```

### Movie Search

```typescript
app.get("/search", async (c) => { /* ... */ })
app.get("/discover", async (c) => { /* ... */ })
```

## Future Enhancements

- Social sharing features for favorite movies
- Comments and discussion threads
- Notifications for new additions to shared lists
- More advanced filtering options
- Improved database schema with additional movie metadata fields
- Better defined user attribution system
