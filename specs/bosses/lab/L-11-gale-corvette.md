# Gale Corvette

> **Area:** bosses · **Prefix:** `MB-GALE-CORVETTE` · **Related:** [common](../common.md),
> [Sky Carrier](L-11-sky-carrier.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Gale Corvette is the mini boss of Lab level L-11: a small, fast armed airship. A riveted cigar
gas envelope rides over a long gondola whose nose juts out ahead of it with the bow gun; an engine
nacelle on a stub wing each side pushes it with a ducted propeller, and a cruciform tail closes its
stern. It sways wide and quick across the screen, chasing the player with aimed fire. At its
transformation it **turns round** (BOSS-46) to bring its stern to bear, its propellers swivelling up
into lift rotors and running backwards, and the fairings over its stern fins burst off on a pair of
batteries: it fights on as a rear guard, laying walls of fans straight down. Shared rules are in
[common](../common.md).

**Not a creature.** BOSS-47 asks for a Cyber-Organic creature; this Lab boss departs from it on the
user's requests (2026-11-06, "drop the animal looking theme"; "flying fortress theme"): it is a
built flying machine of riveted metal, plating, propellers and neon light lines, with no flesh,
eyes or limbs.

## Requirements

### Look

#### MB-GALE-CORVETTE-01 — Silhouette and size · MUST

Seen from above it is a cigar 90 px (2.6 L) long and 26 px across, its nose down the screen, the
gondola's nose and its bow gun jutting 18 px out ahead of it, a nacelle out on a stub wing each side
(72 px across the nacelles) and a cross of fins at its stern: an airship, unlike any other boss.
Turned round, the same airship faces up the screen, its stern and its batteries towards the player.

**Acceptance criteria**
- Manual validation in the boss viewer: a small airship at rest, turned round after its
  transformation.

*Sources: Lab boss request (2026-11-06, flying fortress theme).*

#### MB-GALE-CORVETTE-02 — Envelope, gondola, nacelles and tail · MUST

The envelope is a 14-sided loft along its length, its gores in two shades, a rivet row down each
side of its back, three dark bands with a lit ring round it, a catwalk down its back between the
dorsal turret's seat and the rotor's well, a dark nose cap with a lit mooring ring. The gondola is a
long bevelled boat under it, lit bridge windows down its sides, hangers up into the envelope, the
bow gun's seat on its nose. Each nacelle is a cigar along the boat, a lit intake ring at its nose, a
lit band and exhaust vents near its tail, on a stub wing out of the envelope's flank with two struts
under it to the gondola. The tail is two flat stern fins, lit along their tips, and a tall upper fin
with a lit stripe down its rudder.

**Acceptance criteria**
- Manual validation: one airship, its envelope, gondola, nacelles and tail readable from above.

*Sources: BOSS-49, user request (2026-11-06).*

#### MB-GALE-CORVETTE-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Engine guns** (`engine-left`, `engine-right`): an armoured, lit octagonal cowl on each nacelle's
  back, cheek plates down its sides, round a twin-barrelled turret (its aimed pairs).
- **Bow gun** (`bow-gun`): a lit drum on the gondola's nose, a rangefinder bar behind it and a lit
  chevron ahead, round a three-barrelled turret (its bursts).
- **Dorsal turret** (the core's, on the envelope's back): two barrels side by side (its aimed shots,
  spreads and fans).
- **Stern rotor** (the core's, behind it on the envelope's back): ten barrels round a hub (its last
  rings). Until its last stage it lies under an octagonal hatch with a lit seam; as the rotor comes
  into use the hatch bursts off (BOSS-58), leaving a collar, and the rotor rises out.

A destroyed engine gun leaves its stump on its nacelle; the bow gun's on the gondola's nose.

**Acceptance criteria**
- Given its model, then it draws its three parts and every gun mount.

*Sources: BOSS-18, BOSS-48, BOSS-58.*

#### MB-GALE-CORVETTE-04 — Lights · MUST

The envelope's rings and mooring ring, the bridge windows, the nacelles' intake rings and bands, the
stub wings' leading edges, the fins' tips and rudder stripe, the cowls' and the drum's rims, the
fairings' seams and the propellers' ducts and blade tips glow. Its neon colour, set sky blue, shows
bright green (BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright green.

*Sources: BOSS-50.*

#### MB-GALE-CORVETTE-05 — Its propellers (a view rig) · MUST

Behind each nacelle a ducted pusher propeller turns on a short shaft: a duct with a lit lip, two
struts across it to the hub's spinner, three blades with lit tips. They spin all the time (16 rad/s).
As it turns round (MB-GALE-CORVETTE-10), each swivels its shaft a quarter turn up about the
nacelle's tail (from 0.12 to 0.7 of the transformation), its duct ending level over the nacelle like
a lift rotor, and its spin slows, stops and runs backwards (from 0.05 to 0.85), faster than before.
The propellers are drawn only: no part, no muzzle, nothing the player can hit or that fires.

**Acceptance criteria**
- Manual validation: the propellers spin, swivel up and reverse as it turns round.
- Given its model at rest and after its transformation, then it holds together (unit test).

*Sources: user request (2026-11-06, "get creative on how the boss transforms"), BOSS-52.*

### Behaviour

#### MB-GALE-CORVETTE-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then sways wide and
quick and bobs: a small, fast ship. While it is fought the ground scrolls at ×1.3 (it is chased).

**Acceptance criteria**
- Given the fight, then the ground eases to ×1.3 of the level's speed and back after it.

*Sources: BOSS-03, BOSS-10.*

#### MB-GALE-CORVETTE-07 — Parts and core · MUST

It has three parts as it comes in, all shielding its core: `engine-left`, `engine-right` and
`bow-gun`. The core's guns (the dorsal turret and the stern rotor) fire the core's volleys and are
the last the player destroys.

**Acceptance criteria**
- Given its design, then its three parts all shield the core.

*Sources: BOSS-12, BOSS-13, BOSS-14.*

#### MB-GALE-CORVETTE-08 — Stage patterns: chase, then rear guard · MUST

In every stage while they stand, each engine gun sweeps an aimed pair of red bullets 6° apart, the
two in turn, and the bow gun fires bursts of 3 orange bullets at the player. The core fires:
- stage 0: an aimed blue bullet;
- stage 1: an aimed spread of 3, 8° apart;
- stage 2: a fan of 5 orange bullets, 12° apart, straight down;
- stage 3 (all three parts gone): a ring of 10 from the stern rotor, turning 9° at each volley (a
  spiral), and an aimed pair of red bullets.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys; each shot leaves a barrel (a fight in
  the simulation).

*Sources: BOSS-21, BOSS-23, BOSS-58.*

#### MB-GALE-CORVETTE-09 — Angry · MUST

After its transformation it is angry (BOSS-27): its two batteries fire all out for
`boss_rage_seconds`. It has no angry pattern of its own.

**Acceptance criteria**
- Given its transformation is over, then it is angry and fires only its batteries.

*Sources: BOSS-27.*

#### MB-GALE-CORVETTE-10 — Transformation: it turns round · MUST

It transforms when both engine guns are destroyed (named). As one event over the transformation:
- it **turns round** (BOSS-46), half a turn, easing, its stern coming round to face the player; its
  parts' places, hit circles and muzzles turn with it (the bow gun, if it still stands, ends at its
  back, firing over the envelope);
- its propellers swivel up into lift rotors and reverse (MB-GALE-CORVETTE-05);
- the armoured fairings over its stern fins (heavy streamlined plates with a lit seam and rivets)
  strain and burst off (`wing` frame left on the fins), and a **battery** unfolds on each stern fin,
  sweeping fans of 7 straight down the screen. They shield the core.

The fight changes character: from a ship chasing the player with aimed shots to a rear guard
walling the screen with straight fans the player has to slip between.

**Acceptance criteria**
- Given both engine guns destroyed, then it transforms, turning round by pi, its fairings burst and
  its two batteries are revealed on its stern fins (unit tests on the design).

*Sources: BOSS-35, BOSS-36, BOSS-42, BOSS-46.*

#### MB-GALE-CORVETTE-11 — Never easier · MUST

Its weighted fire rate (BOSS-39) goes up at its transformation.

**Acceptance criteria**
- Given its design, then its weighted fire rate is higher after its transformation than as it
  comes in (unit test).

*Sources: BOSS-39.*

#### MB-GALE-CORVETTE-12 — Death, drops and points · MUST

Its parts drop a weapon bonus 50 % of the time, its hidden weapons 30 % (BOSS-57). It scores the
points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/gale_corvette.py` (`_GALE_CORVETTE`, `GALE_CORVETTE`); its model
in `src/game/view/bosses/lab/gale_corvette_model.py` and `gale_corvette_rig.py` (the propellers).

| Name | Value | Notes |
|------|-------|-------|
| size | 3.2 L | `stats.size` |
| envelope | y -44..46, radius up to 13, axis 22 px high | `ENVELOPE`, `ENV_H` |
| gondola | y -62..14, half width 6, 3–11 px high | `GONDOLA`, `GONDOLA_HALF`, `GONDOLA_LOW`, `GONDOLA_TOP` |
| nacelles | (±36, 2), 22 px long, radius 4.5, axis 17 px high | `NACELLE_AT`, `NACELLE_HALF`, `NACELLE_RADIUS`, `NACELLE_H` |
| propellers | hub 4 px behind each nacelle's tail, blades 8 px; spin 16 rad/s, reversed ×1.3 once turned; swivel 0.12–0.7, reversal 0.05–0.85 of the transformation | `PROP_Y`, `PROP_RADIUS`; rig `SPIN`, `SWIVEL`, `REVERSE` |
| stern fins | root y 28..47, tip y 37..46 at x ±26, top 22.6 px | `FIN_ROOT`, `FIN_TIP`, `FIN_SPAN`, `FIN_TOP` |
| core | health 1 150, radius 15 | |
| `engine-left`, `engine-right` | (∓36, -3) on the nacelles, radius 10, health 640, shield, drop 0.5 | |
| `bow-gun` | (0, -52) on the gondola's nose, radius 10, health 720, shield, drop 0.5 | |
| engine guns | 22.3 px high; 2 barrels 2.8 px apart, bore 1, 7 px long; dome radius 4 | `ENGINE_GUN` |
| bow gun | (0, -54), 11.5 px high; 3 barrels 2.9 px apart, bore 1.1, 8 px long; dome radius 4.6 | `BOW_GUN` |
| dorsal turret (core) | (0, -15), 35 px high; 2 barrels 3 px apart, bore 1.1, 7.5 px long | `DORSAL_GUN` |
| stern rotor (core) | (0, 15), 34 px high; 10 barrels, bore 0.8, 3.4 px long; hub radius 4.2 | `ROTOR` |
| rotor hatch | octagon of radius 5.5 round (0, 15) | `armour_region` `rotor-hatch` (`mount`) |
| fairings (armour) | x ±7..25, y 30..47.5, 22–27 px; `wing` frame | `FAIRING`; form 1 |
| batteries | (∓16, 40) on the stern fins, radius 8, health 580, pod 22.6–25.2 px, orange; first 1.2 s / 2.0 s | in the fairings |
| turn | pi at its transformation | `turns` |
| full health | 4 310 (core 1 150, parts 2 000, batteries 1 160) | BOSS-54 |
| points | 3 800 | |
| ground speed | ×1.3 | |
| stop height | 0.74 | `stopFraction` |
| sway / bob | 75 px over 5.2 s / 7 px over 2.6 s | |
| engine guns' pairs | aimed 2, 6° apart, red 190 px/s, every 2 s (first 0.8 s / 1.8 s) | sweeps |
| bow gun's bursts | 3, 0.12 s apart, orange 180 px/s, every 2.4 s (first 1.3 s) | |
| core stage 0 | aimed 1, blue 175 px/s, every 2.8 s | dorsal turret |
| core stage 1 | aimed 3, 8° apart, every 2.4 s | dorsal turret |
| core stage 2 | fan of 5, 12° apart, orange, every 2.4 s | dorsal turret |
| core stage 3 | ring of 10 turning 9°, blue, every 1.5 s; aimed 2, 6° apart, red, every 2.6 s | rotor; dorsal turret |
| weighted fire rate | 3.6 as it comes in, 10.3 after its transformation | BOSS-39 |
| transformation | `engine-left` and `engine-right` | `transformParts` |
| neon | sky blue (0.5, 0.9, 1), shown green | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time and its place in a
  world's health order (BOSS-55, BOSS-56) are not set. Its full health is about the Lab's other
  mini bosses' (4 040 to 4 880).
- **Not a creature** (see the top): BOSS-47's creature look does not apply; BOSS-48 to BOSS-53 do.
- **The propellers are the view's.** The sim knows nothing of them: their swivel and spin follow
  the boss's `form`, `transforming_into` and `transform`. No engine change was needed.
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-06): 600 shots, every one
  from a barrel, along it; it dies at about 74 s.
