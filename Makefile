# Aida Github Plugin Makefile
# Run `make help` for available targets

PLUGIN_PATH := $(shell pwd)
PLUGIN_NAME := aida-github-plugin

.PHONY: help lint lint-md lint-fix-md lint-yaml lint-frontmatter clean

help: ## Show this help message
	@echo "Aida Github Plugin - Available targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

# Linting (shared)
lint-md: ## Run markdownlint on Markdown files
	markdownlint '**/*.md' --ignore node_modules

lint-fix-md: ## Fix markdownlint issues
	markdownlint '**/*.md' --ignore node_modules --fix

lint-yaml: ## Run yamllint on YAML files
	yamllint -c .yamllint.yml .

lint-frontmatter: ## Validate frontmatter in Markdown files
	@echo "Frontmatter validation not yet configured"


# Python targets
.PHONY: lint-py test format install

lint-py: ## Run ruff linter on Python files
	ruff check .

lint: lint-py lint-md lint-yaml lint-frontmatter ## Run all linters

test: ## Run pytest
	pytest tests/ -v

format: ## Auto-format Python code
	ruff check . --fix
	ruff format .

install: ## Install Python dependencies
	pip install -e ".[dev]"

clean: ## Remove build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
