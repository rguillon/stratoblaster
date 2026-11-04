# Six targets: setup, check, tests, build, e2e, serve. uv runs the Python tools (ENG-04); Transcrypt
# compiles src/ to JavaScript and esbuild bundles it. The first target, `setup`, is the default.

.PHONY: setup check tests build e2e serve FORCE

# The git hooks, ENG-60.
setup:
	uv run pre-commit install

# Every code check: ruff (lint and format, all Python files), import-linter, mypy --strict.
check: src/build_info.py
	@echo "🚀 Checking lock file consistency with 'pyproject.toml'"
	@uv lock --locked
	@echo "🚀 Linting code: Running pre-commit"
	@uv run pre-commit run -a
	@echo "🚀 Static type checking: Running ty"
	@uv run mypy
	@echo "🚀 Checking for obsolete dependencies: Running deptry"
	@uv run deptry src


# Unit tests (pytest, CPython over src/ ) with the coverage gate: 100 % of src/, lines and branches
# (ENG-43). XML report in coverage/coverage.xml.
UNIT_WORKERS ?= auto
tests: src/build_info.py
	uv run pytest -v -n $(UNIT_WORKERS) --cov --cov-config=pyproject.toml --cov-report=term --cov-report=xml:coverage/coverage.xml

# The production game in dist/: Babylon.js fetched if missing or wrong (ENG-02, D-173), Transcrypt
# then esbuild (ENG-23). Fails if a compiler pragma or the e2e test API leaks into the bundle.
DIST := dist
TRANSCRYPT_OUT := build
ESBUILD := node/node_modules/.bin/esbuild

# Babylon.js: the pinned UMD build, vendored under public/vendor/ and checked against its SHA-256.
# Bump the version and the hash together.
BABYLON_VERSION := 9.32.0
BABYLON_URL := https://cdn.jsdelivr.net/npm/babylonjs@$(BABYLON_VERSION)/babylon.js
BABYLON_SHA256 := 58c486bececb6cde67b188e6410321e72d1d051ea7a9e5f23c560b6049ab37a5
VENDOR := public/vendor
BABYLON_FILE := $(VENDOR)/babylon.js
SHA256SUM := $(shell command -v sha256sum >/dev/null 2>&1 && echo sha256sum || echo "shasum -a 256")

# The version (latest release tag, `v` dropped) and the short commit on the title screen (ENG-83).
# src/build_info.py is git-ignored and rewritten only when its content changes.
APP_VERSION := $(or $(patsubst v%,%,$(shell git tag --sort=-v:refname 2>/dev/null | head -n 1)),unknown)
GIT_COMMIT := $(or $(shell git rev-parse --short HEAD 2>/dev/null),unknown)

src/build_info.py: FORCE
	@printf 'APP_VERSION = "%s"\nAPP_COMMIT = "%s"\n' '$(APP_VERSION)' '$(GIT_COMMIT)' > $@.tmp
	@cmp -s $@.tmp $@ && rm -f $@.tmp || mv $@.tmp $@

build: src/build_info.py
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
	npm ci --prefix node
	cd src && uv run transcrypt -b -n -od ../$(TRANSCRYPT_OUT)/game main.py
	cd src && uv run transcrypt -b -n -od ../$(TRANSCRYPT_OUT)/worker worker_main.py
	rm -rf $(DIST)
	mkdir -p $(DIST)/js
	$(ESBUILD) ./$(TRANSCRYPT_OUT)/game/main.js --bundle --format=esm --minify --log-level=warning --outfile=$(DIST)/js/game.js
	$(ESBUILD) ./$(TRANSCRYPT_OUT)/worker/worker_main.js --bundle --format=esm --minify --log-level=warning --outfile=$(DIST)/js/ground_worker.js
	cp index.html $(DIST)/
	cp -r public/. $(DIST)/
	# ENG-84: the script URLs carry the short commit, so a new deploy is never served stale from a cache.
	sed -e 's|js/game\.js|js/game.js?v=$(GIT_COMMIT)|' -e 's|vendor/babylon\.js|vendor/babylon.js?v=$(GIT_COMMIT)|' $(DIST)/index.html > $(DIST)/index.html.tmp && mv $(DIST)/index.html.tmp $(DIST)/index.html
	sed -e 's|\./ground_worker\.js|./ground_worker.js?v=$(GIT_COMMIT)|g' $(DIST)/js/game.js > $(DIST)/js/game.js.tmp && mv $(DIST)/js/game.js.tmp $(DIST)/js/game.js
	@if grep -qE '__pragma__ *\(' $(DIST)/js/game.js; then \
		echo 'ENG-52: compiler pragmas leaked into the bundle' >&2; exit 1; fi
	# AUD-ENGINE-01: the only audio files are the sound effect samples, in sfx/, each as .ogg and .mp3.
	@if find $(DIST) \( -iname '*.ogg' -o -iname '*.mp3' -o -iname '*.wav' -o -iname '*.m4a' -o -iname '*.flac' \) -not -path '$(DIST)/sfx/*' | grep -q .; then \
		echo 'AUD-ENGINE-01: audio files outside $(DIST)/sfx/:' >&2; \
		find $(DIST) \( -iname '*.ogg' -o -iname '*.mp3' -o -iname '*.wav' -o -iname '*.m4a' -o -iname '*.flac' \) -not -path '$(DIST)/sfx/*' >&2; exit 1; fi
	@for f in $(DIST)/sfx/*.ogg; do [ -f "$${f%.ogg}.mp3" ] || { echo "AUD-ENGINE-01: $$f has no .mp3 fallback" >&2; exit 1; }; done
	@if grep -q '__GAME_TEST__' $(DIST)/js/game.js; then \
		echo 'ENG-52: the e2e test API leaked into the production bundle' >&2; exit 1; fi

# End-to-end tests (Playwright, Chromium) on the e2e build (ENG-51, ENG-52): the game with its test
# API, copied from dist/ into dist-e2e/. Traces, screenshots and videos of failures in test-results/.
# E2E_ARGS passes pytest options (-k smoke); E2E_SHARD=K/N runs one slice (CI).
E2E_DIST := dist-e2e
E2E_WORKERS ?= 4
E2E_ARGS ?=
E2E_SHARD ?=
e2e: build
	cd src && uv run transcrypt -b -n -s e2e -od ../$(TRANSCRYPT_OUT)/e2e main.py
	rm -rf $(E2E_DIST)
	cp -r $(DIST) $(E2E_DIST)
	$(ESBUILD) ./$(TRANSCRYPT_OUT)/e2e/main.js --bundle --format=esm --minify --log-level=warning --outfile=$(E2E_DIST)/js/game.js
	@grep -q '__GAME_TEST__' $(E2E_DIST)/js/game.js || { \
		echo 'ENG-52: the e2e bundle has no test API' >&2; exit 1; }
	uv run playwright install $(if $(CI),--with-deps --only-shell,) chromium
	uv run pytest tests/e2e -p no:cacheprovider -n $(E2E_WORKERS) $(if $(E2E_SHARD),--shard $(E2E_SHARD),) --tracing retain-on-failure --screenshot only-on-failure --video retain-on-failure --output test-results $(E2E_ARGS)

# The production game served locally (ENG-22): rebuilt, then dist/ on SERVE_PORT. No hot reload:
# run it again to see a change.
SERVE_PORT ?= 5173
serve: build
	@echo 'serving $(DIST)/ on http://localhost:$(SERVE_PORT) (Ctrl-C to stop)'
	uv run python -m http.server $(SERVE_PORT) --directory $(DIST)
