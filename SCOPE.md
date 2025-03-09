# Movie Watchlist Application Scope

## Core Features

### Access & Authentication

- UUID-based shareable links with no traditional login required
- Optional display name for user attribution on suggestions/comments
- Backend validation of list access:
  ```python
  @app.get("/list/{list_id}")
  async def get_list(list_id: UUID = Depends(valid_list_id)):
      # List retrieval logic
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

| Component     | Technology              | Implementation Details        |
| ------------- | ----------------------- | ----------------------------- |
| API Framework | FastAPI                 | Pydantic validation models    |
| Database      | SQLite + SQLAlchemy 2.0 | Alembic migrations            |
| API Client    | httpx                   | Async Overseerr communication |
| Auth          | UUID4                   | Link-based access control     |

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
  - voteAverageGte/Lte: Quality filtering
  - watchRegion + watchProviders: Streaming availability filters

### API Flow

```
Frontend -> Backend -> Overseerr -> Backend -> Frontend
```

### Database Models

- **MovieList**: id (UUID), name, created_at
- **Movie**: id, title, year, poster_path, overview, tmdb_id, list_id, status, genre_ids, vote_average
- **User** (optional): id, name, list_id

## Deployment & Operations

- Dockerized single-container deployment
- Environment variables for configuration:
  - Overseerr API URL and credentials
  - Database settings
  - Application settings

## User Flow

1. User creates or accesses a watchlist via unique UUID link
2. User searches for movies using the integrated search with advanced filters
3. User adds movies to the "To Watch" list
4. After watching, user marks movies as watched, automatically moving them to "Watched" list
5. Watchlist refreshes automatically every 3 seconds to show updates from other users
6. User can share the watchlist link with others for collaborative management

## Enhancements from Technical Specification

- More detailed Overseerr API integration specifics
- Enhanced filtering capabilities using Overseerr's robust parameter set
- Optimistic UI updates for better user experience
- Structured validation patterns for backend API
- Clear specification of polling mechanism (3-second interval)
- Improved database schema with additional movie metadata fields
- Better defined user attribution system

