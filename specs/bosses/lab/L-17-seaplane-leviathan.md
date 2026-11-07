# Seaplane Leviathan

> **Area:** bosses · **Prefix:** `FB-SEAPLANE-LEVIATHAN` · **Related:** [common](../common.md),
> [Aegis Wing](L-17-aegis-wing.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Seaplane Leviathan is the final boss of Lab level L-17: a gigantic flying boat. A deep boat
hull runs down its middle, a high gull wing crosses it on a pylon, three radial engines turn their
propellers on each wing, a float hangs on struts under each wingtip and a tall fin rises at its
stern. It fights first as a gunship. At its first transformation its **floats morph into mortars**:
each float is pulled up under the wing, swings over the leading edge onto the wingtip and splits
open along its keel into the mortar's cradle. At its second its **bow splits open into a hangar**,
the bow doors swinging apart and a launch deck sliding out over the bow, and its inner engines'
**propeller hubs morph into sweepers**: the propellers stop and retract, the spinners pitch up and
peel open, and a sweeping laser rises out of each. Shared rules are in [common](../common.md).

**Not a creature.** BOSS-47 asks for a Cyber-Organic creature; this Lab boss departs from it on the
user's requests (2026-11-06, "drop the animal looking theme"; "10 more gigantic airplanes but be
really creative on the transformation, not just rotate a part, like pieces morphing into something
else"): it is a built aircraft of dark metal, plating, propellers and neon light lines, with no
flesh, eyes or limbs.

## Requirements

### Look

#### FB-SEAPLANE-LEVIATHAN-01 — Silhouette and size · MUST

Seen from above it is a flying boat 188 px (5.5 L) across its wingtips and 158 px from its bow to
its stern, its bow down the screen: a long boat hull crossed by a straight wing with three engine
nacelles jutting ahead of each half, a float under each tip, a tailplane across its stern. No other
boss is a flying boat.

**Acceptance criteria**
- Manual validation in the boss viewer: a flying boat, its hull, gull wing, engines, floats and
  tail readable.

*Sources: Lab boss request (2026-11-06, gigantic airplanes).*

#### FB-SEAPLANE-LEVIATHAN-02 — Hull, wing, engines and tail · MUST

The hull is a deep boat: its keel the whole length with a V bottom up to the hangar's floor, its
upper hull over it with a flat deck, a lit chine and lit portholes down its sides, the cockpit's
glazing across the deck behind the bow, a walkway down the deck. A streamlined pylon on its back
carries the wing: gull wing inner panels rise from the pylon to a kink 26 px out, the outer panels
run flat to rounded tips, lit along their leading edges, dark aileron seams along their trailing
edges, a lit light at each tip. Three radial engines sit on each outer panel: a tapered nacelle
along the chord, a round cowling at its front with a lit lip, the radial's cylinder heads in a ring
inside it, an exhaust ring behind. At the stern a tall fin stands on the deck, a lit stripe up its
rudder, its tailplane across it high up, lit along its tips.

**Acceptance criteria**
- Manual validation: one flying boat, readable from above and tilted.

*Sources: BOSS-49, user request (2026-11-06).*

#### FB-SEAPLANE-LEVIATHAN-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Wing guns** (`wing-gun-left`, `wing-gun-right`): an armoured octagonal blister on each gull
  panel, lit round its rim, cheek plates ahead of it, round a twin-barrelled turret (its aimed
  pairs).
- **Nose turret** (`nose-turret`): an armoured drum on the bow's deck, lit round its rim, splinter
  plates round its front, a lit chevron ahead, round a three-barrelled turret (its bursts).
- **Tail turret** (`tail-turret`): an octagonal turret ring on the stern behind the fin, round a
  twin-barrelled turret (its fans).
- **Dorsal laser** (`dorsal-laser`): a low glazed dome on the deck ahead of the wing, a lit window
  band, round a laser turret that follows the player (its tracking laser).
- **Dorsal turret** (the core's, on the pylon's top): two barrels side by side.
- **Stern rotor** (the core's, on the deck behind the wing): fourteen barrels round a hub (its last
  spiral). Until its last stage it lies under an octagonal hatch with a lit seam; as the rotor comes
  into use the hatch bursts off (BOSS-58), leaving a collar, and the rotor rises out.

A destroyed wing gun leaves its stump on its plinth on the gull panel, the tail turret's and the
dorsal laser's on their plinths on the deck, the nose turret's on its plinth on the right bow door
(it rides the door as it swings).

**Acceptance criteria**
- Given its model, then it draws its five parts and every gun mount.

*Sources: BOSS-18, BOSS-48, BOSS-58.*

#### FB-SEAPLANE-LEVIATHAN-04 — Lights · MUST

The chine, portholes and cockpit glazing, the hangar's lane lights and doorframe, the wing's
leading edges and tip lights, the cowlings' lips, the propellers' blade tips, the fin's and
tailplane's stripes, the floats' seams and portholes, the guns' rims and the launch deck's lanes
glow. Its neon colour, set sea blue, shows bright green (BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright green.

*Sources: BOSS-50.*

#### FB-SEAPLANE-LEVIATHAN-05 — Its propellers (a view rig) · MUST

Each engine turns a three-bladed propeller ahead of its cowling, the blades' tips lit, a spinner
on the hub, at 14 rad/s all the time (the left and right engines the opposite ways). The inner
engines' propellers and spinners morph at the second transformation (FB-SEAPLANE-LEVIATHAN-10).
The propellers are drawn only: no part, no muzzle, nothing the player can hit or that fires.

**Acceptance criteria**
- Manual validation: the propellers spin.
- Given its model at rest and after its transformations, then it holds together (unit test).

*Sources: user request (2026-11-06), BOSS-52.*

### Behaviour

#### FB-SEAPLANE-LEVIATHAN-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then sways slowly
and briefly and bobs: a huge, heavy flying boat. While it is fought the ground scrolls at ×0.8.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.8 of the level's speed and back after it.

*Sources: BOSS-03, BOSS-10.*

#### FB-SEAPLANE-LEVIATHAN-07 — Parts and core · MUST

It has five parts as it comes in, all shielding its core: `wing-gun-left`, `wing-gun-right`,
`nose-turret`, `tail-turret` and `dorsal-laser`. The core's guns (the dorsal turret and the stern
rotor) fire the core's volleys and are the last the player destroys.

**Acceptance criteria**
- Given its design, then its five parts all shield the core.

*Sources: BOSS-12, BOSS-13, BOSS-14.*

#### FB-SEAPLANE-LEVIATHAN-08 — Stage patterns · MUST

In every stage while they stand, each wing gun sweeps an aimed pair of red bullets 6° apart, the
nose turret fires bursts of 3 orange bullets, the tail turret sweeps a fan of 5 blue bullets 10°
apart straight down, and the dorsal laser fires its tracking laser (1.4 s, every 7.5 s). The core
fires:
- stage 0: an aimed bullet;
- stage 1: an aimed spread of 3, 8° apart;
- stage 2: a fan of 5, 12° apart, straight down;
- stage 3: bursts of 4 red bullets at the player;
- stage 4: a fan of 7, 12° apart, and an aimed red bullet;
- stage 5 (all five parts gone): a ring of 14 from the stern rotor, turning 9° at each volley (a
  spiral), and a fan of 5.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys; each shot leaves a barrel (a fight in
  the simulation).

*Sources: BOSS-21, BOSS-23, BOSS-58.*

#### FB-SEAPLANE-LEVIATHAN-09 — First transformation: the floats morph into mortars · MUST

It transforms the first time when both wing guns are destroyed (named). The floats at rest are an
armour region (`floats`) that leaves no pieces as it bursts: its view rig takes over in the same
pose. As one staged event (shares of `boss_transform_seconds`):
- until 0.15 the floats strain (BOSS-43), shuddering and strobing;
- 0.15–0.27: each float's two struts **telescope in**, pulling it up snug under the wingtip;
- 0.25–0.43: the float **swings forward over the leading edge**, half a turn about it, landing keel
  up on the wingtip, its front half reaching out ahead of the wing;
- 0.42–0.6: its hull **splits open along the keel**, the two halves folding out 1 rad either side
  like open jaws, their lit inner seams showing, the float's deck between them: the float has
  become the mortar's cradle;
- a **mortar** rises out of the cradle (from 0.4, BOSS-43): a squat turret with one short, wide
  barrel on a round base, firing flak shells that burst into rings of 8. They shield the core.

The fight changes character: from a gunship's aimed fire to artillery, slow shells to read and
rings of flak to dodge.

**Acceptance criteria**
- Given both wing guns destroyed, then it transforms, its floats region is shed and its two
  mortars are revealed on the wingtips (unit tests on the design).
- Manual validation in the boss viewer: the floats rise, swing over and split open into the
  mortars.

*Sources: BOSS-35, BOSS-36, BOSS-42, BOSS-46, user request (2026-11-06).*

#### FB-SEAPLANE-LEVIATHAN-10 — Second transformation: the bow becomes a hangar, the hubs sweepers · MUST

It transforms the second time when its nose and tail turrets are destroyed (named). As one staged
event:
- the upper bow **splits open along the keel**: its two halves are bow doors that swing out about
  their after outer corners, 68° each (it changes shape, BOSS-45: two moving regions, between
  `reveal.move`), opening the hangar over the lower hull's lit floor and the lit doorframe at its
  back;
- a **hangar** rises on the bay's floor on the centre line (from 0.4), its doors sliding apart: it
  launches Hornets; and from 0.45 to 0.8 the **launch deck** stowed in the keel slides 28 px out
  over the bow, its lanes lit;
- the inner engines' **propellers stop** (0.08–0.3) and their **blades retract** into the hub
  (0.25–0.4); each **spinner pitches up** onto its cowling (0.35–0.52), its four plates **peel
  open** into a crown (0.5–0.64), and a **sweeper** rises out of it (from 0.4): a laser on a
  turret whose beam sweeps after the player. They shield the core.

The fight changes character again: a carrier, Hornets diving at the player while two beams drag
across the screen after it; then the stern rotor's spiral.

**Acceptance criteria**
- Given its nose and tail turrets destroyed, then it transforms, its bow doors swing open, and its
  hangar and two sweepers are revealed (unit tests on the design).
- Manual validation in the boss viewer: the bow splits and opens on the hangar, the deck slides
  out, the propellers stop and the spinners open into the sweepers.

*Sources: BOSS-35, BOSS-36, BOSS-41, BOSS-45, user request (2026-11-06).*

#### FB-SEAPLANE-LEVIATHAN-11 — Angry · MUST

After each transformation it is angry (BOSS-27): the weapons that transformation revealed fire all
out for `boss_rage_seconds`. It has no angry pattern of its own.

**Acceptance criteria**
- Given a transformation is over, then it is angry and fires only the weapons it revealed.

*Sources: BOSS-27.*

#### FB-SEAPLANE-LEVIATHAN-12 — Never easier · MUST

Its weighted fire rate (BOSS-39) never goes down from one transformation to the next and ends
higher than as it comes in.

**Acceptance criteria**
- Given its design, then its weighted fire rates as it comes in and after each transformation go
  up (unit test).

*Sources: BOSS-39.*

#### FB-SEAPLANE-LEVIATHAN-13 — Death, drops and points · MUST

Its parts drop a weapon bonus 60 % of the time, its hidden weapons 30 %, its core always
(BOSS-57). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/seaplane_leviathan.py` (`_SEAPLANE_LEVIATHAN`,
`SEAPLANE_LEVIATHAN`); its model in `src/game/view/bosses/lab/seaplane_leviathan_model.py` and
`seaplane_leviathan_rig.py` (the propellers, floats, spinners and launch deck).

| Name | Value | Notes |
|------|-------|-------|
| size | 5.5 L | `stats.size` |
| hull | y -80..78, half width up to 13.5; keel 2, chine 13, deck 21 px high | `HULL`, `HULL_LOW`, `HULL_CHINE`, `DECK` |
| bow doors | the upper bow (8–21 px) forward of y -42, each swinging 68° about (±13.3, -42) | `BOW_END`, `BAY_FLOOR`, `DOOR_OPEN`; moving regions `bow-door-right`, `bow-door-left`, form 2 |
| pylon | y -20..16, 25 px high | `PYLON`, `PYLON_TOP` |
| wing | gull kink at x ±26; outer panels 29.5–33 px high to tips at ±94; leading edge y -16 → -13, trailing edge 11 → 6 | `KINK`, `WING_*`, `TIP`, `LEADING`, `TRAILING` |
| engines | x ±36, 54, 72; nacelles y -26..6, radius 4.8, axis 31 px high; propellers at y -27.5, blades 8.4 px, 14 rad/s | `ENGINES`, `NACELLE*`, `HUB_Y`, `PROP_RADIUS`; rig `SPIN` |
| floats | (±85, -24..6), half width 4.2, keel 15, deck 22 px; struts at y -14 and -2 | `FLOAT*`, `STRUTS`; region `floats`, form 1, `shell` frame (drawn: the struts' hinge blocks) |
| float morph | struts in 0.15–0.27, swing 0.25–0.43 about (±85, -13.3, 31.25), split 0.42–0.6, halves 1 rad open | rig `RISE`, `FLIP`, `SPLIT`, `PIVOT`, `SPLIT_OPEN` |
| spinner morph | stop 0.08–0.3, retract 0.25–0.4, pitch 0.35–0.52, peel 0.5–0.64 (1.3 rad) | rig `STOP`, `RETRACT`, `PITCH`, `PEEL`, `PEEL_OPEN` |
| launch deck | 10 × 30 px, from y -70 slid 28 px out, 0.45–0.8 | rig `DECK_*`, `LAUNCH` |
| tail | fin y 44..70 at its root, 56..68 at its 60 px top; tailplane y 54..66, ±26, 42 px high | `FIN*`, `TAILPLANE*` |
| core | health 2 200, radius 22, drop 1 | |
| `wing-gun-left`, `wing-gun-right` | (∓20, -2), radius 9, health 700, shield, drop 0.6 | |
| `nose-turret` | (0, -64), radius 9, health 780, shield, drop 0.6 | on the right bow door |
| `tail-turret` | (0, 72), radius 9, health 740, shield, drop 0.6 | |
| `dorsal-laser` | (0, -32), radius 9, health 820, shield, drop 0.6 | |
| wing guns | 32.6 px high; 2 barrels 3 px apart, bore 1.1, 7.5 px long; dome radius 4.4 | `WING_GUN` |
| nose turret | 22.6 px high; 3 barrels 2.9 px apart, bore 1.1, 8 px long; dome radius 4.8 | `NOSE_GUN` |
| tail turret | 22.4 px high; 2 barrels 2.8 px apart, bore 1, 7 px long | `TAIL_GUN` |
| dorsal laser | 24.4 px high; turret, bore 1.8, 9 px long | `LASER` |
| dorsal turret (core) | (0, 0), 25.6 px high; 2 barrels 3.2 px apart, bore 1.2, 8 px long | `DORSAL_GUN` |
| stern rotor (core) | (0, 30), 21.6 px high; 14 barrels, bore 0.75, 3.6 px long; hub radius 5 | `ROTOR` |
| rotor hatch | octagon of radius 6.2 round (0, 30) | `armour_region` `rotor-hatch` (`mount`) |
| mortars | (±85, -8) on the wingtips, radius 6, health 660, pod 33.6–36.4 px, orange; first 1.2 s / 2.0 s | on the rig (`look.rig`) |
| hangar | (0, -60) on the bay's floor, radius 9, health 820, pod 8–13 px; 2 Hornets every 7 s, first 1.6 s | in the bow doors |
| sweepers | (±36, -22) on the inner cowlings, radius 5, health 820, pod 36.2–38.4 px; first 1.2 s / 3.0 s | on the rig (`look.rig`) |
| full health | 9 720 (core 2 200, parts 3 740, mortars 1 320, hangar and sweepers 2 460) | BOSS-54 |
| points | 9 500 | |
| ground speed | ×0.8 | |
| stop height | 0.7 | `stopFraction` |
| sway / bob | 26 px over 11 s / 5 px over 5.5 s | |
| wing guns' pairs | aimed 2, 6° apart, red 190 px/s, every 2.2 s (first 0.8 s / 1.9 s) | sweeps |
| nose turret's bursts | 3, 0.12 s apart, orange 180 px/s, every 2.6 s (first 1.3 s) | |
| tail turret's fans | 5, 10° apart, blue 175 px/s, straight down, every 3 s (first 2.2 s) | sweeps |
| dorsal laser | 1.4 s, every 7.5 s (first 3.2 s) | tracking turret |
| core stage 0 | aimed 1, orange 175 px/s, every 2.8 s | dorsal turret |
| core stage 1 | aimed 3, 8° apart, every 2.6 s | |
| core stage 2 | fan of 5, 12° apart, every 2.4 s | |
| core stage 3 | burst of 4, 0.13 s apart, red, every 2.4 s | |
| core stage 4 | fan of 7, 12° apart, every 2.6 s; aimed 1, red, every 3 s | |
| core stage 5 | ring of 14 turning 9°, blue, every 1.4 s; fan of 5, every 2.8 s | rotor; dorsal turret |
| weighted fire rate | 6.1 as it comes in, 6.6 after its first transformation, 7.3 after its second | BOSS-39 |
| transformations | `wing-gun-left` and `wing-gun-right`; `nose-turret` and `tail-turret` | `transformParts` |
| neon | sea blue (0.1, 0.8, 1), shown green | `BOSS_LOOK.neon` |
| triangles | about 5 300 (core 2 740, parts 430, armour 830, rig 1 290), gun mounts apart | BOSS-53 (10 000) |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time and its place in a
  world's health order (BOSS-55, BOSS-56) are not set. Its full health (9 720) is the 1-2 final
  boss's (Gull Mothership, 9 740), as asked.
- **Not a creature** (see the top): BOSS-47's creature look does not apply; BOSS-48 to BOSS-53 do.
- **The morphs are the view's.** The sim knows the `floats` region (shed at the first
  transformation), the bow doors (two moving regions), and the mortars, hangar and sweepers. The
  floats' rise, swing and split, the propellers' stop and retraction, the spinners' pitch and peel
  and the launch deck's slide follow the boss's `form`, `transforming_into` and `transform` in the
  view rig. The mortars and sweepers are weapons on the rig (`look.rig`, as the Scorpion's tail
  cannon, D-228): they rise in place out of the opened float and spinner instead of unfolding from
  a region. No engine change was needed; an engine option for a region to hand over to a rig
  instead of bursting (no blasts) would make the floats' hand-over cleaner.
- **Hidden weapons.** Mortar (pair), hangar (centre line) and sweeper (pair): the round's only
  hangar.
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-06): 977 shots and 30
  lasers, every shot from a barrel, along it; it dies at about 134 s.
