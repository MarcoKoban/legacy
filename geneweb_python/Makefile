# Makefile for Geneweb Python TDD Development

# Variables
# Auto-detect a local virtualenv if present, otherwise fall back to the system
# interpreter. Users can still override PYTHON/PIP when invoking make.
DEFAULT_VENV := $(CURDIR)/.venv
ifneq (,$(wildcard $(DEFAULT_VENV)/bin/python))
    PYTHON ?= $(DEFAULT_VENV)/bin/python
else
    PYTHON ?= python3
endif
PIP ?= $(PYTHON) -m pip
PYTEST ?= $(PYTHON) -m pytest

.PHONY: help install test test-unit test-integration test-e2e test-fast test-full lint format type-check coverage clean dev-setup run-api run-api-dev run-api-prod test-api api-info

help:		## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev-setup:	## Setup development environment
	@echo "📦 Installing development dependencies..."
	$(PIP) install -e ".[dev]"
	@echo ""
	@echo "🔧 Setting up pre-commit hooks..."
	@$(PYTHON) scripts/setup_dev.py || (echo "⚠️  Pre-commit setup failed. Run manually: pre-commit install")

install:	## Install package in development mode
	$(PIP) install -e .

test:		## Run all tests
	$(PYTEST)
	@echo ""
	@echo "📊 Updating coverage badge in README..."
	@$(PYTHON) scripts/update_coverage_badge.py || true

test-fast:	## Run tests excluding slow E2E tests
	$(PYTEST) -m "not e2e and not slow"
	@echo ""
	@echo "📊 Updating coverage badge in README..."
	@$(PYTHON) scripts/update_coverage_badge.py || true

test-full:	## Run all tests including E2E
	$(PYTEST) -m "unit or integration or e2e"

test-unit:	## Run unit tests only
	$(PYTEST) -m unit

test-integration:	## Run integration tests only
	$(PYTEST) -m integration

test-e2e:	## Run end-to-end tests only
	$(PYTEST) -m e2e

test-tdd:	## Run TDD cycle tests
	$(PYTEST) -m tdd

test-watch:	## Run tests in watch mode
	pytest-watch

coverage:	## Generate coverage report
	$(PYTEST) --cov=src --cov-report=html --cov-report=term
	@echo ""
	@echo "📊 Updating coverage badge in README..."
	@$(PYTHON) scripts/update_coverage_badge.py || true

lint:		## Run linting
	flake8 src tests --max-line-length=88

format:		## Format code
	black src tests
	isort src tests

type-check:	## Run type checking
	mypy src

quality:	## Run all quality checks
	$(MAKE) format lint type-check

ci-test:	## Run tests for CI environment
	$(PYTEST) --cov=src --cov-report=xml --cov-report=term-missing

ci-quality:	## Run quality checks for CI
	flake8 src tests --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 src tests --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	black --check src tests
	isort --check-only src tests
	mypy src || true

clean:		## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# API Server Commands
run-api:	## Run API server in development mode (auto-reload)
	@echo "🚀 Starting Geneweb API in development mode..."
	$(PYTHON) -m uvicorn src.geneweb.api.main:app --reload --host 0.0.0.0 --port 8000

run-api-dev:	## Run API server in development mode with debug
	@echo "🐛 Starting Geneweb API in development mode with debug..."
	$(PYTHON) -m uvicorn src.geneweb.api.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug

run-api-prod:	## Run API server in production mode
	@echo "🏭 Starting Geneweb API in production mode..."
	$(PYTHON) -m uvicorn src.geneweb.api.main:app --host 0.0.0.0 --port 8000 --workers 4

run-api-test:	## Run API server on test port for development
	@echo "🧪 Starting Geneweb API on test port 8002..."
	$(PYTHON) run_server.py

test-api:	## Test API endpoints
	@echo "🧪 Testing API health endpoint..."
	@sleep 2
	@curl -s http://localhost:8000/health/ | python -m json.tool || echo "❌ API not reachable on port 8000"
	@echo ""
	@echo "📊 Testing API metrics endpoint..."
	@curl -s http://localhost:8000/metrics | head -5 || echo "❌ Metrics not reachable"

check-api:	## Quick API configuration check
	@echo "✅ Checking API configuration..."
	@$(PYTHON) -c "from src.geneweb.api.main import app; from src.geneweb.api.config import settings; print(f'✅ API: {settings.app_name} v{settings.app_version}'); print(f'🔧 Debug: {settings.debug}'); print(f'🌐 Host: {settings.host}:{settings.port}')"

api-info:	## Show API information and available endpoints
	@echo "📋 Geneweb API Information"
	@echo "=========================="
	@$(PYTHON) -c "from src.geneweb.api.config import settings; print(f'📊 Name: {settings.app_name}'); print(f'🔢 Version: {settings.app_version}'); print(f'🐛 Debug: {settings.debug}'); print(f'🌐 Default Host: {settings.host}:{settings.port}'); print(f'🔐 CORS Origins: {settings.security.cors_origins}'); print(f'📈 Monitoring: {settings.monitoring.enable_metrics}')"
	@echo ""
	@echo "🚀 Available API Commands:"
	@echo "  make run-api      - Start API in development mode (port 8000)"
	@echo "  make run-api-dev  - Start API with debug logging"
	@echo "  make run-api-test - Start API on test port (8002)"
	@echo "  make run-api-prod - Start API in production mode"
	@echo "  make test-api     - Test API endpoints"
	@echo "  make check-api    - Quick configuration check"
	@echo ""
	@echo "📚 Endpoints (when running):"
	@echo "  http://localhost:8000/health/  - Health check"
	@echo "  http://localhost:8000/metrics  - Prometheus metrics"
	@echo "  http://localhost:8000/docs     - API documentation (debug mode)"

# TDD Development Cycle
tdd-red:	## TDD: Write failing test
	@echo "🔴 RED: Write a failing test"
	$(PYTEST) --tb=short || true

tdd-green:	## TDD: Make test pass
	@echo "🟢 GREEN: Make the test pass"
	$(PYTEST) --tb=short

tdd-refactor:	## TDD: Refactor code
	@echo "🔵 REFACTOR: Improve code quality"
	$(MAKE) quality
	$(PYTEST)

# Development workflow
dev-cycle:	## Complete development cycle
	$(MAKE) tdd-red
	$(MAKE) tdd-green
	$(MAKE) tdd-refactor

dev-api:	## Complete API development workflow
	@echo "🔧 Starting API development workflow..."
	$(MAKE) check-api
	$(MAKE) test-fast
	$(MAKE) run-api
