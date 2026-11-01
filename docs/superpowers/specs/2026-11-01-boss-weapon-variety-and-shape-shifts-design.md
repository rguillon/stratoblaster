# Boss weapon variety and shape-shifting bosses — design

- **Date:** 2026-11-01
- **Branch:** `feat/ship-glow-boss-transform`
- **Status:** awaiting reviewer approval
- **Scope:** outside a phase, at the reviewer's request (in chat): "Add more diversity to the boss
  weapons that spawn when loosing a part, they are almost all small turrets", then "also make some
  boss transform, not only drop a piece of armor". Builds on D-221, D-224, D-227 and D-228.

## Intent

What the reviewer said: the weapons a boss reveals as it transforms all look like small turrets;
some bosses should really change shape, not only shed armour.

What we found:

- 121 hidden weapons over the 40 bosses, of four kinds only: `gatling` 38, `lance` 35, `orb` 28,
  `rack` 20; radius 5–13 px; always in mirrored left/right pairs, all on the same octagonal pod. Only
  the Scorpion's tail cannon (`beam`, D-228) is different.
- The engine already has shot kinds no hidden weapon uses: flak shells that burst (`bursting`),
  lasers that sweep (`EnemyLaserSpec.sweeps`) and launches (hangars).
- Every transformation but the Scorpion's is an armour region bursting off (D-224); the boss
  outline never changes.

Agreed in chat (reviewer, 2026-11-01): five new weapon kinds with their own look and fire, distinct
pods, centre-line weapons, re-picked kinds for all 40 bosses; hangars on a few bosses only; and
eight bosses whose hull sections move into a new pose (two per world, list below).

Success criteria:

- The revealed weapons of the 40 bosses spread over nine kinds, no kind more than 20 % of them;
  every world uses at least six kinds.
- Eight bosses change their outline as they transform (sections swing or slide), each in its own
  way.
- Kept: no boss gets easier as it transforms (D-221's guard), every boss is one object at rest and
  after each transformation (D-227), triangle budgets (P16-R09).

## Part A — more kinds of hidden weapons

### New kinds (`config/bosses/hidden_weapons.py`, `view/bosses/hidden_weapon_shapes.py`)

Each kind has its own silhouette, muzzles worked out from its size (as today) and its own volley,
all on existing volley shapes. Numbers are starting values, tuned by the escalation guard.

| Kind | Look | Volley |
|---|---|---|
| `cannon` | a big square turret, one heavy long barrel with a neon muzzle ring | aimed, 3 large slow shells (radius 7, ~150 px/s) 12° apart, every ~2.4 s; on its turret |
| `mortar` | a squat round base, a short wide tube tilted up towards the nose, neon mouth | aimed flak: one `bursting` shell bursting into a ring of 8, every ~3.2 s |
| `battery` | a long, low rectangular gun deck, five short barrels in a row | fan straight down, 7 bullets 9° apart, every ~2.0 s |
| `sweeper` | a turret with a two-pronged emitter, a lens glowing between the prongs | a sweeping laser (follows the player while it fires), every ~8 s; on its turret |
| `hangar` | a box bay, two doors sliding apart over a glowing bay floor | launches 2 Gnats or Hornets (existing `launches`), every ~7 s |

- **Pods:** the octagon stays for gatling, lance, rack, orb, cannon and sweeper; the mortar has a
  round base, the battery a rectangular deck, the hangar a box. A kind's look tells it apart before
  anything slides out.
- **What slides out:** a list of slides per weapon instead of one (the hangar's two doors slide
  apart); turrets rise as today.
- **Hangar launches:** `with_weapons` adds a hangar's launch to `design.launches`; a hidden part is
  no volley source until revealed, launches included (as today for any part's volleys).

### Engine change (`core/systems/boss_pattern.py`, game-agnostic)

A turret holds still while its laser's beam fires (phase 8 review). A laser whose spec `sweeps`
now keeps its turret following the player while the beam fires, at the turret's
`laser_turn_rate_deg` (so it can still be outrun). Lasers without `sweeps` are unchanged.
`volley.laser` gains a way to ask for a sweeping beam.

### Size and layout

A weapon may stand alone on the centre line (no mirrored twin), at about 1.5–2× the radius of the
boss's other hidden weapons, where its hull has room. Pairs stay the default.

### Re-picking the 40 bosses

Every boss's hidden weapons are re-picked by hand, keeping their spots where the new kind fits
(a battery or hangar may need a spot moved), to fit its theme: forts, rigs and ships lean to
battery, mortar, hangar and cannon; creatures and sleek craft to sweeper, lance, cannon and orb.
Rules, checked by a config test:

- no kind is more than 20 % of all hidden weapons (`beam`, the Scorpion's, aside);
- each world uses at least six of the nine kinds;
- a final boss never reveals the same kind at both its transformations;
- hangars on final bosses only, at most one per world;
- at least ten bosses reveal a centre weapon.

The Scorpion keeps its tail cannon (D-228). Bullets keep the boss's colours. Health stays 0.8 / 1.0 of its sturdiest original part (D-221).

### Escalation guard

D-221's guard stays (fire rate never drops after a transformation). A launched enemy now weighs 2
(as a homing missile) so a hangar counts; a flak shell counts as one bullet (under-counted, so the
guard errs on the safe side).

## Part B — bosses that change shape

### Moving regions (`hidden_weapons.moving_region`, `view/bosses/boss_armour.py`)

A moving region is an armour region (D-224) whose piece stays on the boss and moves into a new pose
instead of bursting off. It is cut out of the core's drawing in the same way, at full height unless
`heights` says otherwise.

- `moving_region(region_id, form, outline, motion, frame, heights, mirror)`. `motion` is one of:
  - `swing`: a pivot `[x, y, z]` (px from the boss's centre, X right, Y up the screen, Z height),
    an axis (`up`, `along` the boss, `across` it), and `[rest, end]` angles in degrees;
  - `slide`: `[rest, end]` offsets `[dx, dy, dz]` in px.
  The drawn geometry is the pose at angle 0 or offset 0, so a piece can rest folded (a rest angle
  other than 0) and unfold to the model as drawn, or rest as drawn and move away from it.
- Mirrored regions move mirrored: the pivot and offsets have their X negated; `up` and `along`
  angles are negated.
- Timing: the piece strains as armour does, then moves from its rest pose to its end pose in the
  reveal's swing window (`BOSS_LOOK.reveal`, as the Scorpion's tail), then stays there.
- `frame` is optional for a moving region: when given, the frame shows where the piece was drawn
  (a vacated spot reads as dark metal); left out, nothing is drawn there (a piece resting folded
  away from where it is drawn).

### What stands on a moving piece

- A hidden weapon of that transformation may ride the piece (`on_region(weapon, region_id)`): its
  `at` is where it ends up (its hit circle and muzzles once revealed, as the Scorpion's tail
  cannon); the view draws it on the piece at the matching drawn spot, then it unfolds as usual.
- No part the player can hit during a move may stand on the moving piece: an original part over a
  region moving at transformation K, or a weapon revealed before K, must be among the parts that
  call for K (`BossStats.transform_parts`, D-228) or retire at K. Positions in `core/` never move
  except by the boss's turn.
- The sim needs nothing new (`transform_parts`, `retire`, `turns` exist).

### The eight bosses

| Boss | Transformation |
|---|---|
| Storm Petrel (1-1, final) | swept-back wings swing forward to straight out (`up` axis at the wing roots); batteries on the leading edges |
| Mesa Fortress (1-3, final) | splits along its centre line, both halves slide apart; a big centre cannon rises in the gap |
| Snow Owl (2-3, mini) | rests with its wingtips folded up over its back; they swing out to full span (`along` axis); sweepers at the tips |
| Boreal Citadel (2-5, final) | its bow doors swing open sideways (`up` axis at their outer edges), showing a hangar and a mortar |
| Stone Idol (3-3, mini) | its face splits, both halves swing open like doors, showing a big centre sweeper eye |
| Sky Temple (3-3, final) | its four corner wedges slide out diagonally; a mortar in the centre |
| Obsidian Golem (4-3, final) | its flank slabs swing forward like arms (`up` axis at the shoulders), cannons at the fists |
| Steam Dreadnought (4-1, final) | its side hull plates swing out flat (`along` axis at the deck edges) into broadside battery decks |

Final bosses still transform twice: a final boss's other transformation sheds armour (D-224), or
moves a second region, whichever fits. Their kinds follow Part A's rules.

### Checks (config and view tests)

- A weapon `on` a region lies, centre and hit circle, inside that region's outline in its end pose.
- The rule above on what stands on a moving piece.
- Wholeness (D-227) at rest, and after each transformation with every moving piece in its end pose.
- Each of the eight bosses has a moving region; the others are unchanged in kind of transformation.

## Testing

- Unit: muzzles of each new kind; a model of each kind builds (and its slides); the sweeping laser
  turret follows the player while the beam fires, a plain laser's turret holds still; moving-region
  poses (rest, end, mirrored) and the drawn spot of a riding weapon; the config rules of Parts A and
  B; the escalation guard; wholeness; triangle budgets.
- e2e: the per-world boss transform tests still pass; one test triggers a moving-region boss's
  transformation (K) and checks its new weapons appear and fire.
- While working: `make typecheck build e2e` only (CLAUDE.md); `make check` at validation.

## Work order (one commit or more each)

1. Engine: sweeping lasers keep their turret following the player while they fire.
2. New weapon kinds: config (muzzles, volleys, launches, slides list) and view (pods, models), with
   tests.
3. Moving regions: config helper, view (pose and timing in `boss_armour`), riding weapons, wholeness
   in the end pose, with tests.
4. The eight shape-shifting bosses, a world per commit.
5. Re-pick the other 32 bosses' weapons, a world per commit, with the distribution test.
6. `DECISIONS.md`: new kinds, sweeping turret, moving regions, the eight bosses.

## Out of scope

- New core volley shapes, or moving a live part's position in `core/` (other than by the boss's
  turn).
- Changing the 32 other bosses' armour regions, beyond moving a spot where a new kind needs room.
- Re-tuning the core's own stages, rages or regular enemies.
