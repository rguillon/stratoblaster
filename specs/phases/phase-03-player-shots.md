# Phase 03 — Player Shots

> Copy this file to `phase-NN-short-name.md` (e.g. `phase-03-enemies.md`).
> Fill the **Human** sections. Set **Status** to `Ready` when the agent may implement it.
> The agent fills the **Agent** sections and never edits the requirement sections.

**Status:** Ready
**Depends on:**  Phase 2
---

## 🧑 Goal
<!-- One or two sentences: what the player can do / see at the end of this phase that they couldn't before. -->
The different kinds of shots the player ships can have.

## 🧑 Requirements

> ID format `P03-Rxx`. Every requirement is **MUST** (no SHOULD / MAY).
> Write each requirement so it is testable. Add acceptance criteria when "done" isn't obvious.

### P03-R01 — Bullet · MUST

A minigun tracer that moves at constant velocity: a thin streak, white-hot at its head, cooling to orange then red along its tail and fading out (phase 5 review, 2026-10-24; was a neon green blob).

At level 1, a single forward stream
At level 2, a dual forward stream
At level 3, a single forward stream and two diagonal stream (10°)
At level 4, a dual forward stream and two diagonal stream (10°)
At level 5, a single forward stream and 4 diagonal stream (10° and 20°)

Each bullet causes 10 points of damage


### P03-R02 — Laser  · MUST

A bright blue laser with a flow of particles following the stream.

At each level, the laser does more damage per second.
After level1, when the laser hits a ship, the beam goes trough the ship but continue with one less level.


### P03-R03 — Missile  · MUST

A small missile, it has a reactir flame effect. The missile has a constant acceleration. The missiles target the closest enemy within about half the screen height (320 px); enemies further away are not pursued (phase 5 review, 2026-10-24).
On impact, missiles cause a base damage of 8 points for a 10 pixels radius.
A missile stream consists of 4 missiles par seconds.


At level 1, a single forward missile stream
At level 2, a two diagonal stream (10°)
At level 3, a forward stream and a two diagonal stream (10°)
At level 4, a 4 diagonal stream (10° and 20°)
At level 5, a single forward missile stream 4 diagonal stream (10° and 20°)


### P03-R10 — Debug  · MUST

The game shall provide a player_shots/ debug endpoint that shows the different shots from each ship for visual validation.








## 🧑 Tunable values
<!-- Numbers you want to be able to tweak later. The agent puts them in config. -->
| Name | Value | Notes |
|------|-------|-------|
| <!-- enemy_speed --> | <!-- 120 px/s --> | |

## 🧑 Out of scope for this phase
<!-- Things that might seem related but must NOT be done now. -->
-

## 🧑 Engineering additions for this phase
<!-- Optional: phase-specific technical requirements beyond 01-engineering.md (e.g. "add e2e smoke test", "raise coverage to 85%"). -->
-

## 🧑 Manual validation checklist
<!-- What YOU will check in the browser before validating. The agent should make these easy to check. -->
- [ ] Runs on GitHub Pages / `make dev` without console errors
- [ ] 
- [ ] 

## 🧑 Notes, references, sketches
<!-- Links, images, pseudo-code, example level layouts... -->

---

## 🧑 Review feedback
> After the agent reports, write corrections here, then say **"Fix phase 03"**.
> The agent ticks each item when fixed.

- [x] Add a glow at the base of the laser. *Fixed: a pulsing blue glow where the beam leaves the ship, bigger at higher levels (`placeMuzzle` in `laser-renderer.ts`, `SHOT_LOOK.laser.muzzle`).*
- [x] Increase the starting angles for the missiles past level 1. *Fixed: missile diagonal streams launch at ±25° and ±45° instead of ±10° and ±20° (`MISSILE_ANGLES` in `player-weapons.ts`); level 1 and the bullets are unchanged.*
- [x] Make the missiles start from the center of the ship, but the ship stays on top. *Fixed: projectile weapons have a `launchPoint` (`muzzle` or `center`) and `ShotWorld` knows the ship centre; missiles launch from the centre and are drawn 20 units behind the ship (`SHOT_LOOK.missile.depth`), so the ship covers them as they leave. The page grid moved further back, and the stream guides start where the weapon launches.*
- [x] Make the bullet hits create a sparkling metal particle effect instead of a green glow. *Fixed: each hit throws 14 white-gold spark streaks back and to the sides; they slow down, twinkle and shrink away within 0.18-0.4 s (`spark-bursts.ts`, `SHOT_LOOK.impact.bullet`). The green hit flash is gone.*
- [x] Make the bullets smaller. *Fixed: the visible blob radius went from 7 to 4.5 px (`SHOT_LOOK.bullet.radius`); the 4 px hit radius is unchanged.*
- [x] Add a debug tile with FPS and the total number of polygons used. *Fixed: a tile in the top right of `player_shots/` shows the FPS (averaged over 0.5 s) and the polygons (triangles) drawn per frame, from Babylon's active indices; the text refreshes every 0.25 s (`ui/stats-tile.ts`, `SHOT_VIEWER_CONFIG.stats`).*
- [x] Make the bullet core brighter. *Fixed: the blob now has a white-hot centre ring inside the neon green (`SHOT_LOOK.bullet.colors`).*
- [x] The bullets look like they start ahead of the ship; make them start closer to the ship's nose. *Fixed: the muzzle is no longer a fixed height; it is measured on each ship's model, 3 px below its nose tip (`PlayfieldShip.show` returns the nose height, `SHOT_VIEWER_CONFIG.muzzleInset`). Bullets and the laser now start at the nose of every ship.*
- [x] Reduce the bullets' polygon count. *Fixed: a bullet blob is 8 sides and 3 colour rings, 40 triangles instead of 98; each hit spark is a 4-sided diamond, 12 triangles instead of 40 (`SHOT_LOOK.bullet`, `SHOT_LOOK.impact.bullet`). The look is unchanged in screenshots.*
- [x] The laser glow at the ship level is too polygonal; make it look better. *Fixed: the base glow is a 24-sided disc with 6 colour rings following a soft falloff (was 10 sides, 3 rings), 264 triangles for the single glow (`SHOT_LOOK.laser.muzzle`).*

---

## 🤖 Implementation report
> Filled by the agent. Do not edit (comment in Review feedback instead).


### Questions / blockers
Resolved, not blocking. On 2026-10-23 the reviewer answered: "The view is only for visual validation of the shots, it's ok to implement without gameplay." Phase 1 is validated. The other questions had no answer, so the agent's proposed defaults are used. They are all in config and listed under "Deviations from spec" and in D-015, for review:
- Scope (Q2, Q3, Q5): shots only, with no gameplay, no input in the game and no power-ups. The `player_shots/` page fires constantly at dummy targets, and the level is chosen by hand.
- Ships (Q4): every ship has all 3 weapons (GD-30). The page shows one ship at a time and switches between ships.
- Numbers (Q6, Q7, Q9, Q10, Q13, Q14, Q15): see the tunables in "Deviations from spec".
- Diagonals (Q8, Q16): symmetric left and right.
- Piercing (Q11): as described in the question. A level-N laser goes through up to N−1 ships, each segment one level lower, and touches N at most.
- Particles (Q12): bright blue particles flow up the beam, spread over its width.
- IDs (Q17): R01-R03 and R10 are implemented as written.

### Plan
| Task | Requirement IDs |
|------|-----------------|
| Weapon data model and validation (`core/entities/weapon.ts`), shot targets (`core/entities/shot-target.ts`) | P03-R01, R02, R03 |
| Projectile motion (constant velocity, acceleration, homing), beam tracing with piercing, `ShotWorld` (fire, move, collide, area damage, pool) | P03-R01, R02, R03 |
| Game tunables: bullet, laser, missile levels (`game/config/player-weapons.ts`), shot look | P03-R01, R02, R03 |
| Shot renderers: green glow blobs, blue beam with particles and contact glow, missile model with reactor flame, hit flashes and explosions | P03-R01, R02, R03 |
| `player_shots/` page: top-down playfield, ship, dummy targets, stream guides, controls, readouts | P03-R10 |
| Unit tests (core, game, render, app, ui) and e2e for the page | all |

### Requirement traceability
| ID | Status (Done / Partial / Not done) | Code | Tests | Notes |
|----|-----------------------------------|------|-------|-------|
| P03-R01 | Done | `game/config/player-weapons.ts` (`BULLET`), `core/systems/shot-world.ts`, `core/systems/projectile-motion.ts`, `game/view/shots/bullet-renderer.ts`, `game/view/shot-geometry.ts`, `game/view/shots/spark-bursts.ts` | `player-weapons.test.ts`, `shot-world.test.ts`, `projectile-motion.test.ts`, `shot-geometry.test.ts`, `shot-renderers.test.ts`, `spark-bursts.test.ts`, e2e `player-shots.spec.ts` | Neon green additive blob with a black (transparent) rim, stretched along its heading; metal sparks on hit (review). Streams per level as specified; 10 damage per bullet |
| P03-R02 | Done | `game/config/player-weapons.ts` (`LASER`), `core/systems/beam.ts`, `shot-world.ts` (`#fireBeam`), `game/view/shots/laser-renderer.ts`, `laser-particles.ts` | `beam.test.ts`, `shot-world.test.ts`, `laser-particles.test.ts`, `shot-renderers.test.ts`, `player-weapons.test.ts`, e2e | Damage per second rises with the level. Above L1 the beam goes through a ship and continues one level lower (thinner, less damage) |
| P03-R03 | Done (diagonals widened after review) | `game/config/player-weapons.ts` (`MISSILE`), `projectile-motion.ts` (acceleration, homing), `shot-world.ts` (area damage), `game/view/shots/missile-model.ts`, `missile-renderer.ts` | `projectile-motion.test.ts`, `shot-world.test.ts`, `player-weapons.test.ts`, `shot-renderers.test.ts`, e2e | Reuses the ship reactor flame (blue). Homes on the target closest to the missile, re-chosen every step. 8 damage to every target within 10 px of the impact; 4 per second per stream; streams per level as specified |
| P03-R10 | Done | `player_shots/index.html`, `app/start-shot-viewer.ts`, `app/shot-viewer-scene.ts`, `app/dummy-targets.ts`, `app/rate-meter.ts`, `ui/shot-viewer-panel.ts`, `ui/weapon-summary.ts`, `render/shot-playfield.ts`, `render/node-pool.ts`, `app/route.ts`, `vite.config.ts` | `start-shot-viewer.test.ts`, `shot-viewer-panel.test.ts`, `weapon-summary.test.ts`, `dummy-targets.test.ts`, `rate-meter.test.ts`, `shot-playfield.test.ts`, `node-pool.test.ts`, `route.test.ts`, e2e `player-shots.spec.ts` | Every ship × weapon × level, switched by buttons or keys |

### Gate results
```
Light verification (2026-10-23): make typecheck ✔ / make build ✔ (ENG-52 leak check ✔) / make e2e ✔ 27 passed (4 new)
After review fix "glow at the base of the laser" (2026-10-23): make typecheck ✔ / make build ✔ / make e2e ✔ 27 passed
After review fix "wider missile starting angles" (2026-10-23): make typecheck ✔ / make build ✔ / make e2e ✔ 27 passed
After review fix "missiles from the ship centre, under the ship" (2026-10-23): make typecheck ✔ / make build ✔ / make e2e ✔ 27 passed
After review fix "metal sparks on bullet hits" (2026-10-23): make typecheck ✔ / make build ✔ / make e2e ✔ 27 passed
After review fix "smaller bullets" (2026-10-23): make typecheck ✔ / make build ✔ / make e2e ✔ 27 passed
After review fix "FPS / polygons debug tile" (2026-10-23): make typecheck ✔ / make build ✔ / make e2e ✔ 27 passed
After review fix "brighter bullet core" (2026-10-23): make typecheck ✔ / make build ✔ / make e2e ✔ 27 passed
After review fix "bullets start at the ship nose" (2026-10-23): make typecheck ✔ / make build ✔ / make e2e ✔ 27 passed
After review fix "fewer polygons per bullet" (2026-10-23): make typecheck ✔ / make build ✔ / make e2e ✔ 27 passed
After review fix "smoother laser base glow" (2026-10-23): make typecheck ✔ / make build ✔ / make e2e ✔ 27 passed

Full gate, /validate-phase 3 (2026-10-23): make check ✔ (first run, no fix needed)
  lint ✔ (ESLint 0 warnings, Prettier)
  typecheck ✔
  unit tests ✔ 314 passed in 61 files
  coverage ✔ 98.51% statements / 90.8% branches / 98.45% functions / 99.45% lines
  build ✔ (ENG-52 leak check ✔)
  e2e ✔ 27 passed
Deferred to /validate-phase: lint, unit tests, coverage (not run during implementation)
```

### How to test manually
1. `make dev` and open http://localhost:5173/player_shots/ (or `make preview` and `/player_shots/`).
2. The playfield (480×640, faint 40 px grid) shows the Balanced ship at the bottom, firing level-1 bullets at six dummy targets. The targets are red rings with green health bars: a column of four above the ship and one on each side, all swaying together. A destroyed target turns grey and comes back after 1 s.
3. Controls (top left) or keys: **1-5** level, **W** next weapon, **S** next ship, **G** stream guides (yellow lines along each stream's angle), **T** targets on or off. The panel shows a one-line summary of the weapon level, the shots in flight, the damage per second over the last second, and the targets destroyed.
4. Bullet (P03-R01): press G, then step through L1-L5 and check the streams against the guides: L1 1 forward, L2 2 forward 12 px apart, L3 forward ±10°, L4 dual ±10°, L5 forward ±10° ±20°. The bullets are orange-white tracers, at a constant speed. Each hit throws a burst of sparkling white-gold metal sparks.
5. Laser (P03-R02): at L1 the beam stops at the first ship of the column. At L2-L5 it goes through 1-4 ships, getting thinner at each ship, with a glow at each contact and a pulsing glow at its base, bigger at higher levels. Particles flow up the beam. Damage/s rises with the level.
6. Missile (P03-R03): small grey missiles with a red nose and a blue reactor flame, coming out from under the centre of the ship. They start slow, accelerate and curve towards the nearest target within 320 px. Each impact makes an orange explosion. Press T to remove the targets: missiles then fly straight along their streams (check them with G): L1 forward, L2 ±25°, L3 forward ±25°, L4 ±25° ±45°, L5 all five.
7. Press S to check each ship (Balanced, Heavy, Light) with the shots.
8. The tile in the top right shows the FPS and the polygons drawn per frame. Check 60 FPS on your machine; the headless test browser renders in software and shows far less.

### Deviations from spec
Values the spec did not give. All of them are agent defaults in `src/game/config/player-weapons.ts` (D-015):
| Value | Default |
|-------|---------|
| Bullet speed / fire rate / hit radius | 600 px/s / 8 shots/s per stream / 4 px (visual blob 4.5 px after review; a 3.4 × 34 px tracer since the phase 5 review) |
| Dual stream spacing (bullets) | 12 px |
| Laser damage per second, L1-L5 | 40 / 60 / 85 / 115 / 150 |
| Laser hit width, L1-L5 | 4 / 6 / 8 / 10 / 12 px (drawn 1.8× wider for the glow) |
| Missile launch speed / acceleration / max speed | 150 px/s / 600 px/s² / 700 px/s |
| Missile homing | 180°/s towards the target closest to the missile within 320 px (phase 5 review), re-chosen every step; straight when there is none |
| Missile area damage | 8 flat inside the radius (target hitbox within 10 px of the impact), the same at every level |
| Diagonal streams | symmetric (−a and +a) |
| Missile diagonal angles | ±25° and ±45°, not the spec's ±10° and ±20° (phase 3 review feedback) |

- The missile reactor flame reuses the ship's blue flame (`buildReactorFlame`).
- The tunables table in this file is empty, so the values above were not copied into it. They live in the config files.

### Known limitations
- No gameplay: shots are not fired in the game screen, there is no player movement, and nothing levels the weapons up (out of scope per the reviewer).
- Hits use circle checks against the targets' circles (ENG-09). The laser's contact point is the bottom of the target circle.
- The missile flame is a full reactor flame per missile (cones and puffs). This is fine for the debug page (up to about 30 missiles), but may need a lighter version for gameplay with many enemies.
- The look was checked by screenshot only; additive colours depend on the glow layer and tone mapping settings of the scene.

### Suggestions for future phases
- When gameplay arrives, reuse `ShotWorld` per ship and replace the dummy targets with enemy hitboxes. The engine already supports the `ShotTarget` contract.
- Damage numbers or a hit marker per target could make balance tuning easier on this page.
