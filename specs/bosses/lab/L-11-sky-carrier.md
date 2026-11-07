# Sky Carrier

> **Area:** bosses · **Prefix:** `FB-SKY-CARRIER` · **Related:** [common](../common.md),
> [Gale Corvette](L-11-gale-corvette.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Sky Carrier is the final boss of Lab level L-11: a flying aircraft carrier. A long flat flight
deck overhangs its hull, its bow tapering to a point with two catapult tracks down it, its island
tower on a sponson on its right edge, ducted lift engines on sponsons along its sides. It fights in
three characters: first its deck guns and its aircraft (the catapults launch Hornets); then, its
deck split open, a swarm from its hangar and flak from its mortars; last a giant beam cannon swung
out over its bow. Shared rules are in [common](../common.md).

**Not a creature.** BOSS-47 asks for a Cyber-Organic creature; this Lab boss departs from it on the
user's requests (2026-11-06, "drop the animal looking theme"; "flying fortress theme"): it is a
built flying machine of dark metal, deck plating, ducts and neon light lines, with no flesh, eyes or
limbs.

## Requirements

### Look

#### FB-SKY-CARRIER-01 — Silhouette and size · MUST

Seen from above it is a long, flat, straight-sided deck 168 px (4.9 L) long and 52 px across, its
bow tapering to a point down the screen, its island standing on its right edge, three lift engines'
round ducts out on its left side and two on its right: a carrier, unlike any other boss. Its deck
opens in the middle at its first transformation (a gap 34 px across, its halves standing out past
its sides); at its second its island lies folded over its right side and a boom carries its beam
cannon 22 px out ahead of its bow.

**Acceptance criteria**
- Manual validation in the boss viewer: a flat-decked carrier at rest, its deck split open after its
  first transformation, its island folded and its beam boom out after its second.

*Sources: Lab boss request (2026-11-06, flying fortress theme).*

#### FB-SKY-CARRIER-02 — Hull, deck, island, catapults and lift engines · MUST

The hull is a long bevelled keel under the deck, rows of lit ports down its sides; its upper hull
stops fore and aft of the hangar, whose walls, lined with dark bays and lit, and dark floor, lit
lane lines and painted cross lines on it, show once the deck has opened. The deck (a matt, non-skid
coating) overhangs the hull: on its bow the two catapult tracks, dark slots lit along their sides,
and the boom's hinge block at its tip; on its after deck the landing centre line's dashes, stripes
across its stern, an elevator's painted outline, the stern turret's lit barbette and the rotor's
well; lights down both its edges. The island stands on a sponson carried out from the right edge: a
tall plated block, a narrower bridge with a lit window band all round, a raked stack behind it with
a lit band, a mast with a radar bar and a lit yard. Each lift engine is a thick duct with a lit lip
on a sponson arm from the hull, a dark floor, struts and a hub inside it, its rotor turning (the
rig, FB-SKY-CARRIER-05).

**Acceptance criteria**
- Manual validation: one carrier, its deck, island, catapults and lift engines readable from above.

*Sources: BOSS-49, user request (2026-11-06).*

#### FB-SKY-CARRIER-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Deck guns** (`deck-left`, `deck-right`, on the split deck's halves): an armoured octagonal
  barbette, lit round its foot, splinter plates behind, round a twin-barrelled turret (its aimed
  pairs).
- **Catapults** (`catapult-left`, `catapult-right`, on the bow tracks): an armoured shuttle astride
  its track, a dart-winged drone parked on it lit along its spine, the blast deflector raised behind
  it. They launch Hornets and have no gun.
- **Island** (`island`, on its roof): an armoured cupola, lit, round a laser turret (its tracking
  laser, BOSS-31).
- **Stern turret** (the core's, on the after deck): three barrels side by side (its aimed shots,
  spreads, bursts and fans).
- **Stern rotor** (the core's, behind it): fourteen barrels round a hub (its last spiral). Until its
  last stage it lies under an octagonal hatch with a lit seam; as the rotor comes into use the hatch
  bursts off (BOSS-58), leaving a collar, and the rotor rises out.

A destroyed deck gun's stump rides its deck half as it slides; a destroyed island's rides the island
as it folds (BOSS-18).

**Acceptance criteria**
- Given its model, then it draws its five parts, its beam cannon and every gun mount.

*Sources: BOSS-18, BOSS-25, BOSS-48, BOSS-58.*

#### FB-SKY-CARRIER-04 — Lights · MUST

The catapult tracks' sides, the deck's edge lights, the split deck's seams, the hangar's lane lines
and wall lights, the hull's ports, the island's window band, stack band and yard lights, the lift
ducts' lips and hubs, the barbettes' and cupolas' rings, the plating's seams, the boom's rails and
the beam cradle's sides and fins glow. Its neon colour, set orange, shows bright yellow (BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright yellow.

*Sources: BOSS-50.*

#### FB-SKY-CARRIER-05 — Moving pieces and its rig · MUST

- **The split deck** (moving pieces, BOSS-45): the middle of the flight deck (y -48..-4) is two
  halves, each a plated slab from the centre line out to the deck's edge with a lit seam along its
  split edge, the centre line's dashes, an elevator's outline, edge lights, its deck gun's seat and a
  walkway under its outer edge. At the first transformation each slides 17 px straight out
  sideways, mirrored, and stays so; they leave no frame (the hangar is under them).
- **The island** (a moving piece): at the second transformation it swings 90° outboard about its
  outer foot, along the ship, to lie on its side over the rail, its mast pointing out to the right;
  no frame.
- **Its rig** (a view rig of its own, BOSS-46): the beam boom, a lit box girder hinged at the bow's
  tip, stowed lying aft along the deck's centre line between the catapults; at the second
  transformation (from 0.15 to 0.75 of it) it swings up and over the bow, half a turn about its
  hinge, to point straight ahead, the beam cannon rising onto its end. And the lift engines' rotors,
  four blades each, turning all the time (visual only).

The bow quarters' plating and the stern rotor's hatch are shed regions (FB-SKY-CARRIER-11,
BOSS-58).

**Acceptance criteria**
- Given its design, then its first transformation slides its deck halves apart (mirrored), its
  second swings its island, and no part the player can hit stands on them as they move (unit tests
  on the moving regions).
- Given its model, then it holds together at rest and after each transformation (unit test).

*Sources: BOSS-42, BOSS-45, BOSS-46, BOSS-52, user request (2026-11-06, "get creative on how the
boss transforms").*

### Behaviour

#### FB-SKY-CARRIER-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then sways slowly
and bobs a little: a long, heavy ship. While it is fought the ground scrolls at ×0.5.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.5 of the level's speed and back after it.

*Sources: BOSS-03, BOSS-10.*

#### FB-SKY-CARRIER-07 — Parts and core · MUST

It has five parts as it comes in, all shielding its core: `deck-left`, `deck-right`,
`catapult-left`, `catapult-right` and `island`. The island **retires** at the second transformation
(BOSS-46: it folds down and leaves the fight, not destroyed, its health leaving the gauge; the beam
cannon takes over from it). The core's guns (the stern turret and rotor) fire the core's volleys and
are the last the player destroys.

**Acceptance criteria**
- Given its design, then its five parts all shield the core, and the island retires at the second
  transformation.

*Sources: BOSS-12, BOSS-13, BOSS-14, BOSS-46.*

#### FB-SKY-CARRIER-08 — Stage patterns · MUST

In every stage while they stand, each deck gun sweeps an aimed pair of red bullets 6° apart, the two
in turn; the island fires a laser at the player (its turret following the player through its
warning line); each catapult launches two Hornets side by side, which dive at the player (BOSS-25),
the two in turn. The core fires:
- stage 0: an aimed orange bullet;
- stage 1: an aimed spread of 3, 8° apart;
- stage 2: a fan of 5, 12° apart, straight down;
- stage 3: a burst of 4 red bullets and a fan of 3, 12° apart;
- stage 4: a fan of 7, 12° apart, and an aimed red bullet;
- stage 5 (all five parts gone): a ring of 14 magenta bullets from the stern rotor, turning 9° at
  each volley (a spiral), and a fan of 5, 12° apart.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys; each shot leaves a barrel (a fight in
  the simulation).

*Sources: BOSS-21, BOSS-23, BOSS-25, BOSS-58.*

#### FB-SKY-CARRIER-09 — Angry · MUST

After each transformation it is angry (BOSS-27): after the first its hangar and mortars go all out
(Hornets and flak), after the second its beam cannon and gatlings, for `boss_rage_seconds`. It has
no angry pattern of its own.

**Acceptance criteria**
- Given a transformation is over, then it is angry and fires only the weapons it revealed.

*Sources: BOSS-27.*

#### FB-SKY-CARRIER-10 — First transformation: the deck splits · MUST

It transforms the first time when both deck guns are destroyed (named, so that no part the player
can hit stands on a deck half as it moves). As one event: the middle of its flight deck splits down
the centre line and its two halves slide apart sideways (FB-SKY-CARRIER-05), opening the hangar
below; out of its floor rise a **hangar** on the centre line, its doors sliding apart, launching
Hornets, and a **mortar** either side ahead of it, lobbing flak shells that burst into rings. They
shield the core.

The fight changes character: from aimed deck fire and a few aircraft to a swarm (catapults and
hangar) under bursting flak.

**Acceptance criteria**
- Given both deck guns destroyed, then it transforms, its deck halves slide apart and its hangar
  and two mortars are revealed in the hangar below.

*Sources: BOSS-35, BOSS-36, BOSS-41, BOSS-45.*

#### FB-SKY-CARRIER-11 — Second transformation: the island folds, the beam comes out · MUST

It transforms the second time when both catapults are destroyed (named). As one event: its island
tower swings down outboard and lies on its side over the rail (FB-SKY-CARRIER-05), its fire-control
laser retiring with it (FB-SKY-CARRIER-07); the heavy plating of its bow quarters (lit seams and
rivets) bursts off (`shell` frame), and a **gatling** unfolds on each quarter, firing bursts at the
player; and the **beam** cannon's boom swings up from the foredeck and over the bow, the cannon
rising onto its end 22 px ahead of the bow, firing a giant laser (44 px wide) straight down the
screen. They shield the core.

The fight changes character: the player now has to dodge a wide beam laid straight down from its
bow, in the gatlings' bursts.

**Acceptance criteria**
- Given both catapults destroyed, then it transforms, its island retires and swings down, its bow
  plating bursts and its two gatlings and its beam cannon are revealed.

*Sources: BOSS-35, BOSS-36, BOSS-40, BOSS-41, BOSS-42, BOSS-45, BOSS-46.*

#### FB-SKY-CARRIER-12 — Never easier · MUST

Its weighted fire rate (BOSS-39) goes up at each transformation.

**Acceptance criteria**
- Given its design, then its weighted fire rate as it comes in, after its first and after its second
  transformation goes up (unit test).

*Sources: BOSS-39.*

#### FB-SKY-CARRIER-13 — Death, drops and points · MUST

Its parts drop a weapon bonus 60 % of the time, its hidden weapons 30 %, its core always (BOSS-57).
It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/sky_carrier.py` (`_SKY_CARRIER`, `SKY_CARRIER`); its model in
`src/game/view/bosses/lab/sky_carrier_model.py`, `sky_carrier_parts.py` and `sky_carrier_rig.py`
(the boom and the lift rotors).

| Name | Value | Notes |
|------|-------|-------|
| size | 5 L | `stats.size` |
| flight deck | y -98..70, half width 26, 12–15 px high | `DECK`, `DECK_LOW`, `DECK_TOP` |
| hull | y -88..64, half width 19, 2–12 px; hangar floor 5 px | `HULL_HALF`, `HULL_ENDS`, `HULL_LOW`, `HANGAR_FLOOR` |
| split deck | y -48..-4, each half slides 17 px out | `SPLIT`, `SPLIT_OUT`; `moving_region` `deck` (mirrored, form 1) |
| island | x 21..33, y 8..36, bridge to 37 px, mast to 47 px; swings 90° `along` about (33, 22, 15) | `ISLAND`, `ISLAND_TOP`, `MAST_TOP`; `moving_region` `island` (form 2) |
| catapult tracks | x ±9, y -94..-52 | `CATAPULT_X`, `CATAPULT_Y` |
| lift engines | (-33, -62), (-33, 6), (-33, 48), (33, -62), (33, 48); duct radius 7, 8 px high; rotors 9 rad/s | `LIFT_FANS`, `FAN_RADIUS`, `FAN_H`; rig `FAN_SPIN` |
| beam boom | hinge (0, -96) at 16.5 px, 22 px long; swings 0.15–0.75 of the second transformation | `BOOM_HINGE`, `BOOM_LENGTH`; rig `SWING` |
| core | health 1 700, radius 20 | |
| `deck-left`, `deck-right` | (∓17, -26) on the deck halves, radius 10, health 820, shield, drop 0.6 | |
| `catapult-left`, `catapult-right` | (∓9, -66), radius 9, health 760, shield, drop 0.6; 2 Hornets every 8 s (first 3 s / 7 s) | `launches` |
| `island` | (27, 20), radius 10, health 900, shield, drop 0.6; retires at transformation 2 | |
| deck guns | 16 px high; 2 barrels 3 px apart, bore 1.1, 7.5 px long; dome radius 4.6 | `DECK_GUN` |
| island laser | (27, 15), 37.5 px high; turret, bore 1.8, 9 px long | `ISLAND_LASER` |
| stern turret (core) | (0, 44), 16 px high; 3 barrels 3.1 px apart, bore 1.2, 8 px long; dome radius 5.5 | `STERN_GUN` |
| stern rotor (core) | (0, 58), 16 px high; 14 barrels, bore 0.75, 3.6 px long; hub radius 5 | `ROTOR` |
| rotor hatch | octagon of radius 6.4 round (0, 58) | `armour_region` `rotor-hatch` (`mount`) |
| hangar | (0, -24), radius 10, health 720, pod 5–11 px; 2 Hornets every 7 s (first 1.6 s) | under the deck, centre line |
| mortars | (∓9, -40), radius 6.5, health 720, pod 5–8 px, orange; first 1.2 s / 2.0 s | under the deck |
| bow plating (armour) | x ±12..26, y -61..-81, 14.5–17.5 px; `shell` frame | `BOW_PLATING`; form 2 |
| gatlings | (∓18, -72), radius 7, health 900, pod 15–17.5 px, red; first 1.2 s / 2.0 s | in the bow plating |
| beam | (0, -118) at the boom's end, radius 12, health 900; emitter 17.9 px high, pointing down the screen; 44 px wide, 2.4 s every 7 s (first 1.4 s) | `bow_beam` (a rig, like `tail_cannon`) |
| full health | 10 620 (core 1 700, parts 4 060, hangar and mortars 2 160, beam and gatlings 2 700) | BOSS-54; the Storm Petrel's (1-1) is 10 420 |
| points | 9 000 | |
| ground speed | ×0.5 | |
| stop height | 0.7 | `stopFraction` |
| sway / bob | 32 px over 10 s / 5 px over 5 s | |
| deck guns' pairs | aimed 2, 6° apart, red 190 px/s, every 2 s (first 0.8 s / 1.8 s) | sweeps |
| island laser | 1.4 s every 7.5 s (first 3 s) | turret |
| core stage 0 | aimed 1, orange 180 px/s, every 2.8 s | stern turret |
| core stage 1 | aimed 3, 8° apart, every 2.6 s | stern turret |
| core stage 2 | fan of 5, 12° apart, every 2.6 s | stern turret |
| core stage 3 | burst of 4, 0.13 s apart, red, every 2.4 s; fan of 3, 12° apart, every 3 s | stern turret |
| core stage 4 | fan of 7, 12° apart, every 2.4 s; aimed 1, red, every 2.8 s | stern turret |
| core stage 5 | ring of 14 turning 9°, magenta 175 px/s, every 1.4 s; fan of 5, 12° apart, every 2.8 s | rotor; stern turret |
| weighted fire rate | 4.4 as it comes in, 5.2 after its first transformation, 9.3 after its second | BOSS-39 (launched Hornets weigh 2) |
| transformations | `deck-left` and `deck-right`; then `catapult-left` and `catapult-right` | `transformParts` |
| neon | orange (1, 0.45, 0.1), shown yellow | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time and its place in a
  world's health order (BOSS-55, BOSS-56) are not set. Its full health is about the 1-1 final
  boss's (Storm Petrel, 10 420), as asked.
- **Not a creature** (see the top): BOSS-47's creature look does not apply; BOSS-48 to BOSS-53 do.
- **A beam at the bow.** `hidden_weapons.tail_cannon` points its emitter out behind the boss (it is
  meant to turn round first); the Sky Carrier keeps its heading, so its config builds the same
  weapon (`bow_beam`) with its emitter pointing down the screen, at the boom's height. No engine
  change was needed.
- **The wholeness check** poses a rig unfolded from the first transformation on; this boss's boom
  swings at its second, so the check sees it out one form early (it still holds together).
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-06): 1 221 shots and 14
  lasers, every one from a barrel, along it; it dies at about 134 s.
