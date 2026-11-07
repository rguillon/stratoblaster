# Twin-Boom Lancer

> **Area:** bosses · **Prefix:** `MB-TWIN-BOOM-LANCER` · **Related:** [common](../common.md),
> [Swing-Wing Titan](L-18-swing-wing-titan.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Twin-Boom Lancer is the mini boss of Lab level L-18: a gigantic twin-boom fighter seen from
above. A central pod with its cockpit sits on a straight wing between two long engine booms, an
engine cowling at the front of each and a tail fin at the back, a tailplane joining their tails.
Its two boom guns fire **two parallel streams** straight down as it strafes from side to side. At
its transformation it **morphs into one gun**: its tailplane splits and folds up, its inner wings
telescope away, its two booms slide in under the pod and lock together into one long heavy gun body,
their cowlings peel open in petals and a heavy **cannon** rises out of each, their fins, the folded
tailplane and radiator blades rising from the merged tail standing over it as cooling fins. From
then on it fires heavy, concentrated shells. Shared rules are in [common](../common.md).

**Not a creature.** BOSS-47 asks for a Cyber-Organic creature; this Lab boss departs from it on the
user's requests (2026-11-06, "drop the animal looking theme"; "10 more gigantic airplanes but be
really creative on the transformation, not just rotate a part, like pieces morphing into something
else"): it is a built aircraft of dark metal plating, glass, engines and neon light lines, with no
flesh, eyes or limbs.

## Requirements

### Look

#### MB-TWIN-BOOM-LANCER-01 — Silhouette and size · MUST

Seen from above it is a twin-boom fighter about 128 px across its wing tips and 103 px long, its
nose down the screen: two long parallel booms 60 px apart, the shorter pod between them, the
straight wing across all three, the tailplane closing the booms' tails like a gate. Once
transformed it is a narrow dart: one long double gun body under the pod (its two cannons out ahead
of the pod's nose), short wings out either side, a crest of fins over its tail.

**Acceptance criteria**
- Manual validation in the boss viewer: a twin-boom fighter unlike any other boss, and a different
  silhouette once transformed.

*Sources: Lab boss request (2026-11-06, "gigantic airplanes").*

#### MB-TWIN-BOOM-LANCER-02 — Pod, booms and wing · MUST

The pod is a fighter's fuselage (`POD` stations), a smoked canopy painted on its back, lit lines
down its shoulders, an exhaust at its tail, the seats of the nose gun, the dorsal turret and the
tail rotor on its back. Each boom (`BOOM_X`, `BOOM_H`, `BOOM_R`, `BOOM_ENDS`) is a long hexagonal
tube with a plated, lit saddle along its back, a gun pylon behind its cowling, exhaust slots on its
side, a glowing nozzle at its tail and a swept tail fin. Its engine cowling (`COWL`, `COWL_R`) is a
hexagonal shell: its lower half and inner upper facet stay on the boom, its top and outer upper
facets are petals; inside it the engine core along the boom's axis and the intake fan's face behind
a lit lip. The wing (`WING_ROOT`, `WING_TIP`, `WING_SPAN`, `WING_Y`) has a lit leading edge and a
lamp at each tip: its outer panels ride the booms, its inner panels are two sleeves each side (the
outer on the boom, the middle one sliding under it). The tailplane (`TAILPLANE`, `TAILPLANE_H`) is
two halves meeting on the centre line, lit along their leading edges and at the seam.

**Acceptance criteria**
- Manual validation: one aircraft, holding together at rest and once transformed.

*Sources: BOSS-49, BOSS-52, user request (2026-11-06).*

#### MB-TWIN-BOOM-LANCER-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Boom guns** (`boom-left`, `boom-right`), on each boom behind its cowling: an armoured gun pack
  on its pylon, lit, two fixed barrels side by side pointing down the screen (they take turns: a
  stream).
- **Dorsal turret** (`dorsal`), on the pod's back behind the canopy: an armoured collar, lit, a
  three-barrelled turret (its bursts).
- **Nose gun** (the core's, on the pod's nose): two barrels side by side on a turret (its aimed
  shots, spreads and fans).
- **Tail rotor** (the core's, on the pod's back near its tail): twelve barrels round a hub (its last
  rings). Until its last stage it lies under an octagonal hatch with a seam of light round it; as
  the rotor comes into use the hatch bursts off (BOSS-58), leaving a collar, and the rotor rises
  out.
- **Cannons** (`cannon-left`, `cannon-right`), revealed (MB-TWIN-BOOM-LANCER-10): a heavy breech
  block, lit, on the engine core in each opened cowling, three heavy barrels on its turret.

A destroyed boom gun's stump stands on its pylon, on the boom (it moves with it); the dorsal
turret's on its seat; a cannon's on the engine core.

**Acceptance criteria**
- Given its model, then it draws its three parts, its two cannons and every gun mount.

*Sources: BOSS-18, BOSS-40, BOSS-48, BOSS-58.*

#### MB-TWIN-BOOM-LANCER-04 — Lights · MUST

Its lights take its neon colour, gold, shown bright yellow (BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright yellow.

*Sources: BOSS-50.*

#### MB-TWIN-BOOM-LANCER-05 — Moving pieces and rig · MUST

Each boom (with its cowling's fixed half, its outer wing panel, its fin and the outer sleeve of its
inner wing) is a moving piece (`boom-right` and its mirror image `boom-left`, BOSS-45) that slides
`LOCK` (in to X ±8 and 16 px forward) as it transforms. Its cowling's two petals, its tailplane
half, its radiator blades (hidden in its tail), its latches (hidden in its inner side) and the
middle sleeve of its inner wing are its view rig (`drawing.rig`, no hit circle or muzzle on them);
the rig follows its boom's slide. The tail rotor's hatch is a shed region of its own (BOSS-58).

**Acceptance criteria**
- Given its design, then its transformation moves both booms and each cannon rides one of them
  (unit test).
- Given its model, then it holds together at rest and once transformed (BOSS-52).

*Sources: BOSS-45, BOSS-52.*

### Behaviour

#### MB-TWIN-BOOM-LANCER-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then sways wide and
quick, strafing its streams across the screen, and bobs. While it is fought the ground scrolls at
×1.2.

**Acceptance criteria**
- Given the fight, then the ground eases to ×1.2 of the level's speed and back after it.

*Sources: BOSS-03, BOSS-10.*

#### MB-TWIN-BOOM-LANCER-07 — Parts and core · MUST

It has three parts as it comes in, all shielding its core: `boom-left`, `boom-right` and `dorsal`.
The core's guns (the nose gun and the tail rotor) fire the core's volleys and are the last the
player destroys.

**Acceptance criteria**
- Given its design, then its three parts all shield the core.

*Sources: BOSS-12, BOSS-14.*

#### MB-TWIN-BOOM-LANCER-08 — Stage patterns: the twin streams · MUST

As it comes in it strafes: in every stage while they stand, each boom gun fires one orange bullet
straight down every 0.55 s, its two barrels taking turns, so the two booms draw two parallel streams
down the screen as it sways; the dorsal turret fires bursts of 3 red bullets at the player. The
core fires:
- stage 0: an aimed blue bullet;
- stage 1: an aimed spread of 3, 8° apart;
- stage 2: a fan of 5 gold bullets, 12° apart, straight down (a sweep);
- stage 3 (all three parts gone): a ring of 12 from the tail rotor, turning 8° at each volley (a
  spiral), and an aimed pair of red bullets.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys; each shot leaves a barrel (a fight in
  the simulation).

*Sources: BOSS-21, BOSS-23, BOSS-58.*

#### MB-TWIN-BOOM-LANCER-09 — Angry · MUST

After its transformation it is angry (BOSS-27): its two cannons fire all out for
`boss_rage_seconds`. It has no angry pattern of its own.

**Acceptance criteria**
- Given its transformation is over, then it is angry and fires only its two cannons.

*Sources: BOSS-27.*

#### MB-TWIN-BOOM-LANCER-10 — Transformation: two booms become one gun · MUST

It transforms once, when both boom guns are destroyed (`transformParts`, BOSS-36). As a staged
event over the transformation's 2 s (shares of it):
1. 0–0.15: the booms strain (BOSS-45);
2. 0.04–0.3: the tailplane splits on the centre line and each half folds up about its root on its
   boom's inner side, standing upright;
3. 0.15–0.6: the booms slide in and forward, under the pod, until they lie side by side (`LOCK`),
   their outer wing panels and fins riding with them; the inner wings telescope, the middle sleeves
   sliding in under the outer ones and under the pod;
4. 0.45–0.68: each cowling's top and outer petals peel open forward about their back edges, as the
   heavy breech block of a **cannon** rises out of the engine (0.4–0.75), its turret sliding out of
   it (0.7–1);
5. 0.58–0.72: latches shoot out of the booms' inner sides across the seam and lock them together;
6. 0.62–0.85: radiator blades rise out of the merged tail: with the fins and the folded tailplane
   they make a crest of cooling fins.

The two booms have become one long double gun body under the pod, its two cannons out ahead of the
pod's nose. From then on the fight changes character: instead of two thin streams to slip between,
the cannons sweep aimed spreads of 3 large, slow shells, 12° apart, at the player (every 2.4 s,
staggered): heavy, concentrated fire to dodge round. The cannons shield the core.

**Acceptance criteria**
- Given both boom guns destroyed, then it transforms, its booms slide in and its two cannons are
  revealed on them.
- Manual validation: the morph reads as the two booms becoming one gun.

*Sources: BOSS-35, BOSS-36, BOSS-40, BOSS-45, user request (2026-11-06, "pieces morphing into
something else").*

#### MB-TWIN-BOOM-LANCER-11 — Death, drops and points · MUST

Its parts drop a weapon bonus half of the time, its cannons 30 %; it drops a life bonus as a mini
boss (BOSS-57). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/twin_boom_lancer.py` (`_TWIN_BOOM_LANCER`, `TWIN_BOOM_LANCER`);
its model in `src/game/view/bosses/lab/twin_boom_lancer_model.py`, its rig in
`twin_boom_lancer_rig.py`.

| Name | Value | Notes |
|------|-------|-------|
| size | 3.6 L (radius 61.2 px) | `stats.size` |
| pod | from y -46 to 26, 10 px half wide at most, 15 to 33 px high | `POD` |
| booms | axis at X ±30, 12 px high, radius 6; from y -47 to 56 | `BOOM_X`, `BOOM_H`, `BOOM_R`, `BOOM_ENDS` |
| cowlings | y -47 to -30, radius 8 | `COWL`, `COWL_R` |
| wing | chord -18 to -3 at the root, -15 to -6 at the tip, tips at X ±64, 12.6–15.6 px high | `WING_ROOT`, `WING_TIP`, `WING_SPAN`, `WING_Y` |
| tailplane / fins | chord 42–52, 14.6 px high / chord 38–55, tops 31 px high | `TAILPLANE`, `FIN` |
| booms' slide | (∓22, -16) px, mirrored | `LOCK`, `BOOM_SLIDE`; `moving_region` `boom` |
| core | health 1 200, radius 14 | |
| `boom-left` / `boom-right` | (∓30, -22), radius 9, health 640, shield, drop 0.5 | on the booms |
| `dorsal` | (0, -6), radius 10, health 720, shield, drop 0.5 | collar 31.3–34.5 px |
| boom guns | fixed, 21 px high; 2 barrels 2.8 px apart, bore 1, 11 px long; dome radius 4 | `BOOM_GUN` |
| dorsal turret | 34.5 px high; 3 barrels, bore 1.1, 7.5 px long; dome radius 4.8 | `DORSAL_GUN` |
| nose gun (core) | (0, -37), 29.5 px high; 2 barrels, bore 1, 7 px long; dome radius 4.2 | `NOSE_GUN` |
| tail rotor (core) | (0, 13), 30.5 px high; 12 barrels, bore 0.75, 3.2 px long | `ROTOR` |
| rotor hatch | octagon of radius 5.6 round (0, 13) | `armour_region` `rotor-hatch` (`mount`) |
| cannons | (∓8, -55) once locked (drawn at (∓30, -39) on the booms), radius 7, health 580, pod 17–20 px; first 1.2 s / 2.0 s | `hidden_weapon` `cannon`, ride the booms |
| rig timing | tailplane 0.04–0.3, petals 0.45–0.68 (open 2.0 and 1.75 rad), latches 0.58–0.72 (3.2 px), radiator 0.62–0.85 (7.5 px) | `twin_boom_lancer_rig` |
| full health | 4 360 (core 1 200, parts 2 000, cannons 1 160) | BOSS-54 |
| points | 4 300 | |
| ground speed | ×1.2 | |
| stop height | 0.74 | `stopFraction` |
| sway / bob | 66 px over 6.4 s / 8 px over 3 s | strafing |
| boom streams | 1 bullet straight down, orange 200 px/s, every 0.55 s (first 0.6 s / 0.85 s) | fixed guns, barrels in turn |
| dorsal bursts | 3, 0.13 s apart, red 190 px/s, every 2.4 s (first 1.4 s) | |
| core stage 0 | aimed 1, blue 180 px/s, every 2.8 s | nose gun |
| core stage 1 | aimed 3, 8° apart, every 2.4 s | nose gun |
| core stage 2 | fan of 5, 12° apart, straight down, gold 175 px/s, every 2.4 s | nose gun (a sweep) |
| core stage 3 | ring of 12 turning 8°, blue, every 1.6 s; aimed 2, 6° apart, red, every 2.6 s | rotor; nose gun |
| weighted fire rate | 5.24 as it comes in, 5.83 after its transformation | BOSS-39 |
| transformation | once both boom guns are destroyed | `transformParts` |
| neon | gold (1, 0.85, 0.2), shown yellow | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time and its place in a
  world's health order (BOSS-55, BOSS-56) are not set. Its health is about that of the 1-3 mini boss
  level (the Lab's L-3, L-8 and L-13 minis: 4 150 to 4 380).
- **Not a creature** (see the top): BOSS-47's creature look does not apply; BOSS-48 to BOSS-53 do.
- **Its morph** (round 4 asks for pieces turning into something else): the booms' slide is a moving
  region (BOSS-45) carrying the cannons in; the rest of the choreography (the petals, the tailplane,
  the sleeves, the latches, the radiator blades) is a view rig that follows the booms. No engine
  change was needed.
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-06): 512 shots, every one from
  a barrel, along it; it dies at about 74 s.
