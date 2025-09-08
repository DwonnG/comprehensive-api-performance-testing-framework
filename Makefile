# Comprehensive API Performance Testing Framework Makefile

.PHONY: help install test smoke integration performance clean docker-build docker-test format lint type-check security coverage docs

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3.11
PIP := pip
PYTEST := pytest
TOX := tox
DOCKER := docker
DOCKER_COMPOSE := docker-compose

# Help target
help: ## Show this help message
	@echo "Comprehensive API Performance Testing Framework"
	@echo "=============================================="
	@echo ""
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Installation targets
install: ## Install dependencies
	$(PIP) install -r requirements.txt

install-dev: ## Install development dependencies
	$(PIP) install -r requirements-dev.txt

install-all: install install-dev ## Install all dependencies

# Testing targets
test: ## Run all tests
	$(TOX) -e pytest

smoke: ## Run smoke tests
	$(TOX) -e smoke_test

integration: ## Run integration tests
	PYTEST_TAG="integration" $(TOX) -e test_tag

performance: ## Run performance tests
	$(TOX) -e performance_test

users: ## Run user-related tests
	PYTEST_TAG="users" $(TOX) -e test_tag

auth: ## Run authentication tests
	PYTEST_TAG="authentication" $(TOX) -e test_tag

health: ## Run health check tests
	PYTEST_TAG="health_check" $(TOX) -e test_tag

# Quality assurance targets
format: ## Format code with black and isort
	black tests/
	isort tests/

lint: ## Run linting with flake8
	flake8 tests/ --max-line-length=100 --extend-ignore=E203,W503

type-check: ## Run type checking with mypy
	$(TOX) -e typecheck

security: ## Run security checks
	safety check
	bandit -r tests/

coverage: ## Run tests with coverage
	$(TOX) -e coverage

quality: format lint type-check security ## Run all quality checks

# Docker targets
docker-build: ## Build Docker images
	$(DOCKER) build -t api-testing-framework:latest .
	$(DOCKER) build -t api-testing-framework:dev --target development .
	$(DOCKER) build -t api-testing-framework:performance --target performance .

docker-test: ## Run tests in Docker
	$(DOCKER_COMPOSE) up --build smoke-tests integration-tests

docker-performance: ## Run performance tests in Docker
	$(DOCKER_COMPOSE) up --build performance-tests

docker-dev: ## Start development environment
	$(DOCKER_COMPOSE) up --build api-tests-dev

docker-reports: ## Start test report server
	$(DOCKER_COMPOSE) up -d report-server
	@echo "Test reports available at: http://localhost:8080"

docker-clean: ## Clean Docker resources
	$(DOCKER_COMPOSE) down -v
	$(DOCKER) system prune -f

# Environment targets
env-dev: ## Set up development environment
	@echo "Setting up development environment..."
	$(PYTHON) -m venv .venv
	@echo "Activate with: source .venv/bin/activate"

env-staging: ## Run tests against staging environment
	ENVIRONMENT=staging $(MAKE) smoke

env-production: ## Run health checks against production
	ENVIRONMENT=production $(PYTEST) tests/end_to_end/test_health_check.py -v

# Reporting targets
reports: ## Generate all test reports
	mkdir -p reports
	$(PYTEST) tests/end_to_end/ --html=reports/end-to-end-report.html --self-contained-html --junitxml=reports/junit.xml -v
	$(PYTEST) tests/performance/ --html=reports/performance-report.html --self-contained-html -v

reports-open: reports ## Open test reports in browser
	@if command -v open >/dev/null 2>&1; then \
		open reports/end-to-end-report.html; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open reports/end-to-end-report.html; \
	else \
		echo "Reports generated in reports/ directory"; \
	fi

# Performance analysis targets
breaking-point: ## Find API breaking points
	$(PYTHON) tests/performance/test_breaking_point.py

load-test: ## Run extended load testing
	$(PYTEST) tests/performance/test_breaking_point.py::test_comprehensive_breaking_point_analysis -v -s

benchmark: ## Run benchmark tests
	@echo "Running benchmark tests..."
	$(PYTHON) -c "import asyncio; from tests.performance.test_breaking_point import BreakingPointTester; asyncio.run(BreakingPointTester().run_comprehensive_breaking_point_analysis())"

# Cleanup targets
clean: ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .tox/
	rm -rf reports/
	rm -rf .coverage
	rm -rf htmlcov/

clean-all: clean docker-clean ## Clean everything including Docker resources

# Documentation targets
docs: ## Generate documentation
	@echo "Generating documentation..."
	mkdir -p docs/generated
	$(PYTHON) -c "
import json
import os
from tests.utilities.environment_config import EnvironmentConfig
config = EnvironmentConfig()
with open('docs/generated/config.json', 'w') as f:
    json.dump(config.ENVIRONMENTS, f, indent=2)
print('Configuration documentation generated')
"

# Continuous Integration targets
ci-setup: install-all ## Set up CI environment
	@echo "CI environment setup complete"

ci-test: quality test ## Run full CI test suite

ci-performance: performance ## Run CI performance tests

# Development workflow targets
dev-setup: env-dev install-all ## Complete development setup
	@echo "Development environment ready!"
	@echo "Run 'source .venv/bin/activate' to activate the virtual environment"

dev-test: ## Quick development test
	$(PYTEST) tests/end_to_end/ -m smoke -v

dev-watch: ## Watch for changes and run tests
	@echo "Watching for changes... (Ctrl+C to stop)"
	@while true; do \
		$(MAKE) dev-test; \
		echo "Waiting for changes..."; \
		sleep 5; \
	done

# Deployment targets
deploy-check: ## Check deployment readiness
	@echo "Checking deployment readiness..."
	$(MAKE) quality
	$(MAKE) test
	$(MAKE) security
	@echo "✅ Deployment checks passed"

# Utility targets
version: ## Show version information
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Pip: $(shell $(PIP) --version)"
	@echo "Pytest: $(shell $(PYTEST) --version)"
	@echo "Docker: $(shell $(DOCKER) --version)"

status: ## Show project status
	@echo "Project Status:"
	@echo "==============="
	@echo "Tests: $(shell find tests -name '*.py' | wc -l) files"
	@echo "Reports: $(shell ls -la reports/ 2>/dev/null | wc -l || echo 0) files"
	@echo "Docker images: $(shell $(DOCKER) images api-testing-framework --format 'table' | wc -l) images"

# Quick start target
quick-start: install smoke ## Quick start - install and run smoke tests
	@echo "🚀 Quick start completed successfully!"
	@echo "Next steps:"
	@echo "  make test          # Run full test suite"
	@echo "  make performance   # Run performance tests"
	@echo "  make reports-open  # View test reports"
