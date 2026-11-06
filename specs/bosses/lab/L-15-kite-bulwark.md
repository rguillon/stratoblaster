# Kite Bulwark

> **Area:** bosses · **Prefix:** `MB-KITE-BULWARK` · **Related:** [common](../common.md),
> [Throne of Storms](L-15-throne-of-storms.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Kite Bulwark is the mini boss of Lab level L-15: a huge box-kite glider fortress, 3.8 L across,
its very wide braced wings of fabric stretched on metal spars either side of an armoured nacelle,
two tow cables trailing far behind it. Wide open, it fills the sky with wide, slow fans from its
wingtip gun pods and lobs flak from its tail winch. Once both wingtip pods are gone its wings fold
back into a narrow dart (it changes shape, BOSS-45), and a sweeper laser rides in on each folded
wing: the fight turns from wide, slow fans to fast, diving lasers and quick bursts. Shared rules
are in [common](../common.md).

**Departure from BOSS-47 (one Cyber-Organic creature):** on the user's requests (2026-11-06, "drop
the animal looking theme", then "flying fortress theme") this Lab boss is a flying machine, not a
creature: dark metal spars and plating, sailcloth, cables and neon light lines, no flesh, eyes or
veins.

## Requirements

### Look

#### MB-KITE-BULWARK-01 — Silhouette and size · MUST

Seen from above, the Kite Bulwark is a very wide, flat cross, its nose down the screen: a long
armoured nacelle down its middle (from y -36 to 31), a box-kite wing spread straight out either side
to a wingtip 64 px out, a small box-kite tail cell behind the nacelle, and two tow cables trailing
behind it to their drogues (out to about y 80). It is about 3.8 L across at rest; once its wings
have folded back it is a narrow dart about 2.4 L across and 4 L long.

**Acceptance criteria**
- Manual validation in the boss viewer: a wide box-kite cross at rest; a narrow dart, its wings
  swept back along its tail, once it has transformed.

*Sources: Lab boss request (2026-11-06, "flying fortress theme").*

#### MB-KITE-BULWARK-02 — Body · MUST

Its nacelle is a faceted armoured hull of plated steel: a raised deck down its back (a light line
along each shoulder, dark seams, a vent grille), a smoked glass canopy in its nose with a light over
it, the chin turret's seat and the spine rotor's collar. Spar sockets and hinge drums (a lit pin
through each) stand on its flanks at each wing's leading and trailing root. At its tail a winch bay
holds two cable spools (lit rings) paying out the tow cables, each ending in a drogue, a cone with a
lit ring round its mouth; behind the bay a keel boom carries the tail box: two spars across, two
panes of fabric with crossed bracing wires, their tall fabric sides standing along the spars, a light
along its back.

**Acceptance criteria**
- Manual validation: one flying machine of metal, fabric, cables and neon lines; no creature
  features.

*Sources: BOSS-49, BOSS-52; departure from BOSS-47 above.*

#### MB-KITE-BULWARK-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Wingtip pods** (left and right, in each wing's outer cell): an armoured drum (a lit band, fins
  fore and aft) over a cradle on the wing, a turret of three barrels side by side on top (its wide
  fans). The cradle stays on the wing once the pod is destroyed.
- **Winch** (at its tail, over the winch bay): a cable drum lying across the bay, lit rings round
  it, in a cradle whose deck carries the **flak mortar**, a fat barrel in a cradle on a turntable.
  A pedestal in the bay stays under the mortar's spot once it is destroyed.
- **Chin turret** (the core's, on the nacelle's front): two barrels side by side (its aimed shots,
  spreads and bursts).
- **Spine rotor** (the core's): ten barrels round a hub on the nacelle's back (its last rings).
  Until its last stage it lies under an octagonal hatch with a lit seam; as the rotor comes into use
  the hatch bursts off (BOSS-58), leaving a lit collar, and the rotor rises out.

**Acceptance criteria**
- Given its model, then it draws both pods, the winch and every gun mount.

*Sources: BOSS-48, BOSS-58.*

#### MB-KITE-BULWARK-04 — Lights · MUST

Its wings' leading edges and wingtip lamps, the fabric's middle seams, the nacelle's shoulder lines,
the hinge pins, the spools, the drogues, the tail box's light, the pods' bands, the winch's rings
and the hatch's seam glow. Its neon colour is set lime (0.9, 1, 0.3); the viewer folds it into the
enemy palette (BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are in its neon colour.

*Sources: BOSS-50.*

#### MB-KITE-BULWARK-05 — Its wings fold back · MUST

Each wing is a moving piece (BOSS-45), drawn spread open at rest: a leading and a trailing spar of
dark metal from its root out to its tip, a tip spar, ribs across (a collar where each meets a
spar), two cells of pale sailcloth stretched between them with an open gap between the cells (a box
kite's), their tall fabric sides standing along the spars, crossed bracing wires over the fabric, an
armoured root plate with a light, the pod's cradle and the sweeper's lit hardpoint. At its
transformation each wing swings 72° back about the vertical through its trailing root (its hinge
drum), the left one mirrored, and stays there: the wide cross becomes a narrow dart, its wings swept
back alongside the tail box. They leave no frame (nothing was under them).

**Acceptance criteria**
- Given its design, then its transformation swings both wings back, mirrored, and its sweepers ride
  them (unit tests on the moving regions).
- Given its model, then it draws each wing, and it holds together at rest and once they have folded.

*Sources: BOSS-45, BOSS-52.*

### Behaviour

#### MB-KITE-BULWARK-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then sways and bobs
like a kite riding the wind. While it is fought the ground scrolls at ×1.2 (it tows the fight
along).

**Acceptance criteria**
- Given the fight, then the ground eases to ×1.2 of the level's speed and back after it.

*Sources: BOSS-03, BOSS-10.*

#### MB-KITE-BULWARK-07 — Parts and core · MUST

It has three parts as it comes in, all shielding its core: `pod-left`, `pod-right` and `winch`. The
core's guns (the chin turret and the spine rotor) fire the core's volleys and are the last the
player destroys.

**Acceptance criteria**
- Given its design, then its three parts all shield the core.

*Sources: BOSS-12, BOSS-14.*

#### MB-KITE-BULWARK-08 — Stage patterns · MUST

In every stage while they stand, each wingtip pod sweeps a wide fan of 7 slow green bullets 10°
apart down the screen, the left one turned 10° to its left, the right one 10° to its right, so the
two fans cross under it; the winch lobs a flak shell at the player, a big, slow orange bullet that
bursts into a ring of 8 red ones after 1.3 s. The core fires:
- stage 0: an aimed orange bullet;
- stage 1: an aimed spread of 3, 10° apart;
- stage 2: fast bursts of 5 red bullets at the player, 0.1 s apart;
- stage 3 and after: a ring of 10 from the spine rotor, one bullet a barrel, turning 9° at each
  volley (a spiral), and bursts of 3.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys; each shot leaves a barrel (a fight in
  the simulation).

*Sources: BOSS-21, BOSS-23, BOSS-58.*

#### MB-KITE-BULWARK-09 — Angry · MUST

After its transformation it is angry (BOSS-27): its two sweepers fire all out, as often as their
warning, beam and gap allow, for `boss_rage_seconds`. It has no angry pattern of its own.

**Acceptance criteria**
- Given its transformation is over, then it is angry and fires only its two sweepers.

*Sources: BOSS-27.*

#### MB-KITE-BULWARK-10 — Transformation: the dart · MUST

It transforms once, when both wingtip pods are destroyed (named, so that no part the player can hit
stands on a wing as it moves). As an event: its wings strain, shuddering, then swing back about
their hinge drums into a narrow dart, their stumps riding them; a **sweeper** rides in on each
folded wing's inner cell, on the pod it unfolds over the hardpoint there. They shield the core and
fire lasers that sweep after the player, in turn. The fight changes character: no more wide fans to
weave through, but slow-turning beams to outrun, the winch's flak and the core's fast bursts.

**Acceptance criteria**
- Given both wingtip pods destroyed, then it transforms, its wings fold back and its two sweepers
  are revealed on them.

*Sources: BOSS-35, BOSS-36, BOSS-45.*

#### MB-KITE-BULWARK-11 — Death, drops and points · MUST

Its parts drop a weapon bonus half of the time, its sweepers 30 %; it drops a life bonus as a mini
boss (BOSS-57). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/kite_bulwark.py` (`_KITE_BULWARK`, `KITE_BULWARK`) unless
named; its model in `src/game/view/bosses/lab/kite_bulwark_model.py` and `kite_bulwark_wings.py`.

| Name | Value | Notes |
|------|-------|-------|
| size | 3.8 L (radius 65 px) | `stats.size` |
| nacelle | y -36 to 31, 20 px wide, deck 13 px high | `NOSE`, `TAIL`, `NACELLE_HALF`, `NACELLE_TOP`; loft `NACELLE` |
| wing (right, as drawn) | (9, -12) (40, -8) (62, -4) (64, 3) (62, 10) (40, 11) (9, 12); 6 to 9.5 px high | `WING`, `WING_Y` |
| wing cells | x 12–37 and 43–61; ribs at x 12, 24.5, 37, 43, 52, 61 | `kite_bulwark_wings.CELLS`, `RIBS` |
| wing fold (moving region) | swing about `up` through (9, 12, 6), 0° to 72° (mirrored); no frame | `WING_SWING`, `moving_region` `wings` |
| tail box | 34 px wide, spars at y 41 and 55 | `kite_bulwark_model.TAIL_BOX` |
| tow cables | from the spools (±9.4, 32) to drogues at (16, 72) and (-11, 80) | `CABLES` |
| core | health 1 700, radius 14 | |
| `pod-left`, `pod-right` | (∓52, 3), radius 10, health 700, shield, drop 0.5 | on the wings |
| pod turrets | 13 px high; 3 barrels 2.9 px apart, bore 1.1, 7 px long; dome radius 4.6 | `POD_GUN` |
| `winch` | (0, 31), radius 11, health 800, shield, drop 0.5 | |
| flak mortar | (0, 33), 12 px high; 1 barrel, bore 3.2, 4.5 px long, mortar cradle | `WINCH_MORTAR` |
| chin turret (core) | (0, -24), 13 px high; 2 barrels 2.9 px apart, bore 1.1, 7 px long | `CHIN_GUN` |
| spine rotor (core) | (0, 2), 14 px high; 10 barrels, bore 0.8, 3.2 px long; hub radius 4.4 | `ROTOR` |
| rotor hatch | octagon of radius 6 round (0, 2) | `armour_region` `rotor-hatch` (`mount`) |
| full health | 5 180 (core 1 700, parts 2 200, sweepers 1 280) | BOSS-54; about the 1-5 mini boss's (Sentinel, 5 150) |
| points | 5 000 | |
| ground speed | ×1.2 | |
| stop height | 0.72 | `stopFraction` |
| sway / bob | 50 px over 7 s / 7 px over 3.2 s | |
| pod fans | 7 green at 140 px/s, 10° apart, turned ∓10°, every 3.2 s (first 1 s / 2.6 s) | `volley.fan`, a sweep |
| flak | 1 orange shell at 95 px/s, radius 7, bursting after 1.3 s into 8 red at 150 px/s, aimed, every 2.8 s (first 1.8 s) | `FLAK` |
| core stage 0 | aimed 1 orange at 185 px/s, every 3 s | chin turret |
| core stage 1 | aimed 3, 10° apart, every 2.4 s | chin turret |
| core stage 2 | burst of 5 red at 200 px/s, 0.1 s apart, every 1.5 s | chin turret |
| core stage 3+ | ring of 10 orange turning 9°, every 1.5 s; burst of 3 red, every 2 s | rotor; chin turret |
| weighted fire rate | 5.07 as it comes in, 5.69 after its transformation | BOSS-39 |
| transformation | `pod-left` and `pod-right` destroyed | `transformParts` |
| sweepers | (∓25.3, 26.7) on the folded wings (the wing's (28, 1) as drawn), radius 7, health 640, pod from 9.5 to 12.5 px; first 1.2 s / 2.0 s | ride the wings; `sweeper` kind (a sweeping laser 2 s every 8 s) |
| neon | lime (0.9, 1, 0.3) | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time and its place in a
  world's health order (BOSS-55, BOSS-56) are not set. Its full health is about that of the 1-5
  mini boss (Sentinel).
- **Not a creature** (see the departure from BOSS-47 above).
- **Swaying faster once folded (not done).** The brief asked for the dart to sway faster than the
  open kite; a design's sway is one amplitude and period for the whole fight, so the engine cannot
  change it at a transformation. An engine change (a sway per form, e.g. `sway` as a list indexed
  by `boss.form`, eased over the transformation) would allow it; until then the sweepers and the
  core's fast bursts carry the change of pace.
- **Silhouette.** The Moth Lantern (L-3) swings wings the other way (folded back at rest, opening
  wide); the Storm Petrel (1-1) swings its outer wings forward 30°. The Kite Bulwark is a straight,
  rectangular box-kite cross of fabric cells on spars that folds into a dart, with a tail box and
  trailing tow cables.
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-06): 379 shots and 13
  lasers, every shot from a barrel, along it; it dies at about 74 s.
