# Level 3-1 — Canal works

> **Area:** worlds · **Prefix:** `LVL-3-1` · **Related:** [World 3](world.md), [2-5 Factory district](../world-2/2-5-factory-district.md), [3-2 Docklands](3-2-docklands.md), [Mangrove Croc](../../bosses/mini/3-1-mangrove-croc.md), [River Leviathan](../../bosses/final/3-1-river-leviathan.md), [level flow](../../gameplay/level-flow.md), [sky and light](../../graphics/sky-and-light.md)

The first level of World 3. The player flies on from the great works 2-5 ended on, past foundries,
rail yards, the canal docks and factory yards, to the first workshops, under a morning mist that
lifts over the first half. Tier 3 brings 60 % of the enemies,
tier 2 the other 40 %. Its checkpoint is its mini boss, as in every level (see [level flow](../../gameplay/level-flow.md)).

## Requirements

### LVL-3-1-01 — Identity and duration · MUST

Level `3-1`, named "Canal works", is the first level of World 3. Its scenery is `world-3-1`, built
from seed 3101. Its ground scrolls at `ground_speed` for `level_length`: 300 s.

**Acceptance criteria**
- Given level `3-1`, then its scenery id is `world-3-1`, its seed 3101, its ground speed 70 and its length 21 000 units (300 s).

*Sources: P09-R02, P09-R03, D-111.*

### LVL-3-1-02 — Scenery sections · MUST

3-1's ground is these sections, in this order, blending into each other over World 3's
`section_transition`. All of them lie on flat ground (World 3's `flat_relief`) and are laid out as
World 3's widest street blocks (`streets`).

| # | Section | Time | Length | Paved / grass | Buildings (groups) | Building density |
|---|---------|------|--------|---------------|--------------------|------------------|
| 1 | Great works | 0–40 s | 2 800 | 1 / 0 | heavy industry filling every block side by side | 1 |
| 2 | Foundry canal | 40–95 s | 3 850 | 0.96 / 0 | heavy industry, industrial | 0.6 |
| 3 | Rail yards | 95–145 s | 3 500 | 0.94 / 0 | industrial | 0.6 |
| 4 | Canal docks | 145–200 s | 3 850 | 0.92 / 0 | docks, industrial | 0.9 |
| 5 | Factory yards | 200–250 s | 3 500 | 0.88 / 0.02 | industrial, docks | 1 |
| 6 | Canal workshops | 250–300 s | 3 500 | 0.85 / 0.04 | workshops, industrial | 1 |

The first section is 2-5's last one, the great works (its relief, cover, streets and filled blocks),
with World 3's heavy industry group. The last section, the canal workshops, is where 3-2 begins. The
canal between stone walls runs from the second section on (WLD-3-10).

**Acceptance criteria**
- Given 3-1's scenery, then its sections are these, in this order, with these lengths, covers, groups and densities.
- Given 3-1's first section, then it is 2-5's great works, shortened to 40 s.

*Sources: P09-R03, D-111.*

### LVL-3-1-03 — Look · MUST

3-1 is a **morning**: a low, warm sun, white clouds at cover 0.3 (low layer) and 0.2 (high layer), no
weather. A **morning mist** lies over the factories at the start: the haze ends at `morning_mist_fog`
of its clear distance and turns `morning_mist_white` of the way to a pale mist colour. The mist lifts
over the first 150 s (the first half), back to the plain morning.

**Acceptance criteria**
- Given 3-1's look, then it starts at morning with clouds 0.3 / 0.2, the mist on and no weather, and changes from 0 to 150 s to the morning without mist.
- Manual visual validation: the mist is close and white over the factories at the start and gone by 2:30.

*Sources: P09-R04, D-078, D-111.*

### LVL-3-1-04 — Enemy waves · MUST

3-1 mixes two tiers: tier 3 (the main one) is 60 % of its enemy ships and tier 2 40 % (each within 5 points; a Wasp group counts as its 5 ships, and the filler is counted with the beats). It brings every kind of both tiers, each at least once: tier 3's Phantom, Spinner, Mortar, Prism and Broodmother; tier 2's Wasp, Strafer, Harrier, Sweeper and Hatchery, and no other kind. 3-1's waves follow its wave plan (WLD-3-16) from 4 s to 292 s, each wave followed by a breather of `wave_gap` seconds (2.8 s to 2 s), groups growing by `wave_growth` (80 %) over the level. Each beat goes to the tier furthest below its share of the ships so far (the filler that follows a beat counted with it). A tier's beats first bring each of its five kinds once (shooter, laser, missile, carrier, then diver; one group each outside the main tier), then follow the role cycle (shooter, diver, laser, diver, missile, shooter, diver, carrier, laser, shooter, missile). A wave brings no more groups than its tier lacks, the main tier's never fewer than written. The beats are composed around the quiet stretch before each boss, so none is dropped. The filler draws Phantoms, Spinners, Wasps and Strafers, at most `filler_gap` apart.

**Acceptance criteria**
- Unit test: 3-1's waves use only the kinds of tiers 3 and 2, and each of them.
- Unit test: each tier's share of 3-1's enemy ships is within 5 points of its target.
- Unit test: 3-1's waves are the same each time the level is built.

*Sources: P09-R07, P05-R24, D-080, D-090, ENM-50, D-283.*

### LVL-3-1-05 — Difficulty · MUST

3-1's enemy bullets fly at ×1 their speed and its enemies fire at ×1 their rate, as in 2-3: a fresh
start after 2-5. Its second half has more enemy HP than its first.

**Acceptance criteria**
- Given level `3-1`, then its enemy difficulty is bullet speed 1 and fire rate 1.
- Unit test: 3-1's second half has more enemy HP than its first.

*Sources: P09-R08, D-080, D-090.*

### LVL-3-1-06 — Mini boss · MUST

3-1's mini boss is the [Mangrove Croc](../../bosses/mini/3-1-mangrove-croc.md). It comes at the middle
of the level (150 s, 10 500 units), after a quiet stretch with no new wave (see
[level flow](../../gameplay/level-flow.md)). Its fight is a chase: the ground runs at ×1.4.

**Acceptance criteria**
- Given 3-1, then its mini boss is the Mangrove Croc, at half the level's length.

*Sources: P09-R09.*

### LVL-3-1-07 — Final boss · MUST

3-1's final boss is the [River Leviathan](../../bosses/final/3-1-river-leviathan.md). It comes at the
end of the level (300 s, 21 000 units); its fight runs the ground at ×0.5. 3-1 is complete when it is
destroyed.

**Acceptance criteria**
- Given 3-1, then its final boss is the River Leviathan, at the level's end.
- Given `?level=3-1&boss=final`, when K destroys the boss, then "Level complete" shows `3-1` and confirming it highlights `3-2`.

*Sources: P09-R09.*

### LVL-3-1-08 — Runout · MUST

`runout` seconds of ground like the last section (the canal workshops) are drawn past the level's
end, so the ground never runs out during the two fights.

**Acceptance criteria**
- Given 3-1, then its runout is 140 s (9 800 units).

*Sources: P07-R03.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| ground_speed | 70 units/s | `LEVEL_3_1.scrollSpeed`, `src/game/config/world_3/scenery.py` |
| level_length | 21 000 units (300 s) | sum of `CANAL_WORKS` seconds × speed |
| seed | 3101 | `LEVEL_3_1.seed` |
| streets | rows 45–90, columns 50–110 | `STREETS` |
| morning_mist_fog / morning_mist_white | 0.4 / 0.8 | `MORNING_MIST`, `src/game/config/world_3/looks.py` |
| clouds | 0.3 / 0.2 | `MORNING` |
| wave_gap | 2.8 s → 2 s | `PLAN_3_1.gap`, `src/game/config/world_3/waves.py` |
| wave_growth | 0.8 | `PLAN_3_1.growth` |
| filler_gap | 3.4 s → 2.3 s | `WORLD_3_FILLERS["3-1"].maxGap` |
| bullet speed / fire rate factors | 1 / 1 | `WORLD_3_DIFFICULTY["3-1"]` |
| measured | 180.8 enemies/min, 4 384 HP/min, peak 37 on screen | D-090 (seed 606, without shooting) |
| mini boss at | 0.5 of the length | `MINI_BOSS_AT`, `src/game/config/world_1/bosses.py` |
| runout | 140 s | `WORLD_3_BOSSES["3-1"].runout`, `src/game/config/world_3/bosses.py` |

## Notes

- The section names still speak of the canal (foundry canal, canal docks, canal workshops), but no
  water is drawn today (see the discrepancy under WLD-3-10).
- Before the rework (D-111) 3-1 was a river delta with open sea for 80 of its 300 s.
