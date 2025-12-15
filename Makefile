# =============================================================================
# Makefile for MBTQ Smart Financial Platform
# =============================================================================

.PHONY: help install install-dev test lint format clean run docker-build docker-up docker-down

# Default target
.DEFAULT_GOAL := help

# Python interpreter
PYTHON := python3
PIP := pip3

# Project directories
SRC_DIRS := services api config routes

# =============================================================================
# Help
# =============================================================================

help: ## Show this help message
	@echo "MBTQ Smart Financial Platform - Development Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

# =============================================================================
# Installation
# =============================================================================

install: ## Install production dependencies
	$(PIP) install -e .

install-dev: ## Install development dependencies
	$(PIP) install -r requirements-dev.txt

# =============================================================================
# Testing
# =============================================================================

test: ## Run all tests
	$(PYTHON) -m unittest discover tests -v

test-unit: ## Run unit tests only
	$(PYTHON) -m unittest discover tests -v -k "test_*"

test-coverage: ## Run tests with coverage report
	pytest --cov=$(SRC_DIRS) --cov-report=html --cov-report=term

test-api: ## Validate OpenAPI specification
	npx @apidevtools/swagger-cli validate api/specs/openapi.json

# =============================================================================
# Code Quality
# =============================================================================

lint: ## Run all linters
	@echo "Running Flake8..."
	flake8 $(SRC_DIRS)
	@echo "Running Pylint..."
	pylint $(SRC_DIRS) --exit-zero

format: ## Format code with Black
	black $(SRC_DIRS)

format-check: ## Check code formatting without changes
	black --check --diff $(SRC_DIRS)

# =============================================================================
# Security
# =============================================================================

security: ## Run security checks
	@echo "Running Bandit security scan..."
	bandit -r $(SRC_DIRS) -f json -o bandit-report.json || true
	@echo "Running Safety dependency check..."
	safety check || true

# =============================================================================
# Development Server
# =============================================================================

run: ## Run development server
	$(PYTHON) main.py

run-prod: ## Run production server with Gunicorn
	gunicorn --bind 0.0.0.0:5000 --workers 4 --threads 2 wsgi:app

# =============================================================================
# Docker
# =============================================================================

docker-build: ## Build Docker image
	docker build -t mbtq-platform:latest .

docker-up: ## Start all Docker services
	docker-compose up -d

docker-down: ## Stop all Docker services
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f web

docker-shell: ## Open shell in web container
	docker-compose exec web /bin/bash

# =============================================================================
# Database
# =============================================================================

db-migrate: ## Run database migrations
	$(PYTHON) scripts/migrate.py

db-seed: ## Seed database with sample data
	$(PYTHON) scripts/seed.py

db-reset: ## Reset database (WARNING: destroys data)
	$(PYTHON) scripts/reset_db.py

# =============================================================================
# Clean
# =============================================================================

clean: ## Remove generated files and caches
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	rm -rf dist/ build/ 2>/dev/null || true

clean-all: clean ## Remove all generated files including logs
	rm -rf logs/*.log

# =============================================================================
# Deployment
# =============================================================================

deploy-staging: ## Deploy to staging environment
	@echo "Deploying to staging..."
	# Add your staging deployment commands here

deploy-prod: ## Deploy to production environment
	@echo "Deploying to production..."
	# Add your production deployment commands here

# =============================================================================
# Continuous Integration
# =============================================================================

ci: format-check lint test security ## Run all CI checks

# =============================================================================
# Documentation
# =============================================================================

docs: ## Generate documentation
	cd docs && make html

docs-serve: ## Serve documentation locally
	cd docs/_build/html && python -m http.server 8000
