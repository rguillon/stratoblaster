# Storm Petrel

> **Area:** bosses · **Prefix:** `FB-STORM-PETREL` · **Related:** [common](../common.md),
> [1-1 Open Sea](../../worlds/world-1/1-1-open-sea.md), [Reef Warden](../mini/1-1-reef-warden.md),
> [World 1](../../worlds/world-1/world.md)

The Storm Petrel is the final boss of 1-1, the first final boss of the game: a colossal sea-bird
creature (first designed as a seaplane bomber), 4.5 L across its wings, fought in a chase over the
open sea, the ground scrolling faster. A gun pod on each wing, a missile brood on its tail and a
bony plate over its breast all shield its core. It changes shape at its first
transformation (its outer wings swing forward) and sheds plating at its second. Shared rules are in
[common](../common.md).

## Requirements

### Look

#### FB-STORM-PETREL-01 — Silhouette and size · MUST

Seen from above, the Storm Petrel is a great bird, 4.5 L across its wings: a long body from its beak
(down the screen) to its tail, broad straight wings out to either side, tailplanes at its tail.

**Acceptance criteria**
- Manual validation in the boss viewer: a sea-bird with broad wings, larger than the 1-1 mini boss.

*Sources: P07-R05, P16-R06.*

#### FB-STORM-PETREL-02 — Body and wings · MUST

Its body is long and shelled (graphite and slate shades), with plated grafts on its back, ribs
across its shoulders and eyes over its beak; the core has no gun (FB-STORM-PETREL-07). Its wings are membranes on bone struts, with veins across them, an engine sac on each with its
reactor and a float of flesh under each root; they are big, heavy wings and do not flutter. Its
tailplanes are membrane on bone, with bone fins.

**Acceptance criteria**
- Manual validation: a living bird, its wings membrane on bone, metal grafted on its back.

*Sources: P07-R05, P16-R06.*

#### FB-STORM-PETREL-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts, the shared models of [common](../common.md) (BOSS-58):
- **Wing gun pods** (one on each wing): a swollen gun gland, a grafted collar at its front carrying
  a gun turret with three barrels side by side, a vein along each flank.
- **Missile rack** (on its tail): a brood sac, a grafted rim round a missile block of four ports, a
  neon lip along its front.
- **Belly plate** (over its breast, in front of the core): a bony breast shell, its plates seamed,
  a riveted plate and bone barbs on its keel; no weapon.

**Acceptance criteria**
- Given its model, then it draws its four parts and every gun mount (unit test).

*Sources: P07-R05, P16-R06, D-058, D-280.*

#### FB-STORM-PETREL-04 — Lights · MUST

Neon runs along its wings' and tailplanes' leading edges, a vein down its spine and veins along its
breast plate's shoulders. Its neon colour, set magenta, shows bright yellow ([common](../common.md),
BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright yellow.

*Sources: P07-R05, P16-R06, D-231.*

#### FB-STORM-PETREL-05 — What it sheds and moves · MUST

Its wings and its tail plating are drawn as pieces of their own, resting on the body
([common](../common.md), BOSS-42, BOSS-45). Each wing is split at its hinge, 31 px out from the
centre line:

- Its **outer wings** (`outer-wings`, a mirrored pair) are the pieces that move at its first
  transformation: the membrane beyond the hinge (6–9.5 px) with the struts' and the vein's outer
  lengths, the neon round the leading edge and the tip, and the gland at the tip. No frame.
- Its **wing roots** (`wing-roots`, mirrored) are armour it sheds at its second: the membrane from
  the body's flank to the hinge (6–9.5 px) with the struts' and the vein's inner lengths and the
  leading edge's neon, and the engine sac standing on it with its reactor, its grafted plate and its
  intake ring (up to 16 px). Shed, it bursts into plates cracked from the wing root's outline and
  leaves a `wing` frame (ribs and spars) between the body and the outer wing, out of which the
  sweepers rise.
- Its **tail plating** (`tail`, not mirrored) is the length of the body's shell over the tail,
  from the shell's own bottom (about 5 px) up to its ridge (about 15 px), with the spine vein and
  the bone barbs on it; the body's belly runs on beneath. Shed, it bursts into plates cracked from
  its lozenge and leaves a `shell` lattice frame on the belly, out of which the cannon rises.

**Acceptance criteria**
- Given its design, then its first transformation moves its outer wings and its second sheds its
  tail and wing-root regions (unit test).
- Given its model, then it draws each region's piece, and it holds together at rest and after each
  transformation (unit tests).

*Sources: D-224, D-230, D-254.*

### Behaviour

#### FB-STORM-PETREL-06 — Coming in and moving · MUST

It comes in from the top ([common](../common.md), BOSS-08) to `stopFraction` of the playfield's
height, then sways and bobs. While it is fought the ground scrolls at ×1.5: a chase over the sea.

**Acceptance criteria**
- Given the fight, then the ground eases to 1.5 times the level's speed.

*Sources: P07-R03, P07-R05.*

#### FB-STORM-PETREL-07 — Parts and core · MUST

It has four parts as it comes in, all shielding its core: `pod-left`, `pod-right`, the
`missile-rack` and the `belly-plate`. The pods' turrets fire fans of 3 straight down, swept one
bullet at a time as they turn across the fan (BOSS-58), in turn and fast (every 1.2 s each); the
rack fires four homing missiles at once, one from each of its four ports; the belly plate does not
fire. The core has no gun (the owner's request of 2026-11-05): it is never hit, and once its last
gun is destroyed (the weapons its transformations reveal, FB-STORM-PETREL-10 and
FB-STORM-PETREL-11) its health is 0 and it dies (BOSS-58). The turrets turn the way they fire.

**Acceptance criteria**
- Given its design, then its four parts all shield the core (unit test on its design).
- Given all its parts and revealed weapons destroyed, then it dies, without its core being hit
  (unit test).

*Sources: P07-R01, P07-R05, D-058.*

#### FB-STORM-PETREL-08 — Stage patterns · MUST

The pods' fans and the rack's missiles go on in every stage while they stand, and the weapons its
transformations reveal fire theirs. The core fires nothing in any stage (an exception to BOSS-21's
core patterns, the owner's request of 2026-11-05: its wing pods fire faster instead, and it has no
gun of its own).

**Acceptance criteria**
- Given each stage, then the core fires nothing and the parts left fire theirs
  (unit test on its design).

*Sources: P07-R04, D-055.*

#### FB-STORM-PETREL-09 — Angry · MUST

It is angry after each of its transformations, when the weapons that one revealed
fire all out: the two batteries after the first, the heavy cannon and two sweepers after the second.
For `boss_rage_seconds` it fires only those, `boss_rage_rate` times as often, instead of its
stage's pattern ([common](../common.md), BOSS-27). After the second, its batteries still standing
fire all out with them (an exception to BOSS-27, the owner's request of 2026-11-05: they would
otherwise idle through it). A lost part no longer angers it, and it has no angry pattern of its
own.

**Acceptance criteria**
- Given a transformation is over, then it is angry and fires only the weapons it revealed, and
  after the second its batteries still standing (unit: `test_boss_build.py` angry_pattern).
- Given a part is destroyed without a transformation, then it is not angry (unit test).

*Sources: D-063, D-256.*

#### FB-STORM-PETREL-10 — First transformation: its wings swing forward · MUST

Once both wing pods are destroyed, its outer wings swing 30° forward about the roots of their
leading edges (a mirrored pair, [common](../common.md), BOSS-45), and a **battery** for each
outer wing slides straight out of the body's flank as they swing, to its spot on the wing. The
batteries shield the core and fire fans of 7 straight down, swept from their turrets, in turn.
Each battery's deck stands on its wing, behind the stump of the pod it replaces. A strut holds it
to the body: a bracket against the deck's inner side, moving out with it, and an arm with a neon
line along it and a brace below, both stretching out from the body's flank to the bracket, clear
of the sweepers (FB-STORM-PETREL-11). Neither the battery nor its strut turns as it comes out.

**Acceptance criteria**
- Given both pods destroyed, then it transforms, its outer wings end swung forward and a battery
  stands on each (unit tests on its design).
- Manual validation: the outer wings visibly swing forward.

*Sources: D-229, D-230.*

#### FB-STORM-PETREL-11 — Second transformation: tail and wing roots · MUST

Once its missile rack and its belly plate are both destroyed, its tail plating bursts off for a
heavy **cannon** on its centre line, firing aimed spreads of 3 big red shells, and the plating of
its wing roots bursts off for a pair of **sweepers**, firing lasers that sweep after the player.
From then on (stage 4) its batteries fire twice as often: a second fan each, between their usual
ones.

**Acceptance criteria**
- Given the rack and the plate destroyed, then it transforms a second time and its cannon and two
  sweepers are revealed.

*Sources: D-224, D-229, D-230.*

#### FB-STORM-PETREL-12 — Laser colour · MUST

Its sweepers' lasers are drawn in its neon folded into the enemy shots' family: an amber beam round
a white-hot core ([common](../common.md), BOSS-32).

**Acceptance criteria**
- Given its lasers, then their colour is its neon folded into the enemy shots' family (unit
  test).

*Sources: D-072, D-231.*

#### FB-STORM-PETREL-13 — Death, drops and points · MUST

Its parts drop a weapon bonus 60 % of the time, its hidden weapons 30 %, and its core always drops
one ([common](../common.md), BOSS-57). Destroying it ends 1-1
([level flow](../../gameplay/level-flow.md)). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: P07-R07.*

## Tunable values

All in `src/game/config/bosses/final_bosses.py` (`_STORM_PETREL`, `STORM_PETREL`) unless named.

| Name | Value | Notes |
|------|-------|-------|
| size | 4.5 L (radius 76.5 px) | |
| core | radius 20, drop 1; never hit (no gun) | `coreRadius`, `coreDrop`; `coreHealth` 2 010 unused |
| `pod-left`, `pod-right` | (∓56, 4), radius 15, health 1 010, shield, drop 0.6 | |
| `missile-rack` | (0, 40), radius 14, health 820, shield, drop 0.6 | |
| `belly-plate` | (0, -32), radius 15, health 920, shield, drop 0.6 | no weapon |
| pod turrets | (∓56, -6), 19.3 px high; 3 barrels 3.1 px apart, bore 1.2, 7 px long; dome radius 5.5 | `PETREL_POD`, `mounts` |
| rack's missile block | (0, 40), 12.6 px high; 4 ports | `mounts` `missile-rack` |
| full health | 8 410 (3 760 without the hidden weapons), the core left out | BOSS-54, BOSS-55, BOSS-58 |
| points | 8 000; 800 a part | |
| ground speed | ×1.5 | chase |
| stop height | 0.72 | |
| sway / bob | 45 px over 8 s / 10 px over 4 s | |
| pod fans | 3, 15° apart, magenta 185 px/s, every 1.2 s (first 0.6 s / 1.2 s) | a sweep |
| rack missiles | 4, 30° apart, every 5.5 s (first 3 s) | |
| core stages 0–4 | none | |
| angry | the revealed weapons, BOSS-27; after the second, the batteries too | `boss_build.angry_pattern`, `rageAlso` |
| transformation 1 | `pod-left` and `pod-right` destroyed | `transformParts` |
| outer wings (moving region) | the outer wing's own outline beyond the hinge: x 31..77, y -13.4..13.8 at the hinge narrowing to the squared tip, mirrored; the membrane 6–9.5 px; swing about the vertical at (±31, -13.4, 8) by 30° forward; no frame | `moving_region`, `swing`; `heights` 4 px tell the batteries ride it |
| batteries | (∓50, -5), radius 8, health 810, deck on the wing from 9 px to 15 px, magenta; first 1.2 s / 2.0 s; fans of 7, 9° apart, every 2 s, every 1 s in stage 4 | slide out of the body (`out_of`) |
| transformation 2 | `missile-rack` and `belly-plate` destroyed | |
| tail region (shed) | a lozenge the shell's shape: x ±12.5 at y 18..30 narrowing to ±8 at y 48, `shell`, not mirrored; the plating about 5–15 px | |
| wing-root region (shed) | the wing root's own outline: x 12.5..31, y -18.7..18.7 at the flank narrowing to -13.4..13.9 at the hinge, `wing`, mirrored; the membrane 6–9.5 px, the engine sac on it up to 16 px | |
| `cannon` | (0, 32), radius 11, health 1 010, pod 14.5 px, red; first 1.4 s | |
| sweepers | (∓19, -12), radius 6, health 1 010, pod 12.9 px; first 2.2 s / 4.6 s | |
| neon | magenta (1, 0.1, 0.85), shown yellow | `BOSS_LOOK.neon` |

## Notes

- Its missile rack sits right behind the core: while the core is shielded, shots go through the
  core and reach it (D-062). Destroying the rack and the plate was optional (they did not shield
  the core) until every part came to shield it (BOSS-14, D-280); its second transformation now
  always comes.
