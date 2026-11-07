# Stratoblaster specifications

The specs are organised **by function**: one file per feature, entity or level, not one file per
delivery phase. They describe the game as it is meant to be, and they are the single source of truth:
code follows the specs.

The previous, phase-based specs (`phases/phase-NN-*.md`, `02-game-design.md`, the decision log
D-001 to D-233 and the progress board) are kept, unchanged, in [`../specs_old/`](../specs_old/).
[`TRACEABILITY.md`](TRACEABILITY.md) maps every old requirement ID and every old decision to the
requirements that now carry it.

## Layout

| Path | ID prefix | Content |
|------|-----------|---------|
| [`00-vision.md`](00-vision.md) | — | What the game is, scope, non-goals |
| [`01-engineering.md`](01-engineering.md) | `ENG` | Stack, layout, layering, tooling, tests, CI, deployment, Transcrypt rules |
| [`performance.md`](performance.md) | `PERF` | Frame rate, loading, freezes, budgets |
| [`gameplay/`](gameplay/) | `GAME-<FILE>` | Screen, controls, player ship handling, weapons, lives, bombs, bonuses, scoring, level flow |
| [`ui/`](ui/) | `UI-<FILE>` | Screen flow, menu input, look, boot and loading, title, ship select, level select, HUD, pause, settings, continue / game over |
| [`audio/`](audio/) | `AUD-<FILE>` | Audio engine, music, sound effects |
| [`graphics/`](graphics/) | `GFX-<FILE>` | Art direction, readability, edge trim, player ships, shots, effects, camera, terrain, water, sky and light, weather, roads, buildings, props, traffic |
| [`enemies/common.md`](enemies/common.md) | `ENM` | Rules shared by every enemy kind |
| [`enemies/weapons.md`](enemies/weapons.md) | `WPN` | Guns that recoil, the Overlord's lasers and hexagonal missile ports, for every enemy and boss |
| `enemies/<kind>.md` | `ENM-<KIND>` | One file per enemy kind: its look and its behaviour |
| [`bosses/common.md`](bosses/common.md) | `BOSS` | Rules shared by every boss (mini and final) |
| `bosses/mini/<N-M>-<name>.md` | `MB-<NAME>` | One file per mini boss |
| `bosses/final/<N-M>-<name>.md` | `FB-<NAME>` | One file per final boss |
| `worlds/world-N/world.md` | `WLD-N` | What a world shares: theme, progression across its levels, difficulty curve |
| `worlds/world-N/<N-M>-<slug>.md` | `LVL-N-M` | One file per level |
| [`dev/`](dev/) | `DEV-<FILE>` | Dev menu and viewers, debug options, test API, perf tools |
| [`TRACEABILITY.md`](TRACEABILITY.md) | — | Old IDs and decisions → new IDs |
| [`DECISIONS.md`](DECISIONS.md) | `D-NNN` | Technical decisions taken from now on (D-234 and later) |

### Files and prefixes

**gameplay/** — `screen.md` `GAME-SCREEN` · `controls.md` `GAME-CTRL` · `player-ship.md` `GAME-SHIP` ·
`weapons.md` `GAME-WPN` · `lives-and-damage.md` `GAME-LIFE` · `bombs.md` `GAME-BOMB` ·
`bonuses.md` `GAME-BONUS` · `scoring.md` `GAME-SCORE` · `level-flow.md` `GAME-LEVEL`

**ui/** — `screen-flow.md` `UI-FLOW` · `menu-input.md` `UI-INPUT` · `look-and-layout.md` `UI-LOOK` ·
`boot-and-loading.md` `UI-LOAD` · `title-screen.md` `UI-TITLE` · `ship-select.md` `UI-SHIP` ·
`level-select.md` `UI-LEVEL` · `hud.md` `UI-HUD` · `pause-menu.md` `UI-PAUSE` · `settings.md` `UI-SET` ·
`continue-and-game-over.md` `UI-OVER`

**audio/** — `engine.md` `AUD-ENGINE` · `music.md` `AUD-MUSIC` · `sfx.md` `AUD-SFX`

**graphics/** — `art-direction.md` `GFX-ART` · `readability.md` `GFX-READ` · `edge-trim.md` `GFX-TRIM` ·
`player-ships.md` `GFX-SHIP` · `shots.md` `GFX-SHOT` · `effects.md` `GFX-FX` · `camera.md` `GFX-CAM` ·
`terrain.md` `GFX-TERRAIN` · `water.md` `GFX-WATER` · `sky-and-light.md` `GFX-SKY` ·
`weather.md` `GFX-WEATHER` · `roads.md` `GFX-ROAD` · `buildings.md` `GFX-BLDG` · `props.md` `GFX-PROP` ·
`traffic.md` `GFX-CAR`

**enemies/** — tier 1: `hornet` `scout` `rocketeer` `lancer` `carrier` · tier 2: `wasp` `strafer`
`harrier` `sweeper` `hatchery` · tier 3: `phantom` `spinner` `mortar` `prism` `broodmother` ·
tier 4: `splitter` `hydra` `juggernaut` `scissor` `hive` (file `enemies/hornet.md`, prefix
`ENM-HORNET`).

**bosses/** — one file per boss, named after its level:

| Level | Mini boss (`bosses/mini/`) | Final boss (`bosses/final/`) |
|-------|----------------------------|------------------------------|
| 1-1 | `1-1-reef-warden.md` `MB-REEF-WARDEN` | `1-1-storm-petrel.md` `FB-STORM-PETREL` |
| 1-2 | `1-2-breakwater.md` `MB-BREAKWATER` | `1-2-gull-mothership.md` `FB-GULL-MOTHERSHIP` |
| 1-3 | `1-3-dust-devil.md` `MB-DUST-DEVIL` | `1-3-mesa-fortress.md` `FB-MESA-FORTRESS` |
| 1-4 | `1-4-scorpion.md` `MB-SCORPION` | `1-4-refinery-titan.md` `FB-REFINERY-TITAN` |
| 1-5 | `1-5-sentinel.md` `MB-SENTINEL` | `1-5-overlord.md` `FB-OVERLORD` |
| 2-1 | `2-1-floe-breaker.md` `MB-FLOE-BREAKER` | `2-1-narwhal.md` `FB-NARWHAL` |
| 2-2 | `2-2-fjord-lynx.md` `MB-FJORD-LYNX` | `2-2-harbour-kraken.md` `FB-HARBOUR-KRAKEN` |
| 2-3 | `2-3-snow-owl.md` `MB-SNOW-OWL` | `2-3-aurora-station.md` `FB-AURORA-STATION` |
| 2-4 | `2-4-avalanche.md` `MB-AVALANCHE` | `2-4-glacier-colossus.md` `FB-GLACIER-COLOSSUS` |
| 2-5 | `2-5-ice-queen.md` `MB-ICE-QUEEN` | `2-5-boreal-citadel.md` `FB-BOREAL-CITADEL` |
| 3-1 | `3-1-mangrove-croc.md` `MB-MANGROVE-CROC` | `3-1-river-leviathan.md` `FB-RIVER-LEVIATHAN` |
| 3-2 | `3-2-toucan.md` `MB-TOUCAN` | `3-2-canopy-spider.md` `FB-CANOPY-SPIDER` |
| 3-3 | `3-3-stone-idol.md` `MB-STONE-IDOL` | `3-3-sky-temple.md` `FB-SKY-TEMPLE` |
| 3-4 | `3-4-mosquito.md` `MB-MOSQUITO` | `3-4-dam-breaker.md` `FB-DAM-BREAKER` |
| 3-5 | `3-5-jaguar.md` `MB-JAGUAR` | `3-5-verdant-crown.md` `FB-VERDANT-CROWN` |
| 4-1 | `4-1-cinder-crab.md` `MB-CINDER-CRAB` | `4-1-steam-dreadnought.md` `FB-STEAM-DREADNOUGHT` |
| 4-2 | `4-2-ash-wraith.md` `MB-ASH-WRAITH` | `4-2-geyser-rig.md` `FB-GEYSER-RIG` |
| 4-3 | `4-3-magma-salamander.md` `MB-MAGMA-SALAMANDER` | `4-3-obsidian-golem.md` `FB-OBSIDIAN-GOLEM` |
| 4-4 | `4-4-furnace-drake.md` `MB-FURNACE-DRAKE` | `4-4-foundry-ark.md` `FB-FOUNDRY-ARK` |
| 4-5 | `4-5-ember-herald.md` `MB-EMBER-HERALD` | `4-5-caldera-throne.md` `FB-CALDERA-THRONE` |

**worlds/** — `world-1/`: `1-1-open-sea` `1-2-green-coast` `1-3-green-country` `1-4-dry-lands`
`1-5-deep-desert` · `world-2/`: `2-1-great-erg` `2-2-mining-mesas` `2-3-oil-fields`
`2-4-industrial-belt` `2-5-factory-district` · `world-3/`: `3-1-canal-works` `3-2-docklands`
`3-3-workers-quarter` `3-4-suburbs` `3-5-garden-villages` · `world-4/`: `4-1-garden-town`
`4-2-inner-town` `4-3-midtown` `4-4-business-district` `4-5-downtown` (file
`worlds/world-1/1-1-open-sea.md`, prefix `LVL-1-1`; the world file `worlds/world-1/world.md`, prefix `WLD-1`).

**dev/** — `dev-menu.md` `DEV-MENU` · `debug-options.md` `DEV-OPT` · `test-api.md` `DEV-API` ·
`perf-tools.md` `DEV-PERF`

## Requirement IDs

- An ID is the file's prefix, a dash and a two-digit number: `ENM-HORNET-03`, `LVL-2-4-07`,
  `GFX-ROAD-12`, `BOSS-05`. `ENG` keeps the three-digit numbers it already had (`ENG-52`, `ENG-110`).
- Numbers are never reused. A removed requirement keeps its heading, marked *Removed* with the date
  and the reason.
- In code, a requirement is traced by its ID in a comment or docstring (`# ENM-HORNET-03: ...`) or in a
  test name, lower case with underscores (`def test_enm_hornet_03_follows_the_s_path():`).
- Every requirement has a priority: **MUST** (mandatory), **SHOULD** (expected unless a decision
  says why not), **MAY** (optional).

## File template

```markdown
# <Title>

> **Area:** <area> · **Prefix:** `<PREFIX>` · **Related:** [<file>](<relative link>), …

<Overview: 2–5 sentences. What this is in the game; what it is not.>

## Requirements

### <PREFIX>-01 — <short title> · MUST

<The requirement: present tense, testable, one idea per requirement. Numbers that are tunable go in
the table below and are named here.>

**Acceptance criteria**
- Given <context>, when <action>, then <result>.

*Sources: P05-R01, P16-R03, D-165.*

### <PREFIX>-02 — …

## Tunable values

| Name | Value | Notes |
|------|-------|-------|

## Notes

<Optional: history worth keeping, known gaps.>
```

Entity files (enemies, bosses) group their requirements under `### Look` and `### Behaviour`
sub-headings inside `## Requirements` (`####` requirement headings then). Level files give the
level's identity, scenery, waves, bosses and difficulty.
