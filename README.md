# Movie Watchlist Application

A collaborative movie tracking app that lets you create, share, and manage watchlists with friends. Built on the webapp-starter template.

![Movie Watchlist App](https://placehold.co/300x100?text=Movie+Watchlist+App)

## Planned Features

- Create shareable watchlists with unique URLs
- Search and discover movies with advanced filtering options
- Organize movies in "To Watch" and "Watched" lists
- Real-time updates when collaborating with others
- Responsive poster grid layout with dark mode by default
- Overseerr API integration for comprehensive movie information

## Tech Stack

- **Frontend**: Next.js with TypeScript, Tailwind CSS, shadcn/ui
- **Backend**: Hono API with TypeScript
- **Database**: PostgreSQL with Drizzle ORM
- **State Management**: React Query for server state, Zustand for UI state
- **Deployment**: Docker containerization

## Getting Started

### Prerequisites

- Node.js 18+ and pnpm
- Overseerr API access

### Installation

1. Clone the repository:

2. Install dependencies:
   ```bash
   nvm install 18.19.1
   nvm use 18.19.1
   npm install -g pnpm
   pnpm install
   ```

3. Configure environment variables:

4. Set up the database:
   ```bash
   pnpm db:push
   ```

5. Start the development servers:
   ```bash
   pnpm dev
   ```

6. Open your browser and navigate to http://localhost:3000
