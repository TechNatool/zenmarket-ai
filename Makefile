.PHONY: help setup fmt lint type test cov audit docs build clean precommit install-dev compile-deps sync-deps

# Default target
.DEFAULT_GOAL := help

# Python and pip
PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
BLACK := $(PYTHON) -m black
ISORT := $(PYTHON) -m isort
RUFF := $(PYTHON) -m ruff
MYPY := $(PYTHON) -m mypy
BANDIT := $(PYTHON) -m bandit
PIP_AUDIT := $(PYTHON) -m pip_audit
INTERROGATE := $(PYTHON) -m interrogate
MKDOCS := $(PYTHON) -m mkdocs
PIP_COMPILE := $(PYTHON) -m piptools compile

# Directories
SRC_DIR := src
TEST_DIR := tests
DOCS_DIR := docs
REPORTS_DIR := reports
COVERAGE_DIR := htmlcov

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)ZenMarket AI - Development Makefile$(NC)"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Quick start:$(NC)"
	@echo "  make setup          # Install all dependencies"
	@echo "  make precommit      # Run all pre-commit checks"
	@echo "  make test           # Run tests"
	@echo "  make docs           # Build documentation"

setup: ## Install all dependencies (dev + prod)
	@echo "$(BLUE)Installing dependencies...$(NC)"
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -e ".[dev]"
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

install-dev: setup ## Alias for setup
	@echo "$(GREEN)✓ Development environment ready$(NC)"

compile-deps: ## Compile requirements files with pip-tools
	@echo "$(BLUE)Compiling requirements...$(NC)"
	$(PIP_COMPILE) --upgrade --resolver=backtracking -o requirements.txt requirements.in
	$(PIP_COMPILE) --upgrade --resolver=backtracking -o requirements-dev.txt requirements-dev.in
	@echo "$(GREEN)✓ Requirements compiled$(NC)"

sync-deps: ## Sync environment with compiled requirements
	@echo "$(BLUE)Syncing dependencies...$(NC)"
	$(PYTHON) -m piptools sync requirements-dev.txt
	@echo "$(GREEN)✓ Dependencies synced$(NC)"

fmt: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	$(BLACK) $(SRC_DIR) $(TEST_DIR)
	$(ISORT) $(SRC_DIR) $(TEST_DIR)
	@echo "$(GREEN)✓ Code formatted$(NC)"

lint: ## Lint code with ruff
	@echo "$(BLUE)Linting code...$(NC)"
	$(RUFF) check $(SRC_DIR) $(TEST_DIR)
	@echo "$(GREEN)✓ Linting passed$(NC)"

lint-fix: ## Lint and auto-fix issues with ruff
	@echo "$(BLUE)Linting and fixing code...$(NC)"
	$(RUFF) check --fix $(SRC_DIR) $(TEST_DIR)
	@echo "$(GREEN)✓ Linting with auto-fix completed$(NC)"

type: ## Type check with mypy
	@echo "$(BLUE)Type checking...$(NC)"
	$(MYPY) $(SRC_DIR)
	@echo "$(GREEN)✓ Type checking passed$(NC)"

test: ## Run tests with pytest
	@echo "$(BLUE)Running tests...$(NC)"
	$(PYTEST)
	@echo "$(GREEN)✓ Tests passed$(NC)"

test-fast: ## Run tests in parallel (faster)
	@echo "$(BLUE)Running tests in parallel...$(NC)"
	$(PYTEST) -n auto
	@echo "$(GREEN)✓ Tests passed$(NC)"

test-unit: ## Run only unit tests
	@echo "$(BLUE)Running unit tests...$(NC)"
	$(PYTEST) -m unit
	@echo "$(GREEN)✓ Unit tests passed$(NC)"

test-integration: ## Run only integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	$(PYTEST) -m integration
	@echo "$(GREEN)✓ Integration tests passed$(NC)"

cov: ## Generate coverage report
	@echo "$(BLUE)Generating coverage report...$(NC)"
	$(PYTEST) --cov=$(SRC_DIR) --cov-report=html --cov-report=term --cov-report=xml
	@echo "$(GREEN)✓ Coverage report generated in $(COVERAGE_DIR)/$(NC)"
	@echo "Open $(COVERAGE_DIR)/index.html in your browser to view the report"

audit: ## Run security audits (bandit + pip-audit)
	@echo "$(BLUE)Running security audits...$(NC)"
	@echo "$(YELLOW)→ Running bandit...$(NC)"
	$(BANDIT) -r $(SRC_DIR) -f screen
	@echo "$(YELLOW)→ Running pip-audit...$(NC)"
	$(PIP_AUDIT) --require-hashes --disable-pip
	@echo "$(GREEN)✓ Security audits completed$(NC)"

audit-bandit: ## Run bandit security scan
	@echo "$(BLUE)Running bandit...$(NC)"
	$(BANDIT) -r $(SRC_DIR) -f screen
	@echo "$(GREEN)✓ Bandit scan completed$(NC)"

audit-pip: ## Run pip-audit for CVE scanning
	@echo "$(BLUE)Running pip-audit...$(NC)"
	$(PIP_AUDIT)
	@echo "$(GREEN)✓ Pip-audit completed$(NC)"

docstrings: ## Check docstring coverage with interrogate
	@echo "$(BLUE)Checking docstring coverage...$(NC)"
	$(INTERROGATE) $(SRC_DIR) -vv
	@echo "$(GREEN)✓ Docstring check completed$(NC)"

docs: ## Build documentation with mkdocs
	@echo "$(BLUE)Building documentation...$(NC)"
	$(MKDOCS) build --strict
	@echo "$(GREEN)✓ Documentation built in docs/site/$(NC)"

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation...$(NC)"
	$(MKDOCS) serve

docs-deploy: ## Deploy documentation to GitHub Pages
	@echo "$(BLUE)Deploying documentation...$(NC)"
	$(MKDOCS) gh-deploy --force
	@echo "$(GREEN)✓ Documentation deployed$(NC)"

precommit: fmt lint type docstrings test ## Run all pre-commit checks
	@echo "$(GREEN)✓✓✓ All pre-commit checks passed ✓✓✓$(NC)"

check: precommit ## Alias for precommit

ci: lint type test audit docstrings ## Run all CI checks (no formatting)
	@echo "$(GREEN)✓✓✓ All CI checks passed ✓✓✓$(NC)"

build: clean ## Build distribution packages
	@echo "$(BLUE)Building distribution packages...$(NC)"
	$(PYTHON) -m build
	@echo "$(GREEN)✓ Build completed in dist/$(NC)"

clean: ## Clean build artifacts and caches
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	rm -rf build/ dist/ *.egg-info/
	rm -rf $(COVERAGE_DIR)/ .coverage coverage.xml
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/
	rm -rf docs/site/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.egg" -delete
	@echo "$(GREEN)✓ Cleanup completed$(NC)"

clean-reports: ## Clean test and backtest reports
	@echo "$(BLUE)Cleaning reports...$(NC)"
	rm -rf $(REPORTS_DIR)/
	@echo "$(GREEN)✓ Reports cleaned$(NC)"

install-hooks: ## Install pre-commit hooks
	@echo "$(BLUE)Installing pre-commit hooks...$(NC)"
	pre-commit install
	@echo "$(GREEN)✓ Pre-commit hooks installed$(NC)"

run-hooks: ## Run pre-commit hooks on all files
	@echo "$(BLUE)Running pre-commit hooks...$(NC)"
	pre-commit run --all-files
	@echo "$(GREEN)✓ Pre-commit hooks completed$(NC)"

simulate: ## Run trading simulator (example: make simulate ARGS="--help")
	@echo "$(BLUE)Running trading simulator...$(NC)"
	$(PYTHON) -m src.cli simulate $(ARGS)

backtest: ## Run backtest (example: make backtest ARGS="--symbol AAPL")
	@echo "$(BLUE)Running backtest...$(NC)"
	$(PYTHON) -m src.cli backtest $(ARGS)

brief: ## Generate financial brief (example: make brief ARGS="--symbols AAPL,MSFT")
	@echo "$(BLUE)Generating financial brief...$(NC)"
	$(PYTHON) -m src.cli brief $(ARGS)

version: ## Show installed versions
	@echo "$(BLUE)ZenMarket AI - Installed Versions$(NC)"
	@echo "Python: $$($(PYTHON) --version)"
	@echo "pip: $$($(PIP) --version | cut -d' ' -f2)"
	@$(PYTHON) -c "import pytest; print(f'pytest: {pytest.__version__}')" 2>/dev/null || echo "pytest: not installed"
	@$(PYTHON) -c "import black; print(f'black: {black.__version__}')" 2>/dev/null || echo "black: not installed"
	@$(PYTHON) -c "import ruff; print(f'ruff: {ruff.__version__}')" 2>/dev/null || echo "ruff: not installed"
	@$(PYTHON) -c "import mypy; print(f'mypy: {mypy.__version__}')" 2>/dev/null || echo "mypy: not installed"

info: version ## Show project information
	@echo ""
	@echo "$(GREEN)Project Structure:$(NC)"
	@tree -L 2 -I '__pycache__|*.pyc|.git|.venv|venv|*.egg-info|htmlcov|.coverage|.pytest_cache|.mypy_cache|.ruff_cache' || echo "Install 'tree' for better output"
