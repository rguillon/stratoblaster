# Overlord

> **Area:** bosses · **Prefix:** `FB-OVERLORD` · **Related:** [common](../common.md),
> [1-5 Deep Desert](../../worlds/world-1/1-5-deep-desert.md), [Sentinel](../mini/1-5-sentinel.md),
> [World 1](../../worlds/world-1/world.md)

The Overlord is the final boss of 1-5, the last and hardest boss of World 1: a city-sized organism,
6 L across (first designed as a city-ship), a city of living towers grown on its back. Two wing
laser cannons and two missile batteries fire at the player; two shield generators in front are the
only parts shielding its core, a citadel firing every kind of attack. It sheds its flank armour for
a pair of laser lances, then its spine plating for a pair of flak mortars. Shared rules are in
[common](../common.md).

## Requirements

### Look

#### FB-OVERLORD-01 — Silhouette and size · MUST

Seen from above, the Overlord is a vast mantle, 6 L across: a shelled spine down its middle carrying
the citadel, membrane wings out to a laser cannon at each wing tip, two shield generators at its
front (down the screen), two missile batteries at its back, and a skyline of towers over its whole
back.

**Acceptance criteria**
- Manual validation in the boss viewer: a city grown on a living mantle, the biggest World 1 boss.

*Sources: P07-R05, P16-R06.*

#### FB-OVERLORD-02 — Body and city · MUST

Its body is a vast dark mantle (slate and graphite shades) with ribs across it, veins out to its
edges and swim bladders across its tail, four reactors in flesh sacs there. Its shelled spine (the
boulevard) carries missile hatches behind the citadel, lit as missiles load. Its membrane wings
stretch on bone struts out to the laser cannons. Living towers of flesh and bone, lit with window
glands, grow out of its back; the skyline is not symmetrical: a broadcast spire and a neon billboard
on the left (the screen's left), a command stalk with a lit cab on the right.

**Acceptance criteria**
- Manual validation: towers lit with windows over the whole back; the spire and billboard on one
  side, the command stalk on the other.

*Sources: P07-R05, P16-R06.*

#### FB-OVERLORD-03 — Its parts and the citadel · MUST

- **Wing laser cannons** (at the wing tips): a swollen gland on the wing, a grafted collar, a long
  barrel, coils and a lens charging.
- **Missile batteries** (two, at its back): a missile brood on the mantle, a swollen mound under a
  grafted plate with six hatches lit as it loads.
- **Shield generators** (two, at its front): a glowing gland in a ring of grafted coil swelling out
  of a flesh mound, three bone horns round it tipped with neon; no weapon.
- **Citadel** (over the core): a swollen, tiered brain-head ringed with neon, eyes on its front, a
  ring emitter on top and a grafted weapon array before it (twin cannons and a laser).

**Acceptance criteria**
- Given its model, then it draws its six parts and its citadel's guns where its design puts them
  (unit test).

*Sources: P07-R05, P16-R06.*

#### FB-OVERLORD-04 — Lights · MUST

Neon lines its mantle's rim and rings its citadel; window glands light its towers; its generators
and horns glow. Its neon colour, set purple, shows bright yellow ([common](../common.md), BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright yellow.

*Sources: P07-R05, P16-R06, D-231.*

#### FB-OVERLORD-05 — What it sheds · MUST

Its deck (the mantle) is drawn in two layers: a lower slab the whole deck wide (-8 to 3 px), its
neon rim on it, and an upper one (3 to 6 px) whose flanks and front are its armour, drawn as pieces
of their own ([common](../common.md), BOSS-42); the upper layer runs on along its middle, under the
citadel and the boulevard behind it. The raised boulevard (5 to 10 px) is cut across before the
citadel's weapon array.

- The **flank plates** (`flanks`, mirrored), from the city's edge (32 px either side of the centre
  line) out to the deck's edge, are shed at its first transformation, with the city standing on
  them (its towers there, the broadcast spire, the billboard and the command stalk) and the two
  veins across each from the boulevard. Shed, they burst into plates cracked from their outline and
  leave `wing` frames on the lower layer, out of which the lances rise.
- The **front plate** (`spine`), the deck before the citadel's weapon array out to its nose, is
  shed at its second: it carries the boulevard's front, the front rib, two grafted plates, the
  barbs at its nose and the two towers there. Shed, it leaves a `shell` lattice on the lower layer,
  out of which the mortars rise.

**Acceptance criteria**
- Given its design, then each transformation sheds its region and its weapons lie in it (unit
  test).
- Given its model, then it draws each region's piece, and it holds together at rest and after each
  transformation (unit tests).

*Sources: D-224, D-254.*

### Behaviour

#### FB-OVERLORD-06 — Coming in and moving · MUST

It comes in from the top ([common](../common.md), BOSS-08) to `stopFraction` of the playfield's
height, then sways a little and bobs. While it is fought the ground scrolls at ×0.25.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.25 of the level's speed and back after it.

*Sources: P07-R03, P07-R05.*

#### FB-OVERLORD-07 — Parts and core · MUST

It has six parts as it comes in: `generator-left` and `generator-right`, the only ones shielding its
core, and `laser-left`, `laser-right`, `battery-left` and `battery-right`, which do not. Each wing
cannon fires a laser straight down, the two in turn, locked once it fires; each battery fires pairs
of homing missiles, in turn; the generators do not fire. The citadel fires the core's volleys from
its twin cannons, its ring emitter, its laser and its missile hatches; none of them turns.

**Acceptance criteria**
- Given its design, then only its generators shield the core.

*Sources: P07-R01, P07-R05.*

#### FB-OVERLORD-08 — Stage patterns · MUST

The wing lasers and the batteries' missiles go on in every stage while they stand. The core fires:
- stage 0: one purple bullet at the player;
- stage 1: an aimed fan of 3;
- stage 2: a burst of 4 at the player;
- stage 3: a fan of 5;
- stage 4: a ring of 10 turning at each volley;
- stage 5: a fan of 7 and red bursts of 3;
- stage 6 (all six parts gone): every attack kind at once: a ring of 14 purple turning at each
  volley, its own laser and pairs of homing missiles.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys and the parts left fire theirs
  (unit test on its design).

*Sources: P07-R04, D-055.*

#### FB-OVERLORD-09 — Angry · MUST

Its angry pattern is two at once, the hottest of World 1 (heat 4.5): **spirals** (purple and blue)
on 0.6 of its rate and a **flower** (magenta and purple) on 0.4.

**Acceptance criteria**
- Given its design, then its rage is that pattern at that heat, fired from its core.

*Sources: D-063.*

#### FB-OVERLORD-10 — First transformation: lances · MUST

Once two of its parts are destroyed, its flank armour bursts off, baring a dark metal frame, and two
**lances** unfold either side of its middle. They shield the core and fire lasers straight down, in
turn.

**Acceptance criteria**
- Given two parts destroyed, then it transforms and its two lances are revealed.

*Sources: D-221, D-224, D-229.*

#### FB-OVERLORD-11 — Second transformation: mortars · MUST

Once four of its parts are destroyed, the plating of its spine at its front bursts off, baring a
dark metal lattice, and two **mortars** unfold before the citadel, either side of its centre line.
They shield the core and lob purple flak shells that burst into rings of 8, in turn.

**Acceptance criteria**
- Given four parts destroyed, then it transforms a second time and its two mortars are revealed.

*Sources: D-221, D-224, D-229.*

#### FB-OVERLORD-12 — Laser colour · MUST

Its lasers (the wing cannons', the citadel's and the lances') are drawn in its neon folded into the
enemy shots' family: an amber beam round a white-hot core ([common](../common.md), BOSS-32).

**Acceptance criteria**
- Given its lasers, then their colour is its neon folded into the enemy shots' family (unit
  test).

*Sources: D-072, D-231.*

#### FB-OVERLORD-13 — Death, drops and points · MUST

Its parts drop a weapon bonus 60 % of the time, its hidden weapons 30 %, and its core always drops
one ([common](../common.md), BOSS-57). Destroying it ends 1-5
([level flow](../../gameplay/level-flow.md)). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: P07-R07.*

## Tunable values

All in `src/game/config/bosses/final_bosses.py` (`_OVERLORD`, `OVERLORD`) unless named.

| Name | Value | Notes |
|------|-------|-------|
| size | 6 L (radius 102 px) | |
| core | health 5 540, radius 24, drop 1 | twin cannons (±7, -39.6), ring emitter (0, 0) 33.6 px high, laser (0, -38), 4 missile cells |
| `laser-left`, `laser-right` | (∓78, -6), radius 15, health 1 660, no shield, drop 0.6 | |
| `battery-left`, `battery-right` | (∓46, 30), radius 14, health 1 520, no shield, drop 0.6 | 6 cells each |
| `generator-left`, `generator-right` | (∓34, -36), radius 13, health 1 940, shield, drop 0.6 | no weapon |
| full health | 22 760 (15 780 without the hidden weapons) | BOSS-54 |
| points | 15 000; 1 500 a part | |
| ground speed | ×0.25 | |
| stop height | 0.75 | |
| sway / bob | 25 px over 11 s / 6 px over 5 s | |
| wing lasers | 1.4 s every 6.5 s (first 2 s / 5.25 s) | |
| battery missiles | 2, 24° apart, every 5.5 s (first 3.5 s / 6.25 s) | |
| core stage 0 | 1 aimed purple bullet, 195 px/s, every 2.8 s | |
| core stage 1 | aimed 3, 12° apart, every 2.4 s | |
| core stage 2 | burst of 4, 0.13 s apart, every 2.4 s | |
| core stage 3 | fan of 5, 14° apart, every 2.4 s | |
| core stage 4 | ring of 10 turning 6°, every 2 s | |
| core stage 5 | fan of 7, 12° apart, every 2.2 s; red burst of 3 every 2.6 s | |
| core stage 6 | ring of 14 turning 9° every 1.2 s; laser 1.4 s every 5 s; 2 missiles, 30° apart, every 6 s | |
| angry | spirals × 0.6 and flower × 0.4, heat 4.5 (56 bullets a second in all, 156 px/s) | |
| transformations | 2 and 4 parts destroyed | default thresholds |
| flank region (shed) | the deck's flank plate, x 32..64 at y -18..30, its edge to (52, -42) and (62.8, 32), back to x 32 at y -42..32, `wing`, mirrored; the plate 3-6 px, the city on it | first |
| spine region (shed) | the deck's front plate: x -32..32 from y -34, out to (±52, -42) along y -42, then along the deck's edge to (±26, -60) and its nose (0, -64), `shell`, not mirrored; the plate 3-6 px, the boulevard's front to 10 px | second |
| lances (`pike-*`) | (∓47, -1), radius 11, health 1 550, pod 41.1 px; first 1.2 s / 2.0 s | |
| mortars | (∓13, -55), radius 11, health 1 940, pod 14.1 px, purple; first 1.2 s / 2.0 s | |
| neon | purple (0.65, 0.2, 1), shown yellow | `BOSS_LOOK.neon` |

## Notes

- Its city look comes from the first spec, written when 1-5 ended over a city centre; 1-5 is now the
  deep desert (no city in World 1, reviewer 2026-10-27; D-200). Re-theming it is the reviewer's
  call.
- Its purple neon (hue 274) is a hair nearer yellow than green, so it is lit yellow.
