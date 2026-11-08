# Enemies — common rules

> **Area:** Enemies · **Prefix:** `ENM` · **Related:** [level flow](../gameplay/level-flow.md),
> [lives and damage](../gameplay/lives-and-damage.md), [scoring](../gameplay/scoring.md),
> [bonuses](../gameplay/bonuses.md), [art direction](../graphics/art-direction.md),
> [readability](../graphics/readability.md), [edge trim](../graphics/edge-trim.md),
> [shots](../graphics/shots.md), [effects](../graphics/effects.md),
> [bosses](../bosses/common.md), [dev menu](../dev/dev-menu.md)

The rules every enemy kind follows: how the kinds are organised in tiers, how they come in and
leave, their hit circles, what they can fire and how they aim, how they move, their moving parts,
and the look they share (Cyber-Organic bodies of flesh and metal, bright yellow or bright green
lights, reactor flames, living motion, standing out from the ground). Each kind's own file
([gnat.md](gnat.md) and the others) gives its shape, movement, attack and numbers. Bosses are built
on the same engine but follow their own rules ([bosses/common.md](../bosses/common.md)). How the
bullets, missiles, lasers and explosions look is in [shots](../graphics/shots.md) and
[effects](../graphics/effects.md).

## Requirements

### Kinds and tiers

#### ENM-01 — Twenty kinds in four tiers of five roles · MUST

The game has 20 enemy kinds, in four tiers. Each tier holds exactly one kind of each of five roles:
a **diver** (rams, or dives at the player), a **shooter** (bullets), a **missile launcher**
(homing missiles the player can shoot down), a **laser** (a warning line, then a beam) and a
**carrier** (launches the tier's diver). The kinds are, tier by tier, role by role in that order:

| Tier | Diver | Shooter | Missile launcher | Laser | Carrier |
|------|-------|---------|------------------|-------|---------|
| 1 | [Hornet](hornet.md) | [Scout](scout.md) | [Rocketeer](rocketeer.md) | [Lancer](lancer.md) | [Carrier](carrier.md) (Hornets) |
| 2 | [Wasp](wasp.md) | [Strafer](strafer.md) | [Harrier](harrier.md) | [Sweeper](sweeper.md) | [Hatchery](hatchery.md) (Wasps) |
| 3 | [Phantom](phantom.md) | [Spinner](spinner.md) | [Mortar](mortar.md) | [Prism](prism.md) | [Broodmother](broodmother.md) (Phantoms) |
| 4 | [Splitter](splitter.md) | [Hydra](hydra.md) | [Juggernaut](juggernaut.md) | [Scissor](scissor.md) | [Hive](hive.md) (Splitters) |

The tiers are in the code's tier table (`src/game/config/enemy_tiers.py`). The pods a Splitter
breaks into are part of the Splitter kind, not a kind of their own. A boss's hangars and bays
launch Hornets.

**Acceptance criteria**
- Given the game's list of enemy kinds, then it holds these 20 ids once each, tier 1 first, each
  tier in the order of the table; and each tier holds one kind of each role (unit test).

*Sources: phase 5 preamble, P05-R12, D-090; reworked into four tiers at the reviewer's request,
2026-11-03.*

#### ENM-02 — The tier shows in the look · MUST

The tier is readable from the look, by its colour theme (ENM-49) and by how armoured and complex
the kind is: a tier 1 kind is one body with a few metal grafts, each higher tier has more armour
plates, limbs and organs than the one below, and a tier 4 kind is heavily armoured, with plated
shells.

**Acceptance criteria**
- Given the dev enemies viewer, when the kinds are seen side by side, then the tier of each kind
  can be told from its look (manual check).

*Sources: P16-R04, P16-R01.*

#### ENM-03 — Triangle budget per tier · MUST

Each enemy model stays within the triangle budget of its tier: `budget.tier1` (400), `budget.tier2`
(600), `budget.tier3` (900) and `budget.tier4` (1200), reactor flames included.

**Acceptance criteria**
- Unit test: each model's triangle count is within its tier's budget.

**Discrepancy:** since the glowing edge trim was built into the models (D-220), some kinds go over
their budget (D-220 left open whether the trim counts); and no unit test checks the budgets since
the Python port.

*Sources: P16-R09, D-220.*

### Engine and content

#### ENM-04 — Enemies in the engine, kinds in the game · MUST

The engine (`src/core/`) knows enemies only as abstractions: an enemy is a circle with health,
moved and armed each step by its update hook, with an optional hook run once when it is destroyed;
its context gives it the playfield size, the player's position, the random source and the level's
fire-rate factor, and lets it fire bullets, missiles and lasers, spawn other enemies, and blow up.
A kind definition has an id, a name and a spawn function that creates one group. The engine steps
the enemies and their shots, scores and removes the destroyed ones, and lists what the player's
shots can hit. The concrete kinds (one class per kind), their numbers and their models live in
`src/game/`. Movement, fire timing and aiming are pure, deterministic logic, unit tested.

**Acceptance criteria**
- No module outside `src/game/` names a concrete enemy kind.
- Given the same seed and inputs, two runs of the same enemies give the same positions and shots.

*Sources: phase 5 engineering additions, P05-R13, D-032.*

#### ENM-05 — Sizes in L · MUST

Enemy sizes are given relative to `L`, the length of the medium (balanced) player ship on the
playfield: `ENEMY_UNIT` logical pixels. Models are drawn in logical pixels.

*Sources: phase 5 preamble, D-032.*

#### ENM-06 — Numbers are tunables · MUST

Each kind's health, points, size, hit radius, speeds, timings, fire rates and bullet specs are
tunables in the game's enemy config (`enemies.py`, `enemies_veteran.py`, `enemies_elite.py`), and
its colours and look values in the enemy look config (`enemy_look.py`, `enemy_look_elite.py`).
Values the specs leave open are the agent's defaults, kept there.

*Sources: phase 5 preamble, D-032.*

### Coming in and leaving

#### ENM-07 — Groups spawned by the waves · MUST

Enemies come in groups that the level's wave script triggers by the distance flown (see
[level flow](../gameplay/level-flow.md)), or that other enemies send out (a Carrier's Gnats, a
Splitter's pods, a Hive's Wasps, a boss's launches). A kind's spawn creates one group (one enemy,
or a swarm) just outside the playfield: `ENEMY_SPAWN_MARGIN` above the top edge, or beside a side
edge for the kinds that cross sideways.

**Acceptance criteria**
- Given any kind and any wave entry, when it spawns, then its enemies are alive and start outside
  the playfield, by the spawn margin.

*Sources: GD-40, D-032, D-036.*

#### ENM-08 — A group follows its wave's entry · MUST

A group comes in where its wave says (an edge and a position along it), as far as the kind's
movement allows: a kind coming in from the top starts at that position; a side pass comes from
that side at that height; a kind on a predefined path mirrors its path towards the entry. Without
an entry, the kind picks: a random X in its own range, a random side, or its path mirrored on a
coin toss. Entry positions are kept `ENTRY_INSET` away from the corners.

**Acceptance criteria**
- Given a side entry on the left at a height, when a Strafer spawns, then it starts just left of
  the playfield at that height.
- Given a top entry, when a path kind spawns, then its path is the one of its two mirror images
  whose start is nearer the entry.

*Sources: P06-R07, D-036.*

#### ENM-09 — Coming in where the ship can reach · MUST

The kinds that come in from the top keep to the X range the player's ship can reach at the bottom
of its flight area (`top_range`): their entry positions, their random X ranges and the X fractions
of their paths are taken across that range, not across the whole width, so no enemy can stay in an
upper corner the player cannot shoot at. Side passes still cross the whole width.

**Acceptance criteria**
- Given a level, when enemies come in from the top, then each starts inside the ship's reach.

*Sources: D-048.*

#### ENM-10 — Leaving the playfield · MUST

An enemy is removed once it has been on the playfield (its centre within its hit radius of it) and
is then more than `cull_margin` outside it, or once it is older than `max_enemy_age`, whatever it
does. An enemy that has not come in yet is kept while it waits outside. A kind on a predefined path
is done once it reaches the end of its path.

**Acceptance criteria**
- Given an enemy that entered the playfield, when it flies more than the cull margin out, then it
  is removed; given one that has not entered yet, then it stays.
- Given an enemy older than the maximum age, then it is removed.

*Sources: D-032.*

### Hit circle and damage

#### ENM-11 — A hit circle about as big as the model · MUST

Each enemy (and each moving part) is hit in a circle that matches its visual: its hit radius is
`HITBOX` of half its size, smaller for the kinds much wider or longer than they are deep (the kind
files give the factor). The player's shots hit the enemy in that circle, and the ship collides with
it there (see [lives and damage](../gameplay/lives-and-damage.md)). The hit circle is not drawn in
the game.

*Sources: GD-21, D-032, P16-R08.*

#### ENM-12 — The model is the size of its kind · MUST

Each model's footprint seen from above (its longest extent across or along, rotors included,
reactor flames left out) is within `hitbox_footprint_tolerance` of its kind's size in `L`. Models
are flat: their height is under half their length.

**Acceptance criteria**
- Unit test: for every kind, the model's footprint is within the tolerance of its size.

*Sources: P16-R08, P16-R01.*

#### ENM-13 — Only enemies on screen can be shot · MUST

The player's shots can only hit the enemies, moving parts and enemy missiles whose centre is
inside what the tilted camera shows. An enemy takes no damage before it comes into view, so no
enemy blows up out of sight.

**Acceptance criteria**
- Given an enemy just above the top edge of the screen, when a player shot reaches it, then it
  takes no damage; once its centre is in view, it does.

*Sources: D-042.*

#### ENM-14 — A destroyed enemy · MUST

An enemy whose health reaches 0 (from the player's shots, a bomb or ramming the ship) is destroyed
once: it scores its kind's points (see [scoring](../gameplay/scoring.md)), may drop a bonus (see
[bonuses](../gameplay/bonuses.md)), blows up in a blast the size of its hit radius (see
[effects](../graphics/effects.md)), and runs its kind's on-destroyed behaviour (e.g. the Splitter's
pods). An enemy that leaves the screen alive scores nothing.

**Acceptance criteria**
- Given an enemy at 0 health, when the world steps, then it scores once, leaves one blast, and its
  on-destroyed hook runs once.

*Sources: D-032, GD-50, GD-62.*

### Attacks

#### ENM-15 — Attacks only over the playfield · MUST

An enemy fires and launches only while its centre is over the playfield. Its attack timer does not
run while it is outside.

**Acceptance criteria**
- Given a shooting kind above the top edge, then it does not fire.

*Sources: D-032.*

#### ENM-16 — Bullets · MUST

Enemies can fire colourful glowing bullets: each flies in a straight line at a constant speed, with
a hit radius of `bullet_radius`, until it leaves the playfield (by the cull margin) or hits the
ship. A bullet's style is a key the game's shot renderer knows (see [shots](../graphics/shots.md)).

*Sources: GD-43, D-032.*

#### ENM-17 — Bursting bullets · MUST

A bullet may burst: a set time after it was fired it is gone, and a ring of bullets leaves from
where it was, evenly all around, the first one on its way. The bullets of a burst follow the same
rules as other bullets.

**Acceptance criteria**
- Given a bursting bullet, when its burst time is up, then it is replaced by its count of bullets
  spread evenly around its heading.

*Sources: GD-43, P08-R10.*

#### ENM-18 — Missiles the player can shoot down · MUST

Enemies can launch missiles: a missile turns towards the player at no more than its turn rate for
its homing time, then flies straight on. A missile has health and is a target of the player's
shots: shot down, it blows up in a small explosion (`blasts.missileScale` of a blast its size). A
missile that reaches the ship hurts it and blows up.

**Acceptance criteria**
- Given a missile in flight, then each step it turns towards the player by at most its turn rate;
  after its homing time it keeps its heading.
- Given a player shot that brings a missile to 0 health, then the missile is gone with a small
  explosion.

*Sources: GD-43, P05-R08, D-032.*

#### ENM-19 — Lasers with a 1 s warning line · MUST

Enemies can fire lasers. A laser first shows a thin warning line from its emitter along its
owner's heading, to the edge of the playfield, for its warning time (1 s for every enemy laser),
then fires its beam along the same line for its firing time. The warning line does not hurt; the
beam does. The beam keeps the heading its owner had when it started firing, unless the laser
sweeps (a laser on a moving part, which turns with it). The laser stops when its owner is gone or
destroyed. The emitter is seen through the tilted camera, so the line starts where the emitter is
drawn.

**Acceptance criteria**
- Given a laser, then a warning line shows for 1 s before the beam appears on the same line.
- Given a laser still showing its warning, when it crosses the ship, then the ship is not hurt.
- Given a laser whose owner is destroyed, then the laser stops.

*Sources: GD-43, P05-R07, D-072, D-090.*

#### ENM-20 — Preset or aimed directions · MUST

Each attack fires either in preset directions, set from straight down the screen or from the
enemy's own heading, whatever the player does (fans around straight down, rings, spirals), or aimed
at the player: towards where the player is at the moment of firing, a fan of several shots centred
on that direction. An aimed shot is aimed from the point it leaves from, not from the enemy's
centre.

**Acceptance criteria**
- Given an aimed shot, then it moves along the line from its muzzle to the player's position at
  the moment it was fired.
- Given a preset fan, then its directions do not depend on the player's position.

*Sources: GD-44, D-057.*

#### ENM-21 — Shots leave from the muzzles · MUST

A gun fires from its muzzles: points of the model (offsets from the enemy's centre as drawn facing
down the screen, and a height above the playfield). A shot leaves from the muzzle furthest along
its way, side-by-side muzzles taking turns, turned with the enemy's heading (and its part's swing
or orbit), and is seen through the tilted camera onto the playfield, so it starts where the barrel
tip is drawn. The model marks its barrel tips, and the config's muzzles are the same points. A muzzle with an
angle is a fixed barrel, and its shots leave along it ([weapons.md](weapons.md) WPN-01).

**Acceptance criteria**
- Given a kind's model, then its marked muzzles are at the config's muzzle offsets.

*Sources: D-057, P16-R08.*

#### ENM-22 — Level difficulty factors · MUST

Every kind's attack timers run at the level's fire-rate factor, and its bullets (and the bullets
they burst into) fly at the level's bullet-speed factor (see [level flow](../gameplay/level-flow.md)).
The Carrier's launches and the lasers' timings are not "fire rate" and keep their own timing;
missiles keep their own speed.

**Acceptance criteria**
- Given a bullet-speed factor of 2, then every bullet an enemy fires flies twice as fast as tuned.

*Sources: P06-R08, D-036.*

#### ENM-23 — Charge lights · SHOULD

Each enemy tells how ready its next attack is (0 to 1): its gun reloading, its laser warning, its
missiles reloading, its next launch coming. Its charge lights brighten with it, from `chargeIdle`
of their brightness to full.

*Sources: D-032, P05-R08.*

### Movement

#### ENM-24 — A preset movement per kind · MUST

Each kind has a preset movement: a predefined path, a straight flight down the screen, a pass
across it from one side, a sine sway on the way down, a stop to attack before leaving, or a dive
right at the player. The kind files say which, with their speeds and timings.

*Sources: GD-45.*

#### ENM-25 — Predefined paths · MUST

A predefined path is a smooth curve through control points, given as fractions of the playfield
(taken across the ship's reach, ENM-09) and mirrored left to right when the entry asks for it. An
enemy follows it by distance travelled, so it keeps a constant speed on the curves, its nose along
the way.

**Acceptance criteria**
- Unit test: a path passes through its control points, and a point moving along it at a constant
  speed covers equal distances in equal times.

*Sources: GD-45, D-032.*

#### ENM-26 — Drawn where it is, its nose along its heading · MUST

Each enemy is drawn at its position on the playfield with its nose along its heading (straight
down the screen at rest). A kind's model is reused when one of its enemies leaves and another
comes.

*Sources: D-032.*

### Moving parts

#### ENM-27 — Parts on joints or in orbit · MUST

Some kinds carry moving parts, like the bosses' limbs. A part either hangs on a joint of the hull
that swings to and fro (a sine of its amplitude, period and phase; a joint may hang on another
joint, so a limb can bend at several points), or orbits the hull, turned by the enemy's spin. A
part cannot do both.

**Acceptance criteria**
- Unit test: a part on a joint moves and turns with its joint (and its parent joints); a part in
  orbit turns with the spin.

*Sources: P05-R13, D-090.*

#### ENM-28 — A part is hit where it is drawn · MUST

Each part is drawn on its joint (or orbit) and moves with it. It has its own hit circle, health and
weapon. The player's shots hit a part where it is now; the hull's own hit circle stays at the
enemy's centre. A part's muzzles move with it, so its shots leave from where it is drawn.

**Acceptance criteria**
- Unit test: a part's hit circle and muzzle follow its joint's swing (or its orbit).

*Sources: P05-R13, P16-R04.*

#### ENM-29 — A destroyed part · MUST

A part shot to 0 health blows up (a small explosion), disappears from the model and stops its
weapon. It gives no points and drops no bonus.

**Acceptance criteria**
- Unit test: shooting a part to 0 destroys only that part and stops its weapon.

*Sources: P05-R13, D-090.*

#### ENM-30 — The enemy goes with its hull · MUST

An enemy with moving parts is destroyed when its hull's health reaches 0, whatever parts it still
has; its death blows up every part still on it. Its points are the kind's.

**Acceptance criteria**
- Unit test: the enemy is destroyed only with its hull, taking its remaining parts with it.

*Sources: P05-R13.*

#### ENM-31 — Shielding parts · MUST

A part may shield the hull: while it stands, the player's shots pass through the hull (as through a
boss's shielded core), but the hull can still ram the ship. Once every shielding part is destroyed,
the hull can be hit.

**Acceptance criteria**
- Unit test: with a shielding part standing, the hull is not among the shot targets; without it,
  it is.

*Sources: D-090.*

#### ENM-32 — Joints held still, sweeping lasers · SHOULD

A kind may hold its joints still for a while (e.g. to aim), and a laser fired from a moving part
may sweep, turning with the part as it fires, instead of keeping its starting heading.

*Sources: D-090.*

#### ENM-33 — Moving parts are an engine feature · MUST

Moving parts are a game-agnostic engine feature, built on the bosses' joints; the kinds that use
them, and their joints and parts, are game data, read from their config records.

*Sources: P05-R13, D-090.*

### Look

#### ENM-34 — Code-generated, seen from above · MUST

Every enemy model is generated from code (no model files), in logical pixels, nose forward. It is
shaped to be seen from above by the tilted camera.

*Sources: phase 5 preamble, GD-60.*

#### ENM-35 — Cyber-Organic bodies · MUST

Every enemy looks Cyber-Organic: living tissue fused with machinery. The body is rounded, swollen
flesh (segmented bodies, carapaces, organs, ribs, tendrils, membrane wings), balanced left and
right; metal is grafted on only where a part is man-made (armour plates, ducts, gun barrels,
nozzles, ports), with straight edges. Each kind keeps a silhouette that tells it apart from the
others and matches its role (the kind files describe it). Kinds that had wings and reactors keep
them.

*Sources: P16-R03, P16-R01, D-165.*

#### ENM-36 — Flesh and metal materials · MUST

An enemy body has two materials: the flesh, a waxy, barely metallic material, and the hull, the
dark metal of the grafts (GD-61: enemies are dark metallic, with neon lights). Their shades stay
dark (flesh shades 0.2 at most), so the lights carry the colour and the enemies keep their contrast
with the ground. Both take more light than the scenery (`hullLight`), so their shapes read.

*Sources: P16-R01, GD-61, D-165, D-127, D-231.*

#### ENM-37 — Lights · MUST

An enemy's lights are of three kinds, all unlit and glowing: steady neon lights (strips, rings,
glands, eye slits), pulsing veins with the eyes and glands lit as veins (ENM-42), and charge lights
(ENM-23).

*Sources: P16-R01, D-032.*

#### ENM-38 — Bright yellow or bright green · MUST

Every enemy's lights (neon, veins, eyes, charge lights), its edge trim and its reactor flames are
bright yellow or bright green, in the hue of its tier (ENM-49), keeping their brightness, never a
shade in between (no khaki), and never pink, magenta, violet or red. A boss's colours each take the
nearer of the two `enemyHues`. The enemy colours stay in the enemy colour family, which the enemy
shots, the bonuses and the player do not use (see [readability](../graphics/readability.md)).

**Acceptance criteria**
- Unit test: an enemy's light colours have its tier's hue; greys stay grey.

*Sources: D-231, P14-R02.*

#### ENM-39 — Body shades never khaki · MUST

The shades of an enemy's body (hull and flesh) keep their colour inside the `enemyBody` hue window
(moss greens, teals, ice blues) and are greyed to `enemyBody.maxSaturation` outside it (yellows,
olives, browns, reds, pinks), so an enemy's yellow or green is its lights'. The hull is tinted
`hull.tint` of the way towards the enemy's colour and lit faintly by it (`hull.selfLight`), the
flesh `flesh.tint`, through the same rule: a green enemy's metal is faintly green, a yellow one's
neutral.

**Acceptance criteria**
- Unit test: warm and pink body shades are greyed; green, teal, blue and grey ones are kept.

*Sources: D-231, phase 5 review.*

#### ENM-40 — Reactor flames · MUST

Every kind that flies on reactors has one or more at the back (the kind files give how many): a
dark open nozzle, a flat glowing core across its mouth, and an animated flame (an outer exhaust
cone and a whiter inner cone that flicker in length, width and brightness, and plasma puffs flowing
down the exhaust), in the enemy's colour, the inner flame `reactor.whiten` of the way to white. A
reactor is kept light (about 40 triangles). It may be set in a flesh sac with a vein running into
the body, read as a glowing organ.

**Acceptance criteria**
- Unit test: a reactor's flame takes the enemy's colour.

*Sources: phase 5 review, P16-R01, P16-R03, D-231.*

#### ENM-41 — Nothing only seen from below · MUST

The enemies are seen from above: a model has no detail placed where only its underside would show.

*Sources: phase 5 review.*

### Living motion

#### ENM-42 — Pulsing veins, fluttering wings · MUST

The enemy bodies feel alive with light, cheap animation: the veins (and the eyes and glands lit as
veins) pulse slowly between `glow.low` and full brightness every `glow.period`; membrane wings flutter about their
root (`flutter.angle` at `flutter.hz`, slower, `flutter.bigHz`, for wings spanning more than
`flutter.bigSpan`); rotors spin. The animation runs on the simulation time each frame, so a paused
game holds still.

**Acceptance criteria**
- Given the game paused, then no vein, wing or rotor moves.

*Sources: P16-R07, D-166.*

#### ENM-43 — No swelling breath · MUST

An enemy's body does not swell and shrink: it stays at its size. Its breath only sets the phase of
its veins' pulse.

*Sources: D-223, P16-R07.*

#### ENM-44 — One breath per creature · SHOULD

All the pieces of one creature (an enemy's hull and its moving parts) share one breath, so they
pulse as one body; breaths are spread from one creature to the next (`breathing.period`,
± `breathing.spread`), in a deterministic sequence.

*Sources: D-166, P16-R07.*

#### ENM-45 — The motion is visual only · MUST

The living motion never moves a hit circle or a shot's origin: the body (hull, flesh, lights,
wings) sits on a body node of its own, and the muzzles and reactor flames are outside it, on the
model's root.

**Acceptance criteria**
- Unit test: the muzzles and hit circles are the same with and without the living motion.

*Sources: P16-R07, P16-R08, D-166.*

### Readability

#### ENM-46 — The look never changes the game · MUST

A change of look (such as the Cyber-Organic rework) changes nothing of the gameplay: hit circles,
speeds, paths, health, attack patterns, points and spawns stay the same.

**Acceptance criteria**
- The gameplay unit tests pass without changing their expected values.

*Sources: P16-R08.*

#### ENM-47 — Standing out from the ground · MUST

Every enemy's silhouette separates from the ground on every world: it has a glowing edge trim in
its colour, lifted towards white (see [edge trim](../graphics/edge-trim.md)), and its dark body is
lit enough that its shape reads. The edge of its silhouette has a contrast ratio of at least
`min_object_contrast` with the ground around it.

**Acceptance criteria**
- Given the readability check of one level of each world (see
  [readability](../graphics/readability.md)), then the enemy measured meets the contrast threshold.

*Sources: P14-R04, P16-R08, D-220, D-127.*

#### ENM-48 — Kinds told apart at a glance · MUST

Each kind is recognisable at gameplay size and told apart from the others by its silhouette, not
only by its colour (the colour tells the tier, ENM-49, not the kind).

**Acceptance criteria**
- Given the dev enemies viewer, when the kinds are seen side by side at gameplay size, then each
  can be named (manual check).

*Sources: P16-R03, D-231.*

#### ENM-49 — One colour theme per tier · MUST

Each tier has a colour theme, the same for its five kinds, picked to stand out from the ground of
its world (the neon sits on the yellow-to-green ladder of the enemy colour family, so it never
leaves it; the hull is tinted its own colour):

| Tier (world) | Neon (hue) | Hull | Against the ground |
|--------------|------------|------|--------------------|
| 1 (World 1: sea, grass, red desert) | yellow, 60° | steel blue | yellow is furthest from the turquoise sea and the green grass; blue-grey against warm sand |
| 2 (World 2: rust desert, industry) | lime, 110° | dark teal | green is the complement of rust and orange light; a cold hull on a warm ground |
| 3 (World 3: dark damp earth, canals, stone) | chartreuse, 85° | indigo slate | brighter than the dark grey-green ground (weakest in hue on the grass of 3-4 and 3-5, so brightness carries it) |
| 4 (World 4: bright city, grey concrete) | emerald, 135° | near-black graphite | a deep saturated green on pale concrete, where yellow would wash out |

The enemy shots keep their own orange to amber family whatever the tier: the colour of an enemy
tells its tier, never what shoots at the player.

**Acceptance criteria**
- Given the four tiers, then their neon hues are in the enemy family (60°–140°) and at least 20°
  apart, and every kind's neon is its tier's (unit test).
- Given a model of a kind of a tier, when it is built, then its lights are drawn in its tier's hue
  and its hull is tinted its tier's colour (unit test).
- Given each world's level, then an enemy of its tier meets the contrast threshold of
  [readability](../graphics/readability.md) (e2e, one level of each world).

*Sources: reviewer request, 2026-11-03.*

#### ENM-50 — Each level mixes tiers · MUST

Each level mixes two or three tiers, each with its share of the level's enemy ships (a group of
several ships, such as a Wasp swarm, counts each of them; the filler counts too; the enemies a
carrier launches do not):

| World | First level | Last level | Between |
|-------|-------------|------------|---------|
| 1 | tier 1 80 %, tier 2 20 % | tier 1 60 %, tier 2 40 % | tier 2 grows by 5 points a level |
| 2 | tier 2 60 %, tier 1 40 % | tier 2 60 %, tier 3 40 % | tier 2 stays 60 %; the other 40 % slides from tier 1 to tier 3 by 10 points a level |
| 3 | tier 3 60 %, tier 2 40 % | tier 3 60 %, tier 4 40 % | as World 2, one tier up |
| 4 | tier 4 60 %, tier 3 40 % | tier 4 100 % | tier 3 shrinks by 10 points a level |

Every kind of each tier a level has comes in that level at least once. The waves of every level are
composed from its tier mix (`tier_mix` and `compose_beats` in `src/game/config/wave_plans.py`): each
beat goes to the tier furthest below its share; each tier brings each of its kinds once first (a
smaller tier one group at a time), then follows the role cycle; a wave brings no more than its tier
lacks; nothing is composed in the quiet stretch before a boss. A wave is one kind, so a share is
met to within 5 points.

**Acceptance criteria**
- Given each level's tier mix, then it is the table's (unit test).
- Given each assembled level, then each tier's share of its ships is within 5 points of its mix,
  and its waves name every kind of its tiers and no other (unit tests).

*Sources: reviewer request, 2026-11-03; owner request, 2026-11-08 (D-283).*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `L` (`ENEMY_UNIT`) | 34 logical px | `src/game/config/enemies.py`; the balanced ship, 4.8 model units × 7 |
| `HITBOX` | 0.85 | hit radius = `HITBOX` × size × L / 2 (`radius()` in `enemies.py`) |
| `ENEMY_SPAWN_MARGIN` | 60 px | `enemies.py`: how far outside the edge a group appears |
| `ENTRY_INSET` | 0.08 | `src/game/sim/enemies/enemy_helpers.py`: entries kept off the corners |
| `top_range` | the ship's reach at the bottom of its flight area (about 120–420 px in the 540 × 720 playfield window, D-252, D-263; 207–793 in the 1000 × 720 one, D-253; 107–373 px when measured on the 3:4 screen, D-048) | set by `LevelRun` |
| `cull_margin` | 80 px | `src/config/game_play.py` `GAME_PLAY_CONFIG` |
| `max_enemy_age` | 40 s | `GAME_PLAY_CONFIG` |
| `bullet_radius` | 4 px | `bullet()` in `enemies.py` |
| `blasts.missileScale` | 0.6 | `src/game/config/enemy_look.py` |
| `budget` tier 1 / 2 / 3 / 4 | 400 / 600 / 900 / 1200 triangles | `ENEMY_LOOK["budget"]` |
| `hitbox_footprint_tolerance` | 15 % | model footprint vs. the kind's size |
| `min_object_contrast` | 3:1 | see [readability](../graphics/readability.md) |
| `hull` metallic / roughness | 0.85 / 0.38 | `ENEMY_LOOK["hull"]`; shades base, panel, dark |
| `hull.tint` / `hull.selfLight` | 0.3 / 0.04 | D-231 (tint was 0.6) |
| `flesh` metallic / roughness / tint | 0.25 / 0.5 / 0.15 | `ENEMY_LOOK["flesh"]`; shades slate, graphite, teal, sinew, bone, membrane, wound |
| `hullLight` direct / environment | 1.8 / 1.8 | `src/game/config/readability.py` `READABILITY` |
| `enemyHues` | 60° (yellow), 125° (green) | `READABILITY`: bosses; enemies use their tier's hue |
| tier themes | neon 60° / 110° / 85° / 135°, hull blue / teal / indigo / graphite | `ENEMY_TIERS` in `src/game/config/enemy_tiers.py` |
| `enemyBody` | hues 100–250° kept, else saturation ≤ 0.1 | `READABILITY` |
| `enemyTrim` | whiten 0.25, strength 2.6, width 1.4 px, offset 0.1 px | `READABILITY` |
| `chargeIdle` | 0.18 | `ENEMY_LOOK` |
| `reactor` | 6-sided nozzle, core 0.75, flame 5 × 1.5 radii, 4-sided cones, 2 puffs, whiten 0.55 | `ENEMY_LOOK["reactor"]` |
| `rotor` | 2 blades, hub 0.22, 30 rad/s | `ENEMY_LOOK["rotor"]` |
| `glow` period / low | 1.2 s / 0.55 | `ENEMY_LOOK["living"]` |
| `breathing` period / spread | 2.5 s / ± 20 % | `ENEMY_LOOK["living"]` (phase only, D-223) |
| `flutter` | 6 Hz, 2 Hz above a 25 px span, 0.16 rad | `ENEMY_LOOK["living"]` |

## Notes

- The P05 enemies were first dark metal hulls with neon strips (lofted fuselages, bevelled wings);
  phase 16 reworked every model as Cyber-Organic. Their neon colours used to differ per kind; since
  the four tiers (2026-11-03) every kind takes its tier's colours (ENM-49).
- The rim outline of phase 14 was replaced by the edge trim built into the models (D-220).
- Reactor flames were all one light blue for a while (phase 5 review); they now take the enemy's
  colour (D-231).
- No unit test compares the models' marked muzzles with the config's muzzles, or the models'
  footprints with their sizes, since the Python port; both were checked by hand for the basic kinds
  (all footprints within 9 % of their size).
