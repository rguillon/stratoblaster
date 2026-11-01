# Traffic

> **Area:** Graphics · **Prefix:** `GFX-CAR` · **Related:** [roads.md](roads.md), [props.md](props.md), [buildings.md](buildings.md), [sky-and-light.md](sky-and-light.md), [terrain.md](terrain.md), [../performance.md](../performance.md), [../dev/dev-menu.md](../dev/dev-menu.md)

Cars, vans, haulers, buses and tankers drive along the streets and main roads of every level, in their
lanes, with their lights on at dusk and at night. They are futuristic hover cars, detailed models that
the levels draw as imposters: a picture of each baked once from its model, one quad per car, while
their lights stay real geometry. Traffic is only scenery: the cars do not turn, stop or collide, and
nothing in the simulation reads them.

## Requirements

### GFX-CAR-01 — Car kinds · MUST

There are eight car kinds, each with its own body, paint and neon accent: a racer (red, cyan neon), a
coupé (blue, pink), a pod (white, cyan), a cruiser (grey, violet), a van (white, pink), a hauler
(green, yellow), a bus (orange, cyan) and a tanker (teal cab, molten neon). Every kind's body differs
from the others in size or in triangle count. The levels' traffic draws from all of them.

**Acceptance criteria**
- Unit test: every car kind has its own body.

*Sources: D-211, D-213.*

### GFX-CAR-02 — Futuristic hover cars · MUST

The cars have no wheels: they ride on flat hover pads tucked under the hull. The coupé has a chamfered
wedge hull with a pointed nose, a teardrop glass canopy with a spine, twin fins carrying a wing and two
thrusters; the van is a tall chamfered pod with a sloping nose, a wraparound glass band and a roof light
bar; the hauler a pointed cab pod with a wraparound windscreen and a chamfered cargo pod with glowing
seams. Each kind's neon accent is painted on the hull (side strips, stripes on top, seams), so it shows
by day, and lit over it, so it glows at night. Car glass is lighter than the buildings' glass, as from
above it shows the sky.

*Sources: D-211.*

### GFX-CAR-03 — The bus and the tanker · SHOULD

The bus is a long chamfered body with a band of windows split by pillars and a white roof with two
cooling units. The tanker is the hauler's cab pulling a long chrome tank on a dark frame, with neon bands
round the tank.

*Sources: D-213.*

### GFX-CAR-04 — Cars keep their own size · MUST

Cars are drawn at `scale` (0.6) of their models, the size that fits a lane of the roads; they are not
stretched to whole tiles as the buildings are.

**Acceptance criteria**
- Given a car model, then it stands on the road and is as long as its shape; a hauler is longer than a
  coupé (unit tests).

*Sources: D-162, D-211.*

### GFX-CAR-05 — Drawn as imposters · MUST

When the look asks for car imposters, every car kind is baked as an imposter
([props.md](props.md)): 16 headings, 128-pixel frames 12 model units across, centred 1.8 up, softly
shaded (ambient 0.75). In play each car's body is one quad facing the camera. The cars' lights stay
real geometry (a lights-only model per kind), so they glow and turn exactly. The car quads do not hide
the ground's glow, as a quad stands in front of its car's far half and would hide its own lights.
Without the real kit (unit tests, and the dev props viewer, which shows them in 3D) the detailed
models are drawn.

*Sources: D-211.*

### GFX-CAR-06 — Cars drive on the streets and main roads · MUST

Cars drive along the streets and main roads (not the paths), right-hand traffic, facing the way they
drive, in a lane of their road (any of its lanes each way, spread evenly across its roadway). Each point
of a road has one chance (`density`, 0.3) of a car starting there, decided by a hash, so terrain chunks
agree. Each car keeps a constant speed (12–30 units/s); all the cars of one lane share one speed, so they
keep their spacing and never catch up with each other. A car's place is a closed form of the time (its
start plus its speed times the time, round the road's length), so no simulation runs. Near both ends of
its road (`length`, 4) a car is hidden, where it turns into the crossing street or leaves the screen,
and it comes back from the other end. Cars go straight through crossings.

**Acceptance criteria**
- Given a road, then its cars of one lane share a speed and are hidden near its ends (unit tests).

*Sources: P15-R11, D-028, D-030.*

### GFX-CAR-07 — Cars stay on the roadway · MUST

On the streets of the districts, cars keep off the sidewalks (`sidewalk`, 2): every car lane's centre
line lies within the roadway of every piece it passes, and no car drives on a sidewalk, a building or
open ground. Cars stand on the road surface, `lift` (0.6) above the ground.

**Acceptance criteria**
- Given every car lane of every district, then its centre line lies within the roadway (unit test on
  streets).
- Manual: cars stay on the roadway, in their lanes.

*Sources: P15-R11.*

### GFX-CAR-08 — Cars placed near the view, every frame · MUST

The cars in view are placed again every frame, as thin instances of their own meshes, apart from the
props that stay put, so the props are never uploaded again for them. Only the roads near the ground in
view are looked at (the roads are indexed by the stretches of Z they span), within the props' reach.

*Sources: D-030.*

### GFX-CAR-09 — Headlights and tail lights · MUST

Each car has full-width headlight and tail-light bars, a warm beam on the road ahead, a red glow behind,
the glow of its hover pads under it and its thrusters' mouths, all part of the ground's glow layer. They
are lit with the strength of the ground's lights ([sky-and-light.md](sky-and-light.md)): on at dusk and
at night.

**Acceptance criteria**
- Manual: at night the cars' lights glow on the roads and move with them.

*Sources: D-030, D-211.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `CAR_RULES.kinds` | 8 kinds | `src/game/config/cars.py` |
| `density` / `lift` / `scale` / `length` | 0.3 / 0.6 / 0.6 / 4 | same place |
| `speed` | 12–30 units/s | same place |
| `sidewalk` | 2 | `TILE.sidewalk`, same place |
| `CAR_IMPOSTERS` | 16 headings, 128 px, 12 units, centre 1.8, ambient 0.75 | same place |
| body sizes (length × width × height) | racer 7.6 × 3.6 × 1.0; coupé 7 × 3.2 × 1.3; pod 4.8 × 2.8 × 1.8; cruiser 8.6 × 3.4 × 1.5; van 7.6 × 3.4 × 2.8; bus 10.4 × 3.6 × 2.6; hauler and tanker 10 × 3.6 × 3.4 | `src/game/view/props/car_props.py` `SHAPES` |
| paints and accents | per kind | `src/game/view/props/prop_models.py` `make_car_models`, `src/game/config/prop_look.py` |

## Notes

- Cars pass through each other at crossings, and vanish and reappear at road ends; they do not turn at
  junctions or stop at crossings (out of scope since phase 4).
- The speed-ups of the cars (lazy setup, lookup by Z, no bounds) are in
  [../performance.md](../performance.md); the cars' entries in the dev props viewer are in
  [../dev/dev-menu.md](../dev/dev-menu.md).
