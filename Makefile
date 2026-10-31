# Single entry point for people, git hooks and CI (specs/01-engineering.md §3).
# Public targets: setup, check, tests, e2e, serve, help. The other targets are steps the public
# ones and the git hooks call: they work on their own too, but they are not listed by `make help`.
# uv manages the Python toolchain; Transcrypt compiles src/ to JavaScript; esbuild bundles it.

.DEFAULT_GOAL := help
.PHONY: help setup check tests e2e serve lint typecheck format check-fast build e2e-build \
	build-info babylon check-tools clean

DIST := dist
# The e2e build (ENG-51, ENG-52): the game with its test API, served to Playwright by tests/e2e.
E2E_DIST := dist-e2e
# Stamp files: what each install or compile step last did (git-ignored).
STAMPS := .make

# Babylon.js (ENG-02, D-173): the pinned UMD build, vendored under public/vendor/ and checked
# against its SHA-256. Bump the version and the hash together.
BABYLON_VERSION := 9.32.0
BABYLON_URL := https://cdn.jsdelivr.net/npm/babylonjs@$(BABYLON_VERSION)/babylon.js
BABYLON_SHA256 := 58c486bececb6cde67b188e6410321e72d1d051ea7a9e5f23c560b6049ab37a5
VENDOR := public/vendor
BABYLON_FILE := $(VENDOR)/babylon.js
SHA256SUM := $(shell command -v sha256sum >/dev/null 2>&1 && echo sha256sum || echo "shasum -a 256")

# The Node major version the game builds with (esbuild, in node/).
NODE_MAJOR := $(shell cat node/.nvmrc)

help: ## List the targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

# The tools the game needs. Every step below checks them first, so a missing one is named before
# anything is installed.
check-tools:
	@missing=""; \
	for t in uv node npm curl git; do command -v $$t >/dev/null 2>&1 || missing="$$missing $$t"; done; \
	command -v sha256sum >/dev/null 2>&1 || command -v shasum >/dev/null 2>&1 || missing="$$missing sha256sum-or-shasum"; \
	if [ -n "$$missing" ]; then \
		echo "missing tools:$$missing" >&2; \
		echo "  uv: https://docs.astral.sh/uv/   node $(NODE_MAJOR): https://nodejs.org (or nvm: reads node/.nvmrc)" >&2; \
		exit 1; \
	fi
	@major=$$(node -p 'process.versions.node.split(".")[0]'); \
	if [ "$$major" != "$(NODE_MAJOR)" ]; then \
		echo "node is $$major, but node/.nvmrc asks for $(NODE_MAJOR)" >&2; exit 1; \
	fi

# Python: the locked environment (.venv), made again when pyproject.toml or uv.lock change.
UV_SYNC := $(STAMPS)/uv-sync
$(UV_SYNC): pyproject.toml uv.lock | check-tools
	@mkdir -p $(STAMPS)
	uv sync --locked
	@touch $@

# Node: esbuild, made again when node/package-lock.json changes.
NPM_CI := $(STAMPS)/npm-ci
$(NPM_CI): node/package.json node/package-lock.json | check-tools
	@mkdir -p $(STAMPS)
	npm ci --prefix node
	@touch $@

# Chromium for Playwright (ENG-21); its system libraries too on CI. SKIP_BROWSER=1 leaves it out
# of `setup` (the e2e tests still install it when they run).
PLAYWRIGHT_INSTALL_FLAGS := $(if $(CI),--with-deps,)
PLAYWRIGHT := $(STAMPS)/playwright
$(PLAYWRIGHT): $(UV_SYNC)
	@mkdir -p $(STAMPS)
	uv run playwright install $(PLAYWRIGHT_INSTALL_FLAGS) chromium
	@touch $@

# Babylon.js: downloaded when missing, and checked on every use (a wrong file is replaced).
babylon: | check-tools
	@mkdir -p $(VENDOR)
	@if echo '$(BABYLON_SHA256)  $(BABYLON_FILE)' | $(SHA256SUM) -c --status 2>/dev/null; then \
		echo 'babylon: $(BABYLON_FILE) is Babylon.js $(BABYLON_VERSION) (checksum OK)'; \
	else \
		tmp=$$(mktemp) && \
		{ curl -fsSL -o "$$tmp" '$(BABYLON_URL)' || { rm -f "$$tmp"; echo 'babylon: download failed: $(BABYLON_URL)' >&2; exit 1; }; } && \
		actual=$$($(SHA256SUM) "$$tmp" | cut -d' ' -f1) && \
		if [ "$$actual" != '$(BABYLON_SHA256)' ]; then \
			rm -f "$$tmp"; \
			echo "babylon: SHA-256 mismatch for Babylon.js $(BABYLON_VERSION): expected $(BABYLON_SHA256), got $$actual" >&2; \
			exit 1; \
		fi && \
		mv "$$tmp" $(BABYLON_FILE) && \
		echo 'babylon: downloaded Babylon.js $(BABYLON_VERSION), checksum OK'; \
	fi

# The version and the short commit shown on the title screen (ENG-83): `src/build_info.py`, written
# from git (git-ignored). The version is the latest release tag (`v` dropped): `unknown` without one.
APP_VERSION := $(or $(patsubst v%,%,$(shell git tag --sort=-v:refname 2>/dev/null | head -n 1)),unknown)
BUILD_INFO := src/build_info.py

build-info:
	@commit=$$(git rev-parse --short HEAD 2>/dev/null || echo unknown); \
	printf 'APP_VERSION = "%s"\nAPP_COMMIT = "%s"\n' '$(APP_VERSION)' "$$commit" > $(BUILD_INFO).tmp; \
	if cmp -s $(BUILD_INFO).tmp $(BUILD_INFO); then rm -f $(BUILD_INFO).tmp; else mv $(BUILD_INFO).tmp $(BUILD_INFO); fi

# Transcrypt writes one ES module per Python module; esbuild bundles the game (main.py) and its
# ground worker (a Web Worker entry, not reached from main.py) into one file each under dist/js/.
# Transcrypt has no incremental mode here, so it compiles everything (about 20 s) whenever a Python
# source changed: the stamp file records the last compile.
TRANSCRYPT_OUT := build
ESBUILD := node/node_modules/.bin/esbuild
PY_SOURCES := $(shell find src -name '*.py' -not -path '*/__pycache__/*')
TRANSCRYPT_STAMP := $(TRANSCRYPT_OUT)/.stamp
TRANSCRYPT_E2E_STAMP := $(TRANSCRYPT_OUT)/.stamp-e2e

$(TRANSCRYPT_STAMP): $(PY_SOURCES) $(UV_SYNC)
	cd src && uv run transcrypt -b -n -od ../$(TRANSCRYPT_OUT)/game main.py
	cd src && uv run transcrypt -b -n -od ../$(TRANSCRYPT_OUT)/worker worker_main.py
	touch $@

# The e2e game (ENG-52): the Transcrypt symbol `e2e` keeps the `__pragma__("ifdef", "e2e")` blocks
# of main.py (the test API, no render loop). The ground worker is the same as in production.
$(TRANSCRYPT_E2E_STAMP): $(PY_SOURCES) $(UV_SYNC)
	cd src && uv run transcrypt -b -n -s e2e -od ../$(TRANSCRYPT_OUT)/e2e main.py
	touch $@

# Lint, types and tests (the code checks).

lint: build-info $(UV_SYNC)
	uv run ruff check src
	uv run ruff format --check src
	PYTHONPATH=src uv run lint-imports

typecheck: build-info $(UV_SYNC)
	uv run mypy

format: $(UV_SYNC)
	uv run ruff format src
	uv run ruff check --fix src

check-fast: lint typecheck
	@true

tests: build-info $(UV_SYNC) ## Unit tests (pytest, CPython over src/) with coverage: src/ at 70 %, core/ at 90 %; HTML in coverage/
	uv run pytest --cov --cov-config=pyproject.toml --cov-report=term --cov-report=xml:coverage/coverage.xml --cov-report=html:coverage/html
	uv run coverage report --include='src/core/*' --fail-under=90

# The game: build, end-to-end tests, serving.

build: build-info $(TRANSCRYPT_STAMP) $(NPM_CI) babylon
	rm -rf $(DIST)
	mkdir -p $(DIST)/js
	$(ESBUILD) ./$(TRANSCRYPT_OUT)/game/main.js --bundle --format=esm --minify --log-level=warning --outfile=$(DIST)/js/game.js
	$(ESBUILD) ./$(TRANSCRYPT_OUT)/worker/worker_main.js --bundle --format=esm --minify --log-level=warning --outfile=$(DIST)/js/ground_worker.js
	cp index.html $(DIST)/
	cp -r public/. $(DIST)/
	@if grep -qE '__pragma__ *\(' $(DIST)/js/game.js; then \
		echo 'ENG-52: compiler pragmas leaked into the bundle' >&2; exit 1; fi
	@if grep -q '__GAME_TEST__' $(DIST)/js/game.js; then \
		echo 'ENG-52: the e2e test API leaked into the production bundle' >&2; exit 1; fi

e2e-build: build $(TRANSCRYPT_E2E_STAMP) $(NPM_CI)
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
e2e: e2e-build $(PLAYWRIGHT) $(UV_SYNC) ## End-to-end tests (Playwright, Chromium) on the e2e build; E2E_ARGS="-k smoke" to filter
	uv run pytest tests/e2e -p no:cacheprovider -n $(E2E_WORKERS) --tracing retain-on-failure --screenshot only-on-failure --video retain-on-failure --output test-results $(E2E_ARGS)

# The port the game is served on.
SERVE_PORT ?= 5173
serve: build $(UV_SYNC) ## Serve the game (dist/, production build) on http://localhost:5173
	@echo 'serving $(DIST)/ on http://localhost:$(SERVE_PORT) (Ctrl-C to stop)'
	uv run python -m http.server $(SERVE_PORT) --directory $(DIST)

# Everything at once: setup and the full gate.

setup: check-tools $(UV_SYNC) $(NPM_CI) babylon $(if $(SKIP_BROWSER),,$(PLAYWRIGHT)) ## Check the tools, install the dependencies and the git hooks (pre-commit, pre-push)
	uv run pre-commit install --hook-type pre-commit --hook-type pre-push
	@echo 'setup: done'

check: lint typecheck tests build e2e ## Every code check, the unit tests with coverage, the build and the e2e tests

clean:
	rm -rf $(DIST) $(E2E_DIST) test-results build coverage .coverage src/__target__ .mypy_cache .ruff_cache .pytest_cache
