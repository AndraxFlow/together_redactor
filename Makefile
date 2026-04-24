SHELL := /bin/bash

COMPOSE := docker compose
APP_SERVICE := app
DB_SERVICE := db
DB_USER := postgres
DB_NAME := together_redactor

.PHONY: help up down restart build logs ps app-shell db-shell migrate current history heads version table-status

help: ## Show available commands
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## ' Makefile | sed 's/:.*## / - /'

up: ## Start containers in background
	$(COMPOSE) up -d --build

down: ## Stop and remove containers
	$(COMPOSE) down

restart: ## Restart containers
	$(MAKE) down
	$(MAKE) up

build: ## Rebuild app image
	$(COMPOSE) build

logs: ## Follow compose logs
	$(COMPOSE) logs -f

ps: ## Show containers status
	$(COMPOSE) ps

app-shell: ## Open shell inside app container
	$(COMPOSE) exec $(APP_SERVICE) sh

test: ## Run tests
	$(COMPOSE) exec $(APP_SERVICE) pytest

db-shell: ## Open psql inside db container
	$(COMPOSE) exec $(DB_SERVICE) psql -U $(DB_USER) -d $(DB_NAME)


# new-migration: ## Create new Alembic migration 
#	$(COMPOSE) exec $(APP_SERVICE) alembic revision --autogenerate -m ""

migrate: ## Apply Alembic migrations to head
	$(COMPOSE) exec $(APP_SERVICE) alembic upgrade head

current: ## Show currently applied Alembic revision
	$(COMPOSE) exec $(APP_SERVICE) alembic current

history: ## Show Alembic migration history
	$(COMPOSE) exec $(APP_SERVICE) alembic history

heads: ## Show Alembic head revision
	$(COMPOSE) exec $(APP_SERVICE) alembic heads

version: ## Show alembic_version table content
	$(COMPOSE) exec $(DB_SERVICE) psql -U $(DB_USER) -d $(DB_NAME) -c "SELECT * FROM alembic_version;"

table-status: ## Show user tables in public schema
	$(COMPOSE) exec $(DB_SERVICE) psql -U $(DB_USER) -d $(DB_NAME) -c "\dt"
