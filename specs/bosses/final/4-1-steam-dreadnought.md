# Steam Dreadnought (4-1 final boss)

> **Area:** bosses · **Prefix:** `FB-STEAM-DREADNOUGHT` · **Related:** [common boss rules](../common.md),
> [4-1 Garden town](../../worlds/world-4/4-1-garden-town.md), [World 4](../../worlds/world-4/world.md),
> [Cinder Crab](../mini/4-1-cinder-crab.md), [readability](../../graphics/readability.md),
> [shots](../../graphics/shots.md)

The Steam Dreadnought is the final boss of level 4-1, met at the end of the level. It is a flying
battleship 5 L long: a long armoured hull under a deck with sponsons for two broadside turrets, a
stepped bridge over its core, two smokestacks puffing steam amidships, a laser ram at its bow and a
missile rack on its stern. It was designed for the Volcanic Lands' black-sand coast; since World 4
became the Metropolis (D-112) it keeps its name and its forge look and flies over the garden town.
It transforms twice: first its front side decks fan out, a gun battery riding each; then its stern
and spine plating burst off for two mortars and a ring emitter. Everything shared by all bosses is
in [bosses/common.md](../common.md); this file only gives what is the Dreadnought's own. Positions
are px from the boss's centre, X right, Y up the screen (its bow at -Y); heights are above the
playfield.

## Requirements

### Look

#### FB-STEAM-DREADNOUGHT-01 — Silhouette · MUST

Seen from above, the Dreadnought is a battleship about 5 L long (radius 2.5 L), bow down the screen:
a long hull about 164 px from stern to stem and 56 px wide, under a deck that widens at the
sponsons to about 140 px across, a raised citadel amidships, a stepped bridge of three tiers over
the centre, the two smokestacks behind it, the broadside turrets on the sponsons ahead of them, a
gun block and a laser ram at the bow and the missile rack on the stern.

**Acceptance criteria**
- Given the dev bosses viewer, when the Dreadnought is shown, then it reads as a long battleship
  with a bridge, two stacks and two broadside turrets (manual).

*Sources: P10-R11.*

#### FB-STEAM-DREADNOUGHT-02 — Cyber-Organic body · MUST

It is a living sky-leviathan (Cyber-Organic): a flesh hull banded in darker seams, its deck a
scorched hide ribbed in bone (rib arches fore and aft), molten veins along both sides of the deck
and glowing glands on it, its smokestacks steaming flesh blowholes. Metal is grafted on as the
citadel, the bridge (tiers with lit windows, wings, a mast and the beacon), the bow's gun block and
laser ram, the turrets and the rack. The World 4 forge dressing lies over it: molten stripes low on
the hull's sides, molten seams between the deck plates, soot behind the stacks and at the bow,
cowls, bolts and a hot vent. Its three reactors sit in glowing flesh sacs at the stern.

**Acceptance criteria**
- Given the model, then it reads as one creature with a battleship grafted on, not as parts stuck on
  a box (manual).

*Sources: P10-R11, P16-R06.*

**Discrepancy:** P16-R06 asks for the world's theme to stay recognisable ("a metropolis boss feels
like a city-sized organism"); the model keeps the volcanic forge theme of its design (D-112 left the
World 4 bosses unchanged) and nothing in it reads as a city.

#### FB-STEAM-DREADNOUGHT-03 — Smokestacks · MUST

Each smokestack is a tall flesh casing banded with worn metal and a neon ring, sooted at its top,
its mouth glowing (a charge light) as the next ring loads, three puffs of steam trailing back from
it (static geometry, faintly lit). Destroyed, a stack is hidden and leaves nothing in its place.

**Acceptance criteria**
- Given the model, then each stack's mouth sits at its muzzle, 34 px high (unit:
  `test_boss_models.py`; manual).

*Sources: P10-R11, P16-R06, D-225, D-167.*

#### FB-STEAM-DREADNOUGHT-04 — Broadside turrets · MUST

Each broadside turret stands on a flesh barbette ringed with neon on its sponson, with a hazard
stripe on the deck beside it. The turret itself is a faceted metal dome with a mantlet, a
rangefinder across its roof, a molten seam on its roof and twin barrels pointing down the screen at
rest; it turns on its barbette the way it fires next. Destroyed, a turret and its barbette are
hidden and leave nothing in their place.

**Acceptance criteria**
- Given a turret stands, then its dome and barrels turn to follow the player (manual; unit: turret
  rule in [common](../common.md)).

*Sources: P10-R11, P16-R06, D-225.*

#### FB-STEAM-DREADNOUGHT-05 — Missile rack · MUST

The missile rack on the stern is an armoured launcher box, lights along its sides, four missile tips
in their tubes and soot from the launches. Destroyed, it is hidden and leaves nothing in its place.

**Acceptance criteria**
- Given the model, then the rack's four cells sit at its missile muzzles (unit: `test_boss_models.py`).

*Sources: P10-R11, P16-R06, D-225.*

#### FB-STEAM-DREADNOUGHT-06 — Lights and colours · MUST

Its registered neon is red (`steam-dreadnought`); like every boss's lights it is drawn bright yellow
(see [readability](../../graphics/readability.md)). Neon lights the deck's whole rim, the bridge's
windows and wing lights, the mast, the beacon's ring, the stacks' rings and the barbettes' rings;
its molten stripes, seams, veins and glands are in the same yellow family. White charge lights sit
on the beacon, in the stacks' mouths, at the barrels' mouths and in the laser ram's lens.

**Acceptance criteria**
- Given the model, then every neon and glowing vein is bright yellow (unit: enemy colour family
  tests).

*Sources: P10-R11, D-231.*

### Behaviour

#### FB-STEAM-DREADNOUGHT-07 — Entry, place and ground speed · MUST

The Dreadnought comes in from above the top edge and stops at 0.74 of the playfield's height. In
place it sways up to 40 px either side over 10 s and bobs 5 px over 5 s. While it is fought the
ground runs at ×0.6 the level's speed.

**Acceptance criteria**
- Given the fight starts, then the ground slows to ×0.6 and the boss stops at 0.74 of the
  playfield height (unit: `test_world_boss.py` for the rule; design values in the config).

*Sources: P10-R11.*

#### FB-STEAM-DREADNOUGHT-08 — Parts and health · MUST

The Dreadnought has a core (hit radius 18 px, 3 600 HP) and five original parts: two broadside
turrets (10 px, 950 HP each) and two smokestacks (10 px, 850 HP each), the four shielding the core,
and the missile rack (10 px, 600 HP) on the stern, which does not. Its full health is 7 800 HP with
the original parts, 12 170 HP with its five hidden weapons, which count in the health bar from the
start.

**Acceptance criteria**
- Given the design, then it has five original parts and five hidden ones, and the rack is the only
  original part that does not shield the core (unit: `test_steam_dreadnought.py`).

*Sources: P10-R11, D-088, D-221.*

#### FB-STEAM-DREADNOUGHT-09 — Smokestack rings · MUST

While they stand, in every stage, each smokestack pours a ring of 10 `orange` bullets (195 px/s)
out of its mouth every 3.6 s, the left one turning 9° each time and the right one -9°, the left
first 1.2 s and the right 3 s into a stage.

**Acceptance criteria**
- Given a stack stands, then its rings leave its mouth (unit: design guns and stages).

*Sources: P10-R11.*

#### FB-STEAM-DREADNOUGHT-10 — Broadside bursts · MUST

While they stand, in every stage, each broadside turret fires a burst of 4 `red` bullets (205 px/s,
0.12 s apart) at the player every 3.2 s from its twin barrels, turning to aim, the left one 0.8 s and
the right one 2.4 s into a stage.

**Acceptance criteria**
- Given a turret stands, then its bursts leave its barrels' tips as the turret has turned (unit:
  turret volleys in `boss_build.py`).

*Sources: P10-R11.*

#### FB-STEAM-DREADNOUGHT-11 — Missile rack · MUST

While it stands, in every stage, the rack fires 2 homing missiles (30° apart) every 6.5 s from its
cells, first 3.5 s into a stage.

**Acceptance criteria**
- Given the rack stands, then two missiles leave it every 6.5 s (unit: design stages).

*Sources: P10-R11.*

#### FB-STEAM-DREADNOUGHT-12 — Core: bow laser and patterns by stage · MUST

The core fires its bow laser straight down the screen at every stage, after its warning line, and
something new beside it (stage k: k parts destroyed; from the fifth on, its last pattern):
- stage 0: the laser every 7 s (1.5 s long), alone;
- stage 1: the laser every 6.5 s (1.5 s), and aimed spreads of 3 `magenta` (210 px/s, 12° apart)
  every 2.8 s from the twin bow guns;
- stage 2: the laser every 6.5 s, and fans of 5 `magenta` (14° apart) every 2.6 s;
- stage 3: the laser every 6 s (1.6 s), and a ring of 12 `purple` (200 px/s) every 2.4 s from the
  bridge's beacon, turning 11°;
- stage 4: the laser every 5.5 s, a fan of 7 `magenta` (12° apart) and a single aimed `red` bullet,
  both every 2.4 s;
- stage 5: the laser every 5 s, and two spirals turning opposite ways from the beacon (rings of 4
  every 0.5 s, `blue` turning 19° and `purple` turning -23°), used by no earlier stage.

**Acceptance criteria**
- Given the design, then it has one stage per original part plus one, the laser is in every stage
  and the last stage's spirals are used by no earlier stage (unit: `test_steam_dreadnought.py`).

*Sources: P10-R11, D-088.*

#### FB-STEAM-DREADNOUGHT-13 — Laser colour · MUST

Its lasers are drawn in its own colour: its red neon moved into the enemy shots' family, an amber
(about [1, 0.81, 0.08]) round a white-hot core, the warning line with a white core as all World 4
warning lines (see [shots](../../graphics/shots.md)).

**Acceptance criteria**
- Given the bow laser fires, then its beam is amber, not red (unit: `enemy_lasers.color_of`).

*Sources: P10-R11, D-072.*

#### FB-STEAM-DREADNOUGHT-14 — Rage · MUST

After the pause that follows each destroyed part, the Dreadnought is angry: it fires a flower (a
dense, slowly turning ring and small aimed fans) at heat 10, in `red` and `orange`: about 100
bullets a second at 200 px/s, World 4's coolest final boss rage.

**Acceptance criteria**
- Given a part is destroyed, when its pause is over, then the core fires the flower for the rage
  time (unit: `test_boss_rage.py`, `test_steam_dreadnought.py`).

*Sources: D-088, D-063.*

#### FB-STEAM-DREADNOUGHT-15 — First transformation: the decks fan out · MUST

Once both broadside turrets are destroyed, the Dreadnought transforms: its two front side decks
swing 25° outwards, each on a hinge at its inner bow corner (20 px out, 54 px ahead), turning
about the vertical, and stay in their new pose. Each is a piece of the model's own ([common](../common.md),
BOSS-42, BOSS-45): the sponson deck plate from its seam with the core's deck at 20 px out round
the deck's own edge (from 54 px ahead of the centre to 2 px behind it, 70 px out at the widest),
a bevelled slab of scorched hide 4.5 to 9 px high with the deck's red rim lights on its edge, and
on it the molten vein's forward run, two glands and a soot stain; the broadside turret's barbette
stands on it while the turret lives. Dark metal `wing` frames show in the wedges they open, on the
hull flanks where the decks lay. A gun battery rides each deck: drawn where the deck ends up, it
comes in with it. The turrets, which stood on the decks, are gone before they move. The boss
stays one object after the move.

**Acceptance criteria**
- Given both turrets are destroyed, then the boss transforms and its decks swing out 25° (unit:
  `test_boss_kinds.py`: transform parts, no hit part on a moving piece, the riding batteries end
  up on their decks).
- Given the boss after this transformation, then nothing of it hangs in the air (unit:
  `test_d227_the_boss_holds_together_in_every_state`).

*Sources: D-230, D-221, D-224, D-227, D-254.*

#### FB-STEAM-DREADNOUGHT-16 — First hidden weapons: two gun batteries · MUST

The first transformation reveals two gun batteries riding the decks, 57 px either side of the
centre and 45 px ahead of it (radius 9 px, pods 16 px high, 760 HP each, 30 % drop chance). They
shield the core and fire `red` fans straight down as every battery does (see
[common](../common.md)), the left one 1.2 s and the right one 2.0 s into a stage.

**Acceptance criteria**
- Given the first transformation is over, then both batteries are live targets that fire (unit:
  `test_boss_kinds.py` weapon checks).

*Sources: D-221, D-229, D-230.*

#### FB-STEAM-DREADNOUGHT-17 — Second transformation: stern and spine plating burst off · MUST

Once both smokestacks are destroyed, the Dreadnought transforms again: its stern flank decks and
its spine plating, pieces of the model's own ([common](../common.md), BOSS-42), burst off. Each
flank deck is the stern deck plate from its seam with the core's deck at 18 px out round the deck's
own edge (from 17 px to 76 px behind the centre, 39.5 px out at the widest, the stern edge at 76),
a bevelled slab of scorched hide 4.5 to 9 px high with the deck's red rim lights, and on it the
molten vein's stern run, a soot stain and a cowl. The spine plating is the stern half of the
citadel (36 px wide across the centre line, from 13 px to 46 px behind the centre, 9 to 12 px high)
with the molten seam on its top. They leave dark metal frames: `wing` frames on the hull flanks
where the decks lay, a `shell` lattice on the deck where the citadel stood. The mortars lie folded
under the flank decks and the ring emitter under the spine plating. The boss stays one object
after it.

**Acceptance criteria**
- Given both stacks are destroyed, then the boss transforms a second time and these regions burst
  off (unit: `test_boss_kinds.py`, `test_boss_armour.py`).
- Given the boss after its second transformation, then nothing of it hangs in the air (unit:
  `test_d227_the_boss_holds_together_in_every_state`).

*Sources: D-221, D-224, D-227, D-230, D-254.*

#### FB-STEAM-DREADNOUGHT-18 — Second hidden weapons: two mortars and an orb · MUST

The second transformation reveals two mortars on the stern, 30 px either side of the centre and
47 px behind it (radius 8 px, pods 12.6 px high, 950 HP each), firing `orange` flak shells, and a
ring emitter (orb) on the spine's centre line, 29 px behind the centre (radius 11 px, pod 15.6 px
high, 950 HP), firing `red` rings, as those kinds do (see [common](../common.md)); first 1.2 s,
2.6 s and 1.6 s into a stage. They shield the core and drop a bonus 30 % of the time. Its fire goes
up at each transformation (about 9.8, then 16.3, then 16.9 weighted shots a second).

**Acceptance criteria**
- Given the second transformation is over, then the mortars and the orb are live targets that fire,
  of kinds not revealed at the first (unit: `test_boss_kinds.py`).

*Sources: D-221, D-229.*

#### FB-STEAM-DREADNOUGHT-19 — Points and drops · MUST

Destroying the Dreadnought scores 21 000 points, and each part destroyed 2 100. Its original parts
drop a bonus 60 % of the time, its hidden weapons 30 %, and its core always drops one.

**Acceptance criteria**
- Given a turret is destroyed, then the score rises by 2 100 (unit: scoring rule, design values).
- Given e2e `?level=4-1&boss=final`, when K destroys the Dreadnought, then the level is complete
  (e2e: `test_world_4.py`).

*Sources: P07-R07, P11-R01, D-088.*

## Tunable values

All in `src/game/config/bosses/world_4/steam_dreadnought.py` (`STEAM_DREADNOUGHT`) unless noted.

| Name | Value | Notes |
|------|-------|-------|
| level | 4-1, final | `src/game/config/world_4/bosses.py` `WORLD_4_BOSSES` |
| size | 5 L (radius 85 px) | `stats.size` |
| core | radius 18 px, 3 600 HP | `coreRadius`, `coreHealth` |
| turrets | (±56, -20), radius 10, 950 HP, shield | `DREAD_PARTS.turret` |
| smokestacks | (±30, 16), radius 10, 850 HP, shield | `DREAD_PARTS.stack` |
| missile rack | (0, 54), radius 10, 600 HP, no shield | `DREAD_PARTS.rack` |
| full health | 7 800 (12 170 with hidden weapons) | D-088 |
| stop / sway / bob | 0.74 / 40 px, 10 s / 5 px, 5 s | `stopFraction`, `sway`, `bob` |
| ground speed | ×0.6 | `groundSpeed` |
| heights | deck 9, stack mouths 34, rack 15 | `DREAD_HEIGHTS` |
| muzzles | bow guns (±9, -70, 11), lens (0, -87, 6), beacon (0, -7, 38), turret barrels (±56 ∓ 2.4, -37, 12.5) | `DREAD_*` |
| stack rings | 10, every 3.6 s, turn ±9°, first 1.2 / 3 s | stage volleys |
| turret bursts | 4, 0.12 s apart, every 3.2 s, first 0.8 / 2.4 s | stage volleys |
| rack | 2 missiles, 30°, every 6.5 s, first 3.5 s | `volley.missiles` |
| bow laser | every 7 → 5 s, 1.5–1.6 s, 1 s warning, 12 px wide | core stages |
| bullets | `red` 205, `orange` 195, `magenta` 210, `purple` 200, `blue` 200 px/s | radius 4 |
| rage | flower, heat 10 (`red`, `orange`) | `rage.flower` |
| transformations | both turrets; then both stacks | `transformParts` |
| decks (moving) | the sponson deck's shape (mirrored): from (20, -54) along the bow edge to (36, -40), (66, -32), (70, -20), (66, -8), (40, -2) and back along x 40 then x 20 to y 2; above -8; swing about up at (±20, -54), 0 → 25° out; deck 4.5–9 px | `moving_region("decks", …)`, `src/game/config/bosses/moving_regions.py`, `steam_dreadnought_armour.py` |
| stern flanks | the stern deck's shape (mirrored): from (18, 17) out to (39.5, 17), along the edge to (39, 30), (32, 60), (20, 76) and back along the stern edge to (18, 76); `wing`; deck 4.5–9 px | `armour_region("flanks", …)` |
| spine | x -18..18, y 13..46, `shell`, not mirrored; the citadel's stern half, 9–12 px | `armour_region("spine", …)` |
| batteries | (±57, -45), radius 9, pod 16, 760 HP, `red`, first 1.2 / 2.0 s | form 1 |
| mortars | (±30, 47), radius 8, pod 12.6, 950 HP, `orange`, first 1.2 / 2.6 s | form 2 |
| orb | (0, 29), radius 11, pod 15.6, 950 HP, `red`, first 1.6 s | form 2 |
| drops | parts 0.6, hidden weapons 0.3, core 1 | `fpart`, `coreDrop` |
| points | 21 000 (2 100 a part) | `points`, `boss_part_points` |
| neon | [1, 0.08, 0.1], drawn bright yellow; laser [1, 0.81, 0.08] | `src/game/config/boss_look.py` `BOSS_LOOK.neon["steam-dreadnought"]` |

## Notes

- Phase 10 fight time with the D-055 bot: 89.2 s, before the hidden weapons (D-221). The turrets
  were placed at ±56 px for the bot's spread (as D-081). The bot seldom destroys the rack, behind
  the core (D-088); a player can still shoot it.
- The steam on its stacks is static geometry; the props' plumes are the moving ones.
- Its full health takes its place in World 4's boss ordering (P10-R12, see
  [World 4](../../worlds/world-4/world.md)).
