# Ember Herald (4-5 mini boss)

> **Area:** bosses · **Prefix:** `MB-EMBER-HERALD` · **Related:** [common boss rules](../common.md),
> [4-5 Downtown](../../worlds/world-4/4-5-downtown.md), [World 4](../../worlds/world-4/world.md),
> [Caldera Throne](../final/4-5-caldera-throne.md), [readability](../../graphics/readability.md)

The Ember Herald is the mini boss of level 4-5, met at the middle of the level, and World 4's second
chase: the ground speeds up under it. It is a fast, spiky interceptor 3.5 L long, wreathed in
embers, with a ring turning over its back that carries three ember lances. It was designed to chase
the ship down the volcano's slope to the caldera; since World 4 became the Metropolis (D-112) it keeps
its name and its look and chases over downtown. It is World 4's hardest mini boss. It transforms
once: its back plating bursts off and two ring emitters unfold. Everything shared by all bosses is in
[bosses/common.md](../common.md); this file only gives what is the Herald's own. Positions are px
from the boss's centre, X right, Y up the screen (its nose at -Y); heights are above the playfield.

## Requirements

### Look

#### MB-EMBER-HERALD-01 — Silhouette · MUST

Seen from above, the Herald is a spiky interceptor about 3.5 L long (radius 1.75 L), nose down the
screen: a long, hard-edged fuselage about 114 px from tail to needle nose, spiky wings about 114 px
across (a forward spike off each wing root, a long spike at each tip, a sawtooth trailing edge and a
spike at the tail), dorsal spikes down its back, and over its centre a spire rising through the hub
of a ring 80 px across that turns over it, carrying three lances pointing out of it to about 61 px
from the centre.

**Acceptance criteria**
- Given the dev bosses viewer, when the Herald is shown, then it reads as a spiky interceptor with a
  ring of three lances turning over it (manual).

*Sources: P10-R11.*

#### MB-EMBER-HERALD-02 — Cyber-Organic body · MUST

It is a living fire-wasp (Cyber-Organic): its long flesh body ribbed in bone, soot-black behind its
canopy, its wings scorched membranes veined molten with soot-dark tops cracked by molten seams and
leading edges lit, bone spines with a molten glow at their roots leaning aft down its back, its
reactors aft; metal is grafted on as its spire (its crown lit where the core's spirals leave), the
ring (its "halo") and the twin ember cannons under its nose. Embers wreathe it: 26 small glowing
motes scattered round the hull and up past the ring (part of the model, the same every time).

**Acceptance criteria**
- Given the model, then it reads as one creature wreathed in embers (manual).

*Sources: P10-R11, P16-R05.*

#### MB-EMBER-HERALD-03 — Turning ring and ember lances · MUST

The ring is a soot-black rim lit along its edge, held by three spokes from a hub round the spire.
Each ember lance stands on the ring, pointing out of it: a soot-black shaft with molten bands and a
collar, a glowing blade out to its tip, two pairs of barbs, a clamp holding it to the ring and a
charge light at its tip where its spiral leaves. The ring stays when its lances are gone; a destroyed
lance is hidden and leaves nothing in its place.

**Acceptance criteria**
- Given the dev viewer, when K destroys a lance, then it disappears and the ring goes on turning
  (manual; `test_boss_models.py` checks every part is drawn).

*Sources: P10-R11, P16-R05, D-225, D-167.*

#### MB-EMBER-HERALD-04 — Lights and colours · MUST

Its registered neon is gold (`ember-herald`); like every boss's warm lights it is drawn bright yellow
(see [readability](../../graphics/readability.md)). Neon lights the gold strips down the fuselage's
flanks, the wings' leading edges, the ring's rim and hub, the lances' collars and blades; its molten
seams, veins, spines' roots and embers (gold, ember and molten in the design) are in the same yellow
family. White charge lights sit at the lances' tips, the nose cannons' mouths and the spire's crown.

**Acceptance criteria**
- Given the model, then every neon light and ember is bright yellow (unit: enemy colour family
  tests).

*Sources: P10-R11, D-231.*

### Behaviour

#### MB-EMBER-HERALD-05 — Entry, place and chase · MUST

The Herald comes in from above the top edge and stops at 0.74 of the playfield's height. In place it
sways up to 60 px either side over 6 s and bobs 8 px over 2.8 s. While it is fought the ground runs
at ×1.4 the level's speed: a chase.

**Acceptance criteria**
- Given the fight starts, then the ground speeds up to ×1.4 and the boss stops at 0.74 of the
  playfield height (unit: `test_world_boss.py` for the rule; design values in the config).

*Sources: P10-R11.*

#### MB-EMBER-HERALD-06 — The ring turns · MUST

The ring and its three lances turn round the core at 0.9 radians a second, from the moment the
Herald comes in. The lances are orbiting parts: their hit circles and their tips turn with the ring.

**Acceptance criteria**
- Given the boss is in place, then the lances circle its centre at 0.9 rad/s, their shots leaving
  their tips where they are (unit: orbit rule; design `spinRate`).

*Sources: P10-R11.*

#### MB-EMBER-HERALD-07 — Parts and health · MUST

The Herald has a core (hit radius 21 px, 1 950 HP) and three original parts: the ember lances (14 px,
1 200 HP each, their centres 40 px from the core at a third of a turn from each other, the first at
its nose), which all shield the core. Its full health is 5 550 HP with the original parts, 7 470 HP
with its two hidden orbs (960 HP each), which count in the health bar from the start.

**Acceptance criteria**
- Given the design, then it has three original parts, all shielding the core and orbiting, and two
  hidden ones (unit: `test_ember_herald.py`).

*Sources: P10-R11, D-088, D-221.*

#### MB-EMBER-HERALD-08 — Lance spirals · MUST

While they stand, in every stage, each lance fires a three-armed spiral from its tip (rings of 3
`purple` bullets, 190 px/s, every 0.85 s, turning 23°), the three 0.28 s apart (first 0.4 s, 0.68 s
and 0.96 s into a stage); as the ring turns, the spirals sweep round the screen.

**Acceptance criteria**
- Given the lances stand, then each fires its spiral from its tip as it turns (unit: design guns and
  stages).

*Sources: P10-R11.*

#### MB-EMBER-HERALD-09 — Core bursts by stage · MUST

The core fires aimed bursts from the twin ember cannons under its nose, changing at each stage
(stage k: k parts destroyed; from the third on, its last pattern):
- stage 0: bursts of 4 `magenta` (215 px/s, 0.13 s apart) every 2.4 s;
- stage 1: bursts of 5 `magenta` (0.11 s apart) every 2.2 s;
- stage 2: bursts of 5 `magenta` (0.1 s apart) every 2.1 s and aimed spreads of 3 `blue` (205 px/s,
  13° apart) every 3.1 s;
- stage 3: two crossing spirals of 5 from the spire's crown (`purple` turning 17° and `blue` turning
  -19°, every 0.5 s), used by no earlier stage, and bursts of 4 `magenta` every 2.4 s.

**Acceptance criteria**
- Given the design, then it has one stage per original part plus one, and the last stage's spirals
  are used by no earlier stage (unit: `test_ember_herald.py`).

*Sources: P10-R11, D-088.*

#### MB-EMBER-HERALD-10 — Rage · MUST

It is angry after its transformation, when the two ring emitters it revealed fire all out,
for `boss_rage_seconds`, `boss_rage_rate` times as often, instead of its stage's
pattern ([common](../common.md), BOSS-27). A lost part no longer angers it, and it has no
angry pattern of its own.

**Acceptance criteria**
- Given its transformation is over, then it is angry and fires only the two ring emitters it
  revealed (unit: `test_boss_build.py` angry_pattern).
- Given a part is destroyed without a transformation, then it is not angry (unit test).

*Sources: D-088, D-063, D-256.*

#### MB-EMBER-HERALD-11 — Transformation: back plating bursts off · MUST

The Herald transforms once, when 2 of its 3 lances are destroyed. Its back plating bursts off
([common](../common.md), BOSS-42): a dome drawn as a piece of its own over the tail half of the
fuselage, which is flattened to a deck 2.6 px high under it (rising to its full height again 5 px
ahead of the centre), from its foot at 2.3 px (sunk into the deck) up to 11 px, as wide as the
fuselage was (12 px either side), soot-black on its back, with the dorsal spikes, the vents and the
ridge seams on it. Its region (`back`, not mirrored) is the dome's footprint, from 6 px to 56 px
behind the centre; it bursts into plates cracked from that outline and leaves a `shell` lattice frame
on the deck, where the body's ribs arch. The orbs lie folded under it, over the wing roots. The boss
stays one object at rest and after its transformation: its embers lie on its wings, its plating, its
ring and its spire, and the ring's hub closes on the spire.

**Acceptance criteria**
- Given two lances are destroyed, then the boss transforms once and its back region bursts off,
  leaving the shell frame (unit: `test_boss_kinds.py`, `test_boss_armour.py`).
- Given its model, then it draws the back region's armour, and it holds together with and without
  it (unit: `test_boss_armour.py`, `test_boss_model.py`).

*Sources: D-221, D-224, D-227, D-254.*

#### MB-EMBER-HERALD-12 — Hidden weapons: two ring emitters · MUST

The transformation reveals two ring emitters (orbs) on the bared back, 10 px either side of the
centre line and 37 px behind the centre (radius 8 px, pods 14 px high, 960 HP each, 30 % drop
chance). They do not turn with the ring. They shield the core and fire `purple` rings as every orb
does (see [common](../common.md)), the left one 1.2 s and the right one 2.0 s into a stage. The
Herald fires more once it has transformed (about 12.3 weighted shots a second before, 14.6 after).

**Acceptance criteria**
- Given the transformation is over, then both orbs are live targets that fire, and the boss's fire
  rate has gone up (unit: `test_boss_kinds.py` escalation and weapon checks).

*Sources: D-221, D-229.*

#### MB-EMBER-HERALD-13 — Points and drops · MUST

Destroying the Herald scores 9 000 points, and each part destroyed 900. Its original parts drop a
bonus half of the time, its hidden weapons 30 % of the time; its core drops one by the game's rule.

**Acceptance criteria**
- Given a lance is destroyed, then the score rises by 900 (unit: scoring rule, design values).

*Sources: P07-R07, P11-R01, D-088.*

## Tunable values

All in `src/game/config/bosses/world_4/ember_herald.py` (`EMBER_HERALD`) unless noted.

| Name | Value | Notes |
|------|-------|-------|
| level | 4-5, mini | `src/game/config/world_4/bosses.py` `WORLD_4_BOSSES` |
| size | 3.5 L (radius 59.5 px) | `stats.size` |
| core | radius 21 px, 1 950 HP | `coreRadius`, `coreHealth` |
| lances | 40 px out at 0, 120°, 240° from the nose; radius 14, 1 200 HP, shield, orbiting | `EMBER_LANCE`, `LANCE_TURNS`, `lance_parts` |
| lance tips | 61 px out, 12 high | `EMBER_LANCE.tip`, `.height` |
| spin | 0.9 rad/s | `spinRate` |
| full health | 5 550 (7 470 with hidden weapons) | D-088 |
| stop / sway / bob | 0.74 / 60 px, 6 s / 8 px, 2.8 s | `stopFraction`, `sway`, `bob` |
| ground speed | ×1.4 | `groundSpeed` |
| muzzles | nose cannons (±5, -57, 3), crown (0, 0, 24) | `EMBER_GUNS`, `EMBER_CROWN` |
| lance spirals | rings of 3, every 0.85 s, turn 23°, first 0.4 / 0.68 / 0.96 s | stage volleys |
| bullets | `magenta` 215, `purple` 190, `blue` 205 px/s | radius 4 |
| angry | the revealed weapons, BOSS-27 | `boss_build.angry_pattern` |
| transformation | once, at 2 original parts destroyed | `src/game/sim/boss_build.py` `default_transforms` |
| back region | the dome's footprint, not mirrored: y 6..56, x ±10.6 at y 6, ±12 at y 14..26, ±10.5 at y 40, ±6.5 at y 52, `shell`; dome 2.3–11 px over a 2.6 px deck | `armour_region("back", …)`; `src/game/view/bosses/world_4/ember_herald_armour.py` |
| orbs | (±10, 37), radius 8, pod 14, 960 HP, `purple`, first 1.2 / 2.0 s | `hidden_weapon`; volleys in `src/game/config/bosses/weapon_kinds.py` |
| embers | 26, 18–62 px out, 4–26 high, 0.7–1.5 px | `src/game/view/bosses/world_4/ember_herald_parts.py` `EMBERS_*` |
| drops | parts 0.5, hidden weapons 0.3 | `part`, `hidden_weapon` defaults |
| points | 9 000 (900 a part) | `points`, `boss_part_points` |
| neon | [1, 0.78, 0.22], drawn [1, 1, 0.22] | `src/game/config/boss_look.py` `BOSS_LOOK.neon["ember-herald"]` |

## Notes

- Phase 10 fight time with the D-055 bot: 59.7 s, before the hidden weapons (D-221).
- Its full health takes its place in World 4's boss ordering (P10-R12, see
  [World 4](../../worlds/world-4/world.md)).
