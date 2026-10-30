# Phase 14 — Playability

> Copy this file to `phase-NN-short-name.md` (e.g. `phase-03-enemies.md`).
> Fill the **Human** sections. Set **Status** to `Ready` when the agent may implement it.
> The agent fills the **Agent** sections and never edits the requirement sections.

**Status:** Ready  <!-- Draft | Ready -->
**Depends on:** Phase 13

---

## 🧑 Goal
At a glance, in every world and level, the player can tell their own ship, the enemies, the enemy bullets and their own shots apart from the background and from each other. Gameplay objects stand out and the ground stays in the background, with the darksynth style (GD-60) kept.

## 🧑 Requirements

> ID format `P14-Rxx`. Every requirement is **MUST** (no SHOULD / MAY).
> Write each requirement so it is testable. Add acceptance criteria when "done" isn't obvious.

### P14-R01 — Background stays in the background  · MUST
The ground, props, sky and ground lights of every world are rendered darker and less saturated than the gameplay layer (player, enemies, bullets, pickups). The cap is a tunable value per world. Gameplay objects are never dimmed by this.

**Acceptance criteria**
- [ ] Given any level of Worlds 1–4, when the background is sampled during play (test API or screenshot), then no background pixel is brighter than `background_max_luminance` for that world, except for at most `background_bright_pixel_budget` of the screen (e.g. small lights).
- [ ] Given the same level, when the player ship, an enemy and an enemy bullet are on screen, then they are not dimmed by the background treatment.
- [ ] The look stays darksynth (GD-60): dark ground, neon accents, sunset gradients.

### P14-R02 — Reserved gameplay colors  · MUST
Each family of gameplay objects uses a color family that the background does not use, so color alone tells them apart:
- player ship accents and player shots: the cool family (cyan / ice blue, in line with GD-61);
- enemy neon lights: the enemy family (magenta / violet / blood red);
- enemy bullets: a dedicated, very bright family (e.g. hot white core with an orange-yellow or pink rim) used by nothing else;
- pickups: their own color family.
The background palette of every world leaves these hues out, or uses them only at low brightness (see R01).

**Acceptance criteria**
- [ ] The color families are defined in one game config (tunables) and every object family reads its colors from there.
- [ ] Given each world's background palette, when it is checked against the reserved enemy-bullet family, then no background color falls in it above the R01 brightness cap (unit test on the palettes).
- [ ] Enemy bullets and player shots never share a color.

### P14-R03 — Player ship stands out  · MUST
The player ship gets a light outline / rim glow in the player color, visible on every background, so the player always knows where they are. The hitbox (GD-21) is not drawn (reviewer, 2026-10-30, D-194: no hitbox marker).

**Acceptance criteria**
- [ ] Given any level, when the ship flies over the brightest part of the ground, then its outline is still visible (contrast ratio with the surrounding background ≥ `min_object_contrast`).
- [ ] While invincible (GD-22), the blinking still applies to the whole ship, outline included.

### P14-R04 — Enemies stand out  · MUST
Every enemy, mini boss and boss gets a rim light or outline in the enemy color, so its silhouette separates from the ground. Its dark metal body (GD-61) stays, but it is lit enough that its shape is readable on every world's ground.

**Acceptance criteria**
- [ ] Given every enemy kind (including veteran / elite kinds and boss parts), when it is placed over each world's ground, then its silhouette edge has a contrast ratio ≥ `min_object_contrast` with the ground around it.
- [ ] Destructible boss parts (GD-46) are outlined so the player can see which parts can still be hit.
- [ ] Enemies on the ground (turrets, tanks, etc.) are as readable as flying ones.

### P14-R05 — Enemy bullets are the most visible thing on screen  · MUST
Enemy bullets, missiles and lasers (GD-43) use the reserved enemy-bullet family (R02): a bright core, so they read on bright and dark ground alike; bullets have no dark rim or ring (reviewer, 2026-10-30, D-194). They have a minimum on-screen size, and they are drawn above everything else in the gameplay layer (above explosions, particles, player shots, enemies).

**Acceptance criteria**
- [ ] Given any enemy bullet kind, when it is over any world's ground, then its core has a contrast ratio ≥ `min_bullet_contrast` with the background around it.
- [ ] Every enemy bullet is at least `min_enemy_bullet_size` logical pixels across (GD-02 resolution); its hitbox does not change.
- [ ] Given an explosion or hit particles at the same spot, when an enemy bullet passes through, then the bullet is still drawn on top and visible.
- [ ] Enemy missiles that the player can shoot and laser warning lines (1 s warning, GD-43) are each recognizable from plain bullets (distinct shape), still within the enemy-bullet family.

### P14-R06 — Player shots don't hide danger  · MUST
Player shots (guns, laser, missiles at every level, GD-30/31) stay in the player color family and are toned down (opacity / brightness cap) so that, even at weapon level 5, they never hide enemy bullets.

**Acceptance criteria**
- [ ] Given weapon level 5 for each weapon, when an enemy bullet overlaps a player shot, then the enemy bullet is drawn on top and still meets `min_bullet_contrast`.
- [ ] Player shot brightness / opacity is capped by `player_shot_max_opacity`.

### P14-R07 — Effects don't clutter the screen  · MUST
Explosions, hit particles and bomb effects (GD-32, GD-62) fade fast enough and are capped in brightness and screen coverage so that they never hide the player ship or enemy bullets for long.

**Acceptance criteria**
- [ ] A single explosion covers at most `effect_max_screen_share` of the screen and is gone after `effect_max_duration`.
- [ ] Given a bomb, when it goes off, then the player ship and enemy bullets that survive it stay visible during the flash.

### P14-R08 — Readability check in the test API  · MUST
The test API (Phase 13 tooling) exposes a way to measure readability so R01–R07 can be checked automatically: e.g. render a level frame with known objects at known spots and return the contrast ratio of each object with its surroundings.

**Acceptance criteria**
- [ ] An e2e test runs, for one level of each world, the contrast check for the player ship, one enemy, one enemy bullet and one player shot, and asserts the R03–R06 thresholds.
- [ ] The F3 debug overlay (Phase 13) MUST NOT be required for the check.

## 🧑 Tunable values
| Name | Value | Notes |
|------|-------|-------|
| background_max_luminance | 0.35 (relative luminance, per world) | R01 |
| background_bright_pixel_budget | 2 % of screen | R01, small ground lights |
| min_object_contrast | 3:1 | R03, R04 (WCAG-style contrast ratio) |
| min_bullet_contrast | 4.5:1 | R05, R06 |
| min_enemy_bullet_size | 6 px | R05, logical pixels at 480×640 |
| player_shot_max_opacity | 0.7 | R06 |
| effect_max_screen_share | 15 % | R07 |
| effect_max_duration | 0.6 s | R07 |
| color families (player, enemy, enemy bullet, pickup) | see R02 | one place in game config |

## 🧑 Out of scope for this phase
- Colorblind modes or a settings option for the palette.
- New enemies, bullets, weapons or levels; changing hitboxes, damage or balance.
- Gameplay changes to make the game easier (lives, bullet speed, enemy counts).
- New world art or new background models (only their brightness / colors change).
- HUD layout changes.

## 🧑 Engineering additions for this phase
- The R08 contrast check runs in e2e, on the software WebGL renderer used by CI.
- Keep the Phase 13 frame time figures: no more long frames than at the end of Phase 13 (outline / glow effects must be cheap).

## 🧑 Manual validation checklist
- [ ] Runs on GitHub Pages / `make dev` without console errors
- [ ] In one level of each world, I can always see my ship, including over the brightest ground
- [ ] I can tell enemy bullets from my own shots at a glance, even with a level 5 weapon
- [ ] Enemies, ground enemies and boss parts are easy to see on every world's ground
- [ ] Explosions and bombs don't hide incoming bullets
- [ ] The game still looks darksynth

## 🧑 Notes, references, sketches
- Classic shmup readability rule: background dull, enemies mid, enemy bullets brightest; player shots semi-transparent.

---

## 🧑 Review feedback
> After the agent reports, write corrections here, then say **"Fix phase 14"**.
> The agent ticks each item when fixed.

- [ ] 

---

## 🤖 Implementation report
> Filled by the agent. Do not edit (comment in Review feedback instead).

### Questions / blockers
<!-- Ambiguities found before implementing. If non-empty, agent stops and waits. -->
P14-R02 (reserved colour families) conflicts with colours set by validated phases:
1. **Enemy neon**: enemies and bosses use cyan, green, orange, yellow and blue neon (P05-R01..R12, P07-R05, P08–P10 bosses), outside the magenta / violet / blood red family. Recolour them all into that family, or keep their colours and rely on the R04 rim light?
2. **Enemy bullets**: six bullet colours (red, magenta, green, orange, blue, purple; P10-R07 says "keep the phase 5 colours"). Move them all into one warm family (white core, orange / yellow / pink), or keep the six colours and give every world the P10-R07 contrast look (dark rim + white spark)?
3. **Player shots**: the minigun tracer is white / orange / red (phase 5 review), in the enemy-bullet family. Recolour it cyan / ice blue (and the missiles' flames)?
4. **Pickups**: weapon bonus acid yellow, life bonus pink, bomb bonus orange (P11-R07), all close to the enemy-bullet family. Move all three to one family (e.g. green, the shapes telling them apart), or keep them?

**Answers (reviewer, 2026-10-27):** 1. recolour every enemy and boss into the magenta / violet / blood red family; 2. one warm family for every enemy shot (white core, orange / yellow), dark rim + white spark in every world; 3. player shots recoloured cyan / ice blue; 4. all pickups in one green family, their shapes telling them apart.

### Plan
| Task | Requirement IDs |
|------|-----------------|
| Colour maths (luminance, contrast, hue families, folding, veil) in `core/math/color.ts`; game families and tunables in `game/config/readability.ts` | R02, all tunables |
| Background veil (engine `SceneryLook.veil`, `render/scenery/background-veil.ts`), one opacity per world | R01 |
| Recolour: enemy lights folded into the enemy family at `buildEnemyModel`; enemy bullets, missiles and lasers in the warm shot family; player tracer, impacts, missile tips cyan; bonuses green | R02 |
| Rims: `render/outline.ts` (metadata + outline renderer), player ships and enemy hulls tagged; hitbox marker (`GameView.hitboxMarker`) | R03, R04 |
| Enemy bullets: contrast look everywhere, drawn last over everything, minimum drawn size; missiles rimmed | R05 |
| Player shots toned to 0.7 (`tonedShots`) | R06 |
| Blasts capped in size and duration; dimmer bomb flash | R07 |
| Readability probe + `__GAME_TEST__.readability()` + e2e per world | R08 |

### Requirement traceability
| ID | Status (Done / Partial / Not done) | Code | Tests | Notes |
|----|-----------------------------------|------|-------|-------|
| P14-R01 | Done | `READABILITY.tones`, `game/view/readability-view.ts` (`toned`), `game/view/scenery-bindings.ts`, `render/scenery/atmosphere-of.ts`, `render/scenery/scenery-kit.ts` (`SceneryLook.tone`) | `readability.test.ts` (palette under the cap), `readability-view.test.ts`, `sky-layers.test.ts`, e2e `readability.spec.ts` (background luminance) | Review: the veil was replaced by a tone per world, applied at the source (D-130). Measured background (98th percentile luminance): 0.13 (1-2), 0.08 (2-1), 0.12 (3-1), 0.10 (4-1), cap 0.35 |
| P14-R02 | Done | `core/math/color.ts`, `READABILITY.families`, `enemy-mesh.ts` (`enemyColor`), `enemy-lasers.ts`, `enemy-look.ts`, `shot-look.ts`, `bonus-look.ts` | `color.test.ts`, `readability.test.ts`, `enemy-readability.test.ts` | Families: player 180–235°, enemy 265–5°, enemy shots 18–58°, pickups 85–160°; saturation ≥ 0.5 (see Deviations) |
| P14-R03 | Done | `render/outline.ts`, `readability-view.ts` (`outlinedShips`, `buildHitboxMarker`), `game-play.ts` | `outline.test.ts`, `readability-view.test.ts`, e2e | Ship contrast 10–13:1 measured. The marker is a white dot ringed cyan, the hitbox's radius, on the ship's pivot (it blinks with the ship) |
| P14-R04 | Done | `enemy-mesh.ts` (`rimOf`, `setOutline` on every hull, boss parts included), `OutlineLayer` | `enemy-readability.test.ts`, `outline.test.ts`, e2e | Enemy contrast 4.1–11:1 measured |
| P14-R05 | Done | `enemy-shot-renderer.ts`, `enemy-lasers.ts`, `enemy-look.ts`, `render/node-adopter.ts` (`ON_TOP_ALPHA_INDEX`) | `contrast-shots.test.ts`, `node-adopter.test.ts`, `readability.test.ts`, e2e | Bullet contrast 6.1–11.6:1 measured. Missiles: an orange rim; warning lines: wide, white core. Bullets, then missile flames and lasers, drawn over every playfield mesh that sets no draw order (D-156, found at validation) |
| P14-R06 | Done | `readability-view.ts` (`tonedShots`), `game/index.ts`, `render/node-adopter.ts` | `readability-view.test.ts`, `contrast-shots.test.ts` (bullets over everything), `node-adopter.test.ts` (player shots, which set no draw order, drawn under them), e2e | Additive player shot materials capped at 0.7 |
| P14-R07 | Done | `enemy-look.ts` (`blasts`), `blast-particles.ts` (`maxRadius`), `bomb-look.ts` | `blast-readability.test.ts`, `blast-particles.test.ts` | Simulated: at most 7.8 % of the screen, over by 0.55 s (cap 15 %, 0.6 s) |
| P14-R08 | Done | `core/math/pixel-contrast.ts`, `app/readability-probe.ts`, `debug/test-api.ts`, `main.ts` | `pixel-contrast.test.ts`, `test-api.test.ts`, e2e `readability.spec.ts` (1-2, 2-1, 3-1, 4-1) | No F3 overlay needed |

### Gate results
```
Light verification (implementation): typecheck ✔ / build ✔ / e2e 131 passed, the 4 new readability tests included
Lint, unit tests and coverage: deferred to /validate-phase (CLAUDE.md).

Full gate (/validate-phase 14, 2026-10-28), make check:
  lint ✔ (ESLint 0 warnings, Prettier)  typecheck ✔
  unit: 199 files, 1681 tests passed
  coverage: 99.03% lines, 87.6% branches, 98.19% statements, 98.18% functions (thresholds met)
  build ✔ (no test API in dist)  e2e: 132 passed (6.4 min)
```
The first full run failed 6 unit tests, all failing since the phase's first commit (4a0d612): enemy bullets were not drawn over the playfield meshes that set no draw order (fixed, D-156), the reactor cores were folded twice and too pale for the enemy family (fixed, D-156), and four tests expected pre-phase-14 colours or Babylon's unset `renderOutline` as `false` (updated). The second run is the one above.

Note: port 4173 was held by a `vite preview` of another project on this machine (`~/pewet`), which Playwright reuses outside CI. Every e2e run of this phase, the full gate's included, used the same config pointed at port 4183 (a throwaway local config, not committed). `make e2e` will test the wrong app while that server runs.

Perf (engineering addition), `scripts/measure-perf.mjs`, 120 s of 2-1, 3-1, 4-1, software WebGL, same machine and load:

| Level | main: frames > 50 ms | phase-14: frames > 50 ms | main / phase-14: median drawn frame |
|-------|---------------------|--------------------------|-------------------------------------|
| 2-1 | 11 | 8 | 2 / 3 ms |
| 3-1 | 9 | 12 | 4 / 5 ms |
| 4-1 | 30 | 32 | 4 / 5 ms |

No more long frames than `main` within noise (this machine was busier than at the end of Phase 13, so both are above Phase 13's 0–3); about 1 ms more per drawn frame for the rims.

### Review fixes
Made at the reviewer's request during review, without items in "Review feedback": D-126..D-155 (World 4 a bright midday city, brighter hulls, the `props/` viewer page, the background darkened at the source instead of a veil, ground glow, blasts without flash, ground drawn twice as big, boulevards, faster level builds and frames, no sea under World 4, lives and bombs kept between levels without limit, the HUD in one bar at the bottom). D-154 amends P11-R05 / P11-R07 and D-155 the place of the score (P11-R02); this phase's "HUD layout changes" out-of-scope line was overridden by the reviewer.

### How to test manually
- `make dev`, play one level of each world (or `?level=1-2&t=40`, `?level=2-1&t=40`, `?level=3-1&t=40`, `?level=4-1&t=90`).
- Look for: the darker ground; the cyan rim round the ship and the white dot on its hitbox; enemies with violet / magenta / crimson lights and a light rim; enemy bullets orange to yellow with a dark ring and a white heart, drawn over explosions and over your own shots; your shots cyan and dimmer; bonuses green (hexagon, heart, B ball); short explosions; a dim bomb flash (R).
- e2e: `npx playwright test tests/e2e/readability.spec.ts`; each test's annotation holds the measured numbers.

### Deviations from spec
- R02: families need a saturation of 0.5 (pale sand and beige are no family's colour), so the desert and beach sand do not count as orange. Hot pink is not in the enemy-shot family: it would overlap the enemy magenta.
- R02: enemy and boss neon tables are kept and folded at drawing time (D-121), not rewritten.
- R08: R06 gives no contrast for player shots; the e2e test checks 2:1 (`minPlayerShotContrast`, a new tunable).
- R07: "gone after 0.6 s" is read as every particle (smoke included) gone; explosions are now noticeably shorter and smaller, boss deaths included.

### Known limitations
- Rims use flat-shaded normals, so at sharp corners the rim has small gaps (visible close up, not at play size).
- The probe measures one object of each kind per frame, the first well inside the view; e2e checks one moment per world.
- Menus (ship select, viewers) show the new colours but no veil or rims: they are not gameplay screens.

### Suggestions for future phases
- A colourblind palette option (out of scope here) could reuse the families and the fold.
- The veil opacities could follow the time of day (World 2 night needs less than midday).
