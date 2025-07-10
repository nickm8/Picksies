# Makefile
# Django Movie App - Docker Commands

.PHONY: help build up down restart logs shell migrate collectstatic superuser populate clean dev prod stop

# Default target
help:  ## Show this help message
	@echo "Django Movie App - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Fix permissions before starting
fix-permissions:  ## Fix file permissions for Docker
	@echo "🔧 Fixing file permissions..."
	mkdir -p logs media staticfiles static/dist
	chmod -R 777 logs/ media/ staticfiles/ migrations/ || true
	chmod +x docker-entrypoint.sh || true
	@echo "✅ Permissions fixed"

# Development Commands
build:  ## Build the Docker images
	make fix-permissions
	docker-compose build

up:  ## Start the development environment
	make fix-permissions
	docker-compose up -d

dev:  ## Start development environment and show logs
	make fix-permissions
	docker-compose up

down:  ## Stop all services
	docker-compose down

restart:  ## Restart all services
	docker-compose restart

stop:  ## Stop all services (alias for down)
	make down

logs:  ## Show logs from all services
	docker-compose logs -f

logs-web:  ## Show logs from web service only
	docker-compose logs -f web

shell:  ## Access Django shell in web container
	docker-compose exec web python manage.py shell

bash:  ## Access bash shell in web container
	docker-compose exec web bash

# Database Commands
migrate:  ## Run database migrations
	docker-compose exec web python manage.py migrate

makemigrations:  ## Create new migrations
	docker-compose exec web python manage.py makemigrations

superuser:  ## Create Django superuser
	docker-compose exec web python manage.py createsuperuser

dbshell:  ## Access database shell
	docker-compose exec web python manage.py dbshell

# Static Files
collectstatic:  ## Collect static files
	docker-compose exec web python manage.py collectstatic --noinput

# Frontend Commands
npm-install:  ## Install frontend dependencies
	docker-compose exec web npm install

npm-clean:  ## Clean and reinstall frontend dependencies
	docker-compose exec web bash -c "cd /app && rm -rf node_modules package-lock.json && npm install"

npm-fix:  ## Fix npm permission issues
	@echo "Fixing npm permissions..."
	docker-compose exec web bash -c "cd /app && npm install"
	@echo "✅ npm permissions fixed!"

npm-rebuild:  ## Rebuild node_modules from scratch
	docker-compose exec web bash -c "cd /app && rm -rf node_modules package-lock.json && npm cache clean --force && npm install"

npm-dev:  ## Start Vite dev server
	docker-compose exec web npm run dev

npm-build:  ## Build frontend for production
	docker-compose exec web npm run build

# Movie Database Population
populate:  ## Populate database with movies from TMDB (improved version)
	docker-compose exec web python manage.py create_movie_database --max-pages=100 --max-workers=2 --batch-size=3

populate-safe:  ## Populate database safely (sequential, SQLite-friendly)
	docker-compose exec web python manage.py populate_movies_safe --max-pages=50 --verbose

populate-full:  ## Full population with many movies (use with caution)
	docker-compose exec web python manage.py create_movie_database --max-pages=500 --max-workers=3 --batch-size=5

populate-bg:  ## Populate database in background (safe version)
	docker-compose exec -d web python manage.py populate_movies_safe --max-pages=100

test-tmdb:  ## Test TMDB API connectivity
	docker-compose exec web python manage.py test_tmdb_api

# Sample Data
create-sample:  ## Create sample movie night for demo
	docker-compose exec web python manage.py create_sample_movie_night

create-migration:  ## Create migration for new models
	docker-compose exec web python manage.py create_initial_migration

test-inertia:  ## Test inertia-django imports
	docker-compose exec web python manage.py test_inertia

# Testing
test:  ## Run tests
	docker-compose exec web python manage.py test

test-coverage:  ## Run tests with coverage
	docker-compose exec web coverage run --source='.' manage.py test
	docker-compose exec web coverage report

# Production Commands
prod-build:  ## Build production images
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

prod-up:  ## Start production environment
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

prod-down:  ## Stop production environment
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

prod-logs:  ## Show production logs
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

# Maintenance Commands
clean:  ## Clean up Docker resources
	docker-compose down -v
	docker system prune -f
	docker volume prune -f

backup-db:  ## Backup database
	docker-compose exec web python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 2 > backup.json

restore-db:  ## Restore database from backup
	docker-compose exec web python manage.py loaddata backup.json

# Quick Setup Commands
setup:  ## Complete setup (build, migrate, collect static)
	make build
	make up
	@echo "Waiting for services to start..."
	@sleep 10
	make migrate
	make collectstatic
	@echo ""
	@echo "🎬 Django Movie App is ready!"
	@echo "📱 Visit: http://localhost:8001"
	@echo "👨‍💼 Admin: http://localhost:8001/admin"
	@echo ""
	@echo "To create a superuser, run: make superuser"
	@echo "To test TMDB API, run: make test-tmdb"
	@echo "To populate with movies, run: make populate-safe"

quick-start: setup  ## Alias for setup

# Movie Night Commands
setup-movie-nights:  ## Setup movie nights (run after migrations)
	docker-compose exec web python manage.py setup_movie_nights

create-sample-night:  ## Create a sample movie night for testing
	docker-compose exec web python manage.py setup_movie_nights --create-sample

show-movie-nights:  ## Show existing movie nights
	docker-compose exec web python manage.py shell -c "from movie_app.models import MovieNight; print('Movie Nights:'); [print(f'- {n.title} (ID: {n.id})') for n in MovieNight.objects.all()]"

debug-movie-nights:  ## Debug movie night tokens and database
	docker-compose exec web python manage.py debug_movie_night

test-token:  ## Test a specific token (usage: make test-token TOKEN=your_token_here)
	docker-compose exec web python manage.py debug_movie_night --test-token $(TOKEN)

check-night:  ## Check specific movie night (usage: make check-night ID=uuid_here)
	docker-compose exec web python manage.py debug_movie_night --night-id $(ID)

test-uuid:  ## Test UUID comparison for debugging
	docker-compose exec web python manage.py test_uuid_comparison

test-request:  ## Test full movie night request (usage: make test-request TOKEN=token NIGHT_ID=uuid)
	docker-compose exec web python manage.py test_movie_night_request --token $(TOKEN) --night-id $(NIGHT_ID)

test-filter:  ## Test movie night filtering functionality
	docker-compose exec web python manage.py test_movie_night_filter

# Reset everything
reset:  ## Reset everything (clean + setup)
	make clean
	make setup
	make setup-movie-nights

# Status check
status:  ## Show status of all services
	docker-compose ps

# Environment info
env:  ## Show environment information
	@echo "🐳 Docker version:"
	@docker --version
	@echo "\n🐙 Docker Compose version:"
	@docker-compose --version
	@echo "\n📊 Service status:"
	@make status