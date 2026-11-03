# Foundry Ark (4-4 final boss)

> **Area:** bosses · **Prefix:** `FB-FOUNDRY-ARK` · **Related:** [common boss rules](../common.md),
> [4-4 Business district](../../worlds/world-4/4-4-business-district.md),
> [World 4](../../worlds/world-4/world.md), [Furnace Drake](../mini/4-4-furnace-drake.md),
> [Hornet](../../enemies/hornet.md), [readability](../../graphics/readability.md),
> [shots](../../graphics/shots.md)

The Foundry Ark is the final boss of level 4-4, met at the end of the level. It is a huge flying
foundry 6 L long: an iron deck carrying a blast furnace at its heart (the core), slag channels
glowing out to two crucibles hung aft, a chimney row on the foredeck, a missile battery on the bow
and two rail cannons on outriggers. It was designed for the Volcanic Lands' forge belt; since World 4
became the Metropolis (D-112) it keeps its name and its look and flies over the business district.
It transforms twice: its fore flanks burst off for two gun batteries, then its aft wings and spine
for two gatlings and a drone hangar. Everything shared by all bosses is in
[bosses/common.md](../common.md); this file only gives what is the Ark's own. Positions are px from
the boss's centre, X right, Y up the screen (its bow at -Y); heights are above the playfield.

## Requirements

### Look

#### FB-FOUNDRY-ARK-01 — Silhouette · MUST

Seen from above, the Ark is a foundry ship about 6 L long (radius 3 L), bow down the screen: a deck
about 124 px wide and 198 px long, closed across the bow, outriggers reaching out to the rail
cannons' turntables about 86 px either side, the blast furnace's stack rising about 36 px at its
centre, the chimney row across the foredeck 50 px ahead of it, the missile battery on the bow ahead
of the chimneys, the two crucibles in their gantries aft either side, and an engine block across
the stern.

**Acceptance criteria**
- Given the dev bosses viewer, when the Ark is shown, then it reads as a flying foundry with a
  furnace, chimneys, crucibles and two long rail cannons (manual).

*Sources: P10-R11.*

#### FB-FOUNDRY-ARK-02 — Cyber-Organic body · MUST

It is a living colossus (Cyber-Organic): its broad back scorched flesh ribbed in bone, its blast
furnace a swollen heart (an octagonal hearth, a tapering stack, glowing slits, the furnace door and
the twin tap guns low on its front), slag running in its veins and in channels glowing across the
deck from the furnace to the crucibles. Metal is grafted on as its stacks, engines (nozzles at the
stern), rails and guns, and as the yard on its deck: casting sheds with sawtooth roofs and
furnace-lit windows along its sides, ore wagons heaped with glowing ore on rails between the furnace
and the battery, pipe runs from the furnace to the chimney row, molten seams between the deck
plates, rust on the old plates, soot, and lamps on the deck's corners.

**Acceptance criteria**
- Given the model, then it reads as one creature carrying a foundry, not as parts stuck on a box
  (manual).

*Sources: P10-R11, P16-R06.*

**Discrepancy:** P16-R06 asks for the world's theme to stay recognisable ("a metropolis boss feels
like a city-sized organism"); the model keeps the volcanic foundry theme of its design (D-112 left
the World 4 bosses unchanged); only its sheds and yard hint at buildings.

#### FB-FOUNDRY-ARK-03 — Rail cannons · MUST

Each rail cannon turns on a low drum ringed with neon at the end of its outrigger: an armoured
breech, two long rails out to the emitter between their tips (about 40 px ahead of its pivot),
glowing coils wound round the rails where the charge builds, the emitter lit as the laser charges.
Destroyed, a rail cannon and its drum are hidden and leave nothing in their place.

**Acceptance criteria**
- Given a rail cannon stands, then it turns to aim at the player during its warning line (manual;
  unit: turret laser rule).

*Sources: P10-R11, P16-R06, D-225, D-167.*

#### FB-FOUNDRY-ARK-04 — Chimney row · MUST

The chimney row is four tall stacks on a brick-dark plinth across the foredeck, sooty at the top
with a heat glow under their lips and a lamp on each; it carries no weapon. Destroyed, it is hidden
and leaves nothing in its place.

**Acceptance criteria**
- Given the model, then the four chimneys stand across the foredeck ahead of the furnace (manual).

*Sources: P10-R11, P16-R06, D-225.*

#### FB-FOUNDRY-ARK-05 — Missile battery · MUST

The missile battery on the bow is an armoured block with four hatches on its top, lit as missiles
load, and hazard strips down its sides. Destroyed, it is hidden and leaves nothing in its place.

**Acceptance criteria**
- Given the model, then the battery's four hatches sit at its missile muzzles (unit:
  `test_boss_models.py`).

*Sources: P10-R11, P16-R06, D-225.*

#### FB-FOUNDRY-ARK-06 — Crucibles · MUST

Each crucible is a heavy bucket brimming with glowing molten metal, hung on chains from a gantry
aft, a pouring lip on its inboard side and a hot band round its belly. Destroyed, it is hidden and
leaves nothing in its place.

**Acceptance criteria**
- Given the model, then both crucibles hang in their gantries clear of the furnace (manual).

*Sources: P10-R11, P16-R06, D-225.*

#### FB-FOUNDRY-ARK-07 — Lights and colours · MUST

Its registered neon is orange (`foundry-ark`), its molten metal hotter and yellower and its warning
lamps red in the design; like every boss's warm lights they are all drawn bright yellow (see
[readability](../../graphics/readability.md)). Neon lights the deck's rim, the turntables, the
battery's strips and the lamps; the slag channels, molten seams, crucibles, ore, coils and furnace
slits glow in the same yellow family. White charge lights sit in the rail emitters, the battery's
hatches, the tap guns and the furnace's throat.

**Acceptance criteria**
- Given the model, then every neon and glowing seam is bright yellow (unit: enemy colour family
  tests).

*Sources: P10-R11, D-231.*

### Behaviour

#### FB-FOUNDRY-ARK-08 — Entry, place and ground speed · MUST

The Ark comes in from above the top edge and stops at 0.75 of the playfield's height. In place it
sways up to 28 px either side over 12 s and bobs 5 px over 5.5 s. While it is fought the ground runs
at ×0.3 the level's speed.

**Acceptance criteria**
- Given the fight starts, then the ground slows to ×0.3 and the boss stops at 0.75 of the playfield
  height (unit: `test_world_boss.py` for the rule; design values in the config).

*Sources: P10-R11.*

#### FB-FOUNDRY-ARK-09 — Parts and health · MUST

The Ark has a core (hit radius 28 px, 5 600 HP) and six original parts: two rail cannons (19 px,
1 500 HP each) and the chimney row (16 px, 2 400 HP), which shield the core, and the missile battery
(13 px, 900 HP) and two crucibles (15 px, 1 450 HP each), which do not. The battery hangs in front of
the chimneys and the crucibles stand clear of the furnace, so every part can be shot. Its full
health is 14 800 HP with the original parts, 25 840 HP with its five hidden weapons, which count in
the health bar from the start.

**Acceptance criteria**
- Given the design, then it has six original parts and five hidden ones, and only the rails, the
  chimneys and the hidden weapons shield the core (unit: `test_foundry_ark.py`).

*Sources: P10-R11, D-088, D-221.*

#### FB-FOUNDRY-ARK-10 — Rail cannon lasers · MUST

While they stand, in every stage, each rail cannon fires a laser every 6.5 s (1.6 s long, after its
1 s warning line) from the emitter between its rails, the left one 2 s and the right one 5.2 s into
a stage. The laser is on its turret: the cannon follows the player slowly during the warning line
and holds still while the beam fires.

**Acceptance criteria**
- Given a rail cannon stands, then its beam leaves its emitter, aimed by its turret (unit: design
  guns; turret laser rule).

*Sources: P10-R11.*

#### FB-FOUNDRY-ARK-11 — Missile battery · MUST

While it stands, in every stage, the battery fires 2 homing missiles (26° apart) every 5.5 s from
its hatches, first 3.5 s into a stage.

**Acceptance criteria**
- Given the battery stands, then two missiles leave it every 5.5 s (unit: design stages).

*Sources: P10-R11.*

#### FB-FOUNDRY-ARK-12 — Crucibles spill when destroyed · MUST

A crucible fires nothing while it stands. Destroyed, it spills its molten metal: it bursts once into
a ring of 14 `orange` bullets (185 px/s) from where it hung.

**Acceptance criteria**
- Given a crucible is destroyed, then a ring of 14 bullets leaves its place, once (unit:
  `test_world_boss.py` break-ring rule; design `breakRings`).

*Sources: P10-R11.*

#### FB-FOUNDRY-ARK-13 — Core patterns by stage · MUST

The core (the blast furnace) fires from its twin tap guns and from its throat at the top of its
stack, a new pattern at each stage (stage k: k parts destroyed; from the sixth on, its last
pattern):
- stage 0: bursts of 4 `red` (215 px/s, 0.12 s apart) every 2.4 s;
- stage 1: a fan of 5 `orange` (210 px/s, 13° apart) every 2.3 s;
- stage 2: a blob of slag aimed at the player every 3 s (`orange`, 115 px/s, radius 7 px, bursting
  after 1.1 s into a ring of 9 `red` at 195 px/s) and aimed spreads of 3 `magenta` (205 px/s, 10°
  apart) every 2.2 s;
- stage 3: a ring of 12 `orange` every 1.9 s, turning 7°, and bursts of 3 `red` every 2.6 s;
- stage 4: a fan of 7 `magenta` (11° apart) every 2.4 s and a four-armed spiral (rings of 4 `red`
  every 0.55 s, turning 19°);
- stage 5: two spirals of 5 turning opposite ways (`orange` 17° and `purple` -19°, every 0.5 s);
- stage 6: two rings of 16 turning opposite ways (`orange` 9° and `red` -11°, every 1.1 s), a fan of
  three slag blobs (30° apart) every 3.2 s and bursts of 4 `magenta` every 2.6 s, used by no earlier
  stage.

**Acceptance criteria**
- Given the design, then it has one stage per original part plus one, and the last stage's rings
  and blobs are used by no earlier stage (unit: `test_foundry_ark.py`).

*Sources: P10-R11, D-088.*

#### FB-FOUNDRY-ARK-14 — Laser colour · MUST

Its rail cannons' lasers are drawn in its own colour: its orange neon moved into the enemy shots'
family, an orange (about [1, 0.38, 0.12]) round a white-hot core.

**Acceptance criteria**
- Given a rail cannon fires, then its beam is orange (unit: `enemy_lasers.color_of`).

*Sources: P10-R11, D-072.*

#### FB-FOUNDRY-ARK-15 — Rage · MUST

After the pause that follows each destroyed part, the Ark is angry: it fires a curtain (fans
sweeping across the screen and back over a ring) and two crossing spirals at once, at heat 13, each
at half the rate (`orange` and `red`, `red` and `orange`): about 124 bullets a second in all, at
224 px/s.

**Acceptance criteria**
- Given a part is destroyed, when its pause is over, then the core fires both angry patterns for the
  rage time (unit: `test_boss_rage.py`, `test_foundry_ark.py`).

*Sources: D-088, D-063.*

#### FB-FOUNDRY-ARK-16 — First transformation: fore flank armour bursts off · MUST

The Ark transforms a first time when 2 of its 6 original parts are destroyed. Its fore flank
plates burst off: pieces of the model's own ([common](../common.md), BOSS-42), an iron plate either
side lying on the flesh deck, 4 to 5.5 px high, from 20 px out to the deck's edge (60 px out at
the widest, 44.9 at the bow end), from 78 px to 13.5 px ahead of the centre; on each the hazard
paint, a vent, a soot stain and a molten seam between the deck plates. Each bursts into plates
cracked from its outline at its own height. Under each the flat deck and a dark metal `wing` frame
(ribs across and two spars) show. The gun batteries lie folded under them. The boss stays one
object after it.

**Acceptance criteria**
- Given two original parts are destroyed, then the boss transforms and its fore flank regions burst
  off (unit: `test_boss_kinds.py`, `test_boss_armour.py`).
- Given the boss after its first transformation, then nothing of it hangs in the air (unit:
  `test_d227_the_boss_holds_together_in_every_state`).

*Sources: D-221, D-224, D-227, D-254.*

#### FB-FOUNDRY-ARK-17 — First hidden weapons: two gun batteries · MUST

The first transformation reveals two gun batteries on the bared fore flanks, 41 px either side of
the centre and 43 px ahead of it (radius 13 px, pods 10.2 px high, 1 920 HP each, 30 % drop chance).
They shield the core and fire `orange` fans straight down as every battery does (see
[common](../common.md)), the left one 1.2 s and the right one 2.0 s into a stage.

**Acceptance criteria**
- Given the first transformation is over, then both batteries are live targets that fire (unit:
  `test_boss_kinds.py` weapon checks).

*Sources: D-221, D-229.*

#### FB-FOUNDRY-ARK-18 — Second transformation: aft wings and spine burst off · MUST

The Ark transforms a second time when 4 of its 6 original parts are destroyed. Its aft wing plates
and its spine plating, pieces of the model's own ([common](../common.md), BOSS-42), burst off. Each
wing plate is an iron plate lying on the flesh deck, 4 to 5.5 px high, from 30 px out to the deck's
edge (62 px out at the widest), from 13.5 px ahead of the centre to 45 px behind it; on it the
forward casting shed, the magma vein's middle run, a gland, a vent and a molten seam. The spine
plating is the furnace's crown plate, an octagon 21 px across the hearth's flat top (16.8 to 18 px
high, its sides facing the axes), carrying the furnace's stack (tapering up to 37.5 px, sooted at
its lip, ringed in orange, the throat's charge light in its mouth); the core's ring volleys keep
leaving from the throat's height. Each bursts into plates cracked from its outline at the plate's
own height. They leave dark metal frames: `wing` frames on the deck where the wing plates lay, a
`shell` lattice on the hearth's top. The gatlings lie folded under the wing plates and the drone
hangar under the crown, in the hearth. The boss stays one object after it.

**Acceptance criteria**
- Given four original parts are destroyed, then the boss transforms a second time and these regions
  burst off (unit: `test_boss_kinds.py`, `test_boss_armour.py`).
- Given the boss after its second transformation, then nothing of it hangs in the air (unit:
  `test_d227_the_boss_holds_together_in_every_state`).

*Sources: D-221, D-224, D-227, D-254.*

#### FB-FOUNDRY-ARK-19 — Second hidden weapons: two gatlings and a drone hangar · MUST

The second transformation reveals two gatling turrets on the bared wings, 48 px either side of the
centre and 13 px behind it (radius 10 px, pods 8.8 px high, 2 400 HP each), firing `orange` bursts
and following the player, and a drone hangar on the centre line 19 px ahead of the centre (radius
10 px, pod 22.4 px high, 2 400 HP), its doors sliding apart to launch 2 [Hornets](../../enemies/hornet.md)
every 7 s, as those kinds do (see [common](../common.md)); first 1.2 s, 2.0 s and 1.6 s into a
stage. They shield the core and drop a bonus 30 % of the time. It is World 4's only hangar. Its fire
goes up at each transformation (about 4.9, then 9.4, then 21.4 weighted shots a second).

**Acceptance criteria**
- Given the second transformation is over, then the gatlings fire and the hangar launches Hornets, of
  kinds not revealed at the first (unit: `test_boss_kinds.py`: kinds, hangars on final bosses only,
  at most one a world).

*Sources: D-221, D-229.*

#### FB-FOUNDRY-ARK-20 — Points and drops · MUST

Destroying the Ark scores 20 000 points, and each part destroyed 2 000. Its original parts drop a
bonus 60 % of the time, its hidden weapons 30 %, and its core always drops one.

**Acceptance criteria**
- Given a crucible is destroyed, then the score rises by 2 000 (unit: scoring rule, design values).

*Sources: P07-R07, P11-R01, D-088.*

## Tunable values

All in `src/game/config/bosses/world_4/foundry_ark.py` (`FOUNDRY_ARK`) unless noted.

| Name | Value | Notes |
|------|-------|-------|
| level | 4-4, final | `src/game/config/world_4/bosses.py` `WORLD_4_BOSSES` |
| size | 6 L (radius 102 px) | `stats.size` |
| core | radius 28 px, 5 600 HP | `coreRadius`, `coreHealth` |
| rail cannons | (±72, -12), radius 19, 1 500 HP, shield, on turrets | `ARK_PARTS.rail` |
| chimney row | (0, -50), radius 16, 2 400 HP, shield, no weapon | `ARK_PARTS.chimneys` |
| missile battery | (0, -82), radius 13, 900 HP, no shield | `ARK_PARTS.battery` |
| crucibles | (±60, 42), radius 15, 1 450 HP, no shield | `ARK_PARTS.crucible` |
| full health | 14 800 (25 840 with hidden weapons) | D-088 |
| stop / sway / bob | 0.75 / 28 px, 12 s / 5 px, 5.5 s | `stopFraction`, `sway`, `bob` |
| ground speed | ×0.3 | `groundSpeed` |
| muzzles | rail emitters (±72, -52, 8), battery cells (±5.5, -87 / -77, 9.1), taps (±9, -33, 7), throat (0, 0, 36) | `ARK_*` |
| rail lasers | every 6.5 s, 1.6 s, first 2 / 5.2 s, on turrets | stage volleys |
| battery | 2 missiles, 26°, every 5.5 s, first 3.5 s | `volley.missiles` |
| crucible spill | ring of 14 `orange`, 185 px/s | `breakRings`, `SPILL` |
| slag blob | 115 px/s, radius 7, bursts after 1.1 s into 9 `red` at 195 px/s | `SLAG` |
| bullets | `red` 215, `orange` 210, `magenta` 205, `purple` 200 px/s | radius 4 |
| rage | curtain + spirals, heat 13, half each | `rage.curtain`, `rage.spirals` |
| transformations | at 2, then 4 original parts destroyed | `src/game/sim/boss_build.py` `default_transforms` |
| fore flanks | the fore deck from x 20 to its edge (mirrored): (20, -78), (44.9, -78), (56, -60), (60, -20), (60.3, -13.5), (20, -13.5); `wing`; plate 4–5.5 px | form 1, `foundry_ark_armour.py` |
| aft wings | the aft deck from x 30 to its edge (mirrored): (30, -13.5), (60.3, -13.5), (62, 40), (61.2, 45), (30, 45); `wing`; plate 4–5.5 px | form 2 |
| spine | an octagon 21 px across the hearth's top, `shell`, not mirrored; crown plate 16.8–18 px, the stack on it | form 2, `octagon(21)` |
| batteries | (±41, -43), radius 13, pod 10.2, 1 920 HP, `orange`, first 1.2 / 2.0 s | form 1 |
| gatlings | (±48, 13), radius 10, pod 8.8, 2 400 HP, `orange`, first 1.2 / 2.0 s | form 2 |
| hangar | (0, -19), radius 10, pod 22.4, 2 400 HP; 2 Hornets every 7 s, first 1.6 s | form 2; `src/game/config/bosses/weapon_kinds.py` `WEAPON_FIRE.hangar` |
| drops | parts 0.6, hidden weapons 0.3, core 1 | `fpart`, `coreDrop` |
| points | 20 000 (2 000 a part) | `points`, `boss_part_points` |
| neon | [1, 0.55, 0.12], drawn [1, 1, 0.12]; laser [1, 0.38, 0.12] | `src/game/config/boss_look.py` `BOSS_LOOK.neon["foundry-ark"]` |

## Notes

- Phase 10 fight time with the D-055 bot: 126.2 s, before the hidden weapons (D-221). The rails were
  placed at ±72 px and the crucibles at ±60 px for the bot's spread (as D-081), and the battery on
  the bow ahead of the chimney row.
- Its full health takes its place in World 4's boss ordering (P10-R12, see
  [World 4](../../worlds/world-4/world.md)).
