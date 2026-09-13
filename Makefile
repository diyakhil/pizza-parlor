# Dev shortcuts. Recipes cd into backend/src because the app uses bare
# imports (`from dtos.user import ...`), so src has to be the working dir.

SRC     := backend/src
ALEMBIC := -c $(SRC)/db/alembic.ini
PORT    ?= 8000

.DEFAULT_GOAL := help
.PHONY: help dev worker redis-start redis-stop migrate revision seed

help: ## Show available targets
	@grep -E '^[a-z][a-z-]*:.*?## ' $(MAKEFILE_LIST) \
		| awk -F':.*?## ' '{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

dev: ## Run the FastAPI app with autoreload (override with PORT=8001)
	cd $(SRC) && uvicorn main:app --reload --port $(PORT)

worker: ## Run the Celery worker (needs redis-start)
	cd $(SRC) && celery -A proj worker -l INFO

redis-start: ## Start Redis in the background
	brew services start redis

redis-stop: ## Stop Redis
	brew services stop redis

migrate: ## Apply migrations up to head
	alembic $(ALEMBIC) upgrade head

revision: ## Autogenerate a migration: make revision m="your message"
	@test -n "$(m)" || { echo 'usage: make revision m="your message"'; exit 1; }
	alembic $(ALEMBIC) revision --autogenerate -m "$(m)"

seed: ## Run the seed script (run migrate first)
	cd $(SRC) && python -m db.seed
