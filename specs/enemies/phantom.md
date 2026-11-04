# Phantom

> **Area:** enemies · **Prefix:** `ENM-PHANTOM` · **Related:** [common.md](common.md), [World 3](../worlds/world-3/world.md), [World 4](../worlds/world-4/world.md), [graphics/edge-trim.md](../graphics/edge-trim.md)

The Phantom is a veteran kind ([common.md](common.md)) and **tier 3's diver**
(`src/game/config/enemy_tiers.py`): a cloaker. It fades out, moves unseen and fades in somewhere
else in the upper half, twice, firing an aimed spread when it comes back the first time. After the
second time it turns its nose to the player and dives at where the player was, leaving at the
bottom. While it is faded out it cannot be hit and cannot ram the player. It has no moving parts. A
Broodmother launches Phantoms from its hatches with the same constructor.

## Requirements

### Look

#### ENM-PHANTOM-01 — Shape and size · MUST

The Phantom is a sleek flying wing 1 L across (about 0.75 L from nose to tail): one wing swept back
from a pointed nose to two tips, its trailing edge notched, a low body blended into the middle of
the wing.

**Acceptance criteria**
- Given the Phantom's model, then it is 1 L across (within the size tolerance of
  [common.md](common.md)) and reads as one flying wing from above.

*Sources: P05-R17, P16-R04.*

#### ENM-PHANTOM-02 — Cyber-Organic body · MUST

The Phantom is Cyber-Organic ([common.md](common.md)). Its wing is a membrane with faceted,
bevelled edges (membrane and graphite shades), held out by bone struts from its shoulders to the
tips; its body is a low, ridged flesh shell (graphite and membrane). Metal is grafted on: a nose cap
over the gun, and the gun barrel under it.

**Acceptance criteria**
- Given the Phantom's model, then its wing and body are flesh on bone struts, and the nose cap and
  gun are metal.

*Sources: P05-R17, P16-R04.*

#### ENM-PHANTOM-03 — Neon edges · MUST

Neon edges run along the wing's leading edges, from the nose to each tip, and across each tip; a
glowing vein runs along each side of the body, and two eyes glow on the nose, all in the Phantom's
neon colour. That colour is a pale green: its configured pale violet is on the green side of the
two enemy hues ([common.md](common.md)), so it is drawn at the enemy green hue, keeping its own
brightness and paleness.

**Acceptance criteria**
- Given the Phantom's model, then its edges, veins and eyes are lit in pale green (hue 125°).

*Sources: P05-R17, P16-R04, D-231.*

#### ENM-PHANTOM-04 — Charge light · SHOULD

A charge light at the gun's mouth brightens as the Phantom fades in and is at full brightness when
its spread leaves ([common.md](common.md)); it also brightens during the pause before the dive.

**Acceptance criteria**
- Given a Phantom fading in, then its charge follows its opacity; after the fade-in it is 0.
- Given a Phantom aiming for its dive, then its charge rises, and is 0 once it dives.

*Sources: P05-R17, P16-R04.*

#### ENM-PHANTOM-05 — Reactors · MUST

Two plain reactors (no flesh sac) sit at the back of its body. Its wing does not flutter.

**Acceptance criteria**
- Given the Phantom's model, then it has two reactors and one gun muzzle.

*Sources: P16-R04.*

#### ENM-PHANTOM-06 — The model fades with it · MUST

Every mesh of the Phantom's model (body, lights, reactors and their flames) is as visible as the
Phantom is (its opacity, 0 to 1): see-through while it fades, hidden when its opacity is 0.

**Acceptance criteria**
- Given a Phantom with opacity 0.3, then each of its meshes is drawn at visibility 0.3.
- Given a Phantom with opacity 0, then none of its meshes is drawn.

**Discrepancy:** its glowing edge trim ([graphics/edge-trim.md](../graphics/edge-trim.md), D-220)
does not fade: the trim meshes are added to the model after it lists the meshes it fades, and they
do not inherit their parents' visibility, so the outline stays lit while the Phantom is hidden
(found by reading the code; not checked in a browser).

*Sources: P05-R17.*

#### ENM-PHANTOM-07 — Triangle budget · MUST

The Phantom's model, reactors included, stays within the veteran triangle budget (700,
[common.md](common.md)). It is about 490 triangles before the edge trim.

**Acceptance criteria**
- Given the Phantom's model, then its triangle count is at most the veteran budget.

*Sources: P16-R04, P16-R09.*

### Behaviour

#### ENM-PHANTOM-08 — Entry · MUST

A Phantom comes in alone from just above the top edge, at the wave's entry position or at a random
X between 25 % and 75 % of the width. It flies down at 150 px/s, slowing over the last 60 px (never
below 25 px/s), to a random height between 60 % and 82 % of the playfield (the upper half), then
holds there 0.6 s. Its constructor takes where it starts and the height where it first stops, so a
Phantom launched from a Broodmother's hatch, anywhere on the screen (above or below that height),
flies to its stop the same way.

**Acceptance criteria**
- Given a Phantom comes in, then it stops at a height between 60 % and 82 % of the playfield.
- Given a Phantom starts below its stop height, then it rises to it and holds there.

*Sources: P05-R17.*

#### ENM-PHANTOM-09 — Two jumps · MUST

Then, twice, the Phantom fades out over 0.4 s, stays invisible for 0.8 s, and reappears at
another place in the upper half: a random X between 15 % and 85 % of the width and a random height
between 60 % and 82 %, at least 110 px from where it was (it tries up to 8 places). It reappears
nose to the player and fades in over 0.4 s; after the first jump it fires (ENM-PHANTOM-10) and
holds 0.6 s, after the second it dives (ENM-PHANTOM-11). Its holds get shorter with the level's
fire rate factor ([common.md](common.md)).

**Acceptance criteria**
- Given a Phantom, then it runs its fade cycle twice, then aims and dives, with its opacity always
  between 0 and 1.
- Given it reappears, then its new place is in the upper half and, but for bad luck after 8 tries,
  at least 110 px from the old one.

*Sources: P05-R17.*

#### ENM-PHANTOM-10 — Aimed spread · MUST

The first time it has faded back in (and only then), the Phantom fires a spread of 5 bullets (200 px/s) 12° apart,
centred on the player, from the gun at its nose, from its new place.

**Acceptance criteria**
- Given a Phantom reappears the first time, then it fires its aimed spread of 5 from its new place,
  once its fade-in ends.
- Given it reappears the second time, then it fires nothing.

*Sources: P05-R17.*

#### ENM-PHANTOM-11 — Dive · MUST

Once it has faded in the second time, the Phantom turns its nose to the player for 0.5 s (easing
in, as the Hornet's, [hornet.md](hornet.md)), then dives in a straight line at where the player was
at the end of that pause, accelerating from rest at 900 px/s² up to 560 px/s, until it is off the
bottom of the screen. It fires nothing during the dive, and is fully visible (it can be hit and can
ram the player).

**Acceptance criteria**
- Given a Phantom has faded in the second time, then it turns to the player, locks the player's
  position at the end of 0.5 s, and moves along that line, faster each step up to 560 px/s.
- Given it dives, then it leaves the screen at the bottom.

*Sources: P05-R17.*

#### ENM-PHANTOM-12 — Cloak · MUST

While the Phantom is faded out, less than half visible (opacity below 0.5), the player's shots pass
through it and it cannot ram the player: it has nothing to hit.

**Acceptance criteria**
- Given a Phantom is faded out, then the player's shots cannot hit it and it has no hit target.
- Given a Phantom at opacity just above 0.5, then it can be hit.

*Sources: P05-R17.*

#### ENM-PHANTOM-13 — Health, points and hit circle · MUST

A Phantom has 90 HP and scores 450 points. Its points are high for its health because its cloak
makes it harder to hit: the rule that tougher enemies score more is checked on the eleven basic
kinds only ([gameplay/scoring.md](../gameplay/scoring.md)). Its hit circle, at its centre, is 0.8 of
the usual one for its size (11.6 px).

**Acceptance criteria**
- Given a Phantom, then it takes 90 damage to destroy and scores 450 points.

*Sources: P05-R17, D-090.*

#### ENM-PHANTOM-14 — Veteran kind, from World 3 · MUST

The Phantom is a veteran kind. No wave of World 1 or World 2 uses it. World 3 brings it in at 3-5,
the last veteran kind, and every level of World 4 uses it.

**Acceptance criteria**
- Given the wave scripts, then no level before 3-5 names the Phantom, and 3-5 and every level of
  World 4 do.

*Sources: P05-R24, D-090.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| size | 1 L | `src/game/config/enemies_veteran.py` `VETERAN_CONFIG.phantom.size` |
| health / points | 90 / 450 | `VETERAN_CONFIG.phantom.stats` |
| hit radius | 11.6 px | `radius(1) * 0.8` |
| xRange | 25 % – 75 % of the width | its entry X, when the wave gives no entry |
| entrySpeed / brakeDistance | 150 px/s / 60 px | slowest 25 px/s (`src/game/sim/enemies/phantom.py` `CREEP`) |
| placeX / placeY | 15 % – 85 % / 60 % – 82 % | its first stop's height and every place it reappears at |
| jumpDistance | 110 px | at least this far from the last place; `TRIES` 8 in `phantom.py` |
| fade / hidden / hold | 0.4 s / 0.8 s / 0.6 s | the hold is divided by the level's fire rate factor |
| jumps / spreadJump | 2 / 1 | it fires after jump 1 only |
| solidOpacity | 0.5 | below it, shots pass through and it cannot ram |
| pause / diveAcceleration / diveMaxSpeed | 0.5 s / 900 px/s² / 560 px/s | the dive; `TURN_EASE` 14 in `phantom.py` |
| spreadCount / spreadSpacing | 5 / 12° | style `purple`, 200 px/s |
| muzzles | `[0, -14.6, 0.6]` | the gun under its nose cap |
| neon | `[0.75, 0.6, 1]`, drawn `[0.6, 1, 0.63]` | `VETERAN_NEON.phantom` |
| triangle budget | 700 (veteran) | `src/game/config/enemy_look.py` `ENEMY_LOOK.budget.veteran` |

## Notes

**Appears in** (`src/game/config/world_3/waves.py`, `world_4/waves.py`): one Phantom in a phrase of
its level's cycle in each of [3-5](../worlds/world-3/3-5-garden-villages.md),
[4-1](../worlds/world-4/4-1-garden-town.md), [4-2](../worlds/world-4/4-2-inner-town.md),
[4-3](../worlds/world-4/4-3-midtown.md) and [4-4](../worlds/world-4/4-4-business-district.md), and
2 (2 s apart) in [4-5](../worlds/world-4/4-5-downtown.md); the groups grow over each level. It is
in no level's filler.

- Known gaps: no unit test checks the model's size, its triangle count or its fading since the
  Python port (D-220).
