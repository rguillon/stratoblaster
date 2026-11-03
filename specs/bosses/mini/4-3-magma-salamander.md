# Magma Salamander (4-3 mini boss)

> **Area:** bosses · **Prefix:** `MB-MAGMA-SALAMANDER` · **Related:** [common boss rules](../common.md),
> [4-3 Midtown](../../worlds/world-4/4-3-midtown.md), [World 4](../../worlds/world-4/world.md),
> [Obsidian Golem](../final/4-3-obsidian-golem.md), [readability](../../graphics/readability.md),
> [shots](../../graphics/shots.md)

The Magma Salamander is the mini boss of level 4-3, met at the middle of the level. It is a
segmented lizard-ship 3.5 L long with a molten glow between its plates, a spiny fin on each side of
its back and a tail curling back to its right that lashes on two joints, sweeping lines of bullets
across the screen. It was designed for the Volcanic Lands' lava fields; since World 4 became the
Metropolis (D-112) it keeps its name and its look and flies over midtown. It transforms once: its
back plating bursts off and two sweeping lasers unfold. Everything shared by all bosses is in
[bosses/common.md](../common.md); this file only gives what is the Salamander's own. Positions are
px from the boss's centre, X right, Y up the screen (its snout at -Y); heights are above the
playfield.

## Requirements

### Look

#### MB-MAGMA-SALAMANDER-01 — Silhouette · MUST

Seen from above, the Salamander is a lizard about 3.5 L long (radius 1.75 L), snout down the screen:
a flat, wedge-shaped head reaching about 64 px ahead of its centre, a narrow body about 26 px wide of
overlapping armour plates, four clawed legs splayed out from its sides, a spiny fin standing out on
each side of its back (out to about 53 px), and a tail curling back to its right, its tip about
50 px behind the centre and 19 px to the right, clear of the core.

**Acceptance criteria**
- Given the dev bosses viewer, when the Salamander is shown, then it reads as a lizard with two back
  fins and a tail curled to one side (manual).

*Sources: P10-R11.*

#### MB-MAGMA-SALAMANDER-02 — Cyber-Organic body · MUST

It is a living lizard (Cyber-Organic): a scorched flesh body under bony scale plates and metal
grafts, a molten seam glowing between each plate and the next (sunk a little under them), magma
glands along its spine, legs armoured at the shoulder and ending in claws, a head with two eyes and
the jaw guns either side of its snout, the magma vent between the fins and its reactors set in flesh
sacs. Its plates are soot-blackened, heat-blued metal.

**Acceptance criteria**
- Given the model, then it reads as one creature with molten seams between its plates (manual).

*Sources: P10-R11, P16-R05.*

#### MB-MAGMA-SALAMANDER-03 — Back fins · MUST

Each back fin is a thick, heat-scarred spiny frill of soot-black armour, its spines lit along their
ridges, a molten glow at its root, and under its leading edge a gun pod with the two barrels of its
fans. Destroyed, a fin is hidden and leaves nothing in its place.

**Acceptance criteria**
- Given the model, then each fin's two barrels sit at its muzzles under its leading edge (unit:
  `test_boss_models.py`; manual).

*Sources: P10-R11, P16-R05, D-225, D-167.*

#### MB-MAGMA-SALAMANDER-04 — Tail · MUST

The tail is drawn in two pieces on its two joints: its root segment (two armoured rings tapering to
the knuckle, a molten glow between them, a row of neon studs along its back), and its tip, the tail
part, on the knuckle: a tapering plated segment ending in a glowing bulb of magma, the stinger barrel
on top of it pointing down the screen. A destroyed tail takes only its tip: the root segment stays on
the body.

**Acceptance criteria**
- Given the dev viewer, when K destroys the tail, then its tip disappears and its root stays
  (manual; `test_boss_models.py` checks every part is drawn).

*Sources: P10-R11, P16-R05, D-225.*

#### MB-MAGMA-SALAMANDER-05 — Lights and colours · MUST

Its registered neon is orange-yellow (`magma-salamander`); like every boss's warm lights it is drawn
bright yellow (see [readability](../../graphics/readability.md)). Neon lights the fins' spines, the
tail's studs, the eyes and the vent; its molten seams (hotter and redder in the design), glands and
the magma bulb are in the same yellow family. White charge lights sit at the barrels' mouths and in
the vent.

**Acceptance criteria**
- Given the model, then every neon and glowing seam is bright yellow (unit: enemy colour family
  tests).

*Sources: P10-R11, D-231.*

#### MB-MAGMA-SALAMANDER-06 — Lashing tail · MUST

The tail is a moving limb on two joints: its root on the body (24 px behind the centre) swings 12°
either way once every 3.6 s, and its knuckle (12 px right, 42 px behind) hangs on the root and swings
18° either way with the same period, a fifth of a swing later, so its tip lashes after the root. The
tail's hit circle and stinger move with it.

**Acceptance criteria**
- Given the boss is in place, then the tail lashes, its tip following the root (manual, dev viewer);
  its muzzle moves with the joints (unit: joint rule).

*Sources: P10-R11, D-061.*

### Behaviour

#### MB-MAGMA-SALAMANDER-07 — Entry, place and ground speed · MUST

The Salamander comes in from above the top edge and stops at 0.74 of the playfield's height. In
place it sways up to 56 px either side over 7 s and bobs 8 px over 3.4 s. While it is fought the
ground runs at ×0.6 the level's speed.

**Acceptance criteria**
- Given the fight starts, then the ground slows to ×0.6 and the boss stops at 0.74 of the
  playfield height (unit: `test_world_boss.py` for the rule; design values in the config).

*Sources: P10-R11.*

#### MB-MAGMA-SALAMANDER-08 — Parts and health · MUST

The Salamander has a core (hit radius 16 px, 2 000 HP) and three original parts: two back fins
(13 px, 900 HP each) that shield the core, and the tail (12 px, 700 HP) that does not; curled to its
right, the tail can be shot past the core. Its full health is 4 500 HP with the original parts,
5 940 HP with its two hidden sweepers (720 HP each), which count in the health bar from the start.

**Acceptance criteria**
- Given the design, then it has three original parts and two hidden ones, and only the fins and the
  sweepers shield the core (unit: `test_magma_salamander.py`).

*Sources: P10-R11, D-088, D-221.*

#### MB-MAGMA-SALAMANDER-09 — Fin fans · MUST

While they stand, in every stage, each fin fires a fan of 3 `magenta` bullets (205 px/s, 13° apart)
every 2.6 s from its two barrels, the two fans crossing under its snout (the left one leaning 9°
right of straight down, the right one 9° left); the left one 1.1 s and the right one 2.4 s into a
stage.

**Acceptance criteria**
- Given both fins stand, then their fans lean towards each other's side (unit: design stages).

*Sources: P10-R11.*

#### MB-MAGMA-SALAMANDER-10 — Tail sweeping lines · MUST

While it stands, in every stage, the tail sweeps a line of bullets across the screen from its
stinger: 20 single drops of magma (`orange`, 230 px/s, radius 3.5 px), 0.12 s apart, at headings
from -45° to 45° in 10° steps and back, one sweep every 5.2 s, first 2 s into a stage.

**Acceptance criteria**
- Given the tail stands, then a line of 20 drops swings across and back every 5.2 s (unit: design
  stages).

*Sources: P10-R11.*

#### MB-MAGMA-SALAMANDER-11 — Core bursts by stage · MUST

The core fires aimed bursts from its jaw guns, changing at each stage (stage k: k parts destroyed;
from the third on, its last pattern):
- stage 0: bursts of 3 `red` bullets (215 px/s, 0.13 s apart) every 2.5 s;
- stage 1: bursts of 4 `red` (0.12 s apart) every 2.3 s;
- stage 2: bursts of 3 `orange` (210 px/s) every 1.5 s and bursts of 5 `red` every 3 s;
- stage 3: a six-armed spiral from the magma vent (rings of 6 `orange` every 0.42 s, turning 19°),
  used by no earlier stage, and bursts of 4 `red` every 2.2 s.

**Acceptance criteria**
- Given the design, then it has one stage per original part plus one, and the last stage's spiral
  is used by no earlier stage (unit: `test_magma_salamander.py`).

*Sources: P10-R11, D-088.*

#### MB-MAGMA-SALAMANDER-12 — Rage · MUST

After the pause that follows each destroyed part, the Salamander is angry: it fires a curtain (fans
sweeping across the screen and back over a ring) at heat 11, in `orange` and `red`: about 108
bullets a second at 208 px/s.

**Acceptance criteria**
- Given a part is destroyed, when its pause is over, then the core fires the curtain for the rage
  time (unit: `test_boss_rage.py`, `test_magma_salamander.py`).

*Sources: D-088, D-063.*

#### MB-MAGMA-SALAMANDER-13 — Transformation: back plating bursts off · MUST

The Salamander transforms once, when 2 of its 3 original parts are destroyed. Its back plating
bursts off ([common](../common.md), BOSS-42): the three scale plates over its back (from 26 px
behind the centre to 10 px ahead of it), drawn as shells of their own over the belly, which is
flattened to 3.2 px under them, from a flat underside at 2.8 px up to their ridges (8, 11 and 12
px), with the molten seams between them, the orange lights along their flanks, the vent, a gland and
the spine's magma vein on them. The two plates over its neck stay on the body. Its region (`back`,
not mirrored) is the three plates' footprint; it bursts into plates cracked from that outline and
leaves a `shell` lattice frame on the flattened belly, where the ribs arch, the fins' sockets stand
and the magma vent's stack rises. The sweepers lie folded under it.

**Acceptance criteria**
- Given two original parts are destroyed, then the boss transforms once and its back region bursts
  off, leaving the shell frame (unit: `test_boss_kinds.py`, `test_boss_armour.py`).
- Given its model, then it draws the back region's armour, and it holds together with and without
  it (unit: `test_boss_armour.py`, `test_boss_model.py`).

*Sources: D-221, D-224, D-227, D-254.*

#### MB-MAGMA-SALAMANDER-14 — Hidden weapons: two sweepers · MUST

The transformation reveals two sweepers (turrets with a two-pronged emitter) on the bared back, 9 px
either side of the centre line and 13 px behind the centre (radius 7 px, pods 12.4 px high, 720 HP
each, 30 % drop chance). They shield the core and fire their sweeping lasers as every sweeper does
(see [common](../common.md)), the beam following the player slowly while it fires; the left one
1.2 s and the right one 2.0 s into a stage. The Salamander fires more once it has transformed (about
7.4 weighted shots a second before, 9.5 after).

**Acceptance criteria**
- Given the transformation is over, then both sweepers are live targets that fire, and the boss's
  fire rate has gone up (unit: `test_boss_kinds.py` escalation and weapon checks).

*Sources: D-221, D-229.*

#### MB-MAGMA-SALAMANDER-15 — Laser colour · MUST

Its sweepers' lasers are drawn in its own colour: its orange-yellow neon moved into the enemy shots'
family, an orange (about [1, 0.36, 0.08]) round a white-hot core.

**Acceptance criteria**
- Given a sweeper fires, then its beam is orange (unit: `enemy_lasers.color_of`).

*Sources: D-072, D-229.*

#### MB-MAGMA-SALAMANDER-16 — Points and drops · MUST

Destroying the Salamander scores 8 000 points, and each part destroyed 800. Its original parts drop
a bonus half of the time, its hidden weapons 30 % of the time; its core drops one by the game's rule.

**Acceptance criteria**
- Given a fin is destroyed, then the score rises by 800 (unit: scoring rule, design values).

*Sources: P07-R07, P11-R01, D-088.*

## Tunable values

All in `src/game/config/bosses/world_4/magma_salamander.py` (`MAGMA_SALAMANDER`) unless noted.

| Name | Value | Notes |
|------|-------|-------|
| level | 4-3, mini | `src/game/config/world_4/bosses.py` `WORLD_4_BOSSES` |
| size | 3.5 L (radius 59.5 px) | `stats.size` |
| core | radius 16 px, 2 000 HP | `coreRadius`, `coreHealth` |
| fins | (±34, 4), radius 13, 900 HP, shield | `SALAMANDER_PARTS.fin` |
| tail | (19, 50), radius 12, 700 HP, no shield, on `tail-tip` | `SALAMANDER_PARTS.tail` |
| full health | 4 500 (5 940 with hidden weapons) | D-088 |
| stop / sway / bob | 0.74 / 56 px, 7 s / 8 px, 3.4 s | `stopFraction`, `sway`, `bob` |
| ground speed | ×0.6 | `groundSpeed` |
| tail joints | root (0, 24) ±12°; knuckle (12, 42) ±18°; 3.6 s, lag 0.2 | `SALAMANDER_TAIL`, `LASH` |
| muzzles | fin barrels (±34 ∓ 2.4, -10, 4), stinger (21, 57, 8), jaws (±5, -64, 2), vent (0, 10, 15) | `SALAMANDER_*` |
| fin fans | 3 × 13°, every 2.6 s, lean ±9° inwards, first 1.1 / 2.4 s | stage volleys |
| tail sweep | 20 drops, 0.12 s apart, -45°..45° and back, every 5.2 s, first 2 s; 230 px/s, radius 3.5 | `SWEEP`, `SWEEP_GAP`, `SWEEP_EVERY`, `DROP` |
| bullets | `red` 215, `orange` 210, `magenta` 205 px/s | radius 4 |
| rage | curtain, heat 11 (`orange`, `red`) | `rage.curtain` |
| transformation | once, at 2 original parts destroyed | `src/game/sim/boss_build.py` `default_transforms` |
| back region | the three back plates' footprint, not mirrored: y -10..26, x ±14.5 at y -10..2, ±13.5 at y 4..17, ±7 at y 26, `shell`; shells 2.8–12 px over a 3.2 px belly | `armour_region("back", …)`; `src/game/view/bosses/world_4/magma_salamander_armour.py` |
| sweepers | (±9, 13), radius 7, pod 12.4, 720 HP, first 1.2 / 2.0 s | `hidden_weapon`; volleys in `src/game/config/bosses/weapon_kinds.py` |
| drops | parts 0.5, hidden weapons 0.3 | `part`, `hidden_weapon` defaults |
| points | 8 000 (800 a part) | `points`, `boss_part_points` |
| neon | [1, 0.62, 0.08], drawn [1, 1, 0.08]; laser [1, 0.36, 0.08] | `src/game/config/boss_look.py` `BOSS_LOOK.neon["magma-salamander"]` |

## Notes

- Phase 10 fight time with the D-055 bot: 53.2 s, before the hidden weapons (D-221).
- Its full health takes its place in World 4's boss ordering (P10-R12, see
  [World 4](../../worlds/world-4/world.md)).
