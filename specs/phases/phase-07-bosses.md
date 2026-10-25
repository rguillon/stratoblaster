# Phase 07 — Bosses

**Status:** Ready  <!-- Draft | Ready -->
**Depends on:** Phase 6

---

## 🧑 Goal
Every World 1 level has a mini boss around its middle and a final boss at its end (GD-41). Each boss is a big code-generated ship made of several parts that can be destroyed one by one (GD-46). It has a health bar on screen, and the ground scrolls at a different speed until the boss is killed. Each time a part is destroyed, the boss changes its shooting pattern, and the part may drop a bonus. A level is complete once its final boss is destroyed, and killing the mini boss gives a checkpoint (GD-42).

## 🧑 Requirements

> ID format `P07-Rxx`. Every requirement is **MUST** (no SHOULD / MAY).
> Write each requirement so it is testable. Add acceptance criteria when "done" isn't obvious.
> Bosses follow GD-43 / GD-44 (bullets, shootable missiles, lasers with a 1 s warning line; preset or aimed directions), GD-60 / GD-61 (made in code, dark metal with neon lights) and the player damage rules of phase 6 (D-050). Sizes are given relative to the medium player ship length (`L`). HP, speeds and chances are listed in **Tunable values**.
> The boss engine (parts, core shield, stages, health, ground speed control) is game-agnostic code outside `src/game/`; the ten bosses are data and models in `src/game/` (`01-engineering.md` §2.3).

### P07-R01 — Bosses made of destroyable parts  · MUST

A boss is one ship made of a **core** and several **destroyable parts** (turrets, pods, hangars, armour plates…), each with its own HP and hit circle. Parts are attached to the core and move with it.
- A player shot that hits a part damages that part only; a part that reaches 0 HP is destroyed.
- Some parts **shield the core**: while any of them is still there, shots that hit the core make sparks but do no damage. Which parts shield the core is part of each boss's data.
- The boss is destroyed when its core reaches 0 HP. Parts still attached are destroyed with it.
- A damaged part shows it: it flashes white for one frame when hit (like the enemies) and smokes once under 50 % HP.
- A destroyed part explodes (GD-62) and its model is replaced by a burnt, sparking stump: the boss is visibly missing that part.
- Mini bosses have **2 or 3** destroyable parts; final bosses have **4 to 6**.

**Acceptance criteria**
- [ ] Given a boss with an intact part, when shots hit that part until its HP reaches 0, then that part is destroyed and the other parts and the core keep their HP (unit test in the engine).
- [ ] Given a part that shields the core is still there, when the core is hit, then the core's HP does not change (unit test).
- [ ] Given every shielding part is destroyed, when the core is hit, then the core loses HP, and at 0 HP the boss and all its remaining parts are destroyed (unit test).
- [ ] Given each mini boss and final boss definition, then it has 2–3 and 4–6 destroyable parts respectively (unit test).
- [ ] Manual visual validation: a destroyed part explodes and leaves a stump; damaged parts smoke.

### P07-R02 — Boss health bar  · MUST

While a boss fight lasts, a health bar is shown at the top of the playfield, in the HUD style (D-013/D-014), with the boss's name and its kind ("MINI BOSS" / "BOSS").
- The bar shows the boss's remaining HP, the core and all its parts together, against its full HP.
- It fills up over 1 s when the boss arrives, goes down as any part or the core is damaged, and is removed when the boss is destroyed.
- Small notches on the bar mark the share of each destroyable part, so the player can see how much a part is worth.

**Acceptance criteria**
- [ ] Given a boss fight starts, then the bar appears with the boss name and is full once the boss is in place.
- [ ] Given a part loses 50 HP, then the bar goes down by 50 ÷ the boss's full HP (unit test on the value given to the HUD).
- [ ] Given the boss is destroyed, then the bar is gone.
- [ ] Manual visual validation: the bar is readable over every level's ground and does not hide the player's HUD.

### P07-R03 — Ground speed during a boss fight  · MUST

When a boss arrives, the ground (scenery, clouds, props, cars) changes from the level's ground speed (GD-01) to the boss's **fight ground speed**, easing over 2 s. It stays at that speed for as long as the boss is alive, however long that is, and eases back to the level's ground speed over 2 s once the boss is destroyed.
- Each boss has its own fight ground speed, as a factor of the level's speed (see the boss table in P07-R05): some bosses slow the ground, at least one stops it (×0), and at least one speeds it up (a chase).
- The ground never runs out: however long a fight lasts, the scenery goes on, also after the level's length for the final boss.
- The level's distance (the wave triggers, P06-R07) only moves with the ground, so no wave is skipped or squeezed by a fight.

**Acceptance criteria**
- [ ] Given a boss with a fight factor of 0.5 arrives in a level scrolling at 60 px/s, then 2 s later the ground scrolls at 30 px/s, and stays so until the boss is destroyed (unit test).
- [ ] Given the boss is destroyed, then the ground is back to the level's speed 2 s later (unit test).
- [ ] Given a final boss fight that lasts 5 minutes (debug, the boss not shot), then the ground keeps scrolling at the fight speed with no gap or edge in the scenery.
- [ ] Manual validation: the change of speed is smooth, and the chase boss feels faster.

### P07-R04 — Shooting patterns change when a part is destroyed  · MUST

Each weapon of a boss is mounted on a part or on the core. A boss goes through **stages**: stage 0 with every part there, then one stage more each time a destroyable part is destroyed (stage *k* = *k* parts destroyed).
- The weapons on a destroyed part stop for good.
- Each stage has its own **shooting pattern** (which weapons fire, what they fire, how often, in which directions), set in the boss's data. The pattern of a stage is never the same as the pattern of the stage before it.
- The last stage (only the core left, or only parts that do not shield the core) uses a pattern used in no earlier stage.
- When the stage changes, the boss flashes its neon lights and does not fire for 1 s, so the player sees the change coming (kid friendly, vision).
- The patterns use the attacks of GD-43 and GD-44: bullets (single, bursts, fans, rings, spirals; aimed or in preset directions), homing missiles the player can shoot down, and lasers with their 1 s warning line. A boss may also launch phase 5 enemies (e.g. Gnats from hangars).

**Acceptance criteria**
- [ ] Given a boss in stage *k*, when a part is destroyed, then the boss is in stage *k*+1 and its active pattern differs from stage *k*'s (unit test, for every boss).
- [ ] Given a part with a weapon is destroyed, then that weapon never fires again (unit test).
- [ ] Given the stage changes, then the boss fires nothing for 1 s (unit test).
- [ ] Given each boss definition, then its last stage's pattern is not used in an earlier stage (unit test).
- [ ] Manual validation: each part destroyed visibly changes the boss's attack.

### P07-R05 — The ten World 1 bosses  · MUST

Each World 1 level has its own mini boss and final boss, ten bosses in all, each with its own code-generated model, in the World 1 theme of its level (P06-R05). The table gives each one's look and parts; the stage patterns (P07-R04) are designed by the agent and listed in the implementation report.

| Level | Kind | Name | Look | Destroyable parts (weapons) | Fight ground speed |
|-------|------|------|------|-----------------------------|--------------------|
| 1-1 | Mini | Reef Warden | A wide hover-gunboat (3 L), a cyan neon ring under its rim | 2 side cannons (aimed bursts), shield the core. Core: prow cannon | ×0.5 |
| 1-1 | Final | Storm Petrel | A seaplane bomber (4.5 L wingspan), magenta neon along the wing edges | 2 wing gun pods (fans), 1 tail missile rack (homing missiles), 1 belly armour plate; the pods shield the core. Core: cockpit turret | ×1.5 (chase over the sea) |
| 1-2 | Mini | Breakwater | An armoured flying landing barge (3 L), orange neon | 1 front armour plate (no weapon, shields the core), 2 mortar turrets (slow, big bullets) | ×0.4 |
| 1-2 | Final | Gull Mothership | A wide carrier (5 L), green neon launch lights | 2 hangar bays (launch Gnat groups), 2 flak turrets (aimed), shield the core. Core: laser emitter | ×0.6 |
| 1-3 | Mini | Dust Devil | A gyro gunship (3 L) with a slowly turning blade ring | 3 blade pods (spiral bullets) on the turning ring, shield the core. Core: rings | ×0.5 |
| 1-3 | Final | Mesa Fortress | A flying fortress (5 L), red neon slits | 2 laser lances (warning line + laser), 2 missile silos, shield the core. Core: fans | ×0 (the ground stops over the canyon) |
| 1-4 | Mini | Scorpion | A gunship (3.5 L) with a tail arched over its back, yellow neon | 2 claw cannons (aimed spreads), 1 tail stinger (laser), shield the core. Core: rings | ×0.5 |
| 1-4 | Final | Refinery Titan | A heavy tanker-gunship (5.5 L) with glowing fuel tanks | 2 fuel tanks (burst into a ring of bullets when destroyed), 2 rotary turrets (spirals), 1 missile battery; the turrets shield the core | ×0.3 |
| 1-5 | Mini | Sentinel | A twin-hull police interceptor (3.5 L), blue and red neon | 2 hull guns (aimed), 1 drone bay (launches Hornets), shield the core. Core: fans | ×0.6 |
| 1-5 | Final | Overlord | A city-ship (6 L), purple neon over its whole hull | 2 wing laser cannons, 2 missile batteries, 2 shield generators (no weapon, shield the core). Core: every attack kind | ×0.25 |

All bosses come in from the top, take their place in the upper part of the screen, and move only inside the player ship's horizontal reach (x 107–373 of 480, D-048). They take no damage until they are in place (shots spark). They never leave the screen: a fight lasts until the boss is destroyed or the game is over.

**Acceptance criteria**
- [ ] Given each World 1 level, then it has exactly one mini boss and one final boss, from the table above (unit test).
- [ ] Given a boss is in place, then its hit circles stay inside x 107–373 (unit test, sampled over a long fight).
- [ ] Given a boss is coming in, when it is hit, then it loses no HP.
- [ ] Manual visual validation of each of the ten models (model and wireframe views, P07-R09).

### P07-R06 — Boss fights in the level  · MUST

Bosses take the calm stretches of the levels (phase 6 notes):
- The **mini boss** arrives at the middle of the level's length; the **final boss** when the scroll reaches the level's length.
- No wave starts after a boss has arrived until the boss is destroyed (enemies the boss launches do come). The waves already on screen carry on. The level's wave scripts leave the 10 s before each boss free of new waves.
- The player is hurt by touching a boss or one of its parts (collision damage, D-050); the boss takes no ramming damage.
- **Level end (replaces P06-R03 for World 1):** the level ends when its final boss is destroyed. After the boss's death explosions (a chain of blasts over its hull for about 2 s, then a big one), the "Level complete" overlay comes as in P06-R03, the bosses counted among the enemies destroyed / spawned.
- The level's scroll time (P06-R04) stays about 4 minutes at the level's ground speed; the boss fights add to the time played.

**Acceptance criteria**
- [ ] Given a World 1 level, when the scroll reaches half its length, then its mini boss arrives (unit test).
- [ ] Given a boss is alive, then no new wave starts (unit test).
- [ ] Given the final boss is destroyed, then the "Level complete" overlay shows after its death explosions; and not before the boss is destroyed (unit test and e2e).
- [ ] Given the player touches a boss part, then the player takes the collision damage and the part loses no HP (unit test).

### P07-R07 — Bonuses from destroyed parts  · MUST

When a destroyable part is destroyed, it may drop a bonus, with a chance set in each boss's data. The bonuses are the phase 6 weapon bonuses (D-049): they fall from where the part was, within the ship's reach, and work the same. The core of a final boss always drops one.

Drops are drawn from the level's seed, so the same fight drops the same bonuses (deterministic, like the waves).

**Acceptance criteria**
- [ ] Given a part with a drop chance of 1 is destroyed, then a weapon bonus appears where the part was (unit test).
- [ ] Given a part with a drop chance of 0 is destroyed, then no bonus appears (unit test).
- [ ] Given a final boss is destroyed, then a weapon bonus appears (unit test).
- [ ] Given the same level played twice, with the same parts destroyed in the same order, then the same parts drop bonuses.

### P07-R08 — Checkpoint after the mini boss  · MUST

Destroying a level's mini boss saves a checkpoint (GD-42): the level's distance just after the mini boss, and the player's weapon levels at that moment. If the game is over after the checkpoint, the "Game over" panel (D-050) offers two choices: **Continue** (selected first) restarts the level from the checkpoint with 3 full lives and the saved weapon levels, the waves before the checkpoint skipped; **Level select** goes back as before. Without a checkpoint, the panel is unchanged. The checkpoint is forgotten when the level is left.

**Acceptance criteria**
- [ ] Given the mini boss of 1-2 was destroyed, when the game is over, then the panel offers Continue and Level select.
- [ ] Given Continue is confirmed, then 1-2 starts again just after its mini boss, with 3 lives and the weapon levels the player had when the mini boss was destroyed, and the mini boss does not come again (unit test).
- [ ] Given the game is over before the mini boss was destroyed, then the panel is the phase 6 one.

### P07-R09 — Debug page `bosses/` and debug shortcuts  · MUST

A `bosses/` debug page, like `enemies/` (P05-R11):
- A list to pick one of the ten bosses; it arrives and fights over the scenery of its level, with its fight ground speed; it comes again when it is destroyed.
- The "model" view (close up, rotating slowly, dark grey background; ← / → switch boss) and the "wireframe" view (V; triangle edges and every part's hit circle, shielding parts marked).
- A player ship that moves and shoots (any weapon and level) and cannot die.
- A key (K) destroys the boss's next intact part, so each stage can be checked quickly; the current stage is shown.
- The FPS / polygons debug tile.

On the `game` screen, the debug URL options (P06-R09) also take `boss=mini` or `boss=final` to start the level straight at that boss's arrival, and K works there too while debug is on (never without the debug options).

**Acceptance criteria**
- [ ] Given the user opens `bosses/`, then the page loads without console errors and every boss can be picked.
- [ ] Given a boss is picked, when K is pressed, then one more part is destroyed and the stage shown goes up by one.
- [ ] Given the URL `?level=1-3&boss=final`, then 1-3 starts at its final boss's arrival.
- [ ] Given no debug option, then K does nothing.

### P07-R10 — Boss difficulty across World 1  · MUST

Like the levels (P06-R08), the bosses get harder from 1-1 to 1-5, and every boss stays beatable for a kid in 1-1 (vision):
- the full HP of the mini bosses goes up strictly from 1-1 to 1-5, and so does that of the final bosses;
- each final boss has more full HP than its level's mini boss;
- the boss's bullets use the level's bullet speed and fire rate factors (P06-R08).

**Acceptance criteria**
- [ ] Unit test: mini boss full HP and final boss full HP each go up strictly from 1-1 to 1-5, and each final boss has more than its level's mini boss.
- [ ] Unit test (simulation, as in D-050): with the balanced ship, guns at level 3, always firing at the boss, the fight lasts within the time ranges of **Tunable values**.
- [ ] Manual validation: the 1-1 bosses feel easy, the 1-5 bosses clearly harder.

## 🧑 Tunable values
| Name | Value | Notes |
|------|-------|-------|
| mini_boss_parts / final_boss_parts | 2–3 / 4–6 | P07-R01 |
| boss_speed_ease | 2 s | P07-R03, in and out |
| fight_ground_speed factors | see the boss table | P07-R03, P07-R05 |
| stage_change_pause | 1 s | P07-R04 |
| boss_entry_time | about 3 s | P07-R05, no damage meanwhile |
| health_bar_fill | 1 s | P07-R02 |
| mini_boss_at | 50 % of the level's length | P07-R06 |
| quiet_before_boss | 10 s | P07-R06, no new wave |
| boss_death_explosions | about 2 s, then the final blast | P07-R06 |
| part_drop_chance | 50 % mini boss parts, 60 % final boss parts | P07-R07; the agent may adjust per part |
| final_boss_core_drop | 100 % | P07-R07 |
| mini_fight_time 1-1 → 1-5 | 25–35 s → 40–50 s | P07-R10, balanced ship, guns level 3, always on target |
| final_fight_time 1-1 → 1-5 | 50–70 s → 90–120 s | P07-R10, same |
| boss_triangles | ≤ 6 000 per boss | P07-R05, ENG-101; the agent may adjust |

## 🧑 Out of scope for this phase
- Boss music and sound effects (GD-70, GD-71): there is no audio yet.
- Points for bosses and parts, score display, high score (GD-50, GD-51).
- New bonus kinds (bombs GD-32, extra lives GD-20): parts drop the weapon bonuses only.
- Bosses for worlds 2 to 5, and Level Zero (it stays a test level without bosses).
- New regular enemy kinds (bosses may launch the phase 5 ones).
- Pause.

## 🧑 Engineering additions for this phase
- The boss engine (parts, core shield, stages, health, pattern switching, fight ground speed, checkpoint) is pure `core/` code and unit tested; the ten bosses (models, parts, patterns, tunables) are data and views in `src/game/`.
- An e2e test opens `bosses/` and checks every boss can be picked without console errors.
- An e2e test opens `?level=1-1&boss=final`, destroys the boss with K and the debug fire, and reaches the "Level complete" overlay.
- 60 FPS (ENG-101) during the 1-5 final boss fight in its busiest stage over the city centre.

## 🧑 Manual validation checklist
- [ ] Runs on GitHub Pages / `make dev` without console errors
- [ ] Each World 1 level has a mini boss in the middle and a final boss at the end
- [ ] Each boss's parts can be shot off one by one; the core is shielded until its shielding parts are gone
- [ ] The boss health bar is readable and goes down with every part
- [ ] The ground changes speed for the fight (slower, stopped, or a chase) and comes back to normal after the kill
- [ ] Each destroyed part changes the boss's shooting pattern, with a short pause first
- [ ] Destroyed parts sometimes drop weapon bonuses; the final boss always does
- [ ] After the mini boss, a game over offers Continue from the checkpoint
- [ ] The ten boss models look good in `bosses/` (model and wireframe views)
- [ ] 60 fps in the 1-5 final boss fight

## 🧑 Notes, references, sketches
- **Choices settled by the reviewer (2026-10-25): every default below accepted.**
  1. Ten distinct bosses (one mini + one final per World 1 level) in one phase. Alternative: build the engine and the 1-1 / 1-2 bosses here, and the others in a later phase.
  2. The checkpoint (P07-R08, GD-42) is in this phase because it hangs on the mini boss. It could move to a later phase.
  3. The ground speed during a fight is a factor per boss, from ×0 (stopped) to ×1.5 (chase). Alternative: always slower, or always stopped.
  4. Bonuses from parts are weapon bonuses only; bombs and extra lives stay out of scope.
  5. Boss designs (names, looks, parts) in P07-R05 are suggestions; the stage patterns are left to the agent and reported.
- P07-R06 changes P06-R03 (the level now ends on the final boss, not at the end of the scroll): it is a regression requirement on phase 6, per the CLAUDE.md rules.

---

## 🧑 Review feedback
> After the agent reports, write corrections here, then say **"Fix phase 07"**.
> The agent ticks each item when fixed.

- [ ] 

---

## 🤖 Implementation report
> Filled by the agent. Do not edit (comment in Review feedback instead).

### Questions / blockers
None. The phase was a Draft written by the agent at the reviewer's request; on 2026-10-25 the reviewer accepted every default of its open choices (ten bosses, the checkpoint in this phase, a ground speed per boss, weapon bonuses only, the suggested designs) and it was set to Ready.

### Plan
| Task | Requirement IDs |
|------|-----------------|
| Engine: `Boss` with destroyable parts, shielded core, stages, death blasts, orbiting parts (`core/entities/boss.ts`); enemy hooks (`hitTargets`, `expires`, `rammable`, `dropChance`, `explode`, `breakPart`, `LaserOwner`) | P07-R01, R04, R05 |
| Engine: stage patterns (`core/systems/boss-pattern.ts`) | P07-R04 |
| Engine: fights in a level, ground speed factor and hold (`boss-fights.ts`, `scroll-track.ts`), level end, no waves during a fight, checkpoint (`level-run.ts`, `run-arsenal.ts`) | P07-R02, R03, R06, R08 |
| Bonuses from parts (`bonus-world.ts` per-target chance, `EnemyWorld.brokenParts`) | P07-R07 |
| Game: ten boss designs, `WorldBoss`, launches, World 1 schedule, quiet stretches, runout, health tuning | P07-R03..R07, R10 |
| View: boss model framework (flash, smoke, stump, ring) and ten models | P07-R01, R05 |
| UI / app: boss health bar, Continue choice, restart from checkpoint, `boss=` and K debug, `bosses/` page | P07-R02, R08, R09 |
| Tests (unit with IDs, e2e), docs, decisions | all |

### Requirement traceability
| ID | Status (Done / Partial / Not done) | Code | Tests | Notes |
|----|-----------------------------------|------|-------|-------|
| P07-R01 | Done | `core/entities/boss.ts`, `game/view/bosses/boss-model.ts` | `boss.test.ts`, `bosses.test.ts`, `boss-models.test.ts` | Parts flash white 0.05 s when hit, smoke under 50 %, leave a burnt sparking stump |
| P07-R02 | Done | `core/systems/boss-fights.ts` (`bar`), `ui/boss-bar.ts`, `app/game-play-hud.ts`, `index.html` | `boss-fights.test.ts`, `boss-bar.test.ts`, `game-play.test.ts`, e2e `world-1.spec.ts` | Under the HUD, red to yellow, a notch at the end of each part's share |
| P07-R03 | Done | `core/scenery/scroll-track.ts`, `boss-fights.ts`, `core/scenery/scenery-level.ts` (`withRunout`), `game/config/world-1/bosses.ts` | `scroll-track.test.ts`, `boss-fights.test.ts`, `level-run-bosses.test.ts`, `bosses.test.ts` | Level progress waits, ground goes on (D-054) |
| P07-R04 | Done | `core/systems/boss-pattern.ts`, `game/sim/bosses/world-boss.ts`, `game/config/bosses/*` | `boss-pattern.test.ts`, `boss.test.ts`, `bosses.test.ts` (all orders of destruction) | 1 s pause, charge lights strobing; patterns listed below |
| P07-R05 | Done | `game/config/bosses/`, `game/sim/boss-kinds.ts`, `game/view/bosses/*-model.ts` | `bosses.test.ts`, `boss-models.test.ts` | Two part positions moved (see Deviations) |
| P07-R06 | Done | `level-run.ts`, `game/sim/world-1.ts`, `game/config/world-1/waves.ts` (`quietBefore`), `player-hits.ts` | `level-run-bosses.test.ts`, `world-1.test.ts`, e2e `world-1.spec.ts` | Replaces P06-R03 for World 1 |
| P07-R07 | Done | `bonus-world.ts`, `enemy-world.ts`, `level-run.ts` | `level-run-bosses.test.ts`, `bosses.test.ts` | Weapon bonuses only |
| P07-R08 | Done | `level-run.ts` (`LevelCheckpoint`), `run-arsenal.ts`, `app/menu-flow.ts`, `app/game-session.ts`, `ui/screens/game-screen.ts` | `level-run-bosses.test.ts`, `menu-flow.test.ts`, `menu-view-builder.test.ts`, `menu-overlay.test.ts`, `game-session.test.ts`, `game-play.test.ts` | |
| P07-R09 | Done | `app/start-boss-viewer.ts`, `app/boss-viewer-stage.ts`, `bosses/index.html`, `app/debug-options.ts`, `app/game-play.ts` | `start-boss-viewer.test.ts`, `debug-options.test.ts`, `route.test.ts`, `game-play.test.ts`, e2e `bosses.spec.ts`, `world-1.spec.ts` | |
| P07-R10 | Done | `game/config/bosses/*` | `bosses.test.ts` (health, simulated fights per level) | Bot in `tests/helpers/boss-bot.ts` |

**The ten bosses and their stage patterns (P07-R04, P07-R05).** Part volleys fire in every stage while their part stands; the core fires the volley listed for each stage (stage *k* = *k* parts destroyed). Ground speed factor in brackets.
- **Reef Warden** (1-1 mini, ×0.5): side cannons fire aimed 3-bullet bursts in turn. Core: 3-way fan → 5-way fan → spiral ring of 8.
- **Storm Petrel** (1-1 final, ×1.5 chase): wing pods fire 3-way fans in turn, the tail rack 2 homing missiles; the belly plate does not fire. Core: single aimed → aimed 3 → burst of 4 → 7-way fan → spiral ring of 12.
- **Breakwater** (1-2 mini, ×0.4): mortars lob slow big bullets at the player. Core: 3-way fan → aimed 3 → burst of 4 → spiral ring of 10.
- **Gull Mothership** (1-2 final, ×0.6): hangars launch 3 Gnats every 7 s, flak turrets aimed pairs. Core: laser every 7 s, then the laser comes more often with an aimed shot → a 5-way fan → a ring of 8 → a spiral ring of 12.
- **Dust Devil** (1-3 mini, ×0.5): three orbiting blade pods fire 2-way spirals. Core: aimed → aimed 3 → burst of 4 → spiral ring of 12.
- **Mesa Fortress** (1-3 final, ×0 ground stops): two laser lances in turn, two missile silos. Core: 3-way fan → 5-way → 5-way and aimed → 7-way → spiral ring of 14 and 5-way.
- **Scorpion** (1-4 mini, ×0.5): claws fire aimed 3-spreads, the stinger a laser. Core: aimed → ring of 6 → spiral ring of 8 → spiral ring of 12 and aimed.
- **Refinery Titan** (1-4 final, ×0.3): rotary turrets fire 3-arm spirals (turning opposite ways), the battery 2 missiles; each fuel tank bursts into a ring of 12 when destroyed. Core: aimed → aimed 3 → burst of 4 → 5-way → 7-way and aimed → spiral ring of 14 and burst.
- **Sentinel** (1-5 mini, ×0.6): hull guns fire aimed pairs (blue / red), the drone bay launches 2 Hornets every 5.5 s. Core: 3-way fan → 5-way → 7-way → spiral ring of 14 and 5-way.
- **Overlord** (1-5 final, ×0.25): wing lasers in turn, missile batteries pairs of missiles. Core: aimed → aimed 3 → burst of 4 → 5-way → ring of 10 → 7-way and burst → spiral ring of 14, its own laser and missiles.

Simulated fights (guns level 3, always on target, from arrival to the end of the death blasts): mini 30.1 / 32.8 / 37.5 / 42.7 / 44.1 s, final 58.8 / 72.3 / 81.7 / 91.7 / 103.5 s for 1-1 … 1-5. Models: 1,060–2,250 triangles each (budget 6,000), within 15 % of their sizes.

### Gate results
Light verification only (CLAUDE.md, step 5). Lint, unit tests and coverage run in the full `make check` gate of `/validate-phase`.
```
make typecheck  ✔ (0 errors)
make build      ✔ (ENG-52 leak check ✔, now also for __BOSSES_TEST__)
make e2e        ✔ 53 passed (5.7 min; 50 before + 3 on bosses/; the 1-1 end test now goes through
                  its final boss, and the 1-3 start test expects its mini boss at 2:00)
```
Coverage before this phase: 99.33 % lines (phase 6). New numbers come with `/validate-phase 7`.

### How to test manually
- `make dev`, then a level from the menus: the mini boss comes at about 2:00 of the level's scroll (after 10 s without new waves), the final boss at its end. Shoot the parts off (the shielding ones first); watch the bar, the pattern change after each part (1 s pause, lights strobing), the bonuses, the ground speed (1-1's final boss speeds the sea chase up, 1-3's stops the ground).
- Straight to a boss: `/?level=1-3&boss=final` (or `boss=mini`, any World 1 level, `&ship=heavy`). K destroys the next part, then the core (debug only). F ×4, ← / → still seek.
- Checkpoint: `/?level=1-2&boss=mini`, destroy the mini boss (K × 4), then lose the three lives: the "Game over" panel offers Continue / Level select; Continue starts again after the mini boss with the weapon levels you had.
- `bosses/`: pick a boss (buttons or N / B), it fights over its level; K destroys a part, the panel shows the stage; M model view, V wireframe (core circle red, shielding parts yellow, others cyan), ← / → switch boss in those views; X / 1-5 weapon and level, F fire, P pause.

### Deviations from spec
- P07-R05: the Scorpion's stinger and the Sentinel's drone bay hang in front of the core (spec table: on the back / no place given). Shots come from below, and a shielding part behind the shielded core could not be hit (D-053).
- P07-R04: "the boss flashes its neon lights": the boss's charge lights (its neon colour) strobe during the 1 s pause; the neon strips' material is shared by every enemy of the scene, so they stay lit.
- P07-R03: the final fight keeps the ground scrolling on extra ground drawn past the level's end (`runout`, sized for about a long fight); beyond it, the terrain goes on bare (no props, no roads) — no gap or edge. The scenery gets ahead of the level by each fight's travel (D-054).
- P07-R06: a non-shielding part right behind the core (the Storm Petrel's missile rack, the Refinery Titan's missile battery) can only be hit with angled shots or missiles; destroying it is optional.

### Known limitations
- The ten models have not been seen by the reviewer: please check them in `bosses/` (model and wireframe views). They are lighter than budgeted (1–2.3 k triangles) but made of 31–65 meshes each (a node per part, for the stumps and flashes): the draw calls of the 1-5 final fight should be checked against ENG-106 in the 60 fps check.
- No music change for bosses (no audio yet), no points shown.
- The main bundle chunk is now a little over Vite's 1,500 kB warning size, minified (410 kB gzip; budget ENG-107: 1.5 MB gzip).
- The fight times assume a player always on target; real players will take longer.

### Suggestions for future phases
- Boss music (GD-70) when the bar shows; a short "WARNING" banner as the boss arrives.
- Points for parts and bosses once scoring exists (GD-50).
- If draw calls matter, merge each boss's part meshes by material and hide parts by index ranges.
