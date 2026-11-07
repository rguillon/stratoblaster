# Condor Lifter

> **Area:** bosses · **Prefix:** `MB-CONDOR-LIFTER` · **Related:** [common](../common.md),
> [Stratoliner Colossus](L-16-stratoliner-colossus.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Condor Lifter is the mini boss of Lab level L-16: a gigantic heavy-lift cargo plane seen from
above. A fat fuselage with a glazed cockpit carries a high straight wing with four turboprops on
it, a T-tail over its flat rear, which a cargo ramp closes, and an external cargo deck on its back
with two containers strapped on it. It sways slowly, crossing aimed fire from its two outer
turboprops' guns over the player. At its transformation its cargo **morphs**: the ramp drops open,
the containers' roofs blow off, their walls hinge down flat into gun decks and their cargo
telescopes forward into barrels as a battery rises out of each. Shared rules are in
[common](../common.md).

**Not a creature.** BOSS-47 asks for a Cyber-Organic creature; this Lab boss departs from it on the
user's requests (2026-11-06, "drop the animal looking theme"; "10 more gigantic airplanes"): it is a
built flying machine of dark metal, corrugated containers, propellers and neon light lines, with no
flesh, eyes or limbs.

## Requirements

### Look

#### MB-CONDOR-LIFTER-01 — Silhouette and size · MUST

Seen from above it is a cargo plane 124 px (3.7 L) across its straight wing and 114 px long, its
nose down the screen: a fat fuselage 22 px wide, four turboprop nacelles standing out ahead of the
wing, a T-tail 48 px across at its back and two boxy containers side by side on its back behind the
wing. A straight high-winged four-turboprop freighter, unlike any other boss.

**Acceptance criteria**
- Manual validation in the boss viewer: a cargo plane with containers on its back at rest, gun decks
  after its transformation.

*Sources: Lab boss request (2026-11-06, gigantic airplanes).*

#### MB-CONDOR-LIFTER-02 — Fuselage, wing, turboprops, tail and cargo deck · MUST

The fuselage is a fat rounded-box loft, its belly and spine facets darker, a glazed brow of four lit
windows over the nose, small lit windows and a lit stripe down each flank, a gear sponson along each
lower flank (lit along it), and a flat rear: the cargo bay's mouth, lit inside, closed by the cargo
ramp (MB-CONDOR-LIFTER-05). The wing is a bevelled straight slab over the fuselage, lit along its
leading edge between the nacelles and at its tips, dark flap and aileron strips along its trailing
edge and a rivet line along its spar. Each turboprop is a long cowling on the wing (a lathe), a dark
spinner at its nose with a lit intake ring, exhaust stacks on its sides and a lit stripe on its
back. The T-tail is a swept fin on the centre line, a lit stripe up its rudder, and the tailplane
on its top, lit at its tips. The cargo deck is a pallet over the fuselage's back behind the wing,
wider than the fuselage, lit along its edges, on struts down to the flanks, with tie-down rails.

**Acceptance criteria**
- Manual validation: one aircraft, its fuselage, wing, turboprops, tail and cargo readable from
  above.

*Sources: BOSS-49, user request (2026-11-06).*

#### MB-CONDOR-LIFTER-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Engine guns** (`engine-left`, `engine-right`): an armoured, lit octagonal collar on each outer
  turboprop's back, round a twin-barrelled turret (its aimed pairs).
- **Nose gun** (`nose-gun`): a lit drum ahead of the cockpit, round a three-barrelled turret (its
  bursts).
- **Dorsal turret** (the core's, on the wing's centre section): two barrels side by side (its aimed
  shots, spreads and fans).
- **Cargo rotor** (the core's, on the fuselage behind the cockpit): ten barrels round a hub (its last
  rings). Until its last stage it lies under an octagonal hatch with a lit seam; as the rotor comes
  into use the hatch bursts off (BOSS-58), leaving a collar, and the rotor rises out.

A destroyed engine gun leaves its stump on its turboprop; the nose gun's on the nose.

**Acceptance criteria**
- Given its model, then it draws its three parts and every gun mount.

*Sources: BOSS-18, BOSS-48, BOSS-58.*

#### MB-CONDOR-LIFTER-04 — Lights · MUST

The cockpit's windows, the flank windows and stripes, the sponsons' lines, the wing's leading edges
and tips, the turboprops' intake rings and stripes, the propellers' blade tips, the fin's rudder
stripe and the tailplane's tips, the cargo deck's edges, the containers' straps and rims, the gun
decks' markings, the ramp's treads and the cargo bay's mouth glow, in its neon colour, teal (0.4, 1,
0.9) (BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are teal.

*Sources: BOSS-50.*

#### MB-CONDOR-LIFTER-05 — Its propellers, ramp and container walls (a view rig) · MUST

Its view rig (`condor_lifter_rig.py`) draws what moves and is only looked at:
- **Propellers**: four blades with lit tips on each turboprop's spinner, spinning (14 rad/s, the
  left pair the other way). An outer one winds down to a stop (9 rad/s each second) once the engine
  gun on its turboprop is destroyed.
- **Cargo ramp**: a plate hinged at the foot of the fuselage's flat rear, closing it, lit treads on
  its inside. It drops open at the transformation (MB-CONDOR-LIFTER-10), past level, its treads up.
- **Container walls and cargo**: shown from the moment the containers' roofs blow off; at rest they
  are the containers' armour region's (MB-CONDOR-LIFTER-10).

None of it is a part, a muzzle or anything the player can hit.

**Acceptance criteria**
- Manual validation: the propellers spin, an outer one stops once its engine gun is gone; the ramp
  and the containers morph at the transformation.
- Given its model at rest and after its transformation, then it holds together (unit test).

*Sources: user request (2026-11-06, "pieces morphing into something else"), BOSS-52.*

### Behaviour

#### MB-CONDOR-LIFTER-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then sways slowly
and wide and bobs a little: a heavy lifter. While it is fought the ground scrolls at ×1.1.

**Acceptance criteria**
- Given the fight, then the ground eases to ×1.1 of the level's speed and back after it.

*Sources: BOSS-03, BOSS-10.*

#### MB-CONDOR-LIFTER-07 — Parts and core · MUST

It has three parts as it comes in, all shielding its core: `engine-left`, `engine-right` and
`nose-gun`. The core's guns (the dorsal turret and the cargo rotor) fire the core's volleys and are
the last the player destroys.

**Acceptance criteria**
- Given its design, then its three parts all shield the core.

*Sources: BOSS-12, BOSS-13, BOSS-14.*

#### MB-CONDOR-LIFTER-08 — Stage patterns: crossfire, then walls · MUST

In every stage while they stand, each engine gun sweeps an aimed pair of red bullets 5° apart from
far out on the wing (the two in turn: their streams cross over the player), and the nose gun fires
bursts of 3 orange bullets at the player. The core fires:
- stage 0: an aimed blue bullet;
- stage 1: an aimed spread of 3, 9° apart;
- stage 2: a fan of 5 orange bullets, 12° apart, straight down;
- stage 3 (all three parts gone): a ring of 10 from the cargo rotor, turning 9° at each volley (a
  spiral), and an aimed pair of red bullets.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys; each shot leaves a barrel (a fight in
  the simulation).

*Sources: BOSS-21, BOSS-23, BOSS-58.*

#### MB-CONDOR-LIFTER-09 — Angry · MUST

After its transformation it is angry (BOSS-27): its two batteries fire all out for
`boss_rage_seconds`. It has no angry pattern of its own.

**Acceptance criteria**
- Given its transformation is over, then it is angry and fires only its batteries.

*Sources: BOSS-27.*

#### MB-CONDOR-LIFTER-10 — Transformation: the containers become gun decks · MUST

It transforms when both engine guns are destroyed (named). Over the transformation's 2 s, one
staged morph (shares of the transformation):
- 0–0.35: the **cargo ramp drops open** about its hinge, past level, the lit bay behind it showing;
- to 0.15: the containers strain (their armour region, shuddering and strobing), then their
  **roofs blow off** in four halves (its pieces), their straps snapping;
- 0.17–0.42: each container's **outer, front and back walls hinge down** outward about their feet,
  flat on the deck (the front ones leaning on the wing's trailing edge), into gun decks lit with
  markings; 0.2–0.4: its **inner wall sinks** into the deck;
- 0.15–0.82: its **cargo**, a cradle of five tubes, shows; 0.36–0.62 the tubes **telescope forward**
  (to 2.4 times their length) into barrels;
- 0.4–1: a **battery** (`battery-left`, `battery-right`) rises out of each container's floor, its
  long deck first, then its five-barrelled turret; the tubes are gone at 0.82, the battery's
  barrels standing where they reached.

The containers leave their dark floors on the deck (their frame), the dropped walls stay flat round
the batteries and the ramp stays open. The batteries sweep fans of 7 straight down the screen and
shield the core.

The fight changes character: from aimed streams crossing over the player from the wingtips to
walls of wide fans straight down from the middle of its back, the player slipping between them.

**Acceptance criteria**
- Given both engine guns destroyed, then it transforms, its containers' region is shed and its two
  batteries are revealed in it (unit tests on the design).
- Manual validation: the ramp drops, the roofs blow off, the walls fall flat, the cargo telescopes
  and the batteries rise out.

*Sources: BOSS-35, BOSS-36, BOSS-42, BOSS-43, user request (2026-11-06).*

#### MB-CONDOR-LIFTER-11 — Never easier · MUST

Its weighted fire rate (BOSS-39) goes up at its transformation.

**Acceptance criteria**
- Given its design, then its weighted fire rate is higher after its transformation than as it
  comes in (unit test).

*Sources: BOSS-39.*

#### MB-CONDOR-LIFTER-12 — Death, drops and points · MUST

Its parts drop a weapon bonus 50 % of the time, its hidden weapons 30 % (BOSS-57). It scores the
points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/condor_lifter.py` (`_CONDOR_LIFTER`, `CONDOR_LIFTER`); its model
in `src/game/view/bosses/lab/condor_lifter_model.py`, `condor_lifter_rig.py` (propellers, ramp,
walls, cargo) and `condor_lifter_joints.py` (jointed pieces, shared with the Stratoliner Colossus).

| Name | Value | Notes |
|------|-------|-------|
| size | 3.7 L | `stats.size` |
| fuselage | y -62..44, half width up to 11, 2–20 px high | `FUSELAGE` |
| wing | root y -15..3, tip y -12..0 at x ±62, 19.5–22.5 px high | `WING_ROOT`, `WING_TIP`, `WING_SPAN`, `WING_LOW`, `WING_TOP` |
| turboprops | x ±22, ±42; y -27..6; radius 4.2; axis 25.5 px high | `NACELLE_X`, `NACELLE_Y`, `NACELLE_R`, `NACELLE_H` |
| propellers | hub y -29, blades 8.5 px; 14 rad/s; wind down 9 rad/s² | `PROP_Y`, `PROP_R`; rig `SPIN`, `WIND_DOWN` |
| T-tail | fin y 32..50 up to 44 px; tailplane y 42..52, tips y 47..52 at x ±24 | `FIN_*`, `TAIL_*` |
| cargo ramp | hinge y 44, 6 px high; 16 × 13 px; drops 1.75 rad over 0–0.35 | `RAMP_*`; rig `RAMP_DROP`, `RAMP_OPEN` |
| cargo deck | y 5..31, half width 19, top 21.4 px | `DECK_Y`, `DECK_HALF`, `DECK_TOP` |
| containers (armour) | x ±4..17, y 7..29, 8 px high; `shell` region, own frame (floors), 4 roof pieces | `CONTAINER*`; form 1 |
| walls | fall 0.17–0.42 (front ones 1.36 rad); inner walls sink 0.2–0.4 | rig `WALLS_FALL`, `FRONT_FALL`, `WALL_SINK` |
| cargo | 5 tubes 1.8 px apart, 7 px long; shown 0.15–0.82; telescope ×2.4 over 0.36–0.62 | rig `TUBE_*`, `CARGO_OUT`, `REACH`, `CARGO_GONE` |
| core | health 1 100, radius 16 | |
| `engine-left`, `engine-right` | (∓42, -12) on the outer turboprops, radius 10, health 560, shield, drop 0.5 | |
| `nose-gun` | (0, -48), radius 10, health 640, shield, drop 0.5 | |
| engine guns | (∓42, -13), 30.3 px high; 2 barrels 2.6 px apart, bore 0.9, 7 px long; dome 3.8 | `ENGINE_GUN` |
| nose gun | (0, -47), 20 px high; 3 barrels, bore 1, 7.5 px long; dome 4.4 | `NOSE_GUN` |
| dorsal turret (core) | (0, -5), 23 px high; 2 barrels 3 px apart, bore 1.1, 7.5 px long | `DORSAL_GUN` |
| cargo rotor (core) | (0, -33), 20.5 px high; 10 barrels, bore 0.8, 3.4 px long; hub 4.2 | `ROTOR` |
| rotor hatch | octagon of radius 5.5 round (0, -33) | `armour_region` `rotor-hatch` (`mount`) |
| batteries | (∓10.5, 18) in the containers, radius 7.5, health 510, pod 21.4–23.8 px, rising straight up (`mount` [0, 0, 0]), blue bullets; first 1.2 s / 2.0 s | `BATTERY_AT`, `BATTERY_POD` |
| full health | 3 880 (core 1 100, parts 1 760, batteries 1 020) | BOSS-54 |
| points | 3 800 | |
| ground speed | ×1.1 | |
| stop height | 0.72 | `stopFraction` |
| sway / bob | 55 px over 8.5 s / 5 px over 3.4 s | |
| engine guns' pairs | aimed 2, 5° apart, red 190 px/s, every 1.8 s (first 0.6 s / 1.5 s) | sweeps |
| nose gun's bursts | 3, 0.12 s apart, orange 180 px/s, every 2.4 s (first 1.1 s) | |
| core stage 0 | aimed 1, blue 180 px/s, every 2.8 s | dorsal turret |
| core stage 1 | aimed 3, 9° apart, every 2.6 s | dorsal turret |
| core stage 2 | fan of 5, 12° apart, orange, every 2.6 s | dorsal turret |
| core stage 3 | ring of 10 turning 9°, blue, every 1.5 s; aimed 2, 6° apart, red, every 2.6 s | rotor; dorsal turret |
| weighted fire rate | 3.8 as it comes in, 10.2 after its transformation | BOSS-39 |
| transformation | `engine-left` and `engine-right` | `transformParts` |
| neon | teal (0.4, 1, 0.9) | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time and its place in a
  world's health order (BOSS-55, BOSS-56) are not set. Its full health (3 880) is about a 1-1 mini
  boss's (the Reef Warden's 3 200) and below the Lab's round-3 mini bosses' (4 150 to 5 180).
- **Not a creature** (see the top): BOSS-47's creature look does not apply; BOSS-48 to BOSS-53 do.
- **The morph is the view's.** The sim only sheds the containers' region and reveals the batteries;
  the ramp, the walls, the cargo and the propellers follow the boss's `form`, `transforming_into`
  and `transform` in its view rig. The containers' whole drawing draws the walls with the rig's own
  functions, so the swap at the burst does not show. No engine change was needed.
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-06): 603 shots, every one
  from a barrel, along it; it dies at about 74 s.
