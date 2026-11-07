# Swing-Wing Titan

> **Area:** bosses · **Prefix:** `FB-SWING-WING-TITAN` · **Related:** [common](../common.md),
> [Twin-Boom Lancer](L-18-twin-boom-lancer.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Swing-Wing Titan is the final boss of Lab level L-18: a gigantic variable-geometry bomber seen
from above. A long blended fuselage, big wing gloves either side of it, its swing wings spread wide,
four engines in two pods under its rear, and a cruciform tail: a tall fin, its tailplanes set across
it half way up. Spread, it crosses the screen with fans from its wing guns. At its first
transformation its **wings sweep fully back** and its **gloves unfold into weapons decks**: their
bay doors swing open, racks of feed tubes rise and a **battery** rises out of each, walls of fans
straight down. At its second its **tail splits into a rotor**: its dorsal fairing flips open on two
missile **racks**, its tailplanes swing round under the fin, the fin splits into its two skins that
fold out flat, and the four blades spin up round an **orb** rising on the hub: the tail has become a
spinning gun ring. Shared rules are in [common](../common.md).

**Not a creature.** BOSS-47 asks for a Cyber-Organic creature; this Lab boss departs from it on the
user's requests (2026-11-06, "drop the animal looking theme"; "10 more gigantic airplanes but be
really creative on the transformation, not just rotate a part, like pieces morphing into something
else"): it is a built aircraft of dark metal plating, glass, engines and neon light lines, with no
flesh, eyes or limbs.

## Requirements

### Look

#### FB-SWING-WING-TITAN-01 — Silhouette and size · MUST

Seen from above it is a swing-wing bomber about 196 px across its wing tips and 196 px long, its
nose down the screen: a long narrow fuselage, the big triangular gloves at its shoulders, the long
straight wings spread almost square to it, the engine pods under its rear and the cruciform tail.
Once its wings have swept it is an arrowhead, its wings folded back alongside its rear; once its
tail has split, a four-bladed rotor turns at its tail.

**Acceptance criteria**
- Manual validation in the boss viewer: a swing-wing bomber unlike any other boss, its silhouette
  changing at each transformation.

*Sources: Lab boss request (2026-11-06, "gigantic airplanes").*

#### FB-SWING-WING-TITAN-02 — Fuselage, gloves, engines and tail · MUST

The fuselage (`FUSELAGE` stations) is a blended body, its cockpit glass painted behind the nose,
light lines down its spine and shoulders, dark panel lines across it, the seats of the nose radome,
the spine turret and the spine rotor on its back. Each glove (`GLOVE`, `GLOVE_Y`) is a solid
blended body with a lit leading edge, the swing wing's pivot drum on it (`PIVOT`), vents on its aft
skin and a bay in it (`BAY`, floor `BAY_FLOOR`) under two doors. Each engine pod (`ENGINE_X`,
`ENGINE_H`, `ENGINE_R`, `ENGINES`) is two nacelles joined by a fairing, dark lit intakes, glowing
nozzles, and the barbette's pylon on its tail. The tail is the fin's root stub on the tail cone (the
core's), the fin's two skins over it, the tailplanes across it (`HUB`, `FIN`, `FIN_TOP`,
`FIN_TIP`, `TAILPLANE_*`) and the hub where they cross; the dorsal fairing (`FAIRING`,
`FAIRING_HALF`) ahead of the fin is four flaps.

**Acceptance criteria**
- Manual validation: one aircraft, holding together at rest and after each transformation.

*Sources: BOSS-49, BOSS-52, user request (2026-11-06).*

#### FB-SWING-WING-TITAN-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Wing guns** (`wing-left`, `wing-right`), on the spread wings: an armoured octagonal barbette,
  lit, a twin-barrelled turret on it (its fans).
- **Barbettes** (`barbette-left`, `barbette-right`), on the engine pods' tails: an armoured drum,
  lit, a twin-barrelled turret on it (its bursts).
- **Nose radome** (`nose`): an armoured cupola, lit, a laser turret on it (its tracking laser).
- **Spine gun** (the core's): three barrels side by side on a turret (its aimed shots, spreads,
  bursts and fans).
- **Spine rotor** (the core's): fourteen barrels round a hub (its last spiral). Until its last stage
  it lies under an octagonal hatch with a seam of light round it; as the rotor comes into use the
  hatch bursts off (BOSS-58), leaving a collar, and the rotor rises out.
- **Batteries** (`battery-left`, `battery-right`), revealed at the first transformation: a long low
  deck, lit along its front, five barrels side by side on its turret.
- **Orb** (`orb`), revealed at the second on the rotor's hub: an armoured collar, lit, ten barrels
  round its rotor.
- **Racks** (`rack-left`, `rack-right`), revealed at the second under the dorsal fairing: a pod, four
  missile ports on it.

A destroyed part's stump stands on its seat: a wing gun's on its pedestal on the wing (it moves with
it), a barbette's on its pylon, the orb's on the hub's spindle.

**Acceptance criteria**
- Given its model, then it draws its five parts, its hidden weapons and every gun mount.

*Sources: BOSS-18, BOSS-40, BOSS-48, BOSS-58.*

#### FB-SWING-WING-TITAN-04 — Lights · MUST

Its lights take its neon colour, rose, shown bright yellow (BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright yellow.

*Sources: BOSS-50.*

#### FB-SWING-WING-TITAN-05 — Moving pieces and rig · MUST

Each swing wing is a moving piece (`wing-right` and its mirror image `wing-left`, BOSS-45) that
swings `SWEEP` (58°) back about its pivot as it first transforms. The gloves' bays and the dorsal
fairing are shed regions (`glove-bay`, `tail-split`): their seams and latches burst off and leave
the bays' frames (their own drawings). The bays' doors and feed tubes, the fairing's flaps and the
tail's rotor (the hub, the fin's two skins, the tailplanes) are its view rig (`drawing.rig`, no hit
circle or muzzle on them). The spine rotor's hatch is a shed region of its own (BOSS-58).

**Acceptance criteria**
- Given its design, then its first transformation moves both wings and sheds the bays, its second
  sheds the tail's fairing (unit tests).
- Given its model, then it holds together at rest and after each transformation (BOSS-52).

*Sources: BOSS-42, BOSS-45, BOSS-52.*

### Behaviour

#### FB-SWING-WING-TITAN-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then sways slowly
and wide and bobs gently, a heavy bomber. While it is fought the ground scrolls at ×0.6.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.6 of the level's speed and back after it.

*Sources: BOSS-03, BOSS-10.*

#### FB-SWING-WING-TITAN-07 — Parts and core · MUST

It has five parts as it comes in, all shielding its core: `wing-left`, `wing-right`,
`barbette-left`, `barbette-right` and `nose`. The core's guns (the spine gun and the spine rotor)
fire the core's volleys and are the last the player destroys.

**Acceptance criteria**
- Given its design, then its five parts all shield the core.

*Sources: BOSS-12, BOSS-14.*

#### FB-SWING-WING-TITAN-08 — Stage patterns: the crossfire · MUST

Spread, it fights wide: in every stage while they stand, each wing gun sweeps fans of 5 orange
bullets, 10° apart, slanting 14° in towards the centre line (the two fans cross under it), the
barbettes fire bursts of 3 red bullets at the player and the nose radome fires its tracking laser
(1.4 s every 7.5 s). The core fires:
- stage 0: an aimed rose bullet;
- stage 1: an aimed spread of 3, 8° apart;
- stage 2: a fan of 5 gold bullets, 12° apart, straight down;
- stage 3: a burst of 4 red bullets and a fan of 3;
- stage 4: a fan of 7, 12° apart, and an aimed red bullet;
- stage 5 (all five parts gone): a ring of 14 from the spine rotor, turning 9° at each volley (a
  spiral), and a fan of 5.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys; each shot leaves a barrel or lens (a
  fight in the simulation).

*Sources: BOSS-21, BOSS-23, BOSS-58.*

#### FB-SWING-WING-TITAN-09 — Angry · MUST

After each transformation it is angry (BOSS-27): the weapons it revealed fire all out for
`boss_rage_seconds` (the batteries, then the orb and the racks). It has no angry pattern of its own.

**Acceptance criteria**
- Given a transformation is over, then it is angry and fires only the weapons it revealed.

*Sources: BOSS-27.*

#### FB-SWING-WING-TITAN-10 — First transformation: the gloves become weapons decks · MUST

It first transforms when both wing guns are destroyed (`transformParts`, BOSS-36). As a staged
event over the transformation's 2 s (shares of it):
1. 0–0.15: the wings strain, the bays' seams strobe; at 0.15 the seams and the doors' latches burst
   off;
2. 0.15–0.6: the wings sweep 58° back about their pivots in the gloves, folding alongside the rear
   fuselage over the engine pods;
3. 0.16–0.42: each bay's doors swing open, the fore one up and forward, the aft one up and back,
   standing either end of the bay;
4. 0.32–0.6: two racks of feed tubes rise out of each bay, fore and aft;
5. 0.4–1: a **battery** deck rises out of each bay's floor between them, its five-barrelled turret
   sliding out (0.7–1).

The glove has become a weapons deck. From then on the fight changes character: the crossfire from
the wing tips is gone, and the two batteries sweep fans of 7 orange bullets, 9° apart, straight
down (every 2 s, staggered) from close to its centre line: walls of bullets to weave through.

**Acceptance criteria**
- Given both wing guns destroyed, then it transforms, its wings sweep back and its two batteries are
  revealed.
- Manual validation: the gloves read as unfolding into weapons decks.

*Sources: BOSS-35, BOSS-36, BOSS-40, BOSS-42, BOSS-45, user request (2026-11-06).*

#### FB-SWING-WING-TITAN-11 — Second transformation: the tail becomes a rotor · MUST

It transforms again when both barbettes are destroyed (`transformParts`). As a staged event:
1. 0–0.15: the tail strains, the fairing's seams strobe; at 0.15 its seams and latches burst off;
2. 0.15–0.4: the dorsal fairing's four flaps flip open, the fore ones forward onto the spine, the
   aft ones back onto the tail cone, over two missile **racks** rising out of it (0.4–1);
3. 0.15–0.42: the tailplanes swing a quarter turn round the hub, under the fin;
4. 0.32–0.58: the fin splits into its two skins, which fold out flat either side about its root:
   with the tailplanes they make a cross of four blades round the hub;
5. from 0.55: the cross spins up into a rotor (1.7 rad/s), and keeps turning; the **orb** rises out
   of the hub (0.4–1), its ten barrels round its rotor.

The tail has become a spinning gun ring. From then on the fight changes character again: the orb
fires rings of 10 magenta bullets (every 2.6 s) and the racks pairs of homing missiles (every 6 s,
staggered), so the player circles round the radial waves while shaking off the missiles.

**Acceptance criteria**
- Given both barbettes destroyed, then it transforms again and its orb and two racks are revealed.
- Manual validation: the tail reads as splitting and folding out into a spinning rotor.

*Sources: BOSS-35, BOSS-36, BOSS-40, BOSS-41, BOSS-42, user request (2026-11-06).*

#### FB-SWING-WING-TITAN-12 — Health · MUST

Its full health is about that of the 1-3 final boss (Mesa Fortress, 15 000): see Tunable values.

**Acceptance criteria**
- Given its design, then its full health is that of Tunable values.

*Sources: BOSS-54, Lab boss request (2026-11-06).*

#### FB-SWING-WING-TITAN-13 — Death, drops and points · MUST

Its parts drop a weapon bonus 60 % of the time, its hidden weapons 30 %, its core always (BOSS-57).
It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/swing_wing_titan.py` (`_SWING_WING_TITAN`, `SWING_WING_TITAN`);
its model in `src/game/view/bosses/lab/swing_wing_titan_model.py`, its rig in
`swing_wing_titan_rig.py`.

| Name | Value | Notes |
|------|-------|-------|
| size | 5.8 L (radius 98.6 px) | `stats.size` |
| fuselage | from y -106 to 90, 12.5 px half wide at most, up to 26 px high | `FUSELAGE` |
| gloves | (10, -78), (17, -62), (34, -18), (36, 10), (11, 12), 13.5–21.6 px high | `GLOVE`, `GLOVE_Y` |
| bays | (11, -44), (22.8, -44), (32.2, -16), (11, -16), floor 19 px; doors hinged at y -44 and -16 | `BAY`, `BAY_FLOOR`, `BAY_DOORS` |
| wings | spread to X ±99, 12.4–15.4 px high; pivot (±28, 2) | `WING`, `WING_Y`, `PIVOT` |
| wings' sweep | 0° to 58° back about the vertical, mirrored | `SWEEP`, `WING_SWING`; `moving_region` `wing` |
| engines | nacelles at X ±15 and ±25, 6 px high, radius 4.4, y 20 to 54 | `ENGINE_X`, `ENGINE_H`, `ENGINE_R`, `ENGINES` |
| tail | fin chord 60–88 on the cone, top 62 px (chord 72–90); hub (0, 74), 34 px high; tailplanes 32 px long from X ±4.8, chord 66–82 to 72–80 | `FIN`, `FIN_TOP`, `FIN_TIP`, `HUB`, `TAILPLANE_*` |
| dorsal fairing | y 46 to 62, 13 px half wide | `FAIRING`, `FAIRING_HALF` |
| core | health 3 000, radius 18, drop 1 | |
| `wing-left` / `wing-right` | (∓68, 4), radius 11, health 1 100, shield, drop 0.6 | on the wings |
| `barbette-left` / `barbette-right` | (∓20, 46), radius 9, health 1 050, shield, drop 0.6 | on the engine pods |
| `nose` | (0, -80), radius 10, health 1 400, shield, drop 0.6 | |
| wing guns | 18 px high; 2 barrels 3 px apart, bore 1.1, 8 px long; dome radius 4.6 | `WING_GUN` |
| barbette guns | 14.5 px high; 2 barrels 2.8 px apart, bore 1, 7 px long; dome radius 4.2 | `BARBETTE_GUN` |
| nose laser | 24.6 px high, on a turret; bore 1.8, 9 px long | `NOSE_LASER` |
| spine gun (core) | (0, -40), 26 px high; 3 barrels, bore 1.2, 8 px long; dome radius 5.4 | `SPINE_GUN` |
| spine rotor (core) | (0, 24), 26 px high; 14 barrels, bore 0.75, 3.6 px long | `ROTOR` |
| rotor hatch | octagon of radius 6.4 round (0, 24) | `armour_region` `rotor-hatch` (`mount`) |
| batteries | (∓19, -28), radius 8, health 1 120, pod 19–21.4 px; first 1.2 s / 2.0 s | `hidden_weapon` `battery`, in `glove-bay` |
| orb | (0, 74), radius 9, health 1 400, pod 34–36.4 px; first 1.0 s | `hidden_weapon` `orb`, in `tail-split` |
| racks | (∓8, 54), radius 7, health 1 400, pod 25–27 px; first 1.4 s / 2.4 s | `hidden_weapon` `rack`, in `tail-split` |
| rig timing | doors 0.16–0.42 (2.0 rad), tubes 0.32–0.6 (7.5 px); flaps 0.15–0.4 (3.0 rad), tailplanes 0.15–0.42 (a quarter turn), skins 0.32–0.58 (a quarter turn), spin-up 0.55–1 to 1.7 rad/s | `swing_wing_titan_rig` |
| full health | 15 140 (core 3 000, parts 5 700, batteries 2 240, orb and racks 4 200) | BOSS-54 |
| points | 11 000 | |
| ground speed | ×0.6 | |
| stop height | 0.68 | `stopFraction` |
| sway / bob | 30 px over 11 s / 5 px over 5.5 s | |
| wing fans | 5, 10° apart, 14° in towards the centre line, orange 180 px/s, every 2.8 s (first 1.0 s / 2.4 s) | sweeps |
| barbette bursts | 3, 0.14 s apart, red 190 px/s, every 2.6 s (first 1.6 s / 2.9 s) | |
| nose laser | 1.4 s every 7.5 s (first 3.5 s) | tracking turret |
| core stage 0 | aimed 1, rose (magenta) 175 px/s, every 2.8 s | spine gun |
| core stage 1 | aimed 3, 8° apart, every 2.6 s | spine gun |
| core stage 2 | fan of 5, 12° apart, gold 165 px/s, every 2.6 s | spine gun |
| core stage 3 | burst of 4, red, every 2.4 s; fan of 3, every 3 s | spine gun |
| core stage 4 | fan of 7, every 2.4 s; aimed 1, red, every 2.8 s | spine gun |
| core stage 5 | ring of 14 turning 9°, rose, every 1.4 s; fan of 5, every 2.8 s | rotor; spine gun |
| weighted fire rate | 7.3 as it comes in, 12.3 after its first transformation, 16.5 after its second | BOSS-39 |
| transformations | once both wing guns, then both barbettes are destroyed | `transformParts` |
| neon | rose (1, 0.25, 0.55), shown yellow | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time and its place in a
  world's health order (BOSS-55, BOSS-56) are not set. Its full health is about that of the 1-3
  final boss (Mesa Fortress, 15 000), as asked.
- **Not a creature** (see the top): BOSS-47's creature look does not apply; BOSS-48 to BOSS-53 do.
- **Its morphs** (round 4 asks for pieces turning into something else): the wings' sweep is a moving
  region (BOSS-45); the bays and the tail's fairing are shed regions whose drawn armour is only
  their seams and latches (what bursts), their doors and flaps being the rig, so they swing open
  instead of bursting; the rotor is a view rig. The hidden weapons rise straight out (`mount`
  `[0, 0, 0]`: no fold) so they come up out of the decks and the hub. No engine change was needed.
- **The rotor's blades are looks only**: no hit circle or muzzle is on them; the orb (a part) sits
  on the hub, not on the blades, and does not turn with them.
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-06): 1 670 shots and 5
  lasers, every one from a barrel or lens, along it; it dies at about 134 s (the Mesa Fortress:
  122 s).
