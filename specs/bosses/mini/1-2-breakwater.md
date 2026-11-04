# Breakwater

> **Area:** bosses · **Prefix:** `MB-BREAKWATER` · **Related:** [common](../common.md),
> [1-2 Green Coast](../../worlds/world-1/1-2-green-coast.md),
> [Gull Mothership](../final/1-2-gull-mothership.md), [World 1](../../worlds/world-1/world.md)

The Breakwater is the mini boss of 1-2: a huge armoured shore crab, 3 L across (first designed as an
armoured flying landing barge). A thick bony ram plate over its snout is the one part shielding its
core; two barnacle mortars on its flanks lob slow, big bullets. Once two of its parts are gone it
sheds its back plating and unfolds a pair of missile racks. Shared rules are in
[common](../common.md).

## Requirements

### Look

#### MB-BREAKWATER-01 — Silhouette and size · MUST

Seen from above, the Breakwater is a wide crab, 3 L across: a broad, domed shell over a wide mantle,
a V-shaped ram plate over its snout (down the screen), a mortar on each flank behind its middle, and
three jointed walking legs each side folded under its rim.

**Acceptance criteria**
- Manual validation in the boss viewer: a crab with a ram plate at its front and a mortar on each
  flank.

*Sources: P07-R05, P16-R05.*

#### MB-BREAKWATER-02 — Body · MUST

Its body is a wide flesh mantle under a domed, plated shell (slate, graphite and sinew shades), bone
ribs over its back, its bone legs jointed and still, and eyes on stalks at its front over its mouth.
Metal is grafted on: a riveted back plate, armour bands on its flanks, exhausts, running lights and a
short mast off the centre line, towards its tail (the back plate, the bands and the mast on its rear
shell, the plating of MB-BREAKWATER-05). Its bow gun sits in its mouth (the hold).

**Acceptance criteria**
- Manual validation: a living crab under grafted armour; the mast off-centre.

*Sources: P07-R05, P16-R05.*

#### MB-BREAKWATER-03 — Its parts · MUST

- **Ram plate** (at its snout): the crab's thick bony brow shield, a V of grafted armour on it; no
  weapon.
- **Mortars** (left and right, on its flanks): each a swollen barnacle growth with a spawn sac beside
  it, under a turret: a squat dome with a short, fat, raised barrel.
- **Bow gun** (the core's gun): a twin-barrelled turret turning on the floor of its mouth.

**Acceptance criteria**
- Given its model, then it draws the ram plate, both mortars and their turrets (unit test).

*Sources: P07-R05, P16-R05, D-058.*

#### MB-BREAKWATER-04 — Lights · MUST

An orange vein runs along its spine and round the ram plate's edge; its running lights, eyes and
glands glow. Its neon colour, set orange, shows bright yellow ([common](../common.md), BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright yellow.

*Sources: P07-R05, P16-R05, D-231.*

#### MB-BREAKWATER-05 — Back plating · MUST

The plating of its back, from its middle to its tail, is the armour it sheds at its transformation
([common](../common.md), BOSS-42): its rear shell, a carapace drawn as a piece of its own over the
flattened rear belly (the belly up to 8.9 px, the carapace from 7.7 px, its lowest point 8.2 px at
its widest, up to 16 px), the bone ribs clamped over it, the orange vein along its spine, the glands
on its flanks with veins running down them, and the grafts on it: the riveted back plate, the armour
bands and the mast. Its region is a lozenge the shell's own shape (`back`, not mirrored); it bursts
into plates cracked from that outline and leaves a `shell` lattice frame over the rear belly. The
pair of missile racks lies folded under it.

**Acceptance criteria**
- Given its design, then its one transformation sheds the back region and both racks lie in it
  (unit test).
- Given its model, then it draws the back region's armour, and it holds together with and without
  it (unit tests).

*Sources: D-221, D-224, D-254.*

### Behaviour

#### MB-BREAKWATER-06 — Coming in and moving · MUST

It comes in from the top ([common](../common.md), BOSS-08) to `stopFraction` of the playfield's
height, then sways and bobs. While it is fought the ground scrolls at ×0.4.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.4 of the level's speed and back after it.

*Sources: P07-R03, P07-R05.*

#### MB-BREAKWATER-07 — Parts and core · MUST

It has three parts as it comes in: the `ram-plate`, the only one shielding its core, and
`mortar-left` and `mortar-right`, which do not. Each mortar's turret lobs one slow, big orange
bullet at the player, the two in turn. The bow gun on its turret fires the core's volleys. The three
turrets turn the way they fire.

**Acceptance criteria**
- Given its design, then the ram plate shields the core and the mortars do not (unit test on its
  design).

*Sources: P07-R01, P07-R05, D-058, D-060.*

#### MB-BREAKWATER-08 — Stage patterns · MUST

The mortars fire in every stage while they stand. The core fires:
- stage 0: a fan of 3 red bullets;
- stage 1: an aimed fan of 3;
- stage 2: a burst of 4 at the player;
- stage 3 (all three parts gone): a ring of 10 turning a little at each volley (a spiral).

**Acceptance criteria**
- Given each stage, then the core fires that stage's volley.

*Sources: P07-R04, D-055.*

#### MB-BREAKWATER-09 — Angry · MUST

It is angry after its transformation, when the two missile racks it revealed fire all out,
for `boss_rage_seconds`, `boss_rage_rate` times as often, instead of its stage's
pattern ([common](../common.md), BOSS-27). A lost part no longer angers it, and it has no
angry pattern of its own.

**Acceptance criteria**
- Given its transformation is over, then it is angry and fires only the two missile racks it
  revealed (unit: `test_boss_build.py` angry_pattern).
- Given a part is destroyed without a transformation, then it is not angry (unit test).

*Sources: D-063, D-256.*

#### MB-BREAKWATER-10 — Transformation · MUST

It transforms once, when two of its parts are destroyed: its back plating bursts off, baring a dark
metal lattice, and two **racks** unfold at its tail, on either side of its centre line. They shield
the core and fire pairs of homing missiles, in turn.

**Acceptance criteria**
- Given two parts destroyed, then it transforms and its two racks are revealed (unit test on its
  thresholds).

*Sources: D-221, D-224, D-229.*

#### MB-BREAKWATER-11 — Death, drops and points · MUST

Its parts drop a weapon bonus half of the time, its racks 30 %; it drops a life bonus as a mini boss
([common](../common.md), BOSS-57). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: P07-R07.*

## Tunable values

All in `src/game/config/bosses/mini_bosses.py` (`_BREAKWATER`, `BREAKWATER`) unless named.

| Name | Value | Notes |
|------|-------|-------|
| size | 3 L (radius 51 px) | `stats.size` |
| core | health 930, radius 18 | bow turret pivot (0, -21), twin barrels |
| `ram-plate` | (0, -34), radius 18, health 810, shields, drop 0.5 | no weapon |
| `mortar-left`, `mortar-right` | (∓34, 12), radius 13, health 430, no shield, drop 0.5 | turrets on their centres |
| full health | 3 900 | BOSS-54 |
| points | 3 500; 350 a part | |
| ground speed | ×0.4 | |
| stop height | 0.72 | `stopFraction` |
| sway / bob | 60 px over 8 s / 6 px over 4 s | |
| mortar shot | 1 aimed orange bullet, radius 7, 110 px/s, every 2.4 s (first 1.2 s / 2.4 s) | |
| core stage 0 | fan of 3, 16° apart, red 190 px/s, every 3 s | |
| core stage 1 | aimed 3, 12° apart, every 2.4 s | |
| core stage 2 | burst of 4, 0.15 s apart, every 2.2 s | |
| core stage 3 | ring of 10 turning 9°, every 1.7 s | |
| angry | the revealed weapons, BOSS-27 | `boss_build.angry_pattern` |
| transformation | 2 parts destroyed | default threshold |
| shed region | back: a lozenge the rear shell's shape, x ±23 at its widest, y 14..41, `shell`, not mirrored; plating 7.7–16 px | `armour_region` |
| racks | (∓11, 33), radius 9, health 650, pod 17.7 px; first 1.2 s / 2.0 s | |
| neon | orange (1, 0.5, 0.05), shown yellow | `BOSS_LOOK.neon` |
