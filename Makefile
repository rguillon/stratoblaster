# Single entry point for humans, git hooks and CI (specs/01-engineering.md §3).
# uv manages the Python toolchain; Transcrypt compiles src/ to JavaScript.

.DEFAULT_GOAL := help
.PHONY: help install dev build lint format typecheck check check-fast clean

DIST := dist

help: ## List available targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies from uv.lock, then the git hooks (ENG-21)
	uv sync --locked
	uv run pre-commit install --hook-type pre-commit --hook-type pre-push

build: ## Compile src/ to JavaScript with Transcrypt and assemble dist/
	rm -rf $(DIST)
	cd src && uv run transcrypt -b -n -od ../$(DIST)/js main.py
	cp index.html $(DIST)/
	@if [ -d public ]; then cp -r public/. $(DIST)/; fi
	@if grep -qE '__pragma__ *\(' $(DIST)/js/main.js; then \
		echo 'ENG-52: compiler pragmas leaked into the bundle' >&2; exit 1; fi

dev: build ## Build, then serve dist/ on port 5173 (rebuild to see changes)
	uv run python -m http.server 5173 --directory $(DIST)

lint: ## Ruff check + format check + layering contracts (no auto-fix)
	uv run ruff check src
	uv run ruff format --check src
	PYTHONPATH=src uv run lint-imports

format: ## Ruff format + ruff fix
	uv run ruff format src
	uv run ruff check --fix src

typecheck: ## mypy --strict
	uv run mypy

check-fast: lint typecheck ## Lint + typecheck (pre-push hook; tests come back with the test phase)

check: lint typecheck build ## Full gate currently available (tests and e2e are deferred)

clean: ## Remove build outputs and caches
	rm -rf $(DIST) src/__target__ .mypy_cache .ruff_cache
