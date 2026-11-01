# Boss weapon variety and shape-shifting bosses — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Five new hidden weapon kinds with their own looks and fire, re-picked over the 40 bosses,
and eight bosses whose hull sections swing or slide into a new pose as they transform.

**Architecture:** Weapon kinds stay data in `game/config/bosses/hidden_weapons.py` (muzzles,
volleys, launches) drawn by `game/view/bosses/hidden_weapon_shapes.py`. Moving regions are armour
regions (D-224) with a `motion`: the pure pose maths lives in `game/config/bosses/moving_regions.py`
(used by the view and the config tests); `boss_armour.ArmourView` poses the cut piece instead of
bursting it; weapons riding it hang from a carrier node. One core change: a sweeping laser keeps its
turret following the player while it fires.

**Tech Stack:** Python transpiled by Transcrypt (no keyword arguments, `record` objects), Babylon
through `render/`, pytest, Playwright e2e.

**Spec:** `docs/superpowers/specs/2026-11-01-boss-weapon-variety-and-shape-shifts-design.md`

## Global Constraints

- `core/` stays pure (no Babylon, no DOM); code outside `src/game/` game-agnostic (CLAUDE.md).
- Positional arguments only in game code (Transcrypt); `record(...)` for config objects.
- While working: `make typecheck build e2e` only; no `make lint` / `make tests` (CLAUDE.md). Unit
  tests run one file at a time with `pytest` where a task needs them.
- Never lower thresholds, skip tests or use `--no-verify` (ENG-64).
- Kept: D-221 escalation guard, D-227 wholeness, P16-R09 triangle budgets.

## Review Focus

- A boss transforms by count, not by named parts, with a part standing on a moving piece: the part
  would stay live where the piece left — the config test must reject it.
- A piece resting folded (rest angle ≠ 0) must still hold to the boss at rest (wholeness at form 0).
- A hangar revealed while the boss is transforming must launch nothing until revealed (hidden parts
  are no volley source, launches included).
- Mirrored moving regions: the mirror's motion must be the mirror image (X negated, `up`/`along`
  angles negated), or the two halves move the same way.
- The K debug key and the e2e `destroy_boss` on a `transform_parts` boss must still reach the core.

---

### Task 1: Sweeping lasers keep their turret following the player

**Files:** Modify `src/core/systems/boss_pattern.py` (`_laser_aim`), `src/game/config/bosses/boss_kit.py`
(`sweeping(shot)`). Test: `tests/unit/core/systems/test_boss_pattern*.py`.

- Produces: `boss_kit.sweeping(shot) -> shot` (a laser volley whose beam `sweeps`).
- Test: a turret firing a `sweeps` laser turns towards the player during the firing phase at
  `laser_turn_rate_deg`; a plain laser's turret holds still while firing (existing behaviour).

### Task 2: New weapon kinds (config)

**Files:** `src/game/config/bosses/hidden_weapons.py`; test
`tests/unit/game/config/bosses/test_hidden_weapons.py`.

- `KINDS` gains `cannon`, `mortar`, `battery`, `sweeper`, `hangar`. `WEAPON_SHAPE` gains their
  shares. `weapon_guns(kind, at, radius, height)`: cannon one muzzle on a turret, mortar one muzzle
  (tube mouth), battery five muzzles in a row, sweeper one laser muzzle on a turret, hangar none
  (`{}` plus its centre for launches).
- `weapon_volley(kind, part_id, style, first)` returns a list: cannon aimed 3 × bullet(style, 150,
  7) 12° every 2.4 s; mortar aimed 1 × `bursting(style, 110, 8, [1.1, 8, bullet(style, 170)])`
  every 3.2 s; battery fan 7 × 9° heading 0 every 2.0; sweeper `sweeping(laser every 8, 2.0 s)`;
  hangar none.
- `hidden_weapon` gains `launches` (hangar: `[{from, kind: "gnats", count 2, every 7, first}]`);
  `with_weapons` appends them to `design.launches`.
- Tests: muzzle counts/positions per kind; volley shapes; a hangar's launch lands in
  `design.launches`.

### Task 3: New weapon kinds (view)

**Files:** `src/game/view/bosses/hidden_weapon_shapes.py`, `src/game/view/bosses/boss_model.py`
(`_weapon_slides`), `tests/helpers/boss_wholeness.py`; test
`tests/unit/game/view/bosses/test_hidden_weapon_shapes.py`.

- Pods by kind (octagon; mortar round base; battery rectangular deck; hangar box).
  `weapon_turret_drawing` for gatling, cannon, sweeper. `weapon_slides(look, neon) -> list` of
  `[draw, axis, distance]` (hangar: two doors on ±X; mortar tube up; battery barrels forward).
- Tests: every kind's pod, turret and slides build with triangles; hangar has two slides.

### Task 4: Escalation guard counts launches; hangars fire through launches

**Files:** `tests/unit/game/config/bosses/test_boss_transforms.py`.

- `fire_rate` adds `2 × count / every` for each live launch; "never fires" accepts a launch.

### Task 5: Moving regions

**Files:** Create `src/game/config/bosses/moving_regions.py`; modify
`src/game/view/bosses/boss_armour.py`, `boss_model.py`, `tests/helpers/boss_wholeness.py`; tests
`tests/unit/game/config/bosses/test_moving_regions.py`, `tests/unit/game/view/bosses/test_boss_armour.py`.

- `swing(pivot, axis, angles)`, `slide(offsets)`, `moving_region(region_id, form, outline, motion,
  frame, heights, mirror)` (an armour region with `motion` per outline, mirrored), `on_region(weapon,
  region_id)`; `motion_at(motion, u) -> float | Vec3`, `move_point(motion, point, u)` (config
  coordinates), `region_end_outlines(region)`.
- View: a moving region's whole sits under a mover node posed by `motion_at(u)`; no chunks; frame
  only when given. Weapons riding it hang from a carrier node posed by M(u)·M(1)⁻¹. Progress u:
  0 before its transformation, `share(t, [burst, swing end])` during it, 1 after.
- Cut maths: after its form, a moving region counts as its piece in end pose (not a floor) in
  `_free_after`, `_held_frames` skips frameless regions, `lasting_surfaces` leaves them out.
- Wholeness helper: pieces in rest pose before their form, end pose after; riding weapons at `at`;
  parts named in `transform_parts[K-1]` dropped from form K.
- Tests: poses (rest, end, mirrored), carrier identity at end, point moved, and config rules
  (weapon `on` inside end outline; live parts not on a moving piece unless destroyed or retired).

### Task 6: The eight shape-shifting bosses (a world per commit)

Storm Petrel, Mesa Fortress, Snow Owl, Boreal Citadel, Stone Idol, Sky Temple, Obsidian Golem, Steam
Dreadnought: regions, motions and weapons by hand per the spec's table; `transform_parts` where a
part stands on a moving piece. Each passes the guard, wholeness and budgets.

### Task 7: Re-pick the other 32 bosses (a world per commit) and the distribution test

- Test (in `test_boss_transforms.py`): no kind > 20 % of hidden weapons (`beam` aside); every world
  ≥ 6 kinds; a final boss's two transformations share no kind; hangars on finals only, ≤ 1 a world;
  ≥ 10 bosses with a centre weapon; each of the eight has a moving region.

### Task 8: Decisions, e2e and verification

- `specs/DECISIONS.md`: D-229 (new kinds, sweeping turret), D-230 (moving regions, the eight).
- e2e: one moving-region boss transform test in `tests/e2e/test_boss_transform.py`.
- `make typecheck build e2e`.
