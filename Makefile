# Nine targets: setup, check, tests, build, e2e, serve, learn, rate, serve-ai. uv runs the Python
# tools (ENG-04); Transcrypt compiles src/ to JavaScript and esbuild bundles it. The first target,
# `setup`, is the default.

.PHONY: setup check tests build e2e e2e-build serve learn rate serve-ai FORCE

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

# Every step below is a file target: `make build` redoes only what an input changed (ENG-39).
# Transcrypt runs without `-b`, so it also recompiles only the modules newer than their JavaScript.
STAMPS := .make
PY_SOURCES := $(shell find src -name '*.py' -not -path 'src/__target__/*')
PUBLIC_FILES := $(shell find public -type f -not -path 'public/vendor/*')

DIST_FILES := $(DIST)/js/game.js $(DIST)/js/ground_worker.js $(DIST)/index.html $(DIST)/.public
build: $(DIST_FILES)

# Babylon.js: checked when missing or after a Makefile change (a version bump), downloaded if wrong.
$(BABYLON_FILE): Makefile
	@mkdir -p $(VENDOR)
	@if echo '$(BABYLON_SHA256)  $(BABYLON_FILE)' | $(SHA256SUM) -c --status 2>/dev/null; then \
		echo 'babylon: $(BABYLON_FILE) is Babylon.js $(BABYLON_VERSION) (checksum OK)'; \
		touch $@; \
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

# esbuild, installed again only when node/package*.json change.
$(STAMPS)/npm: node/package.json node/package-lock.json
	npm ci --prefix node
	@mkdir -p $(STAMPS) && touch $@

# Transcrypt, one output directory per entry; src/build_info.py changes only with the version or
# commit.
$(TRANSCRYPT_OUT)/game/.stamp: $(PY_SOURCES) src/build_info.py
	cd src && uv run transcrypt -n -od ../$(TRANSCRYPT_OUT)/game main.py
	@touch $@

$(TRANSCRYPT_OUT)/worker/.stamp: $(PY_SOURCES) src/build_info.py
	cd src && uv run transcrypt -n -od ../$(TRANSCRYPT_OUT)/worker worker_main.py
	@touch $@

# ENG-84: the worker URL carries the short commit, so a new deploy is never served stale from a cache.
$(DIST)/js/game.js: $(TRANSCRYPT_OUT)/game/.stamp $(STAMPS)/npm
	@mkdir -p $(DIST)/js
	$(ESBUILD) ./$(TRANSCRYPT_OUT)/game/main.js --bundle --format=esm --minify --log-level=warning --outfile=$@.tmp
	sed -e 's|\./ground_worker\.js|./ground_worker.js?v=$(GIT_COMMIT)|g' $@.tmp > $@.tmp2 && rm -f $@.tmp
	@if grep -qE '__pragma__ *\(' $@.tmp2; then \
		rm -f $@.tmp2; echo 'ENG-52: compiler pragmas leaked into the bundle' >&2; exit 1; fi
	@if grep -q '__GAME_TEST__' $@.tmp2; then \
		rm -f $@.tmp2; echo 'ENG-52: the e2e test API leaked into the production bundle' >&2; exit 1; fi
	@mv $@.tmp2 $@

$(DIST)/js/ground_worker.js: $(TRANSCRYPT_OUT)/worker/.stamp $(STAMPS)/npm
	@mkdir -p $(DIST)/js
	$(ESBUILD) ./$(TRANSCRYPT_OUT)/worker/worker_main.js --bundle --format=esm --minify --log-level=warning --outfile=$@

# ENG-84: the script URLs carry the short commit (written into src/build_info.py).
$(DIST)/index.html: index.html src/build_info.py
	@mkdir -p $(DIST)
	sed -e 's|js/game\.js|js/game.js?v=$(GIT_COMMIT)|' -e 's|vendor/babylon\.js|vendor/babylon.js?v=$(GIT_COMMIT)|' index.html > $@

# public/ (the sound effects and Babylon.js), copied when a file in it changes.
$(DIST)/.public: $(PUBLIC_FILES) $(BABYLON_FILE)
	@mkdir -p $(DIST)
	cp -r public/. $(DIST)/
	# AUD-ENGINE-01: the only audio files are the sound effect samples, in sfx/, each as .ogg and .mp3.
	@if find $(DIST) \( -iname '*.ogg' -o -iname '*.mp3' -o -iname '*.wav' -o -iname '*.m4a' -o -iname '*.flac' \) -not -path '$(DIST)/sfx/*' | grep -q .; then \
		echo 'AUD-ENGINE-01: audio files outside $(DIST)/sfx/:' >&2; \
		find $(DIST) \( -iname '*.ogg' -o -iname '*.mp3' -o -iname '*.wav' -o -iname '*.m4a' -o -iname '*.flac' \) -not -path '$(DIST)/sfx/*' >&2; exit 1; fi
	@for f in $(DIST)/sfx/*.ogg; do [ -f "$${f%.ogg}.mp3" ] || { echo "AUD-ENGINE-01: $$f has no .mp3 fallback" >&2; exit 1; }; done
	@touch $@

# End-to-end tests (Playwright, Chromium) on the e2e build (ENG-51, ENG-52): the game with its test
# API, copied from dist/ into dist-e2e/. Traces, screenshots and videos of failures in test-results/.
# E2E_ARGS passes pytest options (-k smoke); E2E_SHARD=K/N runs one slice (CI).
E2E_DIST := dist-e2e
E2E_WORKERS ?= 4
E2E_ARGS ?=
E2E_SHARD ?=
e2e: $(E2E_DIST)/js/game.js $(STAMPS)/playwright
	uv run pytest tests/e2e -p no:cacheprovider -n $(E2E_WORKERS) $(if $(E2E_SHARD),--shard $(E2E_SHARD),) --tracing retain-on-failure --screenshot only-on-failure --video retain-on-failure --output test-results $(E2E_ARGS)

$(TRANSCRYPT_OUT)/e2e/.stamp: $(PY_SOURCES) src/build_info.py
	cd src && uv run transcrypt -n -s e2e -od ../$(TRANSCRYPT_OUT)/e2e main.py
	@touch $@

# dist/ with the e2e bundle (with its test API) in place of the game's.
$(E2E_DIST)/js/game.js: $(TRANSCRYPT_OUT)/e2e/.stamp $(DIST_FILES)
	rm -rf $(E2E_DIST)
	cp -r $(DIST) $(E2E_DIST)
	$(ESBUILD) ./$(TRANSCRYPT_OUT)/e2e/main.js --bundle --format=esm --minify --log-level=warning --outfile=$@
	@grep -q '__GAME_TEST__' $@ || { \
		echo 'ENG-52: the e2e bundle has no test API' >&2; rm -f $@; exit 1; }

# The e2e build alone (a step of `e2e` and `serve-ai`, ENG-37).
e2e-build: $(E2E_DIST)/js/game.js

# Chromium for Playwright, installed again only when the locked tools change.
$(STAMPS)/playwright: uv.lock
	uv run playwright install $(if $(CI),--with-deps --only-shell,) chromium
	@mkdir -p $(STAMPS) && touch $@

# The production game served locally (ENG-22): rebuilt, then dist/ on SERVE_PORT. No hot reload:
# run it again to see a change.
SERVE_PORT ?= 5173
serve: build
	@echo 'serving $(DIST)/ on http://localhost:$(SERVE_PORT) (Ctrl-C to stop)'
	uv run python -m http.server $(SERVE_PORT) --directory $(DIST)

# The AI player (tests/ai/): pure Python, it runs the game's simulation in CPython at full speed.
# `learn` trains the brain for LEARN_MINUTES (Ctrl-C stops early and saves), resuming the one in
# data/ if any; `rate` rates the difficulty of each level with it (data/ratings.json). Extra
# options in LEARN_ARGS / RATE_ARGS (`uv run python -m ai.learn --help`, `... ai.rate --help`).
# AI_TORCH=cuda installs and uses the CUDA build of torch (an NVIDIA GPU learns, every CPU core
# plays); the default, cpu, the CPU-only build.
LEARN_MINUTES ?= 60
AI_TORCH ?= cpu
AI_RUN := PYTHONPATH=tests uv run --no-default-groups --group dev --group ai-$(AI_TORCH) python -m
learn:
	$(AI_RUN) ai.learn --minutes $(LEARN_MINUTES) $(LEARN_ARGS)

rate:
	$(AI_RUN) ai.rate $(RATE_ARGS)

# Watch the brain play the real game in your own browser: a server of the e2e build (D-266) on
# SERVE_AI_PORT, where the game runs in real time and asks the brain for its moves. Start a level
# from the menus, or `make serve-ai LEVEL=2-3` (and SHIP=heavy). WATCH_ARGS: more options
# (`--host 0.0.0.0` to open it from another machine, `--sample`).
SERVE_AI_PORT ?= 5174
serve-ai: e2e-build
	$(AI_RUN) ai.watch --port $(SERVE_AI_PORT) $(if $(LEVEL),--level $(LEVEL),) $(if $(SHIP),--ship $(SHIP),) $(WATCH_ARGS)
