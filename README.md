# B(build)stack

A modern full-stack application template built with Turborepo, featuring a Hono + Bun API backend and Next.js frontend.
Easiest way to build a SaaS.


### API (Backend)
- [Bun](https://bun.sh/) 
- [Drizzle ORM](https://orm.drizzle.team/)
- [Supabase](https://supabase.com/)

### Web (Frontend)
- [Next.js](https://nextjs.org/)
- [Tailwind CSS](https://tailwindcss.com/) 
- [Shadcn/ui](https://ui.shadcn.com/) 
- [Clerk](https://clerk.com/) 

### Deployment
- [Vercel](https://vercel.com/)
- [Render](https://render.com/)

### Misc
- [Ngrok](https://ngrok.com/)


## 📦 Project Structure
```
├── apps/
│   ├── api/         # Bun API backend
│   └── web/         # Next.js frontend
└── packages/        # Shared packages, main DB
```

## 🛠️ Setup & Installation


1. **Install dependencies**

pnpm install

2. **Bun Setup**
You can install bun in a few ways, based on your OS.
https://bun.sh/docs/installation


```bash
curl -fsSL https://bun.sh/install | bash # for macOS, Linux, and WSL
```

```bash
npm install -g bun 
```

```bash
brew install oven-sh/bun/bun # for macOS and Linux
```

3. **Environment Setup**

Create .env files in both apps/api and apps/web:

For `apps/api/.env`:

```
DATABASE_URL=your_database_url
CLERK_SECRET_KEY=your_clerk_secret_key
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
CLERK_SIGNING_SECRET=your_clerk_webhook_secret
```

For `apps/web/.env`:

```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
CLERK_SECRET_KEY=your_clerk_secret_key
NEXT_PUBLIC_API_URL=your_api_url
```

To run migrations and push db schema locally create a `.env` file in `packages/db` and add your database url.

`packages/db/.env`
```
DATABASE_URL=your_database_url
```



1. **Supabase Setup (Any postgres DB will work)**
- Create a new project on [Supabase](https://supabase.com)
- Copy your database url to the .env file
- Run `pnpm db:push` to initialize the database and mess around.
- When ready, run `pnpm db:generate` to generate the schema. And then run `pnpm db:migrate` to apply the schema to the database.

1. **Clerk Setup**
- Create a new application on [Clerk](https://clerk.com)
- Copy your API keys to the .env file
- Configure your OAuth providers if needed

#### Webhooks
There is a webhook setup in clerk for the api to handle user creation and authentication. 
Use this to setup a sync between clerk and the user database. Further details can be found in the [api readme](apps/api/README.md).

## Development

Run the development server:

`turbo dev`

This will start both the API and web applications in development mode:
- API: http://localhost:3004
- Web: http://localhost:3000

## 📤 Deployment

### Web (Next.js) on Vercel

1. Connect your repository to [Vercel](https://vercel.com)
2. Select the web directory as your project root
3. Add your environment variables

### API (Bun) on Render

1. Create a new Web Service on [Render](https://render.com)
2. Connect your repository
3. Configure the service (If not using render.yaml):
   - Build Command:  pnpm install
   - Start Command: pnpm start
   - Root Directory: apps/api
4. Add your environment variables


##  Contributing
1. Create a new branch
2. Make your changes
3. Submit a pull request

