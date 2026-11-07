# Arrow Lance

> **Area:** bosses · **Prefix:** `MB-ARROW-LANCE` · **Related:** [common](../common.md),
> [Cathedral Engine](L-8-cathedral-engine.md)

The Arrow Lance is the Lab's L-8 mini boss. **Lab boss: in the dev viewer only** (no level brings
it in; it is listed after the World bosses in the dev viewer's Bosses list). A sleek stealth delta,
a flat faceted arrowhead 3 L across its trailing edge, pointing down the screen: a laser pod on its
nose and a gun pod on each wingtip, all three shielding its core. Speed and precision: it sways fast
and wide, its wingtips fire narrow, fast fans, its core quick aimed shots, and its nose laser aims at
the player through its warning line and locks. Once both wingtip pods are gone it sheds its stealth
panels and unfolds a pair of mortars: slow, heavy flak shells from a fast craft. Shared rules are in
[common](../common.md).

**Departs from BOSS-47.** On the user's request (2026-11-06, "drop the animal looking theme") this
Lab boss is a machine, not a Cyber-Organic creature: dark metal plates, panels, engines and light
lines, no flesh, eyes or veins. The other look rules (BOSS-48 to BOSS-53) hold.

## Requirements

### Look

#### MB-ARROW-LANCE-01 — Silhouette and size · MUST

Seen from above, the Arrow Lance is a flat delta, an arrowhead pointing down the screen: straight
leading edges from its sharp nose back to its two wingtips, about 3 L across, a sawtooth trailing
edge of two teeth either side, a low faceted spine down its middle and two engine nacelles sticking
out behind it.

**Acceptance criteria**
- Manual validation in the boss viewer: a stealth delta, its nose down the screen, its silhouette
  unlike any other boss's.

*Sources: user request (2026-11-06, the Lab bosses, "drop the animal looking theme").*

#### MB-ARROW-LANCE-02 — Body · MUST

Its body is dark metal: a thin delta plate chamfered all round, angular raised facets on its outer
wings round the wingtip pods and behind the stealth panels, dark panel lines and a vent on each
wing; a low faceted spine (a fighter's section) from its tail to its nose, a deck on it the core's
guns stand on, a sensor chine with a smoked glass slit either side of the nose pod; two engine
nacelles at its back, each with a dark nozzle ringed in light and its exhaust glowing.

**Acceptance criteria**
- Manual validation: a machine of dark faceted plates, no creature.

*Sources: user request (2026-11-06).*

#### MB-ARROW-LANCE-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts, the shared models of [common](../common.md) (BOSS-58):
- **Nose pod** (on the arrow's point): a faceted arrow tip over the spine's front, yellow chevrons
  on its flanks, its laser emitter on a turret on top (BOSS-31).
- **Wingtip pods** (left and right): each a long faceted gun pod lying on the wingtip, a light line
  down its outer side and a sensor tip at its front, a twin gun on a turret on its back (two long,
  thin barrels side by side).
- **Spine turret** (the core's): a fan turret of three barrels on the spine's deck (its aimed
  shots, bursts and fans).
- **Back rotor** (the core's): a rotor of ten barrels on the spine's deck behind it (its last ring).
  Until its last stage it lies under a hatch, a flat octagonal cap with a seam of light round it,
  which bursts off as the rotor comes into use (BOSS-58), leaving a collar round the opening.

**Acceptance criteria**
- Given its model, then it draws the nose pod, both wingtip pods and every gun mount (unit test).

*Sources: user request (2026-11-06).*

#### MB-ARROW-LANCE-04 — Lights · MUST

Yellow light lines run along its leading edges and its trailing teeth, down the spine's shoulders,
on its pods and on the stealth panels' front edges; its wingtips, nacelle rings and hatch seam glow.
Its neon colour, set yellow, shows bright yellow ([common](../common.md), BOSS-50); its laser is its
neon folded into the enemy shots' family (BOSS-32).

**Acceptance criteria**
- Given its model, then its lights are bright yellow.

*Sources: user request (2026-11-06).*

#### MB-ARROW-LANCE-05 — Stealth panels · MUST

A thick faceted stealth panel lies over each mid-wing, between the spine and the outer wing, a
yellow slit along its front edge and dark panel lines on it: the armour it sheds at its
transformation ([common](../common.md), BOSS-42), drawn as a piece of its own (from 2.5 px to 7 px).
Its region (`panels`, mirrored) is the panel's own outline; it bursts into plates cracked from that
outline and leaves a `wing` frame of ribs and spars. The pair of mortars lies folded under it.

**Acceptance criteria**
- Given its design, then its one transformation sheds the panels region and both mortars lie in it
  (unit test).
- Given its model, then it draws the panels region's armour, and it holds together with and without
  it (unit tests).

*Sources: D-221, D-224, D-254.*

### Behaviour

#### MB-ARROW-LANCE-06 — Coming in and moving · MUST

It comes in from the top ([common](../common.md), BOSS-08) to `stopFraction` of the playfield's
height, then sways fast and wide (cut to the ship's reach, BOSS-10) and bobs. While it is fought the
ground scrolls at ×1.3: a chase.

**Acceptance criteria**
- Given the fight, then the ground eases to ×1.3 of the level's speed and back after it.

*Sources: BOSS-03.*

#### MB-ARROW-LANCE-07 — Parts and core · MUST

It has three parts as it comes in, all shielding its core: `nose`, `wing-left` and `wing-right`.
The core's guns (the spine turret and the back rotor) fire the core's volleys and are the last the
player destroys. The turrets turn the way they fire; the nose's laser turret aims at the player only
at `boss_laser_turn` through its warning line, then holds still (BOSS-31).

**Acceptance criteria**
- Given its design, then its three parts all shield the core (unit test on its design).

*Sources: BOSS-12, BOSS-14, BOSS-58.*

#### MB-ARROW-LANCE-08 — Stage patterns · MUST

The parts fire in every stage while they stand:
- the nose fires its laser (1 s warning line, then a 1.1 s beam) locked on where the player was;
- each wingtip pod fires aimed fans of 3 fast orange darts, 6° apart, swept one at a time from its
  two barrels, the right one 1.1 s after the left.

The core fires small, fast red needles:
- stage 0: a single needle at the player from the spine turret;
- stage 1: a burst of 3, 0.1 s apart;
- stage 2: an aimed fan of 5, 5° apart, swept;
- stage 3 (all three parts gone): a ring of 10 orange bullets from the back rotor, one a barrel,
  turning 8° at each volley (a spiral), and a single aimed needle from the spine turret.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys, each from its mount (unit test).

*Sources: BOSS-20, BOSS-21, BOSS-58.*

#### MB-ARROW-LANCE-09 — Angry · MUST

It is angry after its transformation, when the two mortars it revealed fire all out for
`boss_rage_seconds`, `boss_rage_rate` times as often, instead of its stage's pattern
([common](../common.md), BOSS-27). A lost part does not anger it.

**Acceptance criteria**
- Given its transformation is over, then it is angry and fires only its two mortars (unit test).

*Sources: BOSS-27.*

#### MB-ARROW-LANCE-10 — Transformation · MUST

It transforms once, when both wingtip pods are destroyed (`transformParts`): its stealth panels
burst off, baring a dark metal frame, and two **mortars** unfold on it, either side of the spine.
They shield the core and fire slow, big red flak shells at the player that burst into rings, in turn.

**Acceptance criteria**
- Given both wingtip pods destroyed, then it transforms and its two mortars are revealed (unit test).

*Sources: D-221, D-224, D-229.*

#### MB-ARROW-LANCE-11 — Death, drops and points · MUST

Its parts drop a weapon bonus half of the time, its mortars 30 %; it drops a life bonus as a mini
boss ([common](../common.md), BOSS-57). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/arrow_lance.py` (`_ARROW_LANCE`, `ARROW_LANCE`) unless named.

| Name | Value | Notes |
|------|-------|-------|
| size | 3.2 L (radius 54.4 px); 102 px across its trailing edge | `stats.size`, `DELTA` |
| core | health 1 300, radius 16 | `coreHealth`, `coreRadius` |
| `nose` | (0, -36), radius 11, health 680, shields, drop 0.5 | `NOSE_AT` |
| nose laser | (0, -36), 8 px high; turret, base radius 4.2, bore 1.8, 11 px long | `NOSE_LASER`, `NOSE_TOP` |
| `wing-left`, `wing-right` | (∓36, 14), radius 11, health 660, shield, drop 0.5 | `WING_AT` |
| wingtip guns | 5 px high; 2 barrels 2.6 px apart, bore 0.9, 9 px long; dome radius 4.2 | `WING_GUN`, `WING_TOP` |
| spine turret (core) | (0, -12), 9 px high; 3 barrels, bore 0.9, 7 px long; dome radius 4.6 | `mounts` `spine` |
| back rotor (core) | (0, 15), 9 px high; 10 barrels, bore 0.8, 3 px long; hub radius 4.4 | `mounts` `tail-rotor` |
| rotor hatch | octagon of radius 6 round (0, 15) on the spine's deck; bursts as the rotor comes into use | `armour_region` `rotor-hatch` (`mount`) |
| full health | 4 380 (core 1 300, parts 2 000, mortars 1 080) | BOSS-54; the L-3 mini boss (Moth Lantern) has 4 330 |
| points | 4 000; 400 a part | |
| ground speed | ×1.3 | |
| stop height | 0.74 | `stopFraction` |
| sway / bob | 90 px over 4.2 s / 6 px over 2.4 s | |
| nose laser | 1.1 s beam every 4.6 s (first 2.2 s) | `volley.laser` |
| wingtip fans | aimed fans of 3, 6° apart, orange 235 px/s radius 3.5, every 2.2 s (first 0.9 s / 2.0 s) | `DART` |
| core stage 0 | 1 aimed red needle 225 px/s radius 3.5, every 1.5 s | spine turret, `NEEDLE` |
| core stage 1 | burst of 3, 0.1 s apart, every 2 s | spine turret |
| core stage 2 | aimed fan of 5, 5° apart, every 1.6 s | spine turret, a sweep |
| core stage 3 | ring of 10 orange 165 px/s turning 8°, every 1.6 s; 1 aimed needle every 1.6 s | back rotor; spine turret |
| angry | the revealed mortars, BOSS-27 | `boss_build.angry_pattern` |
| transformation | both wingtip pods destroyed | `transformParts` |
| shed region | panels: x 11..33, y -16..13, 2.5..7 px high, `wing`, mirrored | `armour_region` `panels`, `WING_PANEL` |
| mortars | (∓21, -1), radius 9, health 540, pod from 2.5 to 6.5 px; red flak 110 px/s radius 8 bursting into 8 at 170 px/s after 1.1 s, every 3.2 s; first 1.2 s / 2.0 s | `hidden_weapon` |
| fire rate (BOSS-39) | 5.1 as it comes in, 5.5 after its transformation | weighted shots a second |
| neon | yellow (1, 1, 0.2) | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** It is registered in `BOSS_DESIGNS`, `BOSS_MODELS` and `BOSS_LOOK.neon` after the
  World bosses, and no level's boss table names it.
- **Not a creature (2026-11-06).** BOSS-47's Cyber-Organic look is set aside for this boss on the
  user's request; it is drawn from hull metal only (no flesh layer).
- **Simulated fight (2026-11-06, a part broken every 12 s):** 322 shots and 2 lasers, every one
  from a barrel's tip along it (0 off); dead at 74 s.
- **Triangles (scratch count, 2026-11-06):** about 2 490 seen from above for its body, parts,
  armour, mortars and gun mounts, of the 4 000 budget (BOSS-53).
