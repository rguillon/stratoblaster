# Twin Hammerhead

> **Area:** bosses · **Prefix:** `MB-TWIN-HAMMERHEAD` · **Related:** [common](../common.md),
> [Hive Carrier](L-2-hive-carrier.md)

The Twin Hammerhead is the mini boss of the Lab's level L-2. **Lab boss: in the dev viewer only**;
no level brings it in. It is a catamaran of two hammerhead sharks side by side, wide apart (3.2 L
across), joined by a bony bridge that carries its core. A cannon on each hammer head sweeps aimed
spreads at the player from both flanks, so the two streams cross over the player; a missile block
on the bridge launches homing missiles. Once two of its parts are gone it sheds the bridge's armour
plates and unfolds a pair of gatlings. Shared rules are in [common](../common.md).

## Requirements

### Look

#### MB-TWIN-HAMMERHEAD-01 — Silhouette and size · MUST

Seen from above, the Twin Hammerhead is two shark hulls 72 px apart, 3.2 L across at its hammer
heads: each hull a long body with a hammer head across its nose (down the screen), a pectoral fin
on its outer flank, a dorsal fin and a forked tail (its outer lobe the longer); between them, a
bridge from just behind the hammer heads to the hulls' middle, with a domed core in its middle and
a bony hump at its rear. The gap between the hulls is open in front of and behind the bridge.

**Acceptance criteria**
- Manual validation in the boss viewer: two hammerhead sharks side by side, joined by a bridge; it
  reads unlike any other boss.

*Sources: user request (2026-11-05, the Lab bosses).*

#### MB-TWIN-HAMMERHEAD-02 — Body · MUST

Each hull is a flesh body under a plated carapace (slate, membrane and graphite shades) with a
vein along its spine, three gill slits each side, a glowing eye in a dark metal socket at each
hammer tip and a row of bone teeth under the hammer's front edge; riveted plates and an armour band
grafted on its back, and a short mast on the right hull only. The bridge is a dark membrane deck
held by bone: a beam across its front lip (the bridge turret's seat), a beam across its rear (under
the hump), each with vertebra knobs, and a bone rib along each hull's inner flank; the core's dome
in its middle with a vein ring round its foot, veins out to the hulls, a gland, two reactors in sacs
at its rear and running lights at its front corners.

**Acceptance criteria**
- Manual validation: two living sharks and a bone bridge under grafted metal.

*Sources: BOSS-47, BOSS-49.*

#### MB-TWIN-HAMMERHEAD-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Hammer cannons** (left and right, on the hammer heads): each an armoured growth with bone
  spikes behind it and a sac at its side, under a turret with three barrels side by side.
- **Missile block** (on the bridge's rear): a bony hump, a plate grafted on its crown under a block
  of four missile ports.
- **Bridge turret** (the core's): three barrels side by side on the bridge's front lip (its fans,
  aimed spreads and bursts).
- **Bridge rotor** (the core's): a rotor of twelve barrels on the dome (its ring). Until its last
  stage it lies under an armoured hatch with a seam of light round it, which bursts off as the
  rotor comes into use, leaving a collar; the rotor rises out of it.

**Acceptance criteria**
- Given its model, then it draws both cannons, the missile block and every gun mount.

*Sources: BOSS-48, BOSS-58.*

#### MB-TWIN-HAMMERHEAD-04 — Lights · MUST

Its veins, eyes, glands and running lights glow in its neon colour, set red-orange, shown bright
yellow ([common](../common.md), BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright yellow.

*Sources: BOSS-50.*

#### MB-TWIN-HAMMERHEAD-05 — Bridge plates · MUST

The bridge's plates either side of the dome are the armour it sheds at its transformation (BOSS-42):
each a rounded bony scute from 5 to 9.6 px with a raised sinew boss, two bone ridges along it, a
vein along its inner edge and a gland at its rear. Its region is the rectangle x 7..25, y -7..14
(`bridge`, mirrored); it bursts into plates cracked from that outline and leaves a `wing` frame. A
gatling lies folded under each plate.

**Acceptance criteria**
- Given its design, then its one transformation sheds the bridge region and both gatlings lie in it.
- Given its model, then it draws the bridge region's armour.

*Sources: BOSS-42, BOSS-43, BOSS-44.*

### Behaviour

#### MB-TWIN-HAMMERHEAD-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then sways and
bobs. While it is fought the ground scrolls at ×0.7.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.7 of the level's speed.

*Sources: BOSS-03, BOSS-10.*

#### MB-TWIN-HAMMERHEAD-07 — Parts and core · MUST

It has three parts as it comes in, all shielding its core: `cannon-left`, `cannon-right` and
`missile-block`. The core's guns (the bridge turret and the bridge rotor) fire the core's volleys
and are the last the player destroys. The turrets turn the way they fire.

**Acceptance criteria**
- Given its design, then its three parts all shield the core.

*Sources: BOSS-12, BOSS-14.*

#### MB-TWIN-HAMMERHEAD-08 — Stage patterns · MUST

Crossfire: its parts fire in every stage while they stand. Each hammer cannon sweeps an aimed spread
of 3 red bullets at the player, the right one 0.3 s after the left; fired from 72 px apart, the two
streams cross over the player from both flanks. The missile block launches 2 homing missiles. The
core fires:
- stage 0: a fan of 3 orange bullets straight down from the bridge turret, a sweep;
- stage 1: an aimed spread of 3, a sweep;
- stage 2: a burst of 4 at the player;
- stage 3 (all three parts gone): a ring of 12 from the bridge rotor, one bullet a barrel, turning
  9° at each volley (a spiral).

**Acceptance criteria**
- Given each stage, then the core fires that stage's volley.

*Sources: BOSS-20, BOSS-21, BOSS-23.*

#### MB-TWIN-HAMMERHEAD-09 — Angry · MUST

It is angry after its transformation (BOSS-27): the two gatlings it revealed fire all out, alone,
`boss_rage_rate` times as often for `boss_rage_seconds`.

**Acceptance criteria**
- Given its transformation is over, then it is angry and fires only its two gatlings.

*Sources: BOSS-27.*

#### MB-TWIN-HAMMERHEAD-10 — Transformation · MUST

It transforms once, when two of its parts are destroyed: its bridge plates burst off, baring a dark
metal frame, and two **gatlings** unfold on the bridge either side of the dome. They shield the core
and fire bursts at the player, in turn.

**Acceptance criteria**
- Given two parts destroyed, then it transforms and its two gatlings are revealed.

*Sources: BOSS-35, BOSS-36, BOSS-38.*

#### MB-TWIN-HAMMERHEAD-11 — Death, drops and points · MUST

Its parts drop a weapon bonus half of the time, its gatlings 30 % (BOSS-57). It scores the points
of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/twin_hammerhead.py` (`_TWIN_HAMMERHEAD`, `TWIN_HAMMERHEAD`)
unless named; the model in `src/game/view/bosses/lab/twin_hammerhead_model.py`.

| Name | Value | Notes |
|------|-------|-------|
| size | 3.2 L (radius 54 px) | `stats.size` |
| core | health 1 050, radius 18 | |
| `cannon-left`, `cannon-right` | (∓36, -30), radius 13, health 600, shield, drop 0.5 | `HULL_X`, `HAMMER_Y` |
| hammer cannon turrets | 7.2 px high; 3 barrels 3.2 px apart, bore 1.2, 9 px long; dome radius 6.5 | `HAMMER_CANNON` |
| `missile-block` | (0, 19), radius 11, health 680, shield, drop 0.5; 4 ports, 9.5 px high | |
| bridge turret (core) | (0, -13), 5.6 px high; 3 barrels 2.9 px apart, bore 1.1, 7 px long; dome radius 5.5 | `mounts` `bridge-gun` |
| bridge rotor (core) | (0, 4), 12.4 px high; 12 barrels, bore 0.8, 3.4 px long; hub radius 4.6 | `mounts` `bridge-rotor` |
| rotor hatch | octagon of radius 6 round (0, 4), 10.8–13.6 px; bursts as the rotor comes into use | `rotor-hatch` |
| full health | 4 010 | BOSS-54 |
| points | 3 500; 350 a part | |
| ground speed | ×0.7 | |
| stop height | 0.72 | |
| sway / bob | 65 px over 7 s / 8 px over 3.5 s | |
| cannon spreads | aimed 3, 10° apart, red 190 px/s, every 2.4 s (first 1 s / 1.3 s) | sweeps |
| missiles | 2, 30° apart, every 5.5 s (first 3 s) | |
| core stage 0 | fan of 3, 12° apart, orange 180 px/s, every 3 s | bridge turret |
| core stage 1 | aimed 3, 12° apart, every 2.6 s | bridge turret |
| core stage 2 | burst of 4, 0.15 s apart, every 2.2 s | bridge turret |
| core stage 3 | ring of 12 turning 9°, every 1.6 s | bridge rotor |
| transformation | 2 parts destroyed | default threshold |
| shed region | `bridge`: x 7..25, y -7..14, `wing`, mirrored; plates 5–9.6 px | |
| gatlings | (∓16, 4), radius 8, health 540, pod 9.5 px, orange; first 1.2 s / 2.0 s | |
| neon | red-orange (1, 0.3, 0.1), shown yellow | `BOSS_LOOK.neon` |
