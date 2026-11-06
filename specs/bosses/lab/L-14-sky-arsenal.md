# Sky Arsenal

> **Area:** bosses · **Prefix:** `FB-SKY-ARSENAL` · **Related:** [common](../common.md),
> [Windmill Ram](L-14-windmill-ram.md)

**Lab boss: in the dev viewer only.** It is listed after the game bosses in the dev viewer's Bosses
list, and no level brings it in.

The Sky Arsenal is the final boss of Lab level L-14: a tiered flying fortress stacked like a
wedding cake of gun decks. A broad square lower tier (its four corners are bastion petals) carries
a smaller middle tier, which carries a small top tier on a turntable; ducted lift fans are slung
under the lower tier's flanks and an ammunition crane works on the middle tier. Each of its
transformations is a different mechanical event: first its **top tier turns 45°** on its
turntable, its gun stumps going round with it, and the hatches its corners uncover burst on a pair
of mortars; then the **whole fortress turns round** while its **four corner petals slide out**
along rails, a missile rack riding out on each rear petal (now facing the player) and the stern
plating bursting on an orb. Its fight changes character each time: fans and aimed fire, then flak,
then homing missiles and spirals. Shared rules are in [common](../common.md).

**Not a creature.** BOSS-47 asks for a Cyber-Organic creature; this Lab boss departs from it on the
user's requests (2026-11-06, "drop the animal looking theme"; "flying fortress theme"): it is a
built flying fortress of plated metal, rivets, rails, fans and neon light lines, with no flesh,
eyes or limbs.

## Requirements

### Look

#### FB-SKY-ARSENAL-01 — Silhouette and size · MUST

Seen from above it is three stacked squares: a lower tier 100 px across, a middle tier 72 px
across, a top tier 48 px across, square on at rest; a ducted fan 27 px across stands out on each
flank, the crane's jib reaches out over its stern. After its first transformation the top tier
stands as a diamond on the middle tier; after its second the lower tier is an octagon with a
detached petal out on each corner, the whole fortress turned round.

**Acceptance criteria**
- Manual validation in the boss viewer: a stacked, tiered fortress with flank fans, unlike any
  other boss.

*Sources: Lab boss request (2026-11-06, "flying fortress theme").*

#### FB-SKY-ARSENAL-02 — Tiers, engines and fittings · MUST

- **Lower tier:** a plated octagon between its petals, 10 px high, gun ports round its flanks, lit
  bands along its bow and stern, deck plates on its flanks, vent grilles either side of the bow
  turret's lit seat, and two slide-rail girders along each diagonal under each petal.
- **Middle tier:** a square of darker walls 21 px high, a lit band and gun ports round them, a
  lit balcony on each flank, the turntable's drum and its lit track ring on its deck, the crane's
  pedestal on its back left corner, and an ammunition hoist (a lattice tower, a shell drum, a stack
  of crates) on its back right corner.
- **Top tier:** see FB-SKY-ARSENAL-05.
- **Lift engines:** under each flank a ducted fan (an open duct with a lit lip on two pairs of
  pylons, stator arms holding its hub, its blades spinning inside).

**Acceptance criteria**
- Manual validation: one machine; the tiers read apart and the fans spin.

*Sources: BOSS-49, user request (2026-11-06).*

#### FB-SKY-ARSENAL-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Gun decks** (`deck-left`, `deck-right`), on the top tier's front: an armoured octagonal cowl
  on a seat, lit, a five-barrelled turret on it (its fans).
- **Bastions** (`bastion-left`, `bastion-right`), on the front petals: an octagonal armoured
  cupola with dark slits, lit, a three-barrelled turret on it (its bursts).
- **Crane** (`crane`), on the middle tier's back left corner: a turntable ring, a plated cab, a
  lattice jib reaching out over the stern, a counterweight, a shell crate hanging on its cable; a
  laser turret on its cab's roof.
- **Bow turret** (the core's, on the lower tier's front deck): three barrels side by side (its
  aimed shots, spreads, bursts and fans).
- **Top rotor** (the core's, on the top tier's centre): sixteen barrels round a hub (its last
  ring). Until its last stage it lies under an octagonal hatch with a seam of light round it; as
  the rotor comes into use the hatch bursts off (BOSS-58), leaving a collar, and the rotor rises
  out.

A destroyed part's stump stands on a pedestal (the decks' seats, the bastions' pedestals on their
petals, the crane's on the middle tier).

**Acceptance criteria**
- Given its model, then it draws its five parts and every gun mount.

*Sources: BOSS-18, BOSS-48, BOSS-58.*

#### FB-SKY-ARSENAL-04 — Lights · MUST

Its bands, track ring, duct lips, balcony windows, the seams and chevrons of its petals, the rings
of its pinnacles and its parts' trims glow. Its neon colour, sky blue, shows bright green
(BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright green.

*Sources: BOSS-50.*

#### FB-SKY-ARSENAL-05 — Moving pieces and shed regions · MUST

- **Top tier** (`top-tier`, a moving piece, BOSS-45): a plated square block on the middle tier's
  turntable, a lit band and embrasures round it, a parapet, a pinnacle on each corner (a lit ring,
  a spire; a pennant on two of them, a radar dish on the other two, so its turn shows), its gun
  decks' seats and the rotor's well. It turns `TOP_TURN` about the vertical through its centre at
  the first transformation.
- **Petals** (`petal-front-right`, `petal-front-left`, `petal-back-right`, `petal-back-left`,
  moving pieces): each a thick plated wedge in a corner of the lower tier, an armour plate and a lit
  chevron on its top, rivets and lit wall faces along its outer edges, a lit ring where a bastion or
  a rack stands (the front ones' bastion pedestals). They slide `PETAL_OUT` out along their
  diagonals on their rails at the second transformation.
- **Mortar hatches** (`mortar-hatch`, shed at the first transformation, `shell` frame): split
  armoured lids on the middle tier's front corners, under the top tier's front corners at rest.
- **Stern plating** (`stern-hatch`, shed at the second, `shell` frame): a riveted double lid on the
  lower tier's stern, on the centre line.
- **Rotor hatch** (BOSS-58), see FB-SKY-ARSENAL-03.

**Acceptance criteria**
- Given its design, then each transformation moves or sheds its pieces and each hidden weapon lies
  in a region its transformation sheds or rides a petal (unit test).
- Given its model, then it holds together at rest and after each transformation.

*Sources: BOSS-42, BOSS-45, BOSS-46, BOSS-52.*

### Behaviour

#### FB-SKY-ARSENAL-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then drifts in a
slow, heavy sway and a gentle bob. While it is fought the ground scrolls at ×0.3.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.3 of the level's speed and back after it.

*Sources: BOSS-03, BOSS-10.*

#### FB-SKY-ARSENAL-07 — Parts and core · MUST

It has five parts as it comes in, all shielding its core: `deck-left`, `deck-right`,
`bastion-left`, `bastion-right` and `crane`. The core's guns (the bow turret and the top rotor)
fire the core's volleys and are the last the player destroys.

**Acceptance criteria**
- Given its design, then its five parts all shield the core.

*Sources: BOSS-12, BOSS-14.*

#### FB-SKY-ARSENAL-08 — Stage patterns · MUST

Stacked (as it comes in), it lays walls and aimed fire: in every stage while they stand, each gun
deck sweeps fans of 5 orange bullets, 10° apart, straight down; each bastion fires bursts of 3 red
bullets at the player; the crane's laser turret aims a laser at the player (1.4 s every 7.5 s). The
core fires:
- stage 0: an aimed blue bullet;
- stage 1: an aimed spread of 3, 10° apart;
- stage 2: a burst of 4 blue bullets and an aimed spread of 3 red, 8° apart;
- stage 3: a fan of 5 blue, 12° apart, straight down, and an aimed red bullet;
- stage 4: a fan of 7 blue, 10° apart, and a burst of 3 red;
- stage 5 (all five parts gone): a ring of 16 orange from the top rotor, turning 9° at each volley
  (a spiral), and a burst of 4 blue.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys; each shot leaves a barrel (a fight in
  the simulation).

*Sources: BOSS-21, BOSS-23, BOSS-58.*

#### FB-SKY-ARSENAL-09 — Angry · MUST

After each transformation it is angry (BOSS-27): the weapons that transformation revealed fire all
out for `boss_rage_seconds`. It has no angry pattern of its own.

**Acceptance criteria**
- Given a transformation is over, then it is angry and fires only that transformation's weapons.

*Sources: BOSS-27.*

#### FB-SKY-ARSENAL-10 — First transformation: the top tier turns · MUST

When both gun decks are destroyed (`transformParts`), the top tier strains, then turns 45° on its
turntable about the vertical, its gun decks' stumps going round with it; its front corners, which
lay over the middle tier's front corners, swing clear, and the hatches there burst off on a pair of
**mortars** (squat turrets with one short, wide barrel) firing flak shells that burst into rings of
8. The fight turns from fans and aimed fire to area denial: slow shells that burst where the player
is heading. The mortars shield the core.

**Acceptance criteria**
- Given both gun decks destroyed, then the top tier turns 45° and two mortars are revealed in the
  shed hatches.

*Sources: BOSS-35, BOSS-36, BOSS-40, BOSS-45.*

#### FB-SKY-ARSENAL-11 — Second transformation: it turns round and opens · MUST

When both bastions are destroyed (`transformParts`), the whole fortress turns round (`turns`,
BOSS-46: half a turn over the transformation, its parts, hit circles and muzzles with it) while its
four corner petals slide 10 px out along their diagonal rails (the bastions' stumps going out with
the front ones). A missile **rack** rides out on each rear petal (four ports, pairs of homing
missiles) and the stern plating bursts on an **orb** on the centre line (a rotor firing turning
rings of 10): its stern, now facing the player, becomes its battery. The fight turns again: homing
missiles to shoot down and spiralling rings to weave through, over the mortars' flak. The racks and
the orb shield the core.

**Acceptance criteria**
- Given both bastions destroyed, then it turns round by pi, its petals slide out, two racks are
  revealed on the rear petals and an orb in the stern plating.

*Sources: BOSS-35, BOSS-36, BOSS-40, BOSS-41, BOSS-45, BOSS-46.*

#### FB-SKY-ARSENAL-12 — Never easier · MUST

Its weighted fire rate (BOSS-39) goes up from one form to the next (Tunable values).

**Acceptance criteria**
- Given its design, then its weighted fire rate as it comes in and after each transformation never
  goes down and ends higher (unit test).

*Sources: BOSS-39.*

#### FB-SKY-ARSENAL-13 — Death, drops and points · MUST

Its parts drop a weapon bonus 60 % of the time, its hidden weapons 30 %, its core always (BOSS-57).
It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' and core's drop chances and its points are those of Tunable
  values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/sky_arsenal.py` (`_SKY_ARSENAL`, `SKY_ARSENAL`); its model in
`src/game/view/bosses/lab/sky_arsenal_model.py` and `sky_arsenal_parts.py`.

| Name | Value | Notes |
|------|-------|-------|
| size | 5 L (radius 85 px) | `stats.size` |
| tiers | lower 50 px half wide, 10 px high; middle 36, 21 px; top 24, 31 px | `LOW_HALF`, `LOW_TOP`, `MID_HALF`, `MID_TOP`, `TOP_HALF`, `TOP_TOP` |
| petals | the lower tier's corners beyond \|x\| + \|y\| = 64, 0 to 11 px high | `PETAL_CUT`, `PETAL_Y` |
| top tier turn | 0° to 45° about the vertical through (0, 0), at the first transformation | `TOP_SWING`, `TOP_TURN`; `moving_region` `top-tier` |
| petal slide | 10 px out along each diagonal (front: (±10, -10); back: (±10, 10)), at the second | `PETAL_SLIDE_FRONT`, `PETAL_SLIDE_BACK`, `PETAL_OUT` |
| turn round | none at the first transformation, pi at the second | `turns` |
| lift engines | ducts at (±62, 0), radius 12 | `ENGINE_X`, `ENGINE_RADIUS` |
| core | health 4 700, radius 22, drop 1 | |
| `deck-left` / `deck-right` | (∓12, -11), radius 9, health 1 300, shield, drop 0.6 | on the top tier |
| `bastion-left` / `bastion-right` | (∓39, -39), radius 10, health 1 500, shield, drop 0.6 | on the front petals |
| `crane` | (-27, 27), radius 10, health 1 600, shield, drop 0.6 | |
| deck turrets | 32.5 px high; 5 barrels 2.6 px apart, bore 1, 8 px long; dome radius 6.8 | `DECK_GUN` |
| bastion turrets | 15 px high; 3 barrels 2.86 px apart, bore 1.1, 7.5 px long; dome radius 5 | `BASTION_GUN` |
| crane laser | 27 px high, on a turret; bore 2.2, 10 px long | `CRANE_LASER` |
| bow turret (core) | (0, -43), 11 px high; 3 barrels, bore 1.1, 8 px long; dome radius 5.5 | `BOW_GUN` |
| top rotor (core) | (0, 0), 32 px high; 16 barrels, bore 0.7, 3.4 px long | `ROTOR` |
| rotor hatch | octagon of radius 7 round (0, 0) | `armour_region` `rotor-hatch` (`mount`) |
| mortar hatches | squares 14 px across round (±27, -27), 21–22.5 px high; `shell` frame | `armour_region` `mortar-hatch`, form 1 |
| stern plating | (-10, 33) to (10, 48), 10–11.5 px high; `shell` frame | `armour_region` `stern-hatch`, form 2 |
| mortars | (∓27, -27), radius 7, health 1 280, pod 21–24 px, orange; first 1.2 s / 2.0 s | `hidden_weapon` `mortar`, form 1 |
| racks | (∓49, 49) once slid out, radius 8, health 1 600, pod 11–14 px; first 1.2 s / 2.0 s | `hidden_weapon` `rack`, ride the back petals, form 2 |
| orb | (0, 41), radius 8, health 1 600, pod 10–13 px, blue; first 1.6 s | `hidden_weapon` `orb`, form 2 |
| full health | 19 260 (core 4 700, parts 7 200, hidden weapons 7 360) | BOSS-54 |
| points | 13 000 | |
| ground speed | ×0.3 | |
| stop height | 0.73 | `stopFraction` |
| sway / bob | 28 px over 11 s / 5 px over 4.5 s | |
| deck fans | 5, 10° apart, straight down, orange 175 px/s, every 3 s (first 1.0 s / 2.4 s) | sweeps |
| bastion bursts | 3, 0.14 s apart, red 190 px/s, every 2.6 s (first 1.4 s / 2.7 s) | |
| crane laser | 1.4 s every 7.5 s (first 4 s) | aimed during its warning |
| core stage 0 | aimed 1, blue 185 px/s, every 2.6 s | bow turret |
| core stage 1 | aimed 3, 10° apart, every 2.4 s | bow turret |
| core stage 2 | burst of 4, 0.14 s apart, every 1.8 s; aimed 3 red, 8° apart, every 2.4 s | bow turret |
| core stage 3 | fan of 5, 12° apart, every 2.2 s; aimed 1 red, every 2.6 s | bow turret |
| core stage 4 | fan of 7, 10° apart, every 2 s; burst of 3 red, every 2.6 s | bow turret |
| core stage 5 | ring of 16 orange turning 9°, every 1.3 s; burst of 4 blue, every 2.4 s | rotor; bow turret |
| weighted fire rate | 7.1 as it comes in, 7.5 after its first transformation, 11.5 after its second | BOSS-39 |
| transformations | once both gun decks are destroyed; once both bastions are | `transformParts` |
| neon | sky blue (0.2, 0.7, 1), shown green | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time and its place in a
  world's health order (BOSS-55, BOSS-56) are not set. Its health is about that of the 1-4 final
  boss (Refinery Titan, 19 210).
- **Not a creature** (see the top): BOSS-47's creature look does not apply; BOSS-48 to BOSS-53 do.
- **Its mechanisms** (round 3 asks each transformation to be a different mechanical event): the
  first is a single piece turning about the vertical (BOSS-45 swing) with hatches bursting; the
  second is the whole boss turning round (BOSS-46) while four pieces slide (BOSS-45 slide), a
  weapon riding two of them and plating bursting on the third.
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-06): 1 630 shots and 3
  lasers, every one from a barrel, port or lens, along it; it dies at about 134 s.
