import fetch from "node-fetch";

/**
 * Overseerr API client for movie data
 */
export class OverseerrClient {
  private baseUrl: string;
  private apiKey: string;
  
  constructor() {
    // Get API key and URL from environment variables
    this.apiKey = process.env.OVERSEERR_API_KEY || "";
    this.baseUrl = process.env.OVERSEERR_API_URL || "http://localhost:5055/api/v1";
    
    if (!this.apiKey) {
      console.warn("Warning: OVERSEERR_API_KEY not set. Some API calls may fail.");
    }
  }
  
  /**
   * Helper method to make API requests
   */
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      "Content-Type": "application/json",
      ...(this.apiKey ? { "X-Api-Key": this.apiKey } : {}),
      ...options.headers,
    };
    
    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });
      
      if (!response.ok) {
        throw new Error(`Overseerr API error: ${response.status} ${response.statusText}`);
      }
      
      return await response.json() as T;
    } catch (error) {
      console.error("Overseerr API request failed:", error);
      throw error;
    }
  }
  
  /**
   * Search for movies
   */
  async searchMovies(query: string, page = 1) {
    return this.request<any>(`/search?query=${encodeURIComponent(query)}&page=${page}&language=en`);
  }
  
  /**
   * Discover movies with filters
   */
  async discoverMovies(params: {
    page?: number;
    language?: string;
    genre?: number;
    sortBy?: string;
    primaryReleaseDateGte?: string;
    primaryReleaseDateLte?: string;
    voteAverageGte?: number;
    voteAverageLte?: number;
  } = {}) {
    const queryParams = new URLSearchParams();
    
    // Add all params to query string
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        queryParams.append(key, value.toString());
      }
    });
    
    // Ensure we're filtering to movies only
    queryParams.append("mediaType", "movie");
    
    return this.request<any>(`/discover/movies?${queryParams.toString()}`);
  }
  
  /**
   * Get detailed movie info
   */
  async getMovie(id: number) {
    return this.request<any>(`/movie/${id}`);
  }
  
  /**
   * Get trending movies
   */
  async getTrendingMovies(page = 1, timeWindow: "day" | "week" = "week") {
    return this.request<any>(`/trending/movies?page=${page}&timeWindow=${timeWindow}`);
  }
  
  /**
   * Get popular movies
   */
  async getPopularMovies(page = 1) {
    return this.request<any>(`/discover/movies?page=${page}&sortBy=popularity.desc`);
  }
  
  /**
   * Format movie data for our database
   */
  formatMovieData(movie: any) {
    return {
      id: movie.id.toString(),
      title: movie.title,
      overview: movie.overview,
      posterPath: movie.posterPath,
      backdropPath: movie.backdropPath,
      releaseDate: movie.releaseDate,
      voteAverage: movie.voteAverage?.toString(),
      runtime: movie.runtime,
      externalMovieId: movie.id,
    };
  }
}
