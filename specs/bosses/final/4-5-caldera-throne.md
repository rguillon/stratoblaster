# Caldera Throne (4-5 final boss)

> **Area:** bosses · **Prefix:** `FB-CALDERA-THRONE` · **Related:** [common boss rules](../common.md),
> [4-5 Downtown](../../worlds/world-4/4-5-downtown.md), [World 4](../../worlds/world-4/world.md),
> [Ember Herald](../mini/4-5-ember-herald.md), [readability](../../graphics/readability.md),
> [shots](../../graphics/shots.md)

The Caldera Throne is the final boss of level 4-5, World 4's last boss and the game's last and
hardest. It is the enemy's war fortress, 6.5 L long: an armoured hull carrying a stepped keep and a
throne tower over its core, a prow gun deck, side bastions out to two magma cannons, missile batteries
and smokestacks aft, and two heat shield generators ahead of the keep. It was designed to rise from the
caldera's magma lake; since World 4 became the Metropolis (D-112) it keeps its name and its look and
is fought over downtown, the ground stopped under it. It transforms
twice: its flank armour bursts off for two gun decks, then its spine plating for two laser lances and
a missile rack. Everything shared by all bosses is in [bosses/common.md](../common.md); this file
only gives what is the Throne's own. Positions are px from the boss's centre, X right, Y up the screen
(its prow at -Y); heights are above the playfield.

## Requirements

### Look

#### FB-CALDERA-THRONE-01 — Silhouette · MUST

Seen from above, the Throne is a fortress about 6.5 L long (radius 3.25 L), prow down the screen: a
hull about 132 px wide and 202 px long, closed across the prow, side bastions reaching out to the
magma cannons' turntables about 104 px either side, a prow gun deck out to about 108 px ahead of the
centre, the keep's three tiers stepping up over the centre to the throne tower (its crown about 50 px
high), the heat shield generators either side ahead of the keep, the missile batteries aft on either
side, four smokestacks aft and an engine block across the stern.

**Acceptance criteria**
- Given the dev bosses viewer, when the Throne is shown, then it reads as a war fortress with a keep
  and a crowned tower at its heart (manual).

*Sources: P10-R11.*

#### FB-CALDERA-THRONE-02 — Cyber-Organic body · MUST

It is a living tyrant of the caldera (Cyber-Organic): its vast flesh back ribbed in bone and veined
with magma, a keep of flesh and armour rising over its heart, crowned in metal and gold. The keep's
three armoured tiers have their edges lit, molten slits in the lowest one and battlements on it; the
throne tower is an armoured drum with a crown of spikes and its charge light on top, where the core's
rings leave. Metal is grafted on as the prow's gun deck (twin cannons and a laser lens, charging
before they fire), the bastions, the missile hatches in their block behind the keep, the soot-black
smokestacks banded with neon (their mouths glowing), the watchtowers flanking the prow (beacons on
their roofs), rows of lamps along the deck's flanks, and the deck's molten seams, armour plates,
vents and hazard bands. The World 4 heat shows in heat-blued plates and soot.

**Acceptance criteria**
- Given the model, then it reads as one creature-fortress, not as parts stuck on a box (manual).

*Sources: P10-R11, P16-R06.*

**Discrepancy:** P16-R06 asks for the world's theme to stay recognisable ("a metropolis boss feels
like a city-sized organism"); the model keeps the volcanic war-fortress theme of its design (D-112
left the World 4 bosses unchanged); only its keep, towers and lamps hint at a city.

#### FB-CALDERA-THRONE-03 — Magma cannons · MUST

Each magma cannon turns on a low drum ringed with neon on its bastion: a heavy housing, soot-black on
its back, with neon flanks, a long barrel ringed with glowing cooling coils, its lens at the front
(about 38 px ahead of its pivot) glowing as the laser charges. Destroyed, a cannon and its drum are
hidden and leave nothing in their place.

**Acceptance criteria**
- Given a magma cannon stands, then it turns to aim at the player during its warning line (manual;
  unit: turret laser rule).

*Sources: P10-R11, P16-R06, D-225, D-167.*

#### FB-CALDERA-THRONE-04 — Missile batteries · MUST

Each missile battery is an armoured box with cut corners on the aft deck, six hatches on its top lit
as its missiles load, neon strips down its sides and a heat-blued blast shield at its front.
Destroyed, a battery is hidden and leaves nothing in its place.

**Acceptance criteria**
- Given the model, then each battery's six hatches sit at its missile muzzles (unit:
  `test_boss_models.py`).

*Sources: P10-R11, P16-R06, D-225.*

#### FB-CALDERA-THRONE-05 — Heat shield generators · MUST

Each heat shield generator is a molten core glowing in a crown of eight heat-sink fins with lit
edges, on an armoured drum ringed with neon; it carries no weapon. Destroyed, a generator is hidden
and leaves nothing in its place.

**Acceptance criteria**
- Given the model, then both generators stand ahead of the keep, either side of the centre line
  (manual).

*Sources: P10-R11, P16-R06, D-225.*

#### FB-CALDERA-THRONE-06 — Lights and colours · MUST

Its registered neon is crimson (`caldera-throne`), with gold as its second colour over its whole hull;
like every boss's warm lights both are drawn bright yellow (see
[readability](../../graphics/readability.md)). Neon lights the hull's rim, the keep's tiers, the
stacks' bands, the turntables, the batteries' strips, the generators' drums and fins, the cannons'
flanks, the crown, the watchtowers' beacons and the deck's lamp rows; its molten seams, slits, coils
and veins are in the same yellow family. White charge lights sit in the prow's guns and lens, the
cannons' lenses, the hatches and the crown.

**Acceptance criteria**
- Given the model, then every neon and glowing seam is bright yellow (unit: enemy colour family
  tests).

*Sources: P10-R11, D-231.*

### Behaviour

#### FB-CALDERA-THRONE-07 — Entry, place and stopped ground · MUST

The Throne comes in from above the top edge and stops at 0.75 of the playfield's height. In place it
sways up to 22 px either side over 12 s and bobs 5 px over 5.5 s. While it is fought the ground stops
(×0): the only World 4 fight over a still ground.

**Acceptance criteria**
- Given the fight starts, then the ground stops and the boss stops at 0.75 of the playfield height
  (unit: `test_world_boss.py`, which also checks it sways no further than its parts stay in reach;
  design values in the config).
- Given e2e `?level=4-5&boss=final`, then 4-5 starts at the Caldera Throne's arrival (e2e:
  `test_world_4.py`).

*Sources: P10-R11.*

#### FB-CALDERA-THRONE-08 — Parts and health · MUST

The Throne has a core (hit radius 28 px, 7 400 HP) and six original parts: two magma cannons (16 px,
2 300 HP each) and two missile batteries (15 px, 2 000 HP each), which do not shield the core, and
two heat shield generators (15 px, 2 600 HP each), which do. Its full health is 21 200 HP with the
original parts, the most of any boss, and 33 160 HP with its five hidden weapons, which count in the
health bar from the start.

**Acceptance criteria**
- Given the design, then it has six original parts and five hidden ones, and among the original parts
  only the generators shield the core (unit: `test_caldera_throne.py`).

*Sources: P10-R11, D-088, D-221.*

#### FB-CALDERA-THRONE-09 — Magma cannon lasers · MUST

While they stand, in every stage, each magma cannon fires a laser every 5.5 s (1.6 s long, after its
1 s warning line) from its lens, the left one 2 s and the right one 4.75 s into a stage. The laser is
on its turret: the cannon follows the player slowly during the warning line and holds still while the
beam fires.

**Acceptance criteria**
- Given a magma cannon stands, then its beam leaves its lens, aimed by its turret (unit: design guns;
  turret laser rule).

*Sources: P10-R11.*

#### FB-CALDERA-THRONE-10 — Missile batteries · MUST

While they stand, in every stage, each battery fires 2 homing missiles (24° apart) every 4.6 s from
its cells, the left one 3.2 s and the right one 5.5 s into a stage.

**Acceptance criteria**
- Given a battery stands, then two missiles leave it every 4.6 s (unit: design stages).

*Sources: P10-R11.*

#### FB-CALDERA-THRONE-11 — Core: every attack kind, stage by stage · MUST

The core fires from the prow's twin cannons and lens, the crown of the throne tower and the missile
hatches behind the keep, a new kind of attack at each stage until it fires them all (stage k: k parts
destroyed; from the sixth on, its last pattern):
- stage 0: bursts of 4 `magenta` (215 px/s, 0.11 s apart) every 2.2 s;
- stage 1: a fan of 7 `blue` (210 px/s, 12° apart) every 2.1 s;
- stage 2: a magma bomb aimed at the player every 2.8 s (`magenta`, 115 px/s, radius 7 px, bursting
  after 1.05 s into a ring of 9 `blue` at 195 px/s) and aimed spreads of 3 `purple` (205 px/s, 10°
  apart) every 2.1 s;
- stage 3: a ring of 12 `purple` every 1.4 s, turning 9°, and bursts of 3 `magenta` every 2.3 s;
- stage 4: 2 homing missiles from the hatches (30° apart) every 4.2 s, a fan of 5 `blue` (14° apart)
  every 2.2 s and bursts of 3 `magenta` every 2.5 s;
- stage 5: the prow laser straight down every 5 s (1.5 s long), a ring of 14 `purple` every 1.7 s and
  a magma bomb every 2.7 s;
- stage 6: everything at once, with a spiral of its own used by no earlier stage: rings of 18
  `purple` every 1 s turning 10°, the laser every 5 s, 2 missiles every 5 s, a fan of three magma
  bombs (30° apart) every 3.2 s, bursts of 4 `magenta` every 2.4 s and aimed spreads of 3 `blue`
  (12° apart) every 3 s.

**Acceptance criteria**
- Given the design, then it has one stage per original part plus one, its last stage fires every
  attack kind (bullets, fans, rings, bursts, bombs, missiles, laser), and its spiral of 18 is used by
  no earlier stage (unit: `test_caldera_throne.py`).

*Sources: P10-R11, D-088.*

#### FB-CALDERA-THRONE-12 — Laser colour · MUST

Its lasers (the magma cannons', the prow's and the hidden lances') are drawn in its own colour: its
crimson neon moved into the enemy shots' family, an amber (about [0.95, 0.75, 0.05]) round a
white-hot core, the warning line with a white core as all World 4 warning lines (see
[shots](../../graphics/shots.md)).

**Acceptance criteria**
- Given a magma cannon fires, then its beam is amber, not crimson (unit: `enemy_lasers.color_of`).

*Sources: P10-R11, D-072.*

#### FB-CALDERA-THRONE-13 — Rage · MUST

After the pause that follows each destroyed part, the Throne is angry: it fires two crossing spirals
and a vortex (a fast-turning spiral and bursts at the player) at once, at heat 14, each at half the
rate (`magenta` and `purple`, `blue` and `magenta`): about 132 bullets a second in all, at 232 px/s,
the hottest bullet hell of the game.

**Acceptance criteria**
- Given a part is destroyed, when its pause is over, then the core fires both angry patterns for the
  rage time (unit: `test_boss_rage.py`, `test_caldera_throne.py`).

*Sources: D-088, D-063.*

#### FB-CALDERA-THRONE-14 — First transformation: flank armour bursts off · MUST

The Throne transforms a first time when 2 of its 6 original parts are destroyed. Its flank armour
bursts off: a region either side from 34 px to 106 px out, from 53 px ahead of the centre to 15 px
behind it, above 2.2 px high (round the bastions). Under each a dark metal `wing` frame (ribs across
and two spars) shows. The boss stays one object after it.

**Acceptance criteria**
- Given two original parts are destroyed, then the boss transforms and its flank regions burst off
  (unit: `test_boss_kinds.py`, `test_boss_armour.py`).
- Given the boss after its first transformation, then nothing of it hangs in the air (unit:
  `test_d227_the_boss_holds_together_in_every_state`).

*Sources: D-221, D-224, D-227.*

#### FB-CALDERA-THRONE-15 — First hidden weapons: two gun decks · MUST

The first transformation reveals two gun decks (batteries) on the bared flanks, 50 px either side of
the centre and 19 px ahead of it (radius 12 px, pods 14.2 px high, 2 080 HP each, 30 % drop chance).
They shield the core and fire `magenta` fans straight down as every battery does (see
[common](../common.md)), the left one 1.2 s and the right one 2.0 s into a stage.

**Acceptance criteria**
- Given the first transformation is over, then both gun decks are live targets that fire (unit:
  `test_boss_kinds.py` weapon checks).

*Sources: D-221, D-229.*

#### FB-CALDERA-THRONE-16 — Second transformation: spine plating bursts off · MUST

The Throne transforms a second time when 4 of its 6 original parts are destroyed. Its spine plating
bursts off: one region across the centre line, 34 px either side, from 80 px ahead of the centre to
103.1 px behind it, above 11.5 px high (the keep's upper works and the deck's top). Under it a dark
metal `shell` frame (a lattice) shows. The boss stays one object after it.

**Acceptance criteria**
- Given four original parts are destroyed, then the boss transforms a second time and its spine
  region bursts off (unit: `test_boss_kinds.py`, `test_boss_armour.py`).
- Given the boss after its second transformation, then nothing of it hangs in the air (unit:
  `test_d227_the_boss_holds_together_in_every_state`).

*Sources: D-221, D-224, D-227.*

#### FB-CALDERA-THRONE-17 — Second hidden weapons: two lances and a missile rack · MUST

The second transformation reveals, on the bared spine, two laser lances aft, 14 px either side of
the centre line and 75 px behind the centre (radius 12 px, pods 14.2 px high, 2 600 HP each), firing
their lasers straight down the screen, and a missile rack on the centre line 48 px ahead of the centre
(radius 12 px, pod 13.4 px high, 2 600 HP), firing homing missiles, as those kinds do (see
[common](../common.md)); first 1.2 s, 2.0 s and 1.6 s into a stage. They shield the core and drop a
bonus 30 % of the time. Its fire goes up at each transformation (about 6.5, then 10.5, then 14.2
weighted shots a second).

**Acceptance criteria**
- Given the second transformation is over, then the lances and the rack are live targets that fire,
  of kinds not revealed at the first (unit: `test_boss_kinds.py`).

*Sources: D-221, D-229.*

#### FB-CALDERA-THRONE-18 — Points, drops and the end of World 4 · MUST

Destroying the Throne scores 26 000 points, the most of any boss, and each part destroyed 2 600. Its
original parts drop a bonus 60 % of the time, its hidden weapons 30 %, and its core always drops one.
Its death ends level 4-5, the last level of the game.

**Acceptance criteria**
- Given a generator is destroyed, then the score rises by 2 600 (unit: scoring rule, design values).
- Given e2e `?level=4-5&boss=final`, when K destroys the Throne, then the level is complete and the
  level select highlights 4-5 (e2e: `test_world_4.py`).

*Sources: P07-R07, P11-R01, D-088.*

## Tunable values

All in `src/game/config/bosses/world_4/caldera_throne.py` (`CALDERA_THRONE`) unless noted.

| Name | Value | Notes |
|------|-------|-------|
| level | 4-5, final | `src/game/config/world_4/bosses.py` `WORLD_4_BOSSES` |
| size | 6.5 L (radius 110.5 px) | `stats.size` |
| core | radius 28 px, 7 400 HP | `coreRadius`, `coreHealth` |
| magma cannons | (±88, -8), radius 16, 2 300 HP, no shield, on turrets | `CALDERA_PARTS.magma` |
| missile batteries | (±56, 46), radius 15, 2 000 HP, no shield | `CALDERA_PARTS.battery` |
| heat shield generators | (±34, -52), radius 15, 2 600 HP, shield, no weapon | `CALDERA_PARTS.shield` |
| full health | 21 200 (33 160 with hidden weapons) | D-088 |
| stop / sway / bob | 0.75 / 22 px, 12 s / 5 px, 5.5 s | `stopFraction`, `sway`, `bob` |
| ground speed | ×0 | `groundSpeed` |
| muzzles | cannon lenses (±88, -46, 10), battery cells x ±50 / ±62, y 36 / 46 / 56, 15.1 high; prow guns (±10, -104, 10), lens (0, -108, 9), crown (0, 4, 50), hatches (±8, 58 / 68, 10.1) | `CALDERA_*` |
| magma lasers | every 5.5 s, 1.6 s, first 2 / 4.75 s, on turrets | stage volleys |
| batteries | 2 missiles, 24°, every 4.6 s, first 3.2 / 5.5 s | `volley.missiles` |
| prow laser | every 5 s, 1.5 s (stages 5 and 6) | core stages |
| magma bomb | 115 px/s, radius 7, bursts after 1.05 s into 9 `blue` at 195 px/s | `MAGMA_BOMB` |
| bullets | `magenta` 215, `blue` 210, `purple` 205 px/s | radius 4 |
| rage | spirals + vortex, heat 14, half each | `rage.spirals`, `rage.vortex` |
| transformations | at 2, then 4 original parts destroyed | `src/game/sim/boss_build.py` `default_transforms` |
| flank regions | x 34..106 (mirrored), y -53..15, above 2.2, `wing` | form 1 |
| spine | x -34..34, y -80..103.1, above 11.5, `shell` | form 2 |
| gun decks | (±50, -19), radius 12, pod 14.2, 2 080 HP, `magenta`, first 1.2 / 2.0 s | form 1 (`battery`) |
| lances | (±14, 75), radius 12, pod 14.2, 2 600 HP, first 1.2 / 2.0 s | form 2 |
| rack | (0, -48), radius 12, pod 13.4, 2 600 HP, first 1.6 s | form 2 |
| drops | parts 0.6, hidden weapons 0.3, core 1 | `fpart`, `coreDrop` |
| points | 26 000 (2 600 a part) | `points`, `boss_part_points` |
| neon | [0.95, 0.05, 0.22], drawn [0.95, 0.95, 0.05]; laser [0.95, 0.75, 0.05] | `src/game/config/boss_look.py` `BOSS_LOOK.neon["caldera-throne"]` |

## Notes

- Phase 10 fight time with the D-055 bot: 137.6 s, before the hidden weapons (D-221). Its model was
  allowed up to 7 000 triangles in phase 10 (6 000 for the other bosses).
- The Caldera Throne is the game's last boss since World 5 was dropped (D-089).
- Its full health takes its place in World 4's boss ordering, the Throne being the hardest boss of
  the game and still beatable (P10-R12, see [World 4](../../worlds/world-4/world.md)).
