# Single entry point for humans, git hooks and CI (specs/01-engineering.md §3).

.DEFAULT_GOAL := help
.PHONY: help install dev build lint format typecheck test test-watch coverage e2e e2e-build e2e-ui check-fast check preview clean

NPX := npx --no-install
# CI also needs the system libraries for Chromium (requires sudo).
PLAYWRIGHT_INSTALL_FLAGS := $(if $(CI),--with-deps,)

help: ## List available targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies, git hooks and Playwright Chromium
	npm ci
	$(NPX) playwright install $(PLAYWRIGHT_INSTALL_FLAGS) chromium

dev: ## Start the Vite dev server with HMR on port 5173
	$(NPX) vite

build: ## Production build into dist/
	$(NPX) vite build

lint: ## ESLint + Prettier check (no auto-fix)
	$(NPX) eslint . --max-warnings 0
	$(NPX) prettier --check .

format: ## Prettier write + ESLint --fix
	$(NPX) prettier --write .
	$(NPX) eslint . --fix

typecheck: ## TypeScript type check
	$(NPX) tsc --noEmit

test: ## Unit tests, single run
	$(NPX) vitest run

test-watch: ## Unit tests in watch mode
	$(NPX) vitest

coverage: ## Unit tests with coverage; fails below thresholds
	$(NPX) vitest run --coverage

e2e-build:
	$(NPX) vite build --mode e2e

e2e: e2e-build ## Build in e2e mode, serve it and run Playwright
	$(NPX) playwright test

e2e-ui: e2e-build ## Playwright UI mode
	$(NPX) playwright test --ui

check-fast: lint typecheck test ## lint + typecheck + unit tests (pre-push)

check: lint typecheck coverage build e2e ## Full gate (CI and agent)

preview: build ## Serve the production build locally
	$(NPX) vite preview

clean: ## Remove build outputs, reports and caches
	rm -rf dist dist-e2e coverage playwright-report test-results blob-report .eslintcache node_modules/.vite
