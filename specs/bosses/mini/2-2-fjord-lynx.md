# Fjord Lynx — 2-2 mini boss

> **Area:** bosses · **Prefix:** `MB-FJORD-LYNX` · **Related:** [common.md](../common.md), [2-2 Mining mesas](../../worlds/world-2/2-2-mining-mesas.md), [World 2](../../worlds/world-2/world.md), [Harbour Kraken (2-2 final)](../final/2-2-harbour-kraken.md)

The Fjord Lynx is the mini boss of 2-2, met at half the level. It is a fast, low 3 L cyber-lynx of
cold flesh, crouched on two forelegs whose paws carry cannons, tufted antennas over its head and a
radar mast on its left flank, in cyan and white neon. Its radar mast is its rule: while it stands,
its guns aim at the player; once it is gone, they fire in preset directions. It was designed for the
fjords of the Frozen North; World 2 became the Industrial Desert (D-110) and the boss kept its name
and its frost. Everything all bosses share is in [common.md](../common.md).

## Requirements

### Look

#### MB-FJORD-LYNX-01 — Silhouette and size · MUST

The Fjord Lynx is `size` long. Seen from above it is a crouched cat: a low body broad at the
shoulders and narrow at the haunches, its head at the front between two forelegs reaching forward
to its paws, two tufted ears over the head, a short bobtail behind, and a radar mast standing on a
sponson on its left flank, behind the middle.

**Acceptance criteria**
- Given the bosses viewer, when it shows the Fjord Lynx, then it reads as a crouched cat with two forward paws and a mast on its left side.

*Sources: P08-R10, P16-R05.*

#### MB-FJORD-LYNX-02 — A living cyber-lynx · MUST

Its body is Cyber-Organic flesh with metal grafts (see [art direction](../../graphics/art-direction.md)),
drawn by code: a muscled body of cold teal flesh, rimed on top; a back and head of graphite flesh
with dark seams, the head's crown the plating it sheds (MB-FJORD-LYNX-06); bone ribs and a row of
ice spines down its back; forelegs of sinew, a sinew pulling each paw; a bobtail of sinew; reactor
sacs at the stern. Metal shows only on its haunches (frosted armour plates raised over the rear) and
where its guns are grafted. The ears are tufts of sinew on the crown, each with a dark metal whip
ending in a white light.

*Sources: P08-R10, P16-R05.*

#### MB-FJORD-LYNX-03 — Its parts and guns on the body · MUST

- Each paw: a pad of flesh, wider at the toes, three bone claws pointing to the nose, a metal armour
  plate where its twin-barrelled cannon is grafted on a turret.
- The radar mast: a metal mast grafted in a swollen mound of flesh on the sponson, ice crystals round
  it, a scanner bar across its top with a dish and white lights at its ends, a cyan ring round its
  foot.
- The core's gun: a chin cannon turning on the deck in front of the head.

*Sources: P08-R10, P16-R05.*

#### MB-FJORD-LYNX-04 — Lights and colours · MUST

Its neon is a pale cyan (`neon`), with white for its secondary lights. Cyan: stripes along both
sides of its back, glowing veins to its forelegs, lines along its flanks and paws, glands on its
deck, angry eyes on its head, the ears' marks and the mast's ring. White: a line down its spine, the
ears' tips, the scanner's end lights, a bar across each paw.

*Sources: P08-R10, P16-R05.*

#### MB-FJORD-LYNX-05 — Frost · MUST

It keeps the World 2 frost although World 2 is now a desert: snow packed on its rear deck and its
haunches, ice crystals on its flanks and tail, rows of icicles under its flanks and its stern,
frosted pads.

*Sources: P08-R10, D-110.*

#### MB-FJORD-LYNX-06 — What its transformation sheds · MUST

At its transformation the plating over its head is the armour it sheds ([common](../common.md),
BOSS-42), drawn as pieces of its own: the crown of the head, a loft of graphite flesh with dark seams
lying on the flattened head from the neck (3 px ahead of the centre, sunk in the head's slope) to a
point just over the deck 26 px ahead, 7 to 12.5 px high, the two ears on it; and a lobe of rimed
graphite flesh on the deck (5 to 6 px) either side of the chin cannon, from 24 to 40 px ahead, where
the ring emitters lie folded. Its region (`back`, not mirrored) is the crown's footprint (x ±9 at the
neck, ±10 from 24 px ahead) running into the two lobes (x 5.5 to 10, to 6.5 at the nose) round the
chin cannon's channel. It bursts into the crown's three slices, the two ears and the two lobes, and
bares a dark metal lattice (`shell`) on the head and the deck; its two ring emitters rise from the
lobes. The paws, the mast's sponson and the haunches stay; the boss stays one object.

**Acceptance criteria**
- Given its model, then it draws the back region's armour, and it holds together with and without
  it (unit tests).

*Sources: D-221, D-224, D-227, D-229, D-254.*

### Behaviour

#### MB-FJORD-LYNX-07 — Entry and movement · MUST

It comes in as every boss and stops with its centre at `stop_fraction` of the playfield's height. In
place it sways by up to `sway` (the widest and quickest sway of World 2) and bobs by `bob`. During
the fight the ground scrolls at `ground_speed` of 2-2's speed.

*Sources: P08-R10.*

#### MB-FJORD-LYNX-08 — Paw cannons · MUST

Parts `paw-left` and `paw-right`, at ±30 px across and 26 px ahead of the centre, `paw_radius`
round with `paw_hp` each. Both shield the core. Each turns on its turret and fires every 2.2 s, the
two out of step (first at 1 s and 2.1 s):
- while the radar mast stands, an aimed spread of 3 blue bullets, 10° apart;
- once it is destroyed, a fan of 3 blue, 12° apart, at a preset heading 18° to the other side, so
  the two fans cross in front of its nose.

*Sources: P08-R10, D-068.*

#### MB-FJORD-LYNX-09 — Radar mast · MUST

Part `radar-mast`, 25 px to the left of the centre and 22 px behind it, `mast_radius` round with
`mast_hp`. It shields the core and has no weapon. While it stands, the paws and the core fire at the
player (aimed shots); once it is destroyed they fire fans at preset headings instead
(MB-FJORD-LYNX-08, MB-FJORD-LYNX-10). The weapons it reveals later (MB-FJORD-LYNX-12) do not depend on
it.

**Acceptance criteria**
- Given a Fjord Lynx with its radar mast standing, then its paws and core fire aimed volleys and no preset fans (unit test).
- Given its radar mast destroyed, then they fire the preset fans and no aimed volleys (unit test).

*Sources: P08-R10, D-068.*

#### MB-FJORD-LYNX-10 — Core and stage patterns · MUST

Its core (`core_radius`, `core_hp`) fires magenta bullets from its chin cannon, on a turret 30 px
ahead of the centre. One pattern per stage (a stage more for each destroyed part, see
[common.md](../common.md)), the first three depending on the radar mast:
- stage 0 (no part lost, so the mast stands): 1 magenta at the player every 3 s;
- stage 1: an aimed spread of 3, 12° apart, every 2.6 s while the mast stands; a fan of 3, 16°
  apart, every 2.6 s once it is gone;
- stage 2: aimed bursts of 4, 0.14 s apart, every 2.4 s while the mast stands; a fan of 5, 14°
  apart, every 2.2 s once it is gone;
- stage 3 (the last): a fan of 7, 12° apart, every 2.4 s, and a ring of 12
  purple every 1.6 s turning 9° a volley (a spiral fired by no earlier stage).

*Sources: P08-R10, D-068.*

#### MB-FJORD-LYNX-11 — Rage · MUST

It is angry after its transformation, when the two ring emitters (orbs) it revealed fire all out,
for `boss_rage_seconds`, `boss_rage_rate` times as often, instead of its stage's
pattern ([common](../common.md), BOSS-27). A lost part no longer angers it, and it has no
angry pattern of its own.

**Acceptance criteria**
- Given its transformation is over, then it is angry and fires only the two ring emitters (orbs) it
  revealed (unit: `test_boss_build.py` angry_pattern).
- Given a part is destroyed without a transformation, then it is not angry (unit test).

*Sources: D-068, D-256.*

#### MB-FJORD-LYNX-12 — Transformation · MUST

It transforms once, when 2 of its 3 original parts are destroyed. The transformation sheds its head
plating (MB-FJORD-LYNX-06) and reveals a pair of ring emitters (orbs), `orb-left` and `orb-right`,
at ±7 px across and 35 px ahead of the centre, `weapon_radius` round with `weapon_hp` each (0.8 of a
paw's), firing blue rings ([common.md](../common.md)), first 1.2 s and 2.0 s into each stage. They
shield the core.

*Sources: D-221, D-224, D-229.*

#### MB-FJORD-LYNX-13 — Health, points and death · MUST

Its full health is `full_hp` (core and original parts), `full_hp_with_weapons` with its orbs. It is
worth `points`. Its parts drop a bonus as mini boss parts do, its orbs as hidden weapons do. It dies
as every boss.

*Sources: P08-R10, P08-R11, D-068, D-221.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| size | 3 L (102 px) | `src/game/config/bosses/world_2/fjord_lynx.py` `_FJORD_LYNX["stats"]` |
| neon | pale cyan (0.55, 0.95, 1), white secondary | `src/game/config/boss_look.py` `BOSS_LOOK.neon["fjord-lynx"]` |
| stop_fraction | 0.72 | `stopFraction` |
| sway | 75 px, 6 s | `sway` |
| bob | 8 px, 3 s | `bob` |
| ground_speed | ×0.6 | `groundSpeed` |
| core_radius / core_hp | 18 px / 1 080 | `coreRadius`, `coreHealth` |
| paw_radius / paw_hp | 13 px / 600 | `part("paw-…")`, `PAW` |
| mast_radius / mast_hp | 11 px / 600 | `part(RADAR …)` |
| paw fan heading | ±18° | `only_after(volley.fan(…, 18))` |
| bullets | blue 185, magenta 190, purple 175 px/s | `BLUE`, `MAGENTA`, `PURPLE`; times the level's factors |
| angry | the revealed weapons, BOSS-27 | `boss_build.angry_pattern` |
| transformation | after 2 of 3 parts | `boss_build.default_transforms` |
| weapon_radius / weapon_hp | 5 px / 480 | `hidden_weapon("orb-…")`, pod 7.2 px high |
| region `back` | the crown and two lobes, not mirrored: x ±9 at y −3, ±10 at y −24…−34, lobes x 5.5…10 to 5.5…6.5 at y −40 round the channel x ±5.5 from y −25; crown 7–12.5 px, lobes 5–6 px; `shell` | `armour_region("back", 1, …)`; `src/game/view/bosses/world_2/fjord_lynx_armour.py` |
| full_hp / full_hp_with_weapons | 2 880 / 3 840 | core + parts |
| points | 3 500 (350 a part) | `points` |

## Notes

- No unit test checks the radar-mast rule on the Fjord Lynx itself: the `needs` / `after` volleys
  are tested generically (`tests/unit/core/systems/test_boss_pattern.py`,
  `tests/unit/game/config/bosses/test_boss_kit.py`). MB-FJORD-LYNX-09's acceptance criteria ask for
  one on the design.
- The old table gave its core "fans"; the core fires aimed shots while the mast stands and fans once
  it is gone, as the mast's rule says for every weapon (P08-R10 implementation report).
