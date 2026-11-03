# Sky Temple (3-3 final boss)

> **Area:** bosses · **Prefix:** `FB-SKY-TEMPLE` · **Related:** [common boss rules](../common.md),
> [3-3 Workers' quarter](../../worlds/world-3/3-3-workers-quarter.md),
> [World 3](../../worlds/world-3/world.md), [Stone Idol](../mini/3-3-stone-idol.md),
> [readability](../../graphics/readability.md)

The Sky Temple is the final boss of level 3-3, met at the level's end. It is a flying stepped pyramid
fortress 5.5 L across, grown on the back of a living beast: an obelisk on each corner of its lowest
tier, a beacon tower before the sanctum on its summit, a grand stair up its front, and the rock it was
torn from hanging under it. It was designed for the old Jungle world's lost temples and, since World
3 became the factories-to-garden-villages world (D-111), it keeps its name and look and flies over the
workers' quarter. It transforms twice by changing shape: its corner wedges slide out, carrying new
guns. Its core fires every bullet pattern. Shared rules are in [bosses/common.md](../common.md); this
file only gives what is the Temple's own.

## Requirements

### Look

#### FB-SKY-TEMPLE-01 — Silhouette · MUST

Seen from above, the Temple is a square stepped pyramid, its grand stair pointing down the screen:
four tiers 9 px high each, 148, 108, 88 and 68 px across, the sanctum on the 36 px high summit, an
obelisk standing on each corner of the lowest tier (60 px out and 62 px ahead or behind the centre),
and under its base an upside-down four-sided cone of rock. It is a 5.5 L boss (radius 2.75 L).

**Acceptance criteria**
- Given the dev bosses viewer, then it reads as a flying stepped pyramid with four corner obelisks
  (manual).

*Sources: P09-R09.*

#### FB-SKY-TEMPLE-02 — Cyber-Organic body · MUST

The lowest tier is the living beast itself: a huge, swollen body of moss-skinned flesh, its back flat
under the stone tiers it carries like a shell, roots of sinew hanging from it, veins climbing the tiers along
their diagonals up to the sanctum, and its reactors in flesh sacs at its back. Under the stones is the
dark metal of a fortress: a bank of thrusters at the back and armoured buttresses on its sides with
lights.

**Acceptance criteria**
- Given the model, then the beast's flesh shows under the lowest tier and veins climb the stones
  (manual).

*Sources: P16-R06.*

#### FB-SKY-TEMPLE-03 — Summit, stair and core guns · MUST

The grand stair runs up its front face from beyond the base to the summit, between walls with neon
balustrades. The sanctum on the summit (the core) has stepped roofs, a door framed in neon between two
pillars, twin cannons either side of the door (8 px out, 11 px ahead, 41 px high) and a crystal on its
roof (64 px high) for its rings and spirals. Braziers stand on the summit's corners and flare as the
next attack charges.

**Acceptance criteria**
- Given the model, then the twin cannons and the crystal stand at the design's muzzles (unit:
  `test_boss_models.py`).

*Sources: P09-R09.*

#### FB-SKY-TEMPLE-04 — Parts on the model · MUST

- Each **obelisk** (a part) is a plinth on the lowest tier's corner, a tapering stone shaft carved with
  neon glyphs on its four faces at three heights, a gilt pyramidion whose tip (56 px high) fires its
  spiral, and a vine climbing it.
- The **beacon** (a part) is a square tower at the front of the summit, a lantern burning with neon
  light under a gilt roof, and four missile tubes on the roof.

A destroyed part is hidden; a dark socket is left on the tier where each obelisk stood and on the
summit where the beacon stood.

**Acceptance criteria**
- Given K destroys an obelisk, then it disappears and a socket shows on the corner (manual).

*Sources: P09-R09, P16-R06, D-225, D-167.*

#### FB-SKY-TEMPLE-05 — Temple growth · MUST

Moss lies on the steps, vines are draped over the tiers' edges, roots hang under the rock's rim and
shrubs grow on the second tier to the left of the stair; the layout is a little asymmetric. The stone
is weathered on its top faces and darker in its recesses, the moss a clear green.

**Acceptance criteria**
- Given the model, then moss, vines and shrubs are visible, not mirrored exactly (manual).

*Sources: P09-R09, D-231.*

#### FB-SKY-TEMPLE-06 — Lights and colours · MUST

Its neon is its own gold (`sky-temple`) and a cyan it shares its lights with: under the enemy colour
rule the gold shows bright yellow and the cyan bright green. The lowest tier is trimmed in cyan and
the upper tiers in gold; the glyphs are gold; the stair's balustrades, the door's frame and the
beacon's lantern are cyan; the buttresses carry both. Its gilding is a body shade, greyed by the same
rule. White charge lights glow at the cannons' tips, the crystal, the braziers and the missile tubes.

**Acceptance criteria**
- Given the model, then every neon light is bright yellow or bright green (unit: enemy colour family
  tests).

*Sources: P09-R09, D-231.*

### Behaviour

#### FB-SKY-TEMPLE-07 — Entry, place and ground speed · MUST

The Temple stops at 0.74 of the playfield's height, sways up to 30 px either side over 11 s and bobs
6 px over 5 s. While it is fought the ground runs at ×0.3.

**Acceptance criteria**
- Given the fight starts, then the ground slows to ×0.3 (design values; common rule tests).

*Sources: P09-R09.*

#### FB-SKY-TEMPLE-08 — Parts and health · MUST

The core (hit radius 22 px, 3 550 HP) has five original parts: four obelisks (13 px, 1 000 HP each),
which shield the core, and the beacon (16 px, 2 400 HP), which does not. Its full health is 9 950 HP
with the original parts, 20 510 HP with its five hidden weapons.

**Acceptance criteria**
- Given the design, then it has five original parts and five hidden ones, the obelisks shielding the
  core (unit: `test_sky_temple.py`).

*Sources: P09-R09, P09-R10, D-081, D-221.*

#### FB-SKY-TEMPLE-09 — Part weapons · MUST

While they stand, in every stage:
- each obelisk turns its own spiral from its tip: rings of 4 `orange` bullets (200 px/s) every 1.6 s,
  turning 23° (front left), -23° (front right), -19° (back left) and 19° (back right);
- the beacon fires 2 homing missiles (30° apart) every 5.5 s from its tubes.

**Acceptance criteria**
- Given the four obelisks stand, then four spirals turn, the front and back ones on each side turning
  opposite ways (unit: design volleys).

*Sources: P09-R09, D-081.*

#### FB-SKY-TEMPLE-10 — Core patterns by stage: every bullet pattern · MUST

The core fires every bullet pattern, a new one at each stage, from its twin cannons and its crystal:
- stage 0: one aimed `red` bullet (210 px/s) every 2.8 s;
- stage 1: an aimed spread of 3 `red` (12° apart) every 2.6 s;
- stage 2: bursts of 4 `magenta` (195 px/s, 0.13 s apart) every 2.4 s;
- stage 3: a fan of 5 `blue` (205 px/s, 14° apart) every 2.4 s;
- stage 4: a ring of 12 `green` (190 px/s) every 2 s, and a fan of 7 `blue` (12° apart) every 2.6 s;
- stage 5 (alone): two spirals of 6 turning opposite ways every 0.6 s (`orange` 14°, `blue` -19°),
  and bursts of 3 `red` every 2.6 s.

**Acceptance criteria**
- Given the design, then it has six stages, aimed shots, spreads, bursts, fans and rings among them,
  and the last one's twin spirals are used by no earlier stage (unit: `test_sky_temple.py`).

*Sources: P09-R09, D-081.*

#### FB-SKY-TEMPLE-11 — Rage · MUST

After the pause that follows each destroyed part, it fires a vortex inside a blooming flower, each at
half the rate, at heat 7, in `orange` and `blue`.

**Acceptance criteria**
- Given a part is destroyed, when its pause is over, then the core fires the vortex and the flower
  together (unit: rage patterns).

*Sources: D-081, D-063.*

#### FB-SKY-TEMPLE-12 — Transformations on named parts · MUST

The Temple transforms when named parts are gone, not at a count: the first time once both back
obelisks are destroyed, the second once both front obelisks are destroyed. The back obelisks come
before the front ones in its parts' order, so the debug key K calls each transformation in turn.

**Acceptance criteria**
- Given both back obelisks are destroyed (whatever else is), then the first transformation starts;
  given both front ones then are, the second (unit: `test_boss_kinds.py`).

*Sources: D-230.*

#### FB-SKY-TEMPLE-13 — First transformation: back wedges slide out · MUST

At its first transformation ([common](../common.md), BOSS-42, BOSS-45):
- its two back corner **wedges** stay on and slide out diagonally, 15 px out and 15 px back: each is
  a piece drawn apart from the core, the corners of the first two stone tiers standing on the beast's
  flat back (from 34 px out and 20 px behind the centre to the tiers' edges, 54 and 44 px; 8.7 to
  27 px high, sunk 0.3 px into the back) with their gold trims and, on the right one, a patch of
  moss. The core's tiers are notched where they lie. Its region is the corner of the beast's plan
  (x 34..68, y 20..68, mirrored); a dark metal `wing` frame shows on the beast's back where each lay.
  A gun battery rides each wedge, ending at 70 px out and 50 px behind the centre (radius 10 px, pod
  24 px high, 1 920 HP each), firing `orange` fans straight down;
- its back **terrace** bursts off: the steps of the three stone tiers behind the sanctum's back wall
  (20 px behind the centre) between the back wedges, 34 px either side, 8.7 to 36 px high, with
  their gold trims, the two back braziers and moss on the top step. Its region (`back`, not
  mirrored) is x ±33, from 20 to 54 px behind the centre; it bursts into plates cracked from that
  outline and leaves a `shell` frame on the beast's back, and a mortar rises on the centre line,
  36 px behind the centre (radius 13 px, pod 41 px high, 1 920 HP), lobbing `orange` flak.

The weapons fire 1.2 s and 2.0 s (batteries) and 1.6 s (mortar) into a stage.

**Acceptance criteria**
- Given both back obelisks are destroyed, then the back wedges slide out with their batteries on them
  and the back terrace bursts off for the mortar (unit: `test_boss_kinds.py`; riding weapons end up
  on their piece).

*Sources: D-230, D-221, D-224, D-229, D-254.*

#### FB-SKY-TEMPLE-14 — Second transformation: front wedges slide out · MUST

At its second transformation its two front corner wedges (drawn as the back ones, the corners of
the first two tiers from 34 px out and 20 px ahead of the centre; their region the corner of the
beast's plan, x 34..68, y -68..-20, mirrored; moss on the left one) slide out 14 px out and 14 px
forward, a `wing` frame showing where each lay, and a heavy
cannon rides each, ending at 66 px out and 52 px ahead (radius 10 px, pod 24 px high, 2 400 HP each),
firing `orange` spreads of big shells, 1.2 s and 2.4 s into a stage. No part the player can hit stands
on a wedge as it moves (its obelisk is gone by then). It reveals no kind twice, fires no less after
each transformation than before, and stays one object in every state.

**Acceptance criteria**
- Given both front obelisks are destroyed, then the front wedges slide out with their cannons (unit:
  `test_boss_kinds.py`).
- Given each state, then nothing of it hangs in the air (unit:
  `test_d227_the_boss_holds_together_in_every_state`).

*Sources: D-230, D-221, D-229, D-227, D-254.*

#### FB-SKY-TEMPLE-15 — Points and drops · MUST

Destroying the Temple scores 15 000 points, and each part destroyed 1 500. Its original parts drop a
bonus 60 % of the time, its hidden weapons 30 %, and its core always drops one.

**Acceptance criteria**
- Given the core is destroyed, then a bonus drops and the score rises by 15 000 (unit: scoring and
  bonus rules, design values).

*Sources: P07-R07, P11-R01, D-055.*

## Tunable values

All in `src/game/config/bosses/world_3/sky_temple.py` (`SKY_TEMPLE`) unless noted. Px from the
boss's centre, X right, Y up the screen (its stair at -Y).

| Name | Value | Notes |
|------|-------|-------|
| size | 5.5 L (radius 93.5 px) | |
| tiers | half widths 74 / 54 / 44 / 34, 9 px high each | `src/game/view/bosses/world_3/sky_temple_parts.py` `TIERS` |
| core | radius 22 px, 3 550 HP | |
| obelisks | (±60, ±62), radius 13, 1 000 HP, shield; tips 56 px high | `TEMPLE_PARTS`, `TEMPLE_HEIGHTS` |
| beacon | (0, -28), radius 16, 2 400 HP, no shield | |
| full health | 9 950 (20 510 with hidden weapons) | P09-R10 band |
| stop / sway / bob | 0.74 / 30 px, 11 s / 6 px, 5 s | |
| ground speed | ×0.3 | |
| obelisk spirals | 4 × `orange` 200 px/s, every 1.6 s, turn ±23° / ±19° | |
| beacon missiles | 2, 30° apart, every 5.5 s | |
| rage | vortex + flower, heat 7, half share each | |
| transformations | on `transformParts`: back obelisks, then front ones | |
| back wedges | the beast's corner, x 34..68, y 20..68 (mirrored), slide (±15, 15); `wing` frame; the tiers' corners 8.7–27 px | form 1 |
| back terrace | x ±33, y 20..54, `shell`; the tiers' back steps 8.7–36 px | form 1 |
| front wedges | the beast's corner, x 34..68, y -68..-20 (mirrored), slide (±14, -14); `wing` frame; the tiers' corners 8.7–27 px | form 2 |
| batteries | (±70, 50), radius 10, pod 24, 1 920 HP, `orange` | form 1 |
| mortar | (0, 36), radius 13, pod 41, 1 920 HP, `orange` | form 1 |
| cannons | (±66, -52), radius 10, pod 24, 2 400 HP, `orange` | form 2 |
| points | 15 000 (1 500 a part) | |
| neon | gold [1, 0.8, 0.2]; cyan [0.2, 0.95, 1] | `BOSS_LOOK.neon["sky-temple"]`; `sky_temple_parts.py` `TEMPLE_CYAN` |

## Notes

- Phase 9 fight time with the D-055 bot: 102.4 s, before the hidden weapons were added (D-221).
- Known limits (D-224, D-230): the wedges' tiny decorations are checked to hold to them on a sampling
  grid, which holds for a 15 px slide; the pods of riding weapons stand as columns from the playfield
  up.
