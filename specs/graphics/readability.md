# Readability

> **Area:** Graphics · **Prefix:** `GFX-READ` · **Related:** [art-direction.md](art-direction.md), [edge-trim.md](edge-trim.md), [shots.md](shots.md), [effects.md](effects.md), [terrain.md](terrain.md), [sky-and-light.md](sky-and-light.md), [../dev/test-api.md](../dev/test-api.md)

At a glance, in every world and level, the player tells their own ship, the enemies, the enemy
shots and their own shots apart from the background and from each other. The classic shmup rule
holds: the background is dull, the enemies stand out, the enemy shots are the brightest thing and
the player's shots are toned down. This file sets those rules and their thresholds; the looks that
meet them are in the other graphics files, and the measure itself (the test API's readability
probe) is in [DEV-API](../dev/test-api.md). There is no colourblind palette.

## Requirements

### GFX-READ-01 — Background stays in the background · MUST

The ground, props, sky, haze, clouds and ground lights of every world are darker and less saturated
than the gameplay layer (player ship, enemies, bosses, shots, bonuses). Seen during play, no
background pixel is brighter than `backgroundMaxLuminance` (relative luminance), but for at most
`backgroundBrightPixelBudget` of the screen (small lights). The look stays darksynth (GFX-ART-03).

**Acceptance criteria**
- Given one level of each world (1-2, 2-1, 3-1, 4-1), when the background is measured during play
  (test API), then its luminance, but for the bright pixel budget, is at most
  `backgroundMaxLuminance` (e2e).
- The levels still look darksynth: dark ground, neon accents (manual).

*Sources: P14-R01.*

### GFX-READ-02 — Background darkened at the source, one tone per world · MUST

Each world has a tone (`READABILITY.tones`). The colours of its looks' ground textures, shores,
water and roads are multiplied by it (tint factors and lava excepted), and the engine applies it to
the props' lit colours, the haze (fog and clear colour) and the cloud colours as it resolves the
atmosphere. The sun, the ambient light and the props' self-lit accents keep their brightness. No
dark veil is drawn over the background.

**Acceptance criteria**
- Given a world's look, when it is toned, then its ground, sea and road colours are multiplied by
  the world's tone, and its tint factors and lava are not (unit tests).
- Given a level, then no screen-wide plane is drawn between the background and the playfield.

*Sources: P14-R01, D-130, D-122.*

### GFX-READ-03 — Gameplay objects are never dimmed · MUST

The background treatment never touches the gameplay layer: the player ship, the enemies and bosses,
every shot and every bonus keep their full colours and brightness over any ground.

**Acceptance criteria**
- Given a level, when the player ship, an enemy and an enemy bullet are on screen, then none of
  them is darkened by the world's tone.

*Sources: P14-R01.*

### GFX-READ-04 — Reserved colour families · MUST

Each family of gameplay objects has a colour family that nothing else uses, so colour alone tells
them apart. A family is a hue range plus a minimum saturation; pale colours (sand, beige, under
the minimum saturation) belong to none. The families share no hue.

| Family | Hues | Used by |
|--------|------|---------|
| Player | 180°–235°, cyan to ice blue | player ship accents and lights, player shots, their hits |
| Enemy | 60°–140°, bright yellow to bright green | enemy and boss neon, veins, charge lights, reactors, trim |
| Enemy shot | 15°–48°, orange to amber round a white-hot core | enemy bullets, missiles, lasers |
| Pickup | 250°–295°, blue violet to purple | bonuses and their pick-up flash |

The families are defined in one game config and every object family reads its colours there.
Enemy shots and player shots never share a colour.

**Acceptance criteria**
- Given the families, then no two share a hue (unit test).
- Given every enemy bullet style, then it is in the enemy-shot family; given every saturated bonus
  colour, it is in the pickup family (unit tests).
- Given the enemy family, then it holds yellow, lime and green and no pink (unit test).

*Sources: P14-R02, D-121, D-231.*

### GFX-READ-05 — The background leaves the reserved hues out · MUST

The background palette of every world leaves the reserved families out, or uses them only below the
GFX-READ-01 brightness cap. In particular no background colour falls in the enemy-shot family above
that cap.

**Acceptance criteria**
- Given each world's background palette, when it is checked against the enemy-shot family, then no
  colour falls in it above the brightness cap (unit test on the palettes).

**Gap:** no unit test checks the world palettes against the families since the Python port (the
TypeScript palette test was not carried over); only the e2e luminance check of GFX-READ-01 runs.

*Sources: P14-R02.*

### GFX-READ-06 — Colours moved into their family where they are drawn · SHOULD

The per-kind neon tables of the enemies and bosses are kept as they are (they still tell the kinds
apart); their colours are moved into the right family where each model or shot is built, not in
every frame. Enemy and boss lights take the nearer of the two enemy hues (GFX-ART-05). Enemy laser
colours are squeezed into the enemy-shot family, the whole hue wheel in order, so different bosses
keep different laser shades. Greys stay grey. The player shots, the enemy bullets and the bonuses
are coloured in their families directly in their look configs.

**Acceptance criteria**
- Given a neon colour, when it is moved into the enemy family, then its hue is one of the enemy
  hues and its brightness is kept; given a grey, it is unchanged (unit tests).
- Given a boss's neon, then its laser colour is that neon folded into the enemy-shot family (unit
  test).

*Sources: D-121, D-231.*

### GFX-READ-07 — The player ship stands out · MUST

The player ship has a light rim in the player colour, visible on every background, so the player
always knows where they are: its glowing edge trim ([GFX-TRIM](edge-trim.md)). While the ship is
invincible and blinks, the whole ship blinks, trim included.

**Acceptance criteria**
- Given any level, when the ship flies over the brightest part of the ground, then its rim's
  contrast ratio with the background round it is at least `minObjectContrast` (e2e, one level of
  each world).
- Given the ship blinking, then its trim shows and hides with it.

*Sources: P14-R03, D-220, D-123.*

### GFX-READ-08 — No hitbox marker · MUST

Nothing marks the player ship's hitbox: no dot, ring or other marker is drawn on or round the ship.
The hitbox itself is unchanged.

**Acceptance criteria**
- Given a level in play, then no hitbox marker is drawn on the player ship.

*Sources: P14-R03, D-194.*

### GFX-READ-09 — Enemies stand out · MUST

Every enemy, mini boss and boss has a light rim in its enemy colour, its glowing edge trim
([GFX-TRIM](edge-trim.md)), so its silhouette separates from the ground. Its dark body (GFX-ART-06)
stays, but it is lit enough (GFX-ART-08) that its shape reads on every world's ground. Ground
enemies (turrets and the like) are as readable as flying ones. Each destroyable boss part has its
own whole outline, so the player sees which parts can still be hit.

**Acceptance criteria**
- Given an enemy over each world's ground, then its rim has a contrast ratio of at least
  `minObjectContrast` with the ground round it (e2e, one level of each world).
- Given a boss, then each of its destroyable parts is outlined on its own.

*Sources: P14-R04, D-220, D-127.*

### GFX-READ-10 — Enemy shots are the most visible thing on screen · MUST

Enemy bullets, missiles and lasers are in the enemy-shot family with a bright core, so they read on
bright and dark ground alike. Every enemy bullet is drawn at least `minEnemyBulletSize` logical
pixels across (its hitbox does not change). Enemy shots are drawn above everything else of the
gameplay layer: explosions, particles, bonuses' glows, the bomb, the player's shots and the models.

**Acceptance criteria**
- Given any enemy bullet over any world's ground, then its core has a contrast ratio of at least
  `minBulletContrast` with what is round it (e2e, one level of each world).
- Given a bullet whose hit radius would draw it smaller, then it is drawn `minEnemyBulletSize`
  across (unit test).
- Given an explosion or hit particles at the same spot, when an enemy bullet passes through, then
  the bullet is drawn over them.

*Sources: P14-R05, D-124.*

### GFX-READ-11 — Contrast look for the enemy shots in every level · MUST

Every enemy and boss bullet has a white spark at its heart, and every laser warning line has a
white core and is drawn 1.5 times as wide. This holds in every level of every world (it was first
World 4's look over lava and red skies). Bullets have no dark rim or ring behind them
([GFX-SHOT](shots.md)).

**Acceptance criteria**
- Given a level of any world, then its enemy bullets have the white spark and its warning lines the
  white core and the wider width.
- Given 4-3, 4-4 and 4-5, then every enemy and boss bullet kind and the warning lines are easy to
  see over the ground and sky (manual).

*Sources: P10-R07, D-086, D-124, D-194.*

### GFX-READ-12 — Enemy missiles and warning lines look unlike bullets · MUST

Enemy missiles (which the player can shoot) and laser warning lines are each recognisable from
plain bullets by their shape, while staying in the enemy-shot family: a missile is a small body
with a flame and an orange rim, a warning line a thin blinking line ([GFX-SHOT](shots.md)).

**Acceptance criteria**
- Given an enemy missile and an enemy bullet side by side, then they are told apart by shape
  (manual).

*Sources: P14-R05.*

### GFX-READ-13 — Draw order of the see-through playfield meshes · SHOULD

See-through playfield meshes are drawn by draw order, lowest first. The explosions use the lowest
(smoke under fire); every playfield mesh that sets no draw order (player shots, reactor flames,
bonus glows, the bomb) is drawn just under the enemy shots; the enemy missile flames and lasers come
next, over the player's shots and the explosions; the enemy bullet layers come last, in their own
order, and ignore depth. The order of the other meshes among themselves is kept.

**Acceptance criteria**
- Given a mesh adopted by the playfield with no draw order, then it gets the order just under the
  enemy shots, and its clones keep it (unit test).
- Given the enemy bullet layers, then their order is above that of every other playfield mesh.

*Sources: D-156, D-124, P14-R05, P14-R06.*

### GFX-READ-14 — Player shots don't hide danger · MUST

The player's shots (gun, laser, missiles, at every weapon level) stay in the player family and are
toned down: the strength of their added-on glows is capped at `playerShotMaxOpacity`. Even at weapon
level 5 they never hide an enemy bullet: the bullet is drawn over them. They still show over the
ground.

**Acceptance criteria**
- Given each weapon's shot renderer, then its additive materials have an opacity of at most
  `playerShotMaxOpacity` (unit test).
- Given a level-5 weapon, when an enemy bullet overlaps a player shot, then the enemy bullet is drawn
  on top and still meets `minBulletContrast`.
- Given a player shot over the ground, then its contrast is at least `minPlayerShotContrast` (e2e).

*Sources: P14-R06, D-125.*

### GFX-READ-15 — Effects don't clutter the screen · MUST

Explosions, hit particles and bomb effects fade fast and are capped in brightness and size, so they
never hide the player ship or the enemy bullets for long. A single explosion covers at most
`effectMaxScreenShare` of the screen and is gone after `effectMaxDuration`. The bomb's flash is dim,
so the ship and the enemy bullets that survive the bomb stay visible through it. The looks are in
[GFX-FX](effects.md).

**Acceptance criteria**
- Given the biggest explosion, then it covers at most `effectMaxScreenShare` of the screen and every
  one of its particles is gone after `effectMaxDuration` (simulation).
- Given a bomb going off, then the player ship and the enemy bullets drawn during its flash stay
  visible.

**Gap:** the simulation test of the screen share and the duration was not carried over to the
Python port; only the size cap of the explosions is unit-tested.

*Sources: P14-R07, D-124, D-133.*

## Tunable values

All in `src/game/config/readability.py` `READABILITY`.

| Name | Value | Notes |
|------|-------|-------|
| `tones` | world1 0.55, world2 0.45, world3 0.45, world4 0.55 | GFX-READ-02 (World 4 lowered by D-162) |
| `backgroundMaxLuminance` | 0.35 | relative luminance, GFX-READ-01 |
| `backgroundBrightPixelBudget` | 0.02 | share of the screen, GFX-READ-01 |
| `families` | player 180–235, enemy 60–140, enemyShot 15–48, pickup 250–295; `minSaturation` 0.5 | hues in degrees, GFX-READ-04 |
| `minObjectContrast` | 3 | contrast ratio (WCAG), GFX-READ-07, GFX-READ-09 |
| `minBulletContrast` | 4.5 | GFX-READ-10, GFX-READ-14 |
| `minEnemyBulletSize` | 6 | logical px across, GFX-READ-10 |
| `playerShotMaxOpacity` | 0.7 | additive opacity, GFX-READ-14 |
| `minPlayerShotContrast` | 2 | GFX-READ-14 |
| `effectMaxScreenShare` | 0.15 | GFX-READ-15 |
| `effectMaxDuration` | 0.6 s | GFX-READ-15 |
| Draw orders | blasts 0–4; unset 999 999; enemy missile flames and lasers 1 000 000; bullet layers 1 000 001 and up | `src/render/node_adopter.py` `ON_TOP_ALPHA_INDEX`, `src/game/view/enemies/enemy_shot_renderer.py` |

## Notes

- History: the background was first darkened by a screen-wide veil (D-122); the reviewer had it
  replaced by the per-world tone (D-130). The rims were first Babylon's per-mesh outline (D-123);
  the reviewer had them replaced by the edge trim built into the models (D-220). A white dot ringed
  in cyan on the ship's hitbox and a dark disc behind every enemy bullet were removed at the
  reviewer's request (D-194).
- The enemy-shot contrast look was first a per-level shot style named by World 4's looks (D-086);
  since D-124 it is on in every level. The World 4 looks still name the style
  (`SceneryLook.shotStyle`) and the test API reports it, but the enemy shot renderer no longer reads
  it.
- Measured in the e2e readability test at the end of phase 14: background 0.07–0.13, ship contrast
  10–13:1, enemies 4.1–11:1, bullets 6.1–11.6:1; explosions at most 7.8 % of the screen and over by
  0.55 s (simulated).
