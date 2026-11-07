# Siege Crawler

> **Area:** bosses · **Prefix:** `FB-SIEGE-CRAWLER` · **Related:** [common](../common.md),
> [Mantis Lancer](L-4-mantis-lancer.md)

The Siege Crawler is the Lab's L-4 final boss. **Lab boss: in the dev viewer only** (no level brings
it in; it is listed after the 40 World bosses in the dev viewer's Bosses list). A very wide, flat,
low armoured crawler, 4.5 L across: a giant trilobite plated like a tank, rows of legs along both
flanks like tracks. It is heavy artillery: a front cannon sweeping spreads of big, slow shells, two
mortars lobbing flak that bursts into rings after a delay, two missile blocks; few shots, but its
bullet hell is made of their bursts. Once both mortars are gone it sheds its deck plates and unfolds
a pair of laser lances; once both missile blocks are gone it sheds its head shield's cheeks and
unfolds a pair of missile racks. Shared rules are in [common](../common.md).

## Requirements

### Look

#### FB-SIEGE-CRAWLER-01 — Silhouette and size · MUST

Seen from above, the Siege Crawler is a very wide, short, flat crawler, 4.5 L across and about half
as long: a rounded head shield at its front (down the screen) with its cannon on the shield's
raised ridge, a thorax of shingle plates either side of a raised axial ridge, a tail shield, a
mortar on each flank, a missile sponson on each rear flank, and a row of eight short legs under an
armoured fender along each flank, like a tank's tracks.

**Acceptance criteria**
- Manual validation in the boss viewer: a wide, low armoured trilobite, its silhouette unlike any
  other boss's.

*Sources: user request (2026-11-05, the Lab bosses).*

#### FB-SIEGE-CRAWLER-02 — Body · MUST

Its belly is a flesh mantle rimmed with a red vein. Its head shield is dark metal over the belly,
its glabella a ridged carapace; its thorax five shingle plates of flesh shell, alternately slate and
graphite, a red seam of light under each one's back edge; its axial ridge a segmented flesh body
under a ridged plate, a red vein down it, grafted seats for the core's guns; its tail shield flesh
shell ribbed with dark metal. Its face: two clusters of red eyes on the head shield, bone mandibles,
feelers sweeping forward, a row of bone barbs along its front, genal spines sweeping back from the
shield's corners. Grafted metal and lights: the fenders over its legs, a light on each fender, vents
(one off the centre line), a patch on one side only, a mast near its tail, reactor sacs at its tail,
glands on its flanks with veins running in.

**Acceptance criteria**
- Manual validation: a living trilobite under grafted tank armour.

*Sources: user request (2026-11-05).*

#### FB-SIEGE-CRAWLER-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts, the shared models of [common](../common.md) (BOSS-58):
- **Cannon** (on the head shield's ridge): a heavy octagonal armoured mantlet ringed in red, side
  blocks and a feed sac behind it, under a big turret of three heavy barrels side by side.
- **Mortars** (left and right, on the thorax's flanks): each a swollen, armoured flesh cradle ringed
  in red, ammunition sacs beside it, bone barbs before it, under a mortar turret (a single short,
  fat barrel resting in a cradle on a turntable, as the Breakwater's).
- **Missile blocks** (left and right, on the rear flanks): each an armoured sponson over the fender,
  a feed sac and a vein running into the shell, under a block of four missile ports.
- **Keep gun** (the core's): a twin-barrelled turret on the axial ridge (its big shells).
- **Flak mortar** (the core's): a mortar turret on the tail shield (its flak), under an armoured
  hatch until it first fires.
- **Tail rotor** (the core's): a rotor of twelve barrels on the axial ridge between them (its last
  ring), under an armoured hatch until its last stage.

Each hatch is an octagonal cap with a seam of red light round it; it bursts off as its gun comes into
use (BOSS-58), leaving a collar round the opening the gun rises out of.

**Acceptance criteria**
- Given its model, then it draws the cannon, both mortars, both missile blocks and every gun mount
  (unit test).

*Sources: user request (2026-11-05).*

#### FB-SIEGE-CRAWLER-04 — Lights · MUST

Red veins and seams run round its belly, between its shingles, down its ridge and over its cheeks;
its eyes, glands, fender lights and mast glow. Its neon colour, set red, shows bright yellow
([common](../common.md), BOSS-50); its lasers are its neon folded into the enemy shots' family
(BOSS-32).

**Acceptance criteria**
- Given its model, then its lights are bright yellow.

*Sources: user request (2026-11-05).*

#### FB-SIEGE-CRAWLER-05 — What it sheds · MUST

It sheds two armour regions ([common](../common.md), BOSS-42), each drawn as a piece of its own:
- **Deck** (transformation 1, `deck`, mirrored): two thick riveted plates on the thorax's side lobes
  either side of the ridge (from 5.1 px to 8.6 px), a vent and a red seam on each. It bursts into
  plates cracked from its outline and leaves a `shell` lattice frame. The lances lie under it.
- **Cheeks** (transformation 2, `cheeks`, mirrored): wide plated wedges over the head shield from the
  cannon's mantlet out to its genal corners (from 3.8 px to 8 px), ridged, a red vein and a gland on
  each. It bursts into plates and leaves a `wing` frame. The racks lie under it.

**Acceptance criteria**
- Given its design, then each transformation sheds its region and each hidden weapon lies in the
  region its transformation sheds (unit test).
- Given its model, then it draws both regions' armour, and it holds together at rest and after each
  transformation (unit tests).

*Sources: D-221, D-224, D-254.*

### Behaviour

#### FB-SIEGE-CRAWLER-06 — Coming in and moving · MUST

It comes in from the top ([common](../common.md), BOSS-08) to `stopFraction` of the playfield's
height, then sways slowly and barely bobs (a heavy crawler). While it is fought the ground scrolls
at ×0.35.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.35 of the level's speed and back after it.

*Sources: BOSS-03.*

#### FB-SIEGE-CRAWLER-07 — Parts and core · MUST

It has five parts as it comes in, all shielding its core: `mortar-left`, `mortar-right`,
`missile-left`, `missile-right` and `cannon`. The core's guns (the keep gun, the flak mortar and the
tail rotor) fire the core's volleys and are the last the player destroys. The turrets turn the way
they fire.

**Acceptance criteria**
- Given its design, then its five parts all shield the core (unit test on its design).

*Sources: BOSS-12, BOSS-14, BOSS-58.*

#### FB-SIEGE-CRAWLER-08 — Stage patterns · MUST

The parts fire in every stage while they stand:
- the cannon sweeps aimed spreads of 3 big, slow red shells, 12° apart;
- each mortar lobs one slow flak shell at the player, which bursts after 1.3 s into a ring of 10
  orange bullets, the two mortars in turn;
- each missile block launches 2 homing missiles, 30° apart, the two blocks in turn.

The core fires:
- stage 0: one big, slow orange shell at the player from the keep gun;
- stage 1: one flak shell at the player from its flak mortar, bursting after 1.5 s into a ring of
  12 red bullets;
- stage 2: an aimed pair of big shells, 10° apart, from the keep gun;
- stage 3: flak from the flak mortar, and bursts of 3 big shells, 0.25 s apart, from the keep gun;
- stage 4: flak more often, and aimed spreads of 3 big shells, 10° apart;
- stage 5 (all five parts gone): a ring of 12 red bullets from the tail rotor, turning 9° at each
  volley (a spiral), and its flak.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys, each from its mount (unit test).

*Sources: BOSS-20, BOSS-21, BOSS-23, BOSS-58.*

#### FB-SIEGE-CRAWLER-09 — Angry · MUST

It is angry after each transformation, when the weapons that transformation revealed fire all out
for `boss_rage_seconds`, `boss_rage_rate` times as often (its racks `boss_rage_missiles` times as
many missiles, its lances as often as their warning, beam and gap allow), instead of its stage's
pattern ([common](../common.md), BOSS-27).

**Acceptance criteria**
- Given a transformation is over, then it is angry and fires only the weapons it revealed (unit
  test).

*Sources: BOSS-27.*

#### FB-SIEGE-CRAWLER-10 — First transformation · MUST

It transforms the first time once both mortars are destroyed (`transformParts`): its deck plates
burst off, baring a dark metal lattice, and two **lances** unfold on its thorax's side lobes, either
side of its ridge. They shield the core and fire lasers straight down the screen, in turn.

**Acceptance criteria**
- Given both mortars destroyed, then it transforms and its two lances are revealed (unit test).

*Sources: D-221, D-224, D-228, D-229.*

#### FB-SIEGE-CRAWLER-11 — Second transformation · MUST

It transforms the second time once both missile blocks are destroyed: its head shield's cheeks
burst off, baring a dark metal frame, and two **racks** unfold on the head shield, either side of
the cannon. They shield the core and fire pairs of homing missiles, in turn.

**Acceptance criteria**
- Given both missile blocks destroyed, then it transforms again and its two racks are revealed
  (unit test).

*Sources: D-221, D-224, D-228, D-229.*

#### FB-SIEGE-CRAWLER-12 — Death, drops and points · MUST

Its parts drop a weapon bonus 60 % of the time, its hidden weapons 30 %; its core always drops one
([common](../common.md), BOSS-57). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' and core's drop chances and its points are those of Tunable
  values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/siege_crawler.py` (`_SIEGE_CRAWLER`, `SIEGE_CRAWLER`) unless
named.

| Name | Value | Notes |
|------|-------|-------|
| size | 4.5 L (radius 76.5 px) | `stats.size` |
| core | health 5 200, radius 22, drop 1 | `coreHealth`, `coreRadius`, `coreDrop` |
| `mortar-left`, `mortar-right` | (∓34, -4), radius 13, health 1 450, shield, drop 0.6 | |
| mortar turrets | 7 px high; 1 barrel, bore 3.8, 4.5 px long; turntable radius 7.5; barrel axis 0.8 of it | `MORTAR` (`style` `mortar`) |
| `missile-left`, `missile-right` | (∓55, 17), radius 12, health 1 400, shield, drop 0.6 | |
| missile blocks | 4 ports, block top 8 px high | `missile_mount` |
| `cannon` | (0, -30), radius 15, health 1 800, shields, drop 0.6 | |
| cannon turret | 9 px high; 3 barrels 4 px apart, bore 1.6, 13 px long; dome radius 8 | `CANNON` |
| keep gun (core) | (0, -9), 11 px high; 2 barrels 3.6 px apart, bore 1.4, 9 px long; dome radius 5.5 | `mounts` `keep` |
| flak mortar (core) | (0, 27), 7.2 px high; 1 barrel, bore 3.2, 4 px long; turntable radius 5.5 | `mounts` `flak` |
| tail rotor (core) | (0, 10), 9.8 px high; 12 barrels, bore 0.9, 3.5 px long; hub radius 5 | `mounts` `tail-rotor` |
| hatches | octagons of radius 6.5 round (0, 10) and 7 round (0, 27); burst as their gun comes into use | `armour_region` `rotor-hatch`, `flak-hatch` (`mount`) |
| full health | 18 580 (core 5 200, parts 7 500, lances 2 880, racks 3 600) | BOSS-54; the 1-4 final boss (Refinery Titan) has 19 210 |
| points | 12 000; 1 200 a part | |
| ground speed | ×0.35 | |
| stop height | 0.75 | `stopFraction` |
| sway / bob | 30 px over 11 s / 4 px over 5 s | |
| cannon spread | aimed 3, 12° apart, red shells 135 px/s radius 7, every 2.8 s (first 1.4 s) | a sweep |
| mortar flak | 1 aimed orange shell 100 px/s radius 8, bursting after 1.3 s into 10 at 150 px/s, every 3.6 s (first 1 s / 2.8 s) | `MORTAR_FLAK` |
| missiles | 2 homing missiles, 30° apart, every 6.5 s (first 3.5 s / 6.75 s) | |
| core stage 0 | 1 aimed orange shell 120 px/s radius 8, every 3.2 s | keep gun |
| core stage 1 | 1 flak shell (red, 95 px/s, radius 9, bursting after 1.5 s into 12 at 145 px/s), every 3.4 s | flak mortar |
| core stage 2 | aimed 2 shells, 10° apart, every 3 s | keep gun |
| core stage 3 | flak every 3.2 s; bursts of 3 shells 0.25 s apart, every 3 s | flak mortar; keep gun |
| core stage 4 | flak every 2.6 s; aimed 3 shells 10° apart, every 2.6 s | flak mortar; keep gun |
| core stage 5 | ring of 12 red 180 px/s turning 9°, every 1.6 s; flak every 3 s | tail rotor; flak mortar |
| angry | the revealed weapons, BOSS-27 | `boss_build.angry_pattern` |
| transformations | both mortars destroyed; both missile blocks destroyed | `transformParts` |
| shed regions | deck: x 9..25, y -2..28, `shell`; cheeks: x 18..64, y -18..-40, `wing`; both mirrored | `DECK_PLATES`, `CHEEK_PLATES` |
| lances | (∓16, 12), radius 9, health 1 440, pod 6.5 px; laser 1.4 s every 7.5 s; first 1.2 s / 2.0 s | `hidden_weapon`, transformation 1 |
| racks | (∓42, -28), radius 9, health 1 800, pod 6 px; 2 missiles every 6 s; first 1.2 s / 2.4 s | `hidden_weapon`, transformation 2 |
| neon | red (1, 0.15, 0.1), shown yellow | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** It is registered in `BOSS_DESIGNS`, `BOSS_MODELS` and `BOSS_LOOK.neon` after the
  World bosses, and no level's boss table names it.
- **Simulated fight (2026-11-05, a part broken every 12 s):** 627 shots and 18 lasers, every one
  from a barrel's tip, a lens or a port (0 off); dead at 122 s. The bullets its flak bursts into are
  not counted there (they leave the shell, not a gun).
- **Triangles (scratch count, 2026-11-05):** about 5 400 drawn for its body, parts and armour, and
  2 900 for its gun mounts and hidden weapons: about 8 300 of the 10 000 budget (BOSS-53).
