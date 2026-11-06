# Stratoliner Colossus

> **Area:** bosses · **Prefix:** `FB-STRATOLINER-COLOSSUS` · **Related:** [common](../common.md),
> [Condor Lifter](L-16-condor-lifter.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Stratoliner Colossus is the final boss of Lab level L-16: a colossal six-engine swept-wing jet
bomber-airliner seen from above, about 5 L across. A long round fuselage with rows of lit windows
ends in a radome nose; its swept wings carry three podded engines each on pylons ahead of them,
flaps along their inner trailing edges, and its tail is a swept tailplane, a tall fin and a tail
gun. It fights as an airliner first, then **morphs twice**: its outer engine nacelles turn into
gatlings (their fans split, their cowlings peel back in petals, their cores telescope out into
barrels), then its flaps unfold into a second wing tier, biplane-style, carrying a pair of missile
racks, while its nose cone splits into the rails of a lance. Shared rules are in
[common](../common.md).

**Not a creature.** BOSS-47 asks for a Cyber-Organic creature; this Lab boss departs from it on the
user's requests (2026-11-06, "drop the animal looking theme"; "10 more gigantic airplanes"): it is a
built aircraft of dark metal, plating, engines and neon light lines, with no flesh, eyes or limbs.

## Requirements

### Look

#### FB-STRATOLINER-COLOSSUS-01 — Silhouette and size · MUST

Seen from above it is a swept-wing jet 172 px (5 L) across its wingtips and 166 px long, its nose
down the screen: a fuselage 19 px wide, wings swept back 35° to their tips, three engine pods hung
out ahead of each wing, a swept tailplane 68 px across. A six-engine jet, unlike any other boss
(the Storm Petrel is a straight-winged seaplane with two wing pods).

**Acceptance criteria**
- Manual validation in the boss viewer: a swept-wing six-engine jet at rest, with gatlings on its
  outer engines after its first transformation, a second wing tier and a lance between two rails
  after its second.

*Sources: Lab boss request (2026-11-06, gigantic airplanes).*

#### FB-STRATOLINER-COLOSSUS-02 — Fuselage, wings, engines and tail · MUST

The fuselage is a long round loft (14 facets, its belly and spine darker), a lit cheat line and a
row of lit windows down each flank, three lit cockpit windows each side just behind the radome, a
dark walkway along its spine. The radome (the nose cone, ahead of y -66) is drawn as two halves
(FB-STRATOLINER-COLOSSUS-11). The wings are one bevelled chevron through the fuselage, lit along
their leading edges between the engines, lit at their tips, dark ailerons outboard and a rivet line.
Each engine is a long nacelle (a lathe) on a pylon up to the wing, its front 7 px ahead of the
leading edge: intake lip (one segment in three lit), dark fan blades and a spinner at its front, a
lit band and a dark exhaust cone at its back, a lit stripe on its top. The outer ones' cowlings,
cores and fans are drawn apart (FB-STRATOLINER-COLOSSUS-05, -10). The flaps lie along the inner
trailing edges, dark with lit edges. The tailplane is a swept bevelled slab lit at its tips; the fin
a tall swept plate on the centre line, lit up its rudder and along its top.

**Acceptance criteria**
- Manual validation: one aircraft, its fuselage, wings, engines and tail readable from above.

*Sources: BOSS-49, user request (2026-11-06).*

#### FB-STRATOLINER-COLOSSUS-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Wing guns** (`wing-gun-left`, `wing-gun-right`): a lit octagonal barbette on each wing between
  its inner and middle engines, round a twin-barrelled turret (aimed pairs).
- **Outer nacelles** (`nacelle-left`, `nacelle-right`): a lit saddle on each outer nacelle's cowling,
  carrying a fixed mount of three barrels straight down (fans of three).
- **Tail gun** (`tail-gun`): a lit drum on the tail cone behind the fin, round a twin-barrelled
  turret (bursts).
- **Spine gun** (the core's, on the spine ahead of the wings): five barrels side by side (aimed
  shots, spreads, fans, bursts).
- **Spine rotor** (the core's, on the spine behind the wings): fourteen barrels round a hub (its
  last spirals). Until its last stage it lies under an octagonal hatch with a lit seam; as the rotor
  comes into use the hatch bursts off (BOSS-58), leaving a collar, and the rotor rises out.

A destroyed wing gun leaves its stump on the wing, the tail gun's on the tail cone. The outer
nacelles retire (BOSS-46): they leave no stump.

**Acceptance criteria**
- Given its model, then it draws its five parts and every gun mount.

*Sources: BOSS-18, BOSS-46, BOSS-48, BOSS-58.*

#### FB-STRATOLINER-COLOSSUS-04 — Lights · MUST

The cheat lines and windows, the cockpit windows, the leading edges and wingtips, the engines'
intake lips, bands and stripes, the outer cowlings' petals' seams (outside and in), the cores'
muzzles, the flaps' and second tier's edges, the struts' collars, the nose halves' cut faces, the
tailplane's tips, the fin's rudder stripe and top, the barbettes', saddles' and drums' rims glow,
in its neon colour, peach (1, 0.65, 0.3) (BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are peach.

*Sources: BOSS-50.*

#### FB-STRATOLINER-COLOSSUS-05 — Its morphing pieces (a view rig) · MUST

Its view rig (`stratoliner_colossus_rig.py`, on jointed pieces of `condor_lifter_joints.py`) draws
the pieces that morph, posed from the boss's `form`, `transforming_into` and `transform`:
- each outer engine's **cowling**, four petals (each a quarter of it, hinged 5 px behind the
  nacelle's middle, round its axis) and its **core** (a drum with three barrels, inside it);
- each **flap** as it lifts into the second tier, its folded **outer panel** and two **struts**;
- the **nose cone's two halves**.

At rest the petals and cores show; the flaps, panels, struts and nose halves show from the moment
their armour region gives way to them (its whole drawing draws them in place, with the rig's own
drawings). None of it is a part, a muzzle or anything the player can hit: the weapons they turn into
are its hidden weapons.

**Acceptance criteria**
- Manual validation: the pieces morph as FB-STRATOLINER-COLOSSUS-10 and -11 say.
- Given its model at rest and after each transformation, then it holds together (unit test).

*Sources: user request (2026-11-06, "pieces morphing into something else"), BOSS-52.*

### Behaviour

#### FB-STRATOLINER-COLOSSUS-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then sways slowly
and bobs: a huge airliner. While it is fought the ground scrolls at ×1.2.

**Acceptance criteria**
- Given the fight, then the ground eases to ×1.2 of the level's speed and back after it.

*Sources: BOSS-03, BOSS-10.*

#### FB-STRATOLINER-COLOSSUS-07 — Parts and core · MUST

It has five parts as it comes in, all shielding its core: `wing-gun-left`, `wing-gun-right`,
`nacelle-left`, `nacelle-right` (they retire at its first transformation, BOSS-46) and `tail-gun`.
The core's guns (the spine gun and the spine rotor) fire the core's volleys and are the last the
player destroys.

**Acceptance criteria**
- Given its design, then its five parts all shield the core, and the outer nacelles retire at its
  first transformation.

*Sources: BOSS-12, BOSS-13, BOSS-14, BOSS-46.*

#### FB-STRATOLINER-COLOSSUS-08 — Stage patterns · MUST

In every stage while they stand, each wing gun sweeps an aimed pair of red bullets 6° apart (the two
in turn), each outer nacelle fires a fan of three orange bullets straight down (two streams far out
on the wings), and the tail gun fires bursts of 3 magenta bullets. The core fires:
- stage 0: an aimed purple bullet;
- stage 1: an aimed spread of 3, 9° apart;
- stage 2: a fan of 5 orange bullets, 12° apart, straight down;
- stage 3: a fan of 3, 12° apart, and an aimed pair 8° apart;
- stage 4: a fan of 5 purple and a burst of 3 red;
- stage 5 (as many parts lost as it came in with): a ring of 14 from the spine rotor, turning 8° at
  each volley (a spiral), and a fan of 5.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys; each shot leaves a barrel (a fight in
  the simulation).

*Sources: BOSS-21, BOSS-23, BOSS-58.*

#### FB-STRATOLINER-COLOSSUS-09 — Angry · MUST

After each transformation it is angry (BOSS-27): the weapons that transformation revealed fire all
out for `boss_rage_seconds`. It has no angry pattern of its own.

**Acceptance criteria**
- Given a transformation is over, then it is angry and fires only its new weapons.

*Sources: BOSS-27.*

#### FB-STRATOLINER-COLOSSUS-10 — First transformation: the outer engines become gatlings · MUST

It transforms the first time when both wing guns are destroyed (named). The outer nacelles retire
as it starts (their saddles go). Over the transformation's 2 s, one staged morph per outer engine
(shares of the transformation):
- to 0.15: the engine's front (intake lip, fan and spinner; the `fans` armour region) strains,
  then **the fan disc splits**: its two halves fly off (its pieces), leaving a dark cradle;
- 0.15–0.45: the **cowling peels back** in four petals, each swinging out and back 112° about its
  hinge, an open flower lit inside;
- 0.28–0.56: the **core telescopes out** ahead of it (to 1.6 times its length), a cluster of three
  barrels at its tip;
- 0.4–1: a **gatling** (`gatling-left`, `gatling-right`) rises straight up out of the opened
  nacelle, its octagonal pod first, then its three-barrelled turret; the core is gone at 0.8,
  inside the pod, the peeled petals stay round it.

The gatlings follow the player with bursts of 4 (red) and shield the core.

**Acceptance criteria**
- Given both wing guns destroyed, then it transforms, its outer nacelles retire, its fans' region is
  shed and its two gatlings are revealed in it (unit tests on the design).
- Manual validation: the fans split, the cowlings peel back, the cores telescope out and the
  gatlings rise where the nacelles were.

*Sources: BOSS-35, BOSS-36, BOSS-42, BOSS-43, BOSS-46, user request (2026-11-06).*

#### FB-STRATOLINER-COLOSSUS-11 — Second transformation: a second wing tier and a lance · MUST

It transforms the second time when its tail gun is destroyed (named). Over the transformation's
2 s, two staged morphs (shares of the transformation):
- **The flaps become a second wing tier.** To 0.15 the flaps (the `flaps` armour region) strain;
  then each **swings up** on its leading edge to stand on end (0.15–0.26), two **struts telescope
  up** from the wing under it lifting it 13.5 px (0.24–0.36), it **lies back down** flat on them
  (0.34–0.44), a second wing over the first, and the **outer panel** folded on its top **unfolds**
  outward 22 px about its tip (0.44–0.6). A **rack** (`rack-left`, `rack-right`) slides out along
  each tier from its root (0.4–0.75), then raises its four cells. The flaps leave dark wells in the
  wing.
- **The nose cone becomes the rails of a lance.** To 0.15 the radome (the `nose` armour region)
  strains; then its two halves **swing open** like a clamshell about their outer rear corners
  (0.15–0.33, 0.5 rad), then **close up straight but apart**, sliding out 6.8 px each side and 4 px
  forward and **telescoping** to 1.3 times their length (0.35–0.6): two rails, their cut faces lit
  inward. The **lance** (`lance`) rises between them on the nose's keel (0.4–1), its emitter last.
  The radome leaves a bulkhead and a dark keel.

The racks fire pairs of homing missiles, the lance its laser down the centre line; they shield the
core. Its weapons were tracking streams (the gatlings), now a lance splits the screen while missiles
hunt the player on either side.

**Acceptance criteria**
- Given its tail gun destroyed, then it transforms, its flaps' and nose's regions are shed, its two
  racks are revealed in the flaps' and its lance in the nose's (unit tests on the design).
- Manual validation: the flaps lift into a second wing tier on struts, the racks slide out along it,
  the nose splits into two rails and the lance rises between them.

*Sources: BOSS-35, BOSS-36, BOSS-41, BOSS-42, BOSS-43, user request (2026-11-06).*

#### FB-STRATOLINER-COLOSSUS-12 — Never easier · MUST

Its weighted fire rate (BOSS-39) never goes down from one transformation to the next, and is higher
after the last one than as it comes in.

**Acceptance criteria**
- Given its design, then its weighted fire rates as it comes in and after each transformation never
  go down and end higher (unit test).

*Sources: BOSS-39.*

#### FB-STRATOLINER-COLOSSUS-13 — Death, drops and points · MUST

Its parts drop a weapon bonus 60 % of the time, its hidden weapons 30 %, its core always (BOSS-57).
It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' and core's drop chances and its points are those of Tunable
  values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/stratoliner_colossus.py` (`_STRATOLINER_COLOSSUS`,
`STRATOLINER_COLOSSUS`); its model in `src/game/view/bosses/lab/stratoliner_colossus_model.py` and
its rig in `stratoliner_colossus_rig.py`.

| Name | Value | Notes |
|------|-------|-------|
| size | 5 L | `stats.size` |
| fuselage | y -88..77, half width up to 9.5, 2–16 px high; nose cone ahead of y -66 | `FUSELAGE`, `NOSE_JOINT` |
| wings | root (x 9) y -24..14, tip (x 86) y 30..42; 8–10.5 px high | `ROOT_*`, `TIP_*`, `WING_LOW`, `WING_TOP` |
| engines | x ±26, ±46, ±66; centre 7 px ahead of the leading edge; 22 px long, radius 4.6, axis 4.6 px high | `ENGINE_*` |
| petals | 4 an outer engine, hinged 5 px behind its middle; peel 1.95 rad over 0.15–0.45 | `PETAL_HINGE`; rig `PEEL`, `PEEL_SPAN` |
| cores | 12 px drum + 3.5 px barrels; telescope ×1.6 over 0.28–0.56; gone at 0.8 | rig `CORE_*`, `REACH`, `BARREL_LENGTH` |
| tail | tailplane root y 48..62, tip y 62..69 at x ±34, 12 px high; fin y 40..64 up to 36 px | `TAIL_*`, `FIN_*` |
| flaps (armour) | x ±12..44, 11 px chord along the trailing edge; `wing` region, own frame (wells), no pieces | `FLAP_X`, `FLAP_CHORD`; form 2 |
| second tier | lifted 13.5 px (top 24 px); outer panel 22 px; up 0.15–0.26, lift 0.24–0.36, down 0.34–0.44, unfold 0.44–0.6 | `TIER_H`, `TIER_REACH`; rig `FLAP_*` |
| nose (armour) | the radome's outline, not mirrored; `shell` region, own frame (bulkhead, keel), no pieces | `NOSE`; form 2 |
| rails | open 0.5 rad over 0.15–0.33; apart 6.8 px, 4 px ahead, ×1.3 over 0.35–0.6 | rig `NOSE_*`, `RAIL_*` |
| fans (armour) | round each outer engine's front half (x ±60.2..71.8, y -3..14); `ring` region, own frame (cradle), 4 pieces | `FAN`; form 1 |
| core | health 2 100, radius 20, drop 1 | |
| `wing-gun-left`, `wing-gun-right` | (∓36, 8), radius 10, health 1 000, shield, drop 0.6 | |
| `nacelle-left`, `nacelle-right` | (∓66, 9), radius 10, health 600, shield, drop 0.6, retire at 1 | |
| `tail-gun` | (0, 70), radius 10, health 900, shield, drop 0.6 | |
| wing guns | 11.1 px high; 2 barrels 2.8 px apart, bore 1.1, 7.5 px long; dome 4.6 | `WING_GUN` |
| nacelle guns | (∓66, 5), 9.8 px high; 3 barrels 2.2 px apart, bore 0.9, 6 px long, fixed straight down | `NACELLE_GUN` |
| tail gun | 13.5 px high; 2 barrels 2.4 px apart, bore 1, 7 px long | `TAIL_GUN` |
| spine gun (core) | (0, -42), 16.5 px high; 5 barrels, bore 1, 8 px long; dome 6 | `SPINE_GUN` |
| spine rotor (core) | (0, 26), 16.5 px high; 14 barrels, bore 0.75, 3.6 px long; hub 5 | `ROTOR` |
| rotor hatch | octagon of radius 6.2 round (0, 26) | `armour_region` `rotor-hatch` (`mount`) |
| gatlings | (∓66, 8), radius 8, health 800, pod 4–9 px, rising straight up; red; first 1.0 s / 1.8 s | `GATLING_AT`, `GATLING_POD` |
| racks | (∓30, 16) on the tier, radius 5.5, health 1 000, pod 24–27 px, sliding out from (∓14, 10); first 1.4 s / 3.4 s | `RACK_AT`, `RACK_FROM`, `TIER_POD` |
| lance | (0, -74), radius 7, health 1 000, pod 3–8.5 px, rising straight up; first 2.2 s | `LANCE_AT`, `LANCE_POD` |
| full health | 10 800 (core 2 100, parts 4 100 of which the retiring nacelles' 1 200, hidden weapons 4 600) | BOSS-54 |
| points | 8 500 | |
| ground speed | ×1.2 | |
| stop height | 0.7 | `stopFraction` |
| sway / bob | 34 px over 10 s / 6 px over 5 s | |
| wing guns' pairs | aimed 2, 6° apart, red 195 px/s, every 2.2 s (first 0.8 s / 1.9 s) | sweeps |
| nacelles' fans | 3 straight down, orange 180 px/s, every 2 s (first 1.2 s / 2.2 s) | fixed |
| tail gun's bursts | 3, 0.13 s apart, magenta 175 px/s, every 2.6 s (first 1.5 s) | |
| core stages 0–5 | aimed 1; aimed 3 at 9°; fan 5 at 12°; fan 3 + aimed 2 at 8°; fan 5 + burst 3; ring 14 turning 8° every 1.3 s + fan 5 | spine gun; rotor last |
| weighted fire rate | 6.3 as it comes in, 6.7 after its first transformation, 8.0 after its second | BOSS-39 |
| transformations | wing guns (both); tail gun | `transformParts` |
| neon | peach (1, 0.65, 0.3) | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time and its place in a
  world's health order (BOSS-55, BOSS-56) are not set. Its full health (10 800; 9 600 without the
  retiring nacelles, which the player need not destroy) is in line with the 1-1 final boss's (the
  Storm Petrel's 10 420), as asked.
- **Not a creature** (see the top): BOSS-47's creature look does not apply; BOSS-48 to BOSS-53 do.
- **The morphs are the view's.** The sim retires the outer nacelles, sheds the fans', flaps' and
  nose's regions and reveals the weapons; the petals, cores, flaps, panels, struts and nose halves
  follow the boss's `form`, `transforming_into` and `transform` in its view rig. Each region's whole
  drawing draws the rig's pieces at rest with the rig's own drawings and joints, so the swap does
  not show. The racks use `hidden_weapon(..., out_of=...)` to slide out along the tier; the
  gatlings, batteries and lance a `mount` of `[0, 0, 0]` to rise straight up. No engine change was
  needed.
- **Wholeness check.** The test helper poses a rig at 0 (at rest) or 1 (from the first
  transformation on): its 1 is this rig's state after both transformations (tier and rails out),
  so at form 1 the check sees the tier over the flaps it has not left yet. Both hold together.
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-06): 1 004 shots and 11
  lasers, every shot from a barrel, along it; it dies at about 110 s.
