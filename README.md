# Stratoblaster

<!-- ENG-130: the live game, the controls, the requirements and the make targets. -->

An old-school vertical shoot 'em up with modern 3D graphics, running entirely in the browser.

**Play:** <https://rguillon.github.io/stratoblaster/>

**Source:** <https://github.com/rguillon/stratoblaster>

## Controls

### Menus

| Action         | Keyboard                       | Gamepad           | Touch / mouse             |
| -------------- | ------------------------------ | ----------------- | ------------------------- |
| Move selection | Arrows / WASD (Z Q S D AZERTY) | Left stick, D-pad | Tap an entry              |
| Confirm        | Enter, Space                   | A                 | Tap the selected entry    |
| Back           | Esc, Backspace                 | B                 | On-screen **Back** button |
| Change a value | ◀ / ▶ on a slider (Settings)   | Left stick, D-pad | Tap or drag the slider    |

### In game

| Action         | Keyboard                    | Gamepad           | Touch                    |
| -------------- | --------------------------- | ----------------- | ------------------------ |
| Move           | Arrows / WASD (by position) | Left stick, D-pad | Drag anywhere            |
| Shoot (hold)   | Space                       | A, right trigger  | Hold the **Fire** button |
| Switch weapon  | E (same key on AZERTY)      |                   |                          |
| Bomb           | R, Left Shift (by position) | X / Square, LB    | Tap the **Bomb** button  |
| Pause / resume | Esc, P (by position)        | Start, Select     | On-screen **❚❚** button  |

The level pauses by itself when the page is hidden or the gamepad in use is disconnected. The
pause menu has **Resume**, **Settings** and **Main menu** (which asks before leaving the level).
**Settings** (also on the title screen) sets the music and sound effect volumes.

All the music and sounds are generated in the browser (Web Audio); they start with the first key
press, tap, click or gamepad button.

Debug options (any build): `?level=1-3&t=120&ship=heavy` starts level 1-3 at 2:00 with the heavy
ship. With them, F fast-forwards ×4, ← / → jump 10 s, and an FPS / polygons tile shows.

The high score, the last chosen ship and the volumes are kept in cookies (`stratoblaster_high_score`, `stratoblaster_last_ship`, `stratoblaster_music_volume`, `stratoblaster_sfx_volume`).

## Requirements

- Python 3.12 and [uv](https://docs.astral.sh/uv/) (it fetches the Python version and the tools)
- GNU Make
- Node.js 24 LTS and npm (`node/.nvmrc`), only for the build's bundling step (esbuild)

## Getting started

```sh
make setup     # installs the git hooks (pre-commit, pre-push)
make serve     # builds the game into dist/ and serves it on http://localhost:5173
```

Then open http://localhost:5173. `SERVE_PORT=8000 make serve` picks another port.

## Make targets

<!-- ENG-37: the public targets, the only ones `make help` lists. -->

| Target       | What it does                                                                 |
| ------------ | ---------------------------------------------------------------------------- |
| `make setup` | Installs the git hooks (pre-commit, pre-push)                                |
| `make check` | Every code check: ruff (lint and format), import-linter, mypy                |
| `make tests` | Unit tests (pytest, CPython over `src/`) with coverage (HTML in `coverage/`) |
| `make build` | Fetches Babylon.js if needed, builds the game into `dist/`                   |
| `make e2e`   | Builds the e2e game, then runs the end-to-end tests (Playwright, Chromium)  |
| `make serve` | Builds the game, then serves `dist/` on http://localhost:5173 (`SERVE_PORT`) |
| `make learn` | The AI player learns the game for `LEARN_MINUTES` (60); resumes `data/brain.pt` |
| `make rate`  | The AI player rates each level's difficulty, in % (`data/ratings.json`)      |
| `make serve-ai` | Serves the game on http://localhost:5174, where the AI player plays (`LEVEL=2-3`) |

### The AI player

[`tests/ai/`](tests/ai/) is a neural network (convolutional encoders, a GRU memory) that learns to
play the game by reinforcement learning (PPO), in pure Python: it runs the game's own simulation in
CPython as fast as the CPU goes, no browser. It sees the whole playfield and a close-up around the
ship: the enemies and bosses, the bullets, missiles and lasers, and the weapon, life, bomb and
healing bonuses. `make learn` trains it: each game it plays starts at 1-1 with 3 lives and 3
bombs and goes on to the next level with what it earned, until the ship is lost, and it learns to
score the most (D-271). Every minute it says how its games went (score, levels reached); the brain
whose games scored best on average is kept in `data/brain-best.pt`, and `data/learn-log.csv` logs
each update. Ctrl-C stops and saves; `LEARN_ARGS=--fresh` starts over. `make rate` then plays
every level 8 times with the same loadout and rates it from 0 % (cleared without a scratch) to
100 % (lost at once); the ratings are relative to how well the brain plays. Options:
`RATE_ARGS="--episodes 16 --weapon-level 2"`, see
`PYTHONPATH=tests uv run python -m ai.rate --help`. Decision D-263 has the details. On a machine
with an NVIDIA GPU, `make learn AI_TORCH=cuda` learns on the GPU with every CPU core playing (D-264).

`make serve-ai` serves the real game on http://localhost:5174 (`SERVE_AI_PORT`): open it in any
browser, pick a ship and a level in the menus (or `make serve-ai LEVEL=2-3 SHIP=heavy`), and the
brain plays every level you start; the menus and panels stay yours. The game runs in real time in
the browser and asks the brain, in Python, for its keys about 15 times a second (D-266).

[`node/tests/`](node/tests/) keeps the TypeScript test suite of the game this port came from. Nothing
runs it: it is the reference for the tests still to port.

## Project layout

See [`docs/architecture.md`](docs/architecture.md) and the specs in [`specs/`](specs/).

## Credits

The models, the textures and the music are generated by code. The sound effects are recorded
samples from packs released under
[CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) (public domain, compatible with this
project's MIT license):

- Kenney: [Sci-Fi Sounds](https://opengameart.org/content/sci-fi-sounds) (Kenney, CC0): weapons, explosions,
  impacts, thrusters
- Kenney: [Interface Sounds](https://opengameart.org/content/interface-sounds) (Kenney, CC0): menus, bonuses,
  rewards
- [The Free Firearm Sound Library](https://opengameart.org/content/the-free-firearm-sound-library)
  (Ben Jaszczak, et al., CC0): the player gun's minigun burst, made of single AK-47 shots
- [Explosions](https://opengameart.org/content/explosions-4) (compufox, CC0): two of the small and
  large explosion variants

The samples are trimmed, normalised and re-encoded (Ogg Vorbis and MP3) in `public/sfx/`. Which file
each sound comes from is listed in [`CREDITS.md`](CREDITS.md). The 3D engine is
[Babylon.js](https://www.babylonjs.com) (Apache-2.0).

## License

MIT, see [`LICENSE`](LICENSE).
