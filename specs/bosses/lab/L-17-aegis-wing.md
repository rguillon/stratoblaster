# Aegis Wing

> **Area:** bosses · **Prefix:** `MB-AEGIS-WING` · **Related:** [common](../common.md),
> [Seaplane Leviathan](L-17-seaplane-leviathan.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Aegis Wing is the mini boss of Lab level L-17: a giant tailless flying wing. Its leading edge
sweeps straight back from a blunt nose to its tips, its trailing edge is a sawtooth, a low blended
hump runs down its middle with the cockpit's visor, and its engines are buried in the hump, their
intakes on top. It glides slowly and picks at the player with sparse, precise shots. At its
transformation the smooth stealth skin of its outer wings **flips over like tiles**: row after row
of skin panels turns over in a wave running in from the wingtip and from the root, each showing a
bristling weapon face, and where the two waves meet the last panels fold open like petals on an
**orb** each side. From then on it fills the screen with rings. Shared rules are in
[common](../common.md).

**Not a creature.** BOSS-47 asks for a Cyber-Organic creature; this Lab boss departs from it on the
user's requests (2026-11-06, "drop the animal looking theme"; "10 more gigantic airplanes but be
really creative on the transformation, not just rotate a part, like pieces morphing into something
else"): it is a built aircraft of dark metal, stealth skin panels and neon light lines, with no
flesh, eyes or limbs.

## Requirements

### Look

#### MB-AEGIS-WING-01 — Silhouette and size · MUST

Seen from above it is a flying wing 122 px (3.5 L) across its tips and 69 px from its nose to its
tail, its nose down the screen: a broad arrowhead whose back edge is a sawtooth of five teeth, no
tail, no fuselage standing out of it. No other boss is a tailless wing.

**Acceptance criteria**
- Manual validation in the boss viewer: a flying wing, its sawtooth trailing edge readable.

*Sources: Lab boss request (2026-11-06, gigantic airplanes).*

#### MB-AEGIS-WING-02 — Wing, hump and buried engines · MUST

The wing is a thin plank bevelled underneath, in its outline, lit along its leading edge and along
each tooth of its trailing edge, a lit navigation light at each tip, dark panel seams on its inner
wing. Down its middle a low lens-shaped hump runs from the nose to the tail: a dark visor across
its front with a lit rim, a lit seam down its spine. Its two engines are buried in the hump's
flanks: a long rounded fairing over each from behind its intake to its exhaust, a flat dark slot
lit inside in a notch of the trailing edge. Its outer wings carry the skin panels
(MB-AEGIS-WING-05).

**Acceptance criteria**
- Manual validation: one flying wing, its hump, engines and skin panels readable from above.

*Sources: BOSS-49, user request (2026-11-06).*

#### MB-AEGIS-WING-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Intake guns** (`intake-left`, `intake-right`): each engine's raised intake, a wedge cowl rising
  to its dark mouth lit along its lip, a twin-barrelled turret on an armoured ring behind it on the
  engine's fairing (its single aimed shots, the barrels in turn).
- **Nose gun** (`nose-gun`): an armoured drum on the nose, lit round its rim, dark sensor blisters
  either side and lit chevrons on the nose ahead, round a long single-barrelled turret (its quick
  bursts).
- **Dorsal turret** (the core's, on the hump behind the visor): two barrels side by side.
- **Tail rotor** (the core's, on the hump's tail): twelve barrels round a hub (its last rings).
  Until its last stage it lies under an octagonal hatch with a lit seam; as the rotor comes into use
  the hatch bursts off (BOSS-58), leaving a collar, and the rotor rises out.

A destroyed intake gun leaves its stump on the engine's fairing; the nose gun's on the nose's seat.

**Acceptance criteria**
- Given its model, then it draws its three parts and every gun mount.

*Sources: BOSS-18, BOSS-48, BOSS-58.*

#### MB-AEGIS-WING-04 — Lights · MUST

The wing's edges and tip lights, the visor's rim and the spine seam, the intakes' lips, the
exhausts, the guns' rims, the skin panels' weapon faces and the orbs' wells glow. Its neon colour,
set periwinkle, shows bright green (BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright green.

*Sources: BOSS-50.*

#### MB-AEGIS-WING-05 — Its skin panels (an armour region and a view rig) · MUST

On each outer wing five rows of skin panels run along the chord, 7 px apart, from 2 px behind the
leading edge to 2 px before the trailing edge: plates 6.4 px wide, about 6.4 px long, 0.6 px apart,
0.9 px proud of the wing's top, in the wing's own dark finish. The three middle rows run through
the orb's well (y -7.5 to 6), where their panels are the well's petals. At rest the panels are an
armour region (`skin`), drawn whole; it leaves no pieces when it bursts, its view rig taking over
in the same pose (MB-AEGIS-WING-10). Each panel's underside is its **weapon face**: a dark metal
plate, a lit cell in its middle and two vanes standing out of it. What the rig moves is drawn only:
nothing the player can hit or that fires.

**Acceptance criteria**
- Manual validation: at rest the outer wings are smooth skin with fine panel seams.
- Given its model at rest and after its transformation, then it holds together (unit test).

*Sources: user request (2026-11-06, "wing panels flipping over like tiles to show weapon faces"),
BOSS-42, BOSS-52.*

### Behaviour

#### MB-AEGIS-WING-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then glides in slow,
moderate sways and a gentle bob. While it is fought the ground keeps the level's speed (×1).

**Acceptance criteria**
- Given the fight, then the ground keeps the level's speed.

*Sources: BOSS-03, BOSS-10.*

#### MB-AEGIS-WING-07 — Parts and core · MUST

It has three parts as it comes in, all shielding its core: `intake-left`, `intake-right` and
`nose-gun`. The core's guns (the dorsal turret and the tail rotor) fire the core's volleys and are
the last the player destroys.

**Acceptance criteria**
- Given its design, then its three parts all shield the core.

*Sources: BOSS-12, BOSS-13, BOSS-14.*

#### MB-AEGIS-WING-08 — Stage patterns: sparse and precise, then rings · MUST

In every stage while they stand, each intake gun fires a single fast red bullet at the player, the
two 1.4 s apart, and the nose gun bursts of 3 fast orange bullets, 0.1 s apart. The core fires:
- stage 0: an aimed blue bullet, every 3.4 s;
- stage 1: an aimed pair, 4° apart;
- stage 2: an aimed spread of 3, 7° apart;
- stage 3 (all three parts gone): a ring of 12 from the tail rotor, turning 8° at each volley (a
  spiral), and an aimed red bullet.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys; each shot leaves a barrel (a fight in
  the simulation).

*Sources: BOSS-21, BOSS-23, BOSS-58.*

#### MB-AEGIS-WING-09 — Angry · MUST

After its transformation it is angry (BOSS-27): its two orbs fire their rings all out for
`boss_rage_seconds`. It has no angry pattern of its own.

**Acceptance criteria**
- Given its transformation is over, then it is angry and fires only its orbs.

*Sources: BOSS-27.*

#### MB-AEGIS-WING-10 — Transformation: the skin flips over into orbs · MUST

It transforms when both intake guns are destroyed (named). As one staged event over the
transformation (shares of `boss_transform_seconds`):
- until 0.15 the skin strains (BOSS-43), shuddering and strobing;
- from 0.15 the rows **flip over** about their own axes, half a turn each over 0.2, in a wave
  running inwards from both edges of the panel field: the outermost rows (at the root and nearest
  the tip) first, the next ones 0.08 later, the middle row last, each turning up its weapon face:
  the smooth stealth wing becomes a bristling field of dark plates, lit cells and vanes;
- where the two waves meet, the well's panels do not flip but **fold open like petals**: those of
  the side rows about their outer edges (0.36–0.56), the middle row's two fore and aft (0.42–0.62),
  standing open round the well;
- an **orb** rises out of each well (from 0.4, BOSS-43) and slides its ten-barrel rotor out: rings
  of 10 turning 13°, blue. They shield the core.

The fight changes character: from a few precise shots to keep away from, to storms of rings to weave
through, and at the end the tail rotor's spiral on top.

**Acceptance criteria**
- Given both intake guns destroyed, then it transforms, its skin region is shed and its two orbs
  are revealed in it (unit tests on the design).
- Manual validation in the boss viewer: the rows flip in a wave towards the wells, the petals open
  and the orbs rise out where the waves meet.

*Sources: BOSS-35, BOSS-36, BOSS-42, BOSS-43, user request (2026-11-06).*

#### MB-AEGIS-WING-11 — Never easier · MUST

Its weighted fire rate (BOSS-39) goes up at its transformation.

**Acceptance criteria**
- Given its design, then its weighted fire rate is higher after its transformation than as it
  comes in (unit test).

*Sources: BOSS-39.*

#### MB-AEGIS-WING-12 — Death, drops and points · MUST

Its parts drop a weapon bonus 50 % of the time, its hidden weapons 30 % (BOSS-57). It scores the
points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/aegis_wing.py` (`_AEGIS_WING`, `AEGIS_WING`); its model in
`src/game/view/bosses/lab/aegis_wing_model.py` and `aegis_wing_tiles.py` (the skin panels and
their rig).

| Name | Value | Notes |
|------|-------|-------|
| size | 3.5 L | `stats.size` |
| wing | nose (0, -44), tips (±61, 5), sawtooth trailing edge to (0, 25); 3–8 px high | `WING`, `WING_LOW`, `WING_WAIST`, `WING_TOP` |
| hump | y -42..24, half width up to 14, up to 16 px high | `HUMP` |
| engines | intakes at (±11, -4), exhausts at (±10, 17) | `INTAKE_AT`, `EXHAUST_AT` |
| skin panels | 5 rows a wing, axes at x ±21, 28, 35, 42, 49; 6.4 px wide, ~6.4 px long, 0.6 px apart, 0.9 px thick | `ROW_*`, `TILE*`, `MARGIN` |
| orb's well | across the 3 middle rows, y -7.5..6 | `WELL` |
| flip wave | from 0.15, a row 0.08 after the one outside it, each 0.2 long; petals 0.36–0.56 (side), 0.42–0.62 (middle), opened 2 rad | rig `START`, `WAVE`, `FLIP`, `PETALS`, `MIDDLE`, `OPEN` |
| core | health 1 250, radius 15 | |
| `intake-left`, `intake-right` | (∓11, 0), radius 8, health 660, shield, drop 0.5 | |
| `nose-gun` | (0, -37), radius 8, health 760, shield, drop 0.5 | |
| intake guns | (±11, 3), 14.6 px high; 2 barrels 2.6 px apart, bore 0.9, 7 px long; dome radius 3.6 | `INTAKE_GUN` |
| nose gun | (0, -37), 12.4 px high; 1 barrel, bore 1.1, 10 px long; dome radius 3.4 | `NOSE_GUN` |
| dorsal turret (core) | (0, -17), 16 px high; 2 barrels 3 px apart, bore 1, 7 px long | `DORSAL_GUN` |
| tail rotor (core) | (0, 14), 13.4 px high; 12 barrels, bore 0.75, 3.4 px long; hub radius 4.2 | `ROTOR` |
| rotor hatch | octagon of radius 5.4 round (0, 14) | `armour_region` `rotor-hatch` (`mount`) |
| skin (armour) | the 5 rows' staircase outline, x ±17.5..52.5; no pieces; `wing` frame (drawn: a dark floor, the wells lit) | `tile_field()`; form 1 |
| orbs | (±35, -0.75) in the wells, radius 7, health 610, pod 8–11 px, blue; first 1.0 s / 1.8 s | in the skin |
| full health | 4 550 (core 1 250, parts 2 080, orbs 1 220) | BOSS-54 |
| points | 4 200 | |
| ground speed | ×1 | |
| stop height | 0.73 | `stopFraction` |
| sway / bob | 48 px over 9 s / 4 px over 4.5 s | |
| intake guns' shots | aimed 1, red 230 px/s, every 2.8 s (first 1.0 s / 2.4 s) | |
| nose gun's bursts | 3, 0.1 s apart, orange 200 px/s, every 3 s (first 1.6 s) | |
| core stage 0 | aimed 1, blue 175 px/s, every 3.4 s | dorsal turret |
| core stage 1 | aimed 2, 4° apart, every 2.8 s | dorsal turret |
| core stage 2 | aimed 3, 7° apart, every 2.6 s | dorsal turret |
| core stage 3 | ring of 12 turning 8°, blue, every 1.3 s; aimed 1, red, every 2.6 s | rotor; dorsal turret |
| weighted fire rate | 2.0 as it comes in, 9.9 after its transformation | BOSS-39 |
| transformation | `intake-left` and `intake-right` | `transformParts` |
| neon | periwinkle (0.6, 0.6, 1), shown green | `BOSS_LOOK.neon` |
| triangles | about 3 500 (core 730, parts 320, armour 590, rig 1 870), gun mounts apart | BOSS-53 (4 000) |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time and its place in a
  world's health order (BOSS-55, BOSS-56) are not set. Its full health is about the Lab's other
  mini bosses' (4 040 to 5 180).
- **Not a creature** (see the top): BOSS-47's creature look does not apply; BOSS-48 to BOSS-53 do.
- **The morph is the view's.** The sim knows only the `skin` region (shed at the transformation)
  and the two orbs; the panels' flips and petals follow the boss's `form`, `transforming_into` and
  `transform` in the view rig. The region draws its panels whole and leaves no pieces, so the
  rig's panels take over in the same pose as it bursts. No engine change was needed; an engine
  option for a region to hand over to a rig instead of bursting (no blasts, no strain) would make
  this cleaner.
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-06): 805 shots, every one
  from a barrel, along it; it dies at about 74 s.
