# Single entry point for humans, git hooks and CI (specs/01-engineering.md §3).
# uv manages the Python toolchain; Transcrypt compiles src/ to JavaScript.

.DEFAULT_GOAL := help
.PHONY: help install build-info vendor dev build e2e-build e2e lint format typecheck test coverage check check-fast clean

DIST := dist
# The e2e build (ENG-51, ENG-52): the game with its test API, served to Playwright by tests/e2e.
E2E_DIST := dist-e2e

# Babylon.js (ENG-02, P18-R04): the pinned UMD build, vendored under public/vendor/ by `make vendor`
# and checked against its SHA-256 (DECISIONS D-173). Bump the version and the hash together.
BABYLON_VERSION := 9.32.0
BABYLON_URL := https://cdn.jsdelivr.net/npm/babylonjs@$(BABYLON_VERSION)/babylon.js
BABYLON_SHA256 := 58c486bececb6cde67b188e6410321e72d1d051ea7a9e5f23c560b6049ab37a5
VENDOR := public/vendor
BABYLON_FILE := $(VENDOR)/babylon.js
SHA256SUM := $(shell command -v sha256sum >/dev/null 2>&1 && echo sha256sum || echo "shasum -a 256")

help: ## List available targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

# The version and the short commit shown on the title screen (ENG-83): `src/build_info.py`, written
# from git by `make build-info` (git-ignored, so a checkout has none until then). The version is the
# latest release tag (highest version, `v` dropped): a checkout without tags shows `unknown`.
APP_VERSION := $(or $(patsubst v%,%,$(shell git tag --sort=-v:refname 2>/dev/null | head -n 1)),unknown)
BUILD_INFO := src/build_info.py

build-info: ## Write src/build_info.py: the version and the short commit (unknown without git)
	@commit=$$(git rev-parse --short HEAD 2>/dev/null || echo unknown); \
	printf 'APP_VERSION = "%s"\nAPP_COMMIT = "%s"\n' '$(APP_VERSION)' "$$commit" > $(BUILD_INFO).tmp; \
	if cmp -s $(BUILD_INFO).tmp $(BUILD_INFO); then rm -f $(BUILD_INFO).tmp; else mv $(BUILD_INFO).tmp $(BUILD_INFO); fi

# Chromium for Playwright (ENG-21); its system libraries too on CI. `make install SKIP_BROWSER=1`
# skips it (jobs without e2e).
PLAYWRIGHT_INSTALL_FLAGS := $(if $(CI),--with-deps,)

install: build-info ## Install Python and Node dependencies (uv.lock, package-lock.json), Chromium for Playwright, then the git hooks (ENG-21)
	uv sync --locked
	npm ci --prefix node
	$(if $(SKIP_BROWSER),,uv run playwright install $(PLAYWRIGHT_INSTALL_FLAGS) chromium)
	uv run pre-commit install --hook-type pre-commit --hook-type pre-push

vendor: ## Download the pinned Babylon.js build into public/vendor/, checking its SHA-256 (ENG-02)
	@mkdir -p $(VENDOR)
	@if echo '$(BABYLON_SHA256)  $(BABYLON_FILE)' | $(SHA256SUM) -c --status 2>/dev/null; then \
		echo 'vendor: $(BABYLON_FILE) is Babylon.js $(BABYLON_VERSION) (checksum OK)'; \
	else \
		tmp=$$(mktemp) && \
		{ curl -fsSL -o "$$tmp" '$(BABYLON_URL)' || { rm -f "$$tmp"; echo 'vendor: download failed: $(BABYLON_URL)' >&2; exit 1; }; } && \
		actual=$$($(SHA256SUM) "$$tmp" | cut -d' ' -f1) && \
		if [ "$$actual" != '$(BABYLON_SHA256)' ]; then \
			rm -f "$$tmp"; \
			echo "vendor: SHA-256 mismatch for Babylon.js $(BABYLON_VERSION): expected $(BABYLON_SHA256), got $$actual" >&2; \
			exit 1; \
		fi && \
		mv "$$tmp" $(BABYLON_FILE) && \
		echo 'vendor: downloaded Babylon.js $(BABYLON_VERSION), checksum OK'; \
	fi

# Transcrypt writes one ES module per Python module into build/transcrypt/; esbuild bundles the
# game (main.py) and its ground worker (a Web Worker entry, not reached from main.py) into one
# file each under dist/js/, so the page makes 2 requests for code instead of one per module.
TRANSCRYPT_OUT := build
# Node is only a build step: esbuild bundles the compiled game (node/ holds its package.json).
ESBUILD := node/node_modules/.bin/esbuild
# Transcrypt has no incremental mode here (its `-b`-less build fails), so it compiles everything
# (about 20 s) whenever a Python source changed: the stamp file records the last compile.
PY_SOURCES := $(shell find src -name '*.py' -not -path '*/__pycache__/*')
TRANSCRYPT_STAMP := $(TRANSCRYPT_OUT)/.stamp

$(TRANSCRYPT_STAMP): $(PY_SOURCES)
	cd src && uv run transcrypt -b -n -od ../$(TRANSCRYPT_OUT)/game main.py
	cd src && uv run transcrypt -b -n -od ../$(TRANSCRYPT_OUT)/worker worker_main.py
	touch $@

# The e2e game (ENG-52): the Transcrypt symbol `e2e` keeps the `__pragma__("ifdef", "e2e")` blocks
# of main.py (the test API, no render loop). The ground worker is the same as in production.
TRANSCRYPT_E2E_STAMP := $(TRANSCRYPT_OUT)/.stamp-e2e

$(TRANSCRYPT_E2E_STAMP): $(PY_SOURCES)
	cd src && uv run transcrypt -b -n -s e2e -od ../$(TRANSCRYPT_OUT)/e2e main.py
	touch $@

build: build-info $(TRANSCRYPT_STAMP) ## Compile src/ to JavaScript (only when it changed), bundle it into dist/js/, assemble dist/ (needs make vendor)
	@echo '$(BABYLON_SHA256)  $(BABYLON_FILE)' | $(SHA256SUM) -c --status 2>/dev/null || { \
		echo 'build: $(BABYLON_FILE) is missing or not the pinned Babylon.js: run make vendor' >&2; exit 1; }
	rm -rf $(DIST)
	mkdir -p $(DIST)/js
	$(ESBUILD) ./$(TRANSCRYPT_OUT)/game/main.js --bundle --format=esm --minify --log-level=warning --outfile=$(DIST)/js/game.js
	$(ESBUILD) ./$(TRANSCRYPT_OUT)/worker/worker_main.js --bundle --format=esm --minify --log-level=warning --outfile=$(DIST)/js/ground_worker.js
	cp index.html $(DIST)/
	@if [ -d public ]; then cp -r public/. $(DIST)/; fi
	@if [ -d $(VENDOR) ] && [ ! -f $(DIST)/vendor/babylon.js ]; then \
		echo 'build: vendored files were not copied to dist/' >&2; exit 1; fi
	@if grep -qE '__pragma__ *\(' $(DIST)/js/game.js; then \
		echo 'ENG-52: compiler pragmas leaked into the bundle' >&2; exit 1; fi
	@if grep -q '__GAME_TEST__' $(DIST)/js/game.js; then \
		echo 'ENG-52: the e2e test API leaked into the production bundle' >&2; exit 1; fi

e2e-build: build ## Build the e2e game (test API, no render loop) into dist-e2e/ (ENG-51, ENG-52)
	@$(MAKE) --no-print-directory $(TRANSCRYPT_E2E_STAMP)
	rm -rf $(E2E_DIST)
	cp -r $(DIST) $(E2E_DIST)
	$(ESBUILD) ./$(TRANSCRYPT_OUT)/e2e/main.js --bundle --format=esm --minify --log-level=warning --outfile=$(E2E_DIST)/js/game.js
	@grep -q '__GAME_TEST__' $(E2E_DIST)/js/game.js || { \
		echo 'ENG-52: the e2e bundle has no test API' >&2; exit 1; }

# Playwright (Python) on the e2e build, served by tests/e2e/conftest.py (ENG-50, ENG-51). On a
# failure, traces, screenshots and videos are kept in test-results/ (ENG-57).
E2E_ARGS ?=
# Parallel workers (pytest-xdist); each has its own browser and server.
E2E_WORKERS ?= 4
e2e: e2e-build ## End-to-end tests: Playwright (Chromium) on the e2e build; E2E_ARGS="-k smoke" to filter
	uv run pytest tests/e2e -p no:cacheprovider -n $(E2E_WORKERS) --tracing retain-on-failure --screenshot only-on-failure --video retain-on-failure --output test-results $(E2E_ARGS)

dev: build ## Build, then serve dist/ on port 5173 (rebuild to see changes)
	uv run python -m http.server 5173 --directory $(DIST)

lint: build-info ## Ruff check + format check + layering contracts (no auto-fix)
	uv run ruff check src
	uv run ruff format --check src
	PYTHONPATH=src uv run lint-imports

format: ## Ruff format + ruff fix
	uv run ruff format src
	uv run ruff check --fix src

typecheck: build-info ## mypy --strict
	uv run mypy

test: ## Unit tests (pytest, CPython over src/)
	uv run pytest

coverage: ## Unit tests with the coverage report of src/ (70 %) and of core/ (90 %), HTML in coverage/
	@uv run pytest --cov --cov-config=pyproject.toml --cov-report=xml

check-fast: lint typecheck ## Lint + typecheck (pre-push hook; tests come back with the test phase)

check: lint typecheck coverage build e2e ## Full gate: lint, typecheck, unit tests with coverage, build, e2e (ENG-32)

clean: ## Remove build outputs and caches
	rm -rf $(DIST) $(E2E_DIST) test-results build coverage .coverage src/__target__ .mypy_cache .ruff_cache .pytest_cache
