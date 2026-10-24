# Phase 05 — First Enemies

**Status:** Ready  <!-- Draft | Ready -->
**Depends on:** Phase 4

---

## 🧑 Goal
The game has its first 10 kinds of enemies, each with its own code-generated ship model, movement and attack. They can all be watched and shot on an `enemies/` debug page.

## 🧑 Requirements

> ID format `P05-Rxx`. Every requirement is **MUST** (no SHOULD / MAY).
> Write each requirement so it is testable. Add acceptance criteria when "done" isn't obvious.
> All enemies follow GD-43 to GD-45 (attacks and movement) and GD-61 (dark metallic hull with neon lights). Sizes are given relative to the medium player ship length (`L`).
> HP, speeds, fire rates and points are listed in **Tunable values**.

### P05-R01 — Gnat (swarm drone)  · MUST

**Shape:** a small flat disc (0.5 L) with three short fins at 120° and a neon ring around its rim.

**Behavior:** comes in groups of 5, one after the other, following the same predefined S-shaped path from the top of the screen to the bottom. It does not shoot. Killed by a single level 1 bullet.

**Acceptance criteria**
- [ ] Given a Gnat group spawns, then the 5 Gnats follow the same path with a fixed delay between them.
- [ ] Manual visual validation

### P05-R02 — Hornet (diver)  · MUST

**Shape:** an arrow head (0.7 L) with sharply swept wings and a single red neon eye at the nose.

**Behavior:** enters from the top, stops for 0.5 s while turning its nose to the player, then dives in a straight line toward where the player was, accelerating, and leaves the screen. It does not shoot.

**Acceptance criteria**
- [ ] Given a Hornet has finished its pause, then it dives toward the player position recorded at the end of the pause.
- [ ] Manual visual validation

### P05-R03 — Scout (aimed shooter)  · MUST

**Shape:** a small delta wing (0.8 L) with twin tail booms and a cyan neon strip along each boom.

**Behavior:** flies straight down at a slow speed and fires one bullet aimed at the player every 1.5 s.

**Acceptance criteria**
- [ ] Given a Scout is on screen, then each of its bullets moves along the line from the Scout to the player at the moment it was fired.
- [ ] Manual visual validation

### P05-R04 — Strafer (fan shooter)  · MUST

**Shape:** a wide, flat flying wing (1.2 L wide) with a row of magenta neon lights along the leading edge.

**Behavior:** enters from the left or right side in the top third of the screen, crosses horizontally and leaves on the other side. Every second it fires a fan of 3 bullets straight down (preset directions: −15°, 0°, +15°).

**Acceptance criteria**
- [ ] Given a Strafer fires, then its 3 bullets leave at −15°, 0° and +15° from straight down, whatever the player position.
- [ ] Manual visual validation

### P05-R05 — Weaver (sine flyer)  · MUST

**Shape:** a twin-hull catamaran (0.9 L) with the two hulls joined by a glowing green neon bar.

**Behavior:** moves down along a sine wave (left–right sway). Every 2 s it fires a pair of bullets aimed at the player, one from each hull.

**Acceptance criteria**
- [ ] Given a Weaver moves, then its horizontal position follows a sine of its vertical progress.
- [ ] Manual visual validation

### P05-R06 — Spinner (spiral turret)  · MUST

**Shape:** a ring (1 L) with four spokes and a pod at the end of each spoke, an orange neon core in the centre.

**Behavior:** descends to a point in the upper half of the screen and stops. It then spins for 3 s while firing a spiral of bullets from its four pods, then leaves upward.

**Acceptance criteria**
- [ ] Given a Spinner is in its firing state, then bullets leave from its 4 pods in directions that rotate with the ring.
- [ ] Given 3 s of firing have passed, then the Spinner stops firing and leaves upward.
- [ ] Manual visual validation

### P05-R07 — Lancer (laser)  · MUST

**Shape:** a long needle hull (1.3 L) with a glowing emitter at the nose and two small side fins.

**Behavior:** moves to a fixed point in the top part of the screen and stops. A thin warning line is shown straight down from its emitter for 1 s, then it fires a laser along that line for 1.5 s, then it moves away. It does not move while the warning line or the laser is shown.

**Acceptance criteria**
- [ ] Given a Lancer starts its attack, then a warning line is shown for 1 s before the laser appears on the same line (GD-43).
- [ ] Manual visual validation

### P05-R08 — Rocketeer (missile carrier)  · MUST

**Shape:** a bulky hull (1.3 L) with a missile pod on each side; the missile tips glow red when loaded.

**Behavior:** descends slowly. Every 3 s it launches one missile from each pod. The missiles turn toward the player with a limited turn rate. Missiles can be shot down by the player (GD-43).

**Acceptance criteria**
- [ ] Given a Rocketeer missile is in flight, then it turns toward the player no faster than its turn rate.
- [ ] Given a player shot hits a missile, then the missile is destroyed with a small explosion.
- [ ] Manual visual validation

### P05-R09 — Bulwark (heavy gunship)  · MUST

**Shape:** a heavy, wide hull (1.6 L) covered with front armour plates and a blue neon visor slit.

**Behavior:** enters from the top, slowly moves down to the upper third of the screen, drifts left and right for 8 s, then leaves downward. Every 2 s it fires a spread of 5 bullets centred on the player (aimed fan, 10° apart).

**Acceptance criteria**
- [ ] Given a Bulwark fires, then the middle bullet of the spread is aimed at the player.
- [ ] Manual visual validation

### P05-R10 — Splitter (splits on death)  · MUST

**Shape:** a hexagonal core (1 L) with three small pods attached around it, purple neon seams between the core and the pods.

**Behavior:** flies down a predefined curved path and fires one aimed bullet every 2.5 s. When it is destroyed, its three pods break off and each pod dives at the player like a Hornet (P05-R02), at a smaller size.

**Acceptance criteria**
- [ ] Given a Splitter is destroyed, then 3 pods appear at its position and dive toward the player.
- [ ] Manual visual validation

### P05-R11 — Debug page `enemies/`  · MUST

The game shall provide an `enemies/` debug endpoint that shows the 10 enemy kinds for visual validation, over the Level Zero scenery with the playfield camera.

- A list lets the user pick one enemy kind; the page then spawns that kind (a whole group for the Gnat) and spawns it again when it has left the screen or was destroyed.
- A "model" view shows the picked enemy alone, like the `player_ship/` page: close up on the enemy, rotating slowly, on a dark background (no scenery). In this view, the left / right arrow keys switch to the previous / next enemy.
- A player ship is present and can be moved and can shoot (any weapon and level from phase 3), so the attacks aimed at the player and the destruction of the enemies can be checked. The player cannot die on this page.
- Hits on enemies emit particles and destroyed enemies explode (GD-62).
- The page shows the FPS / polygons debug tile, like `player_shots/`.

**Acceptance criteria**
- [ ] Given the user opens `enemies/`, then the page loads without console errors and every enemy kind can be picked.
- [ ] Given an enemy kind is picked, then that enemy spawns and performs its behavior.
- [ ] Given the model view, when the user presses the right (left) arrow, then the next (previous) enemy is shown close up.
- [ ] Manual visual validation

### P05-R12 — Carrier (Gnat launcher)  · MUST

Added at the reviewer's request during the phase 5 review (2026-10-24).

**Shape:** a fat flying carrier (1.8 L): a wide, rounded hull with a spine along its back, and two launch ports on each side, visible from above, with amber neon lights. Nothing on its back looks like a landing deck (review, 2026-10-24).

**Behavior:** enters from the top and slowly flies straight down the screen, then leaves at the bottom. It does not shoot. Every 3 s, a Gnat (P05-R01) comes out of each side port; they fly out sideways, then down the screen. It stops launching in the lower part of the screen. It is listed on the `enemies/` page (P05-R11) like the other kinds.

**Acceptance criteria**
- [ ] Given a Carrier is over the playfield, when its launch timer runs out, then Gnats appear at its side ports and fly away from it, out sideways then down.
- [ ] Given a Carrier, then it never shoots.
- [ ] Manual visual validation

## 🧑 Tunable values
| Name | Value | Notes |
|------|-------|-------|
| gnat_hp / points | 10 / 50 | |
| gnat_group_size / delay | 5 / 0.3 s | |
| hornet_hp / points | 20 / 100 | |
| hornet_pause | 0.5 s | |
| scout_hp / points | 30 / 100 | |
| scout_fire_interval | 1.5 s | |
| strafer_hp / points | 40 / 150 | |
| strafer_fire_interval / fan | 1 s / ±15° | |
| weaver_hp / points | 30 / 120 | |
| weaver_fire_interval | 2 s | |
| spinner_hp / points | 60 / 200 | |
| spinner_fire_duration | 3 s | |
| lancer_hp / points | 80 / 250 | |
| lancer_warning / laser | 1 s / 1.5 s | |
| rocketeer_hp / points | 100 / 300 | |
| rocketeer_fire_interval | 3 s | |
| enemy_missile_hp | 10 | One level 1 bullet |
| bulwark_hp / points | 200 / 500 | |
| bulwark_fire_interval / spread | 2 s / 5 × 10° | |
| bulwark_stay | 8 s | |
| splitter_hp / points | 50 / 200 | |
| splitter_pod_hp / points | 10 / 50 | |
| splitter_fire_interval | 2.5 s | |
| carrier_hp / points | 300 / 600 | P05-R12 |
| carrier_speed | 30 px/s | P05-R12 |
| carrier_launch_interval | 3 s, 1 Gnat a port (2 a side) | P05-R12; none below 30 % height |

## 🧑 Out of scope for this phase
- Spawning enemies in Level Zero or in any real level (waves by distance, GD-40).
- Damage to the player, health bar, lives and game over.
- Bonuses dropped by enemies, scoring display and high score.
- Mini bosses and final bosses.
- Sound effects.

## 🧑 Engineering additions for this phase
- Enemy behaviors (movement, fire timing, aiming) are pure logic in `core/` and unit tested; the 10 kinds and their tunables live in `src/game/`.
- An e2e smoke test opens `enemies/` and picks every enemy kind.

## 🧑 Manual validation checklist
- [ ] Runs on GitHub Pages / `make dev` without console errors
- [ ] Each of the 10 enemies looks like its description and is readable at game scale
- [ ] Each enemy moves and attacks as described
- [ ] Enemies can be shot and explode; Rocketeer missiles can be shot down
- [ ] 60 fps on `enemies/` with the busiest enemy (Spinner, Bulwark)

## 🧑 Notes, references, sketches
<!-- Links, images, pseudo-code, example level layouts... -->

---

## 🧑 Review feedback
> After the agent reports, write corrections here, then say **"Fix phase 05"**.
> The agent ticks each item when fixed.

- [x] Model view like the player ship view: close up on the enemy, left / right arrows to switch enemy, dark background (2026-10-24; P05-R11 updated in the spec at the reviewer's request). Fixed: the model view now has its own scene (`app/enemy-close-up.ts`).
- [x] Add reactor effects to the enemy ships, some may have several (2026-10-24). Fixed: animated reactor flames in each enemy's neon colour.
- [x] Reduce the polygon count of the reactor effect (2026-10-24). Fixed: about 40 triangles a reactor instead of about 150.
- [x] All the reactor effects the same light blue colour (2026-10-24). Fixed: the core and flame of every enemy reactor use one light blue, the player ships' flame colour.
- [x] Most ships looked like a bunch of cubes put together: better geometry without raising the polygon count too much (2026-10-24). Fixed: tapered fuselages, knife-edged wings and sloped armour (`SolidBuilder.loft` and `bevelSlab`), about 19 % more polygons over the 10 models.
- [x] Make them more aggressive looking (2026-10-24). Fixed: fangs, pincers, horns, claws, saw teeth, serrated edges, forward wingtip claws and slanted neon eye slits.
- [x] Remove the added spikes; some ships still look like basic geometry stuck together, make the parts better integrated (2026-10-24). Fixed: spikes removed; one continuous fuselage per ship with its canopy painted on, pods faired or fitted into their bodies, the Bulwark's armour in one band, the Splitter's pods as wedges fitted around its core.
- [x] Rework the Gnat model, make it look like an unmanned drone (2026-10-24). Fixed: a tri-rotor drone, three ducted fans with spinning blades, a sensor turret, an antenna, no cockpit.
- [x] Improve the Hornet's movement: the pause between the flight and the dive was bad, make a smooth transition (2026-10-24). Fixed: it brakes into its stop, its nose eases round to the player, and the dive starts from rest.
- [x] Create a new kind of ship: a fat flying carrier that slowly flies down without shooting, with vents on its sides that spawn Gnats (2026-10-24; P05-R12 added to the spec at the reviewer's request). Fixed: the Carrier, its model, its behaviour and its entry on `enemies/`.
- [x] Rework the Carrier's design: remove the landing stuff on its back, add visible ports on the sides for the Gnats (2026-10-24; P05-R12's shape and behaviour updated to match). Fixed: flight deck, runway lights and island gone, a spine along its back instead; two glowing launch ports in the sloped outer wall of each side sponson, and each Gnat now comes out of one of them.
- [x] Add a wireframe view like the model view, to see the models' polygons (2026-10-24). Fixed: a "Wireframe (V)" view on `enemies/`: the model view's close-up drawn as lines.
- [x] Pick a colour for the model and wireframe views so the models can be seen better: dark grey (2026-10-24). Fixed: both views now have a neutral dark grey background instead of the near-black purple of `player_ship/`.
- [x] The wires were still hard to see; improve that, and show the hitbox in the wireframe view (2026-10-24). Fixed: the hull's edges are drawn in a light unlit grey without glow, and a red circle shows the enemy's hit radius.
- [x] Some models (like the Gnat's little shiny diamond) have details only visible from the bottom: remove them (2026-10-24). Fixed: removed the Gnat's sensor turret, lens and arms, the Scout's gun under its nose, the Weaver's guns under its bows and the Bulwark's chin gun.
- [x] Change the colour scheme of the enemy ships so they are easier to see on screen (2026-10-24). Fixed: each hull is dark metal tinted towards the enemy's neon colour, faintly lit by it, with a thin neon line around its silhouette.

---

## 🤖 Implementation report
> Filled by the agent. Do not edit (comment in Review feedback instead).

### Questions / blockers
None. The requirements were drafted by the agent at the reviewer's request (2026-10-24), and the reviewer chose "set Ready and implement" without changes. Values the spec leaves open use the agent's defaults below (D-032); they are all in `src/game/config/enemies.ts` and `enemy-look.ts`.

### Plan
| Task | Requirement IDs |
|------|-----------------|
| Engine: abstract `Enemy` + `EnemyContext` + `EnemyKindDefinition`, paths and fans, `EnemyShots` (bullets, homing missiles that can be shot down, lasers with a warning), `EnemyWorld` (step, score, blasts, spawns on death, removal), `GameDefinition.enemyKinds` | P05-R01..R10 |
| Game sim: the 10 enemy classes + the Splitter pod, kind registry, tunables | P05-R01..R10 |
| View: 10 + 1 code-generated models (dark PBR metal + neon, charging lights), enemy shot renderer, explosions, `GameView.enemies` | P05-R01..R10, GD-61, GD-62 |
| `enemies/` page: Level Zero view + playfield layer, player ship (move + shoot, cannot die), respawn, model view, panel, keys, stats tile, e2e test API | P05-R11 |
| Unit tests (engine with the sample game, content with `src/game/`) and e2e | all |

### Requirement traceability
| ID | Status (Done / Partial / Not done) | Code | Tests | Notes |
|----|-----------------------------------|------|-------|-------|
| P05-R01 | Done | `game/sim/enemies/gnat.ts`, `game/view/enemies/small-enemy-models.ts` | `game/sim/enemies.test.ts`, `enemy-kinds.test.ts`, `enemy-models.test.ts`, e2e | Group of 5, 0.3 s apart, one S-shaped path (mirrored at random) |
| P05-R02 | Done | `hornet.ts` | `enemies.test.ts`, e2e | Stops at 72 % height, braking into it; dive heading fixed at the end of the pause; dives from rest |
| P05-R03 | Done | `scout.ts` | `enemies.test.ts`, e2e | Shoots only over the playfield |
| P05-R04 | Done | `strafer.ts` | `enemies.test.ts`, e2e | Pass at 80 % height (top third) |
| P05-R05 | Done | `weaver.ts` | `enemies.test.ts`, e2e | X = centre + 90 sin(2π·down / 280) |
| P05-R06 | Done | `spinner.ts`, `heavy-enemy-models.ts` | `enemies.test.ts`, e2e | Bullets leave each pod outwards; ring turns 110°/s while firing |
| P05-R07 | Done | `lancer.ts`, `core/systems/enemy-shots.ts` | `enemies.test.ts`, `enemy-shots.test.ts`, `enemy-renderers.test.ts`, e2e | Emitter glows through the warning |
| P05-R08 | Done | `rocketeer.ts`, `enemy-shots.ts` | `enemies.test.ts`, `enemy-shots.test.ts`, `enemy-world.test.ts`, e2e | Missiles home 3.5 s at 90°/s, 10 HP, explode when shot down |
| P05-R09 | Done | `bulwark.ts` | `enemies.test.ts`, e2e | Fires on entry, drift and exit |
| P05-R10 | Done | `splitter.ts` (pods are `Hornet`s) | `enemies.test.ts`, `enemy-world.test.ts`, e2e | Pods pause 0.35 s, then dive |
| P05-R12 | Done | `game/sim/enemies/carrier.ts`, `game/view/enemies/carrier-model.ts` | `carrier.test.ts`, `enemy-kinds.test.ts`, `enemy-models.test.ts`, e2e | Launched Gnats follow a path from the vent: out 64 px sideways, then down past the bottom |
| P05-R11 | Done | `app/start-enemy-viewer.ts`, `enemy-viewer-scene.ts`, `enemy-close-up.ts`, `enemy-viewer-shots.ts`, `ui/enemy-viewer-panel.ts`, `render/enemy-layer.ts`, `render/node-adopter.ts`, `enemies/index.html` | `start-enemy-viewer.test.ts`, `enemy-viewer-panel.test.ts`, `node-adopter.test.ts`, `enemy-layer.test.ts`, `tests/e2e/enemies.spec.ts` | See "How to test manually" |

### Gate results
Light verification only (CLAUDE.md, step 5). Lint, unit tests and coverage run in the full `make check` gate of `/validate-phase`.
```
make typecheck  ✔ (0 errors)
make build      ✔ (ENG-52 check now covers __GAME_TEST__ and __ENEMIES_TEST__; main chunk 1,416 kB / 368 kB gzip)
make e2e        ✔ 40 passed (35 from earlier phases + 5 new in enemies.spec.ts)
```
Review fix (close-up model view): typecheck ✔, build ✔, e2e 40 passed.
Review fix (reactors): typecheck ✔, build ✔. In the first full e2e run, the model view test failed under the parallel load: its keys were pressed before the page drew its first frames (the readout still showed the previous kind). The enemies tests now wait for the FPS tile first (no timeout changed); the spec alone and the next full run passed, e2e 40 passed.
Review fix (lighter reactors): typecheck ✔, build ✔, e2e 40 passed.
Review fix (light blue reactors): typecheck ✔, build ✔, e2e 40 passed.
Review fix (less boxy ships): typecheck ✔, build ✔, e2e 40 passed.
Review fix (integrated parts): typecheck ✔, build ✔, e2e 40 passed.
Review fix (Gnat drone): typecheck ✔, build ✔, e2e 40 passed.
Review fix (Hornet movement): typecheck ✔, build ✔, e2e 39 passed + 1 failed on the first run (the P05-R11 model view test, the known shader-compile stall on the first close-up draw, unrelated to the Hornet), passed on its own rerun.
Review fix (Carrier, P05-R12): typecheck ✔, build ✔, e2e 40 passed.
Review fix (Carrier rework): typecheck ✔, build ✔, e2e 39 passed + 1 failed on the first run (the P05-R11 model view test, the known stall on the first close-up draw: still "Enemies: 5" after 5 s), passed on its own rerun.
Review fix (wireframe view): typecheck ✔, build ✔, e2e 40 passed.
Review fix (dark grey background): typecheck ✔, build ✔, e2e 40 passed.
Review fix (readable wireframe, hitbox): typecheck ✔, build ✔, e2e 40 passed.
Review fix (nothing underneath): typecheck ✔, build ✔, e2e 39 passed + 1 failed on the first run (the P05-R11 model view test, the known stall on the first close-up draw: still "Enemies: 5" after 5 s), passed on its own rerun.
Model view warm-up: typecheck ✔, build ✔, e2e 40 passed.
Review fix (enemy colours): typecheck ✔, build ✔, e2e 40 passed.
Review fix (aggressive look): typecheck ✔, build ✔. The first full e2e run had 2 failures under load (38 passed); the rerun passed, e2e 40 passed.
Coverage before this phase: 99.35 % lines (phase 4). New numbers come with `/validate-phase 5`.

### How to test manually
1. `make dev`, open http://localhost:5173/enemies/ (or `enemies/` on GitHub Pages).
2. Pick an enemy with its button, or N / B (next / previous). It appears over Level Zero and comes back about 1 s after its group has gone.
3. Fly the ship with the arrows or WASD (by key position, so ZQSD on AZERTY). It fires all the time; F stops and starts the fire. X switches the weapon (bullet, laser, missile), 1-5 sets the level. The ship cannot be hit.
4. M (or "Model") shows the picked enemy alone, close up on a dark background, turning (as on `player_ship/`). ← / → switch to the previous / next enemy; drag to orbit, wheel to zoom. M again goes back to the level.
5. P pauses. The panel shows the enemies on screen, enemy shots, enemies destroyed and the score. The FPS / polygons tile is at the top right.
6. Things to look at: Lancer warning line (1 s, blinking) then red beam; Rocketeer missiles (shoot them down: small explosion); Splitter breaking into 3 pods; Spinner spiral; Bulwark spread aimed at the ship (move the ship to see it follow).

### Review fixes
- Model view (review, P05-R11 updated): instead of a bigger model over Level Zero, the model view switches to its own scene (`app/enemy-close-up.ts`): dark background and lights of `player_ship/`, an orbit camera framed so the enemy fills about 60 % of the width, 45° above it, turning at 0.6 rad/s. ← / → switch the enemy there (in the level view the arrows still fly the ship); the camera's own arrow-key input is removed. Drag orbits, the wheel zooms. The FPS / polygons tile shows the scene on screen. The old in-level showcase, `EnemyBindings.showcaseScale` and `screenCentreY` were removed.

- Reactors (review): every enemy but the Spinner (it spins on itself) has 1 to 4 reactors at the back: a dark nozzle, a neon core and the player ships' animated flame (exhaust cone, hot inner cone, plasma puffs, flicker), in the enemy's neon colour with a whiter inner flame. Gnat 1, Hornet 1, Scout 2 (booms), Strafer 4 (trailing edge), Weaver 2 (hulls), Lancer 3 (main + fins), Rocketeer 2, Bulwark 3 (main + engine pods, replacing the two neon strips), Splitter 1, Splitter pod 1. `buildReactorFlame` now takes optional materials (blue by default, unchanged for the player ships); `EnemyParts.reactor(at, radius)` adds one; enemy models step their animations in `sync`. Sizes in `ENEMY_LOOK.reactor`.
- Lighter reactors (review): an enemy reactor went from about 150 to about 40 triangles. The nozzle is an open 6-sided band (no caps) and the core a flat hexagon across its mouth; the flame cones have 4 sides and no caps (their base is hidden by the nozzle); 2 tetrahedron puffs (4 triangles) instead of 3 icosahedra (20). `FlameSize.light` turns this on; the player ships' flames are unchanged. The Rocketeer close-up went from 952 to 520 triangles in all.
- Light blue reactors (review): every enemy reactor (glowing core, exhaust, inner flame, puffs) now uses the same light blue, `ENEMY_LOOK.reactor.color` = [0.55, 0.85, 1], the player ships' flame colour, instead of the enemy's neon colour. The neon lights and charge lights keep each enemy's colour.
- Less boxy ships (review): two new `SolidBuilder` primitives (engine, game-agnostic): `loft` stretches a cross-section along Z through stations (half width, bottom, top), closing to a point at a nose or tail, or left open at the bottom for a canopy; `bevelSlab` is a slab whose sides slope from a waist to inset top and bottom faces (`insetOutline` in `render/geometry/outline.ts`), giving knife-edged wings and chamfered plates. Section presets (hull, pod, canopy) are in `enemy-shapes.ts`. Fuselages, booms, canopies, nacelles and gun pods are now lofts; wings, fins, spokes, struts and armour bevelled slabs; the Strafer's leading-edge lights follow the edge; the Bulwark's visor follows the tower front; the Gnat's fins are swept blades; the Rocketeer's missile pods taper at both ends. Sizes are unchanged (same outlines). Polygons in the close-up view (model and reactors), before → after: Gnat 328 → 364, Hornet 208 → 292, Scout 344 → 448, Strafer 648 → 680, Weaver 400 → 552, Spinner 704 → 752, Lancer 440 → 516, Rocketeer 520 → 716, Bulwark 552 → 684, Splitter 416 (unchanged, already round); 4,560 → 5,420 in all (+19 %).
- Aggressive look (review): new shape helpers in `enemy-shapes.ts`: `spike` (a fang, claw or horn outline), `angryEyes` (two eye slits whose outer ends sweep back, a frown seen from above) and `decal` (a flat light on a hull, 2 triangles). Gnat: hooked claws, 6 saw teeth on the rim, eyes on the dome. Hornet: pincers either side of the nose, serrated wing trailing edges (its single eye kept, as the spec says). Scout: fangs either side of the nose, notched trailing edge, eyes on the canopy. Strafer: sharper nose, forward wingtip claws, eyes. Weaver: fangs inside the bows, swept tail fins, eyes on each canopy. Spinner: 8 saw teeth on the ring, hooked the way it turns. Lancer: pincers either side of the emitter, eyes. Rocketeer: a ram at the nose, swept fins at the back of the missile pods, red eyes on the armour. Bulwark: ram horns and spikes at the wing corners (the chevron visor stays). Splitter: blades in the two front gaps between the pods. Sizes stay within the spec (the size test allows 15 %; the longest change is the Hornet at about +3 %). Polygons in the close-up view: Gnat 540, Hornet 396, Scout 548, Strafer 744, Weaver 680, Spinner 880, Lancer 580, Rocketeer 804, Bulwark 796, Splitter 472; 6,440 in all (+19 % over the less boxy models). The eyes are flat decals and the small teeth plain slabs to keep the count down.
- Integrated parts (review): the spikes of the previous fix are gone (the `spike` helper too); the serrated wing edges and the eye slits stay where they sit flat on the hull (Gnat dome, Rocketeer armour). `loft` takes options: `open`, and `paint` to colour some faces of the section between some stations, so a canopy is painted on the fuselage's back (`FIGHTER_SECTION` and `canopyPaint` in `enemy-shapes.ts`) instead of being another solid on top; `sideStripe` lofts a neon stripe along a side of a section (the Lancer's flanks). Hornet, Scout, Strafer, Weaver and Lancer: one fighter fuselage each, the wing roots inside it (the Scout's and Strafer's bodies are blended into the middle of the wing). Spinner: the pods grow out of the ring (bevelled teardrops wrapping it), their muzzles at the tip. Rocketeer: thick swept fairings from the hull into the missile pods instead of pylons, nose back to the original. Bulwark: one bevelled armour band along the front instead of 5 plates, the engine nacelles sunk into the back, a chin gun. Splitter: the pods are wedges fitted around the core's flats with a neon seam each (the core's six flats face the three pods and the reactor); the broken-off pod is the same wedge. Polygons in the close-up view: Gnat 444, Hornet 408, Scout 592, Strafer 788, Weaver 656, Spinner 816, Lancer 580, Rocketeer 724, Bulwark 632, Splitter 464; 6,104 in all (5,420 before the aggressive look, 6,440 with it).
- Gnat drone (review): an unmanned tri-rotor drone: the small flat disc body with the neon ring around its rim, three short arms at 120° (the spec's fins) out to ducted fans, a dark sensor turret under the nose with a neon lens, a short antenna, the reactor at the back; no canopy, no eyes. `EnemyParts.rotor(at, radius)` adds a rotor: blades and a hub on their own node, spun by a model animation (`ENEMY_LOOK.rotor`: 2 blades, 30 rad/s). Polygons in the close-up view: 932 (444 before), the most detailed small enemy; ducts and hubs are kept to 8 and 4 sides.
- Hornet movement (review): it used to halt at once from 220 px/s, sit still, then jump to 160 px/s. Now it flies down at full speed until its braking distance, then decelerates at a constant `entryBrake` (440 px/s², about 0.45 s and 55 px) to rest at the stop height; its nose starts coming round to the player as it brakes and eases in on it (turn rate proportional to the angle left, capped at half a turn per pause); after the 0.5 s pause it dives from rest at `diveAcceleration` 1000 px/s² (700 from 160 px/s before), up to the same 620 px/s. The `diveSpeed` option is gone. Splitter pods share the code: they dive from rest at 950 px/s². New test: the speed never changes by more than the braking or dive acceleration allows in one step.
- Carrier (review, new requirement P05-R12): a fat carrier, 1.8 L, 300 HP, 600 points. It flies straight down at 30 px/s and never shoots; every 3 s (the first 1.2 s after it is over the playfield) a pair of Gnats comes out of each side vent, 18 px from its centre, through `EnemyContext.spawn` like the Splitter's pods. They are ordinary Gnats (same model, points and speed) on a path from the vent: out sideways, then down past the bottom of the screen, the second of each pair 0.3 s behind. It stops launching below 30 % of the screen height, too close to the player. Its `charge` lights the vents as the next launch comes. Model (`carrier-model.ts`): a lofted hull (the hull section, the widest of all), a dark flight deck with amber runway lights, a command island with a bridge window, a sponson along each side whose top holds a glowing vent with dark louvres across it, and 2 reactors. Polygons in the close-up view: 756. Tunables in `ENEMY_CONFIG.carrier` and `ENEMY_LOOK.neon.carrier`.
- Carrier rework (review): no landing deck any more: the flight deck, its runway lights and the island are gone; a raised spine runs along the back with an amber stripe on each flank. Each side sponson's outer wall now slopes out at about 48°, so it faces the camera, and holds two launch ports: a dark frame with a mouth that glows as the next launch comes (the vent and louvres on top are gone). The ports' positions are in `ENEMY_CONFIG.carrier.ports` (21 px to each side; 9 px up and 1 px down the screen from the centre) and the model and the simulation both read them: every 3 s each port launches one Gnat (the rear one 0.3 s after the front one), from where the port is. Polygons in the close-up view: 512 (756 before).
- Wireframe view (review): a third view on `enemies/`, "Wireframe (V)" (button or V key; V again goes back to the behaviour view). It is the model view (same close-up scene, turning model, orbit and zoom, ← / → to switch the enemy) with the close-up scene's `forceWireframe` on, so every triangle's edges are drawn; the stats tile still counts the polygons. The dark hulls give dim lines and the neon parts bright ones.
- Dark grey background (review): the model and wireframe views clear to a neutral dark grey (`ENEMY_VIEWER_CONFIG.closeUp.clearColor`, 0.2, 0.2, 0.21) instead of `player_ship/`'s near-black purple, which they shared; the dark metal hulls now stand out against it. In the wireframe view the hull lines are near-black on the grey and the neon lines bright. `player_ship/` keeps its background.
- Readable wireframe and hitbox (review): in the wireframe view the close-up builds the model again with its hull meshes on a light unlit material (`closeUp.wireColor`, no vertex colours, left out of the glow layer), so the dark metal's edges show as crisp light grey lines; the neon parts keep their colours. A red line circle (`closeUp.hitboxColor`, 48 segments) of the enemy's hit radius lies in the model's plane, turning with it: the hit test is that circle in the playfield (GD-21). Back in the model view the model is built again, solid. `EnemyCloseUp.wireframe` switches it.
- Nothing underneath (review): the enemies are seen from above, so parts only visible from below are gone, found by orbiting under each model in the close-up. Gnat: the sensor turret, its neon lens (the shiny diamond) and the three arms under the fans (the fans' ducts overlap the body's rim, so they stay attached); 768 polygons in the close-up (932). Scout: the gun under its nose (572, was 592). Weaver: the guns under its bows (616, was 656). Bulwark: the chin gun, buried in the hull but for its tip (612, was 632). Those three guns were the Scout's, Weaver's and Bulwark's charge lights, so these three no longer glow before they fire; the Spinner's muzzles, the Lancer's emitter, the Rocketeer's missile tips and the Splitter's eye still do.
- Model view warm-up: the e2e test "the model view shows the picked enemy close up" failed now and then (2 runs in 8 under load), the page stalling for seconds when entering the model view: the close-up scene's shaders were compiled on its first draw, which is slow on a software GPU. `EnemyCloseUp.show` now starts compiling them in the background (`scene.whenReadyAsync()`) the first time a model is shown, before the view is entered. It passed 8 runs in 8 under the same load. Committed at the reviewer's request.
- Enemy colours (review): on the desert the grey-black hulls looked like the trees, roads and shadows, and only the small neon parts told the enemies apart. Each enemy now has its own hull material (still named `enemy-hull`, cached per scene and colour): the PBR metal's albedo is `hull.tint` (0.6) of the way from white to the enemy's neon colour, so its reflections take that hue, and it glows `hull.selfLight` (0.04) of it so shaded faces don't go black. The hull mesh also draws Babylon's outline (`renderOutline`, `hull.outline` = 0.9 logical pixels) in the neon colour, a crisp coloured edge on any ground; the wireframe view turns it off. The vertex shades are unchanged (`hull.base` 0.1), so the hulls stay dark metal (GD-61). Cost: one extra draw for each enemy's hull. Warm colours (Carrier amber, Spinner orange) contrast less with this level's desert than cool ones; their outline does most of the work there. The enemy missiles keep the plain grey metal.

### Deviations from spec
- P05-R11 (review): the page has a third view, the wireframe view, at the reviewer's request; the requirement text (behaviour and model views) was not changed.
- P05-R12 (review): the Carrier was added at the reviewer's request, so `enemies/` now lists 11 kinds; P05-R11 and the manual validation checklist still say 10 (human sections, not edited).
- P05-R01 (review): the Gnat's three short fins are now arms carrying ducted fans, at the reviewer's request to make it look like an unmanned drone; the disc, the 120° spacing and the rim's neon ring are kept. The requirement text was not changed.
- "Hits on enemies emit particles" reuses the phase 3 hit effects (bullet sparks, missile flashes, laser contact glow and particles); no new hit effect was added.
- During implementation, a few unit test files were run directly with Vitest (a probe to debug the page's drawing, and the first two new test files) before I stopped: the procedure keeps unit tests for `/validate-phase`. The full unit suite has not been run.
- `make build`'s ENG-52 check was extended to the new e2e handle `__ENEMIES_TEST__` (Makefile).

### Known limitations
- With the tilted camera (D-020), the top of the playfield is squeezed on screen: enemies that stop in the "top third" or "top part" (Strafer, Lancer, Bulwark) are close to the top edge of the screen.
- Enemy shots go through the player ship (player damage is out of scope).
- Under SwiftShader (e2e, headless) the page runs at about 10-12 FPS; the e2e tests step the simulation through `__ENEMIES_TEST__` instead of waiting.
- The neon glow of the enemies uses a second glow layer above the clouds; on very slow GPUs it costs a little.

### Suggestions for future phases
- A wave spawner driven by the distance flown (GD-40) can use `EnemyKindDefinition.spawn` as is.
- A hit flash on enemies, and health bars / hitboxes on the debug page (ENG-111 overlay).
- Player hitbox and damage from enemy shots and collisions (GD-21, GD-22).
