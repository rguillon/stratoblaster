# Lattice Node

> **Area:** bosses · **Prefix:** `MB-LATTICE-NODE` · **Related:** [common](../common.md),
> [Folding Citadel](L-9-folding-citadel.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Lattice Node is the mini boss of Lab level L-9: an open, lopsided space frame, 3.5 L across,
floating over the playfield, a scaffold of dark struts and node spheres with a cluster of glowing
nodes caged at its heart. Weapon nodes at three of its joints fire aimed bursts and narrow fans
whose lines cut across the screen and cross under it; as they break, the pattern changes, and once
two are gone the armoured cells on its rear flanks burst off on a pair of cannons. Shared rules are
in [common](../common.md).

**Not a creature.** BOSS-47 asks for a Cyber-Organic creature; this Lab boss departs from it on the
user's request (2026-11-06, "drop the animal looking theme"): it is a machine of dark metal struts,
plates, crystal and neon light, with no flesh, eyes or limbs.

## Requirements

### Look

#### MB-LATTICE-NODE-01 — Silhouette and size · MUST

Seen from above, the Lattice Node is a see-through triangular lattice, about 3.5 L across: two
layers of struts (an octet truss), the upper layer's joints `PITCH` apart, the lower layer's under
the middle of every triangle of upper joints that points down the screen, diagonals between them.
It is lopsided: an arm reaches out to its front right, a spur to its rear right, its left flank is
cut short. The ground shows through it everywhere but at its nodes, its core and its cells.

**Acceptance criteria**
- Manual validation in the boss viewer: an open, asymmetric space frame, unlike any other boss.

*Sources: Lab boss request (2026-11-06).*

#### MB-LATTICE-NODE-02 — Frame and core · MUST

Its struts are dark metal tubes with no edge trim (only its parts' outlines glow, BOSS-48), a thin
line of light along the top of each, joint to joint (thicker on every third); faceted node spheres
sit at its joints, heavier hubs under its weapon nodes. Its core is a
cluster of glowing nodes at its centre joint (a big one and six smaller ones on dark spokes) in a
cage of two hexagonal hoops and uprights, which hold the crown its rotor hatch sits on; a front
node carries the seat of its turret.

**Acceptance criteria**
- Manual validation: one machine, its glowing cluster readable through its cage.

*Sources: BOSS-49, user request (2026-11-06).*

#### MB-LATTICE-NODE-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Weapon nodes** (`node-left`, on its left flank; `node-right`, at the end of its front-right
  arm; `node-rear`, on its rear-right spur): each an octagonal armour collar round a hub, lit
  lenses round it, a seat on top. The left and right ones carry a twin-barrelled turret (its narrow
  fans), the rear one a three-barrelled turret (its bursts).
- **Cluster turret** (the core's, on the cluster's front node): three barrels side by side (its
  aimed shots, fans and bursts).
- **Cluster rotor** (the core's, on its crown): twelve barrels round a hub (its last ring). Until
  its last stage it lies under an octagonal hatch with a seam of light round it; as the rotor comes
  into use the hatch bursts off (BOSS-58), leaving a collar, and the rotor rises out.

**Acceptance criteria**
- Given its model, then it draws the three weapon nodes and every gun mount.

*Sources: BOSS-48, BOSS-58.*

#### MB-LATTICE-NODE-04 — Lights · MUST

The lines along its struts, its glowing cluster, the lenses and rings of its weapon nodes, the rims
of its cell decks and the crystal panes of its cells glow. Its neon colour, set mint, shows bright
green (BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright green.

*Sources: BOSS-50.*

#### MB-LATTICE-NODE-05 — Cannon cells · MUST

Under each rear flank's triangle of upper joints (mirrored across the centre line) its lower layer
holds a hex deck, its struts ending on the deck's rim. At rest an armoured cell stands on each deck:
a hex capsule of dark plates, a glowing crystal pane in its top, ribs down its sides. The cells are
one shed region (`cells`, a `shell` frame); the cluster's rotor hatch is a shed region of its own
(BOSS-58).

**Acceptance criteria**
- Given its design, then its transformation sheds the cells and both cannons lie in them (unit
  test).
- Given its model, then it holds together at rest and once the cells are shed.

*Sources: BOSS-42, BOSS-52.*

### Behaviour

#### MB-LATTICE-NODE-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then sways slowly
and bobs gently: a level drift. While it is fought the ground scrolls at ×0.5.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.5 of the level's speed and back after it.

*Sources: BOSS-03, BOSS-10.*

#### MB-LATTICE-NODE-07 — Parts and core · MUST

It has three parts as it comes in, all shielding its core: `node-left`, `node-right` and
`node-rear`. The core's guns (the cluster turret and rotor) fire the core's volleys and are the last
the player destroys.

**Acceptance criteria**
- Given its design, then its three parts all shield the core.

*Sources: BOSS-12, BOSS-14.*

#### MB-LATTICE-NODE-08 — Stage patterns: intersecting lines · MUST

In every stage while they stand, the left node sweeps a narrow fan of 4 green bullets 5° apart
heading 22° to the screen's right, the right node the same heading 22° to its left, so their lines
cut across the screen and cross under it; the rear node fires bursts of 4 blue bullets at the
player. The core fires:
- stage 0: an aimed blue bullet;
- stage 1: two narrow fans of 5, 6° apart, one heading 14° to each side, in turn: an X of lines;
- stage 2: a burst of 5 at the player and a fan of 7, 6° apart, straight down;
- stage 3 (all three nodes gone): a ring of 12 from the cluster rotor, turning 11° at each volley
  (a spiral), and an aimed spread of 3.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys; each shot leaves a barrel (a fight in
  the simulation).

*Sources: BOSS-21, BOSS-23, BOSS-58.*

#### MB-LATTICE-NODE-09 — Angry · MUST

After its transformation it is angry (BOSS-27): its two cannons fire all out for
`boss_rage_seconds`. It has no angry pattern of its own.

**Acceptance criteria**
- Given its transformation is over, then it is angry and fires only its two cannons.

*Sources: BOSS-27.*

#### MB-LATTICE-NODE-10 — Transformation · MUST

It transforms once, when two of its weapon nodes are destroyed (any two, BOSS-36): its cells burst
off and a **cannon** unfolds on each cell's deck, sweeping aimed spreads of 3 big orange shells.
They shield the core.

**Acceptance criteria**
- Given two weapon nodes destroyed, then it transforms, its cells burst and its two cannons are
  revealed on their decks.

*Sources: BOSS-35, BOSS-36, BOSS-40.*

#### MB-LATTICE-NODE-11 — Death, drops and points · MUST

Its parts drop a weapon bonus half of the time, its cannons 30 %; it drops a life bonus as a mini
boss (BOSS-57). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/lattice_node.py` (`_LATTICE_NODE`, `LATTICE_NODE`); its model
in `src/game/view/bosses/lab/lattice_node_model.py`.

| Name | Value | Notes |
|------|-------|-------|
| size | 3.5 L (radius 59.5 px) | `stats.size` |
| lattice | pitch 22 px, rows 19.05 px apart; upper layer 16 px high, lower layer 5 px | `PITCH`, `ROW`, `UPPER_H`, `LOWER_H`; joints `UPPER_JOINTS` |
| core | health 1 300, radius 14 | cluster radius 13 |
| `node-left` | (-44, 0), radius 11, health 780, shield, drop 0.5 | |
| `node-right` | (44, -38.1), radius 11, health 780, shield, drop 0.5 | |
| `node-rear` | (22, 38.1), radius 11, health 780, shield, drop 0.5 | |
| fan node turrets | 23.5 px high; 2 barrels 2.6 px apart, bore 1, 7 px long; dome radius 4.5 | `FAN_GUN` |
| rear node turret | 23.5 px high; 3 barrels 2.6 px apart, bore 1, 6.5 px long; dome radius 4.5 | `BURST_GUN` |
| cluster turret (core) | (0, -12), 19 px high; 3 barrels, bore 1.1, 7 px long; dome radius 5 | `CLUSTER_GUN` |
| cluster rotor (core) | (0, 3), 24 px high; 12 barrels, bore 0.8, 3.4 px long; hub radius 5 | `CLUSTER_ROTOR` |
| rotor hatch | octagon of radius 6.5 round (0, 3) | `armour_region` `rotor-hatch` (`mount`) |
| cells | hexagons of radius 9.5 round (∓22, 12.7), from the deck (5 px) to 14.5 px; `shell` frame | `armour_region` `cells`, form 1 |
| cannons | (∓22, 12.7) on the decks, radius 7, health 620, pod 5–8.5 px, orange; first 1.2 s / 2.0 s | `hidden_weapon` `cannon` |
| full health | 4 880 (core 1 300, nodes 2 340, cannons 1 240) | BOSS-54 |
| points | 4 500 | |
| ground speed | ×0.5 | |
| stop height | 0.72 | `stopFraction` |
| sway / bob | 45 px over 10 s / 5 px over 3.4 s | |
| node fans | 4, 5° apart, heading ∓22°, green 185 px/s, every 2.6 s (first 0.8 s / 2.1 s) | a sweep |
| rear node bursts | 4, 0.12 s apart, blue 175 px/s, every 2.6 s (first 1.4 s) | |
| core stage 0 | aimed 1, blue, every 2.8 s | cluster turret |
| core stage 1 | fans of 5, 6° apart, heading -14° (first 0.6 s) and 14° (first 2.1 s), every 3 s | cluster turret, sweeps |
| core stage 2 | burst of 5, 0.1 s apart, every 2.2 s; fan of 7, 6° apart, every 2.6 s | cluster turret |
| core stage 3 | ring of 12 turning 11°, every 1.5 s; aimed 3, 8° apart, every 2.4 s | rotor; turret |
| weighted fire rate | 5.0 as it comes in, 9.0 after its transformation | BOSS-39 |
| transformation | once 2 of its 3 nodes are destroyed | BOSS-36 default |
| neon | mint (0.2, 1, 0.55), shown green | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time and its place in a
  world's health order (BOSS-55, BOSS-56) are not set. Its health is about that of the 1-4 mini
  boss (Scorpion, 4 760).
- **Not a creature** (see the top): BOSS-47's creature look does not apply; BOSS-48 to BOSS-53 do.
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-06): 589 shots, every one
  from a barrel, along it; it dies at about 74 s.
