# Bosses — common rules

> **Area:** bosses · **Prefix:** `BOSS` · **Related:** [level flow](../gameplay/level-flow.md),
> [lives and damage](../gameplay/lives-and-damage.md), [bonuses](../gameplay/bonuses.md),
> [scoring](../gameplay/scoring.md), [HUD](../ui/hud.md), [music](../audio/music.md),
> [enemies common](../enemies/common.md), [edge trim](../graphics/edge-trim.md),
> [readability](../graphics/readability.md), [effects](../graphics/effects.md),
> [shots](../graphics/shots.md), [debug options](../dev/debug-options.md)

Every level has two bosses: a mini boss around its middle and a final boss at its end. A boss is
one big code-generated creature made of a core and destroyable parts. The player shoots its parts
off one by one, its shielding parts first; each lost part changes its attack and, at set points, makes it
transform: it sheds armour or changes shape and reveals hidden weapons, which it then fires all out
for a few seconds (it is angry). This file holds every rule the bosses share. The boss files
(`bosses/mini/<N-M>-<name>.md`, `bosses/final/<N-M>-<name>.md`) only give what is specific to one
boss: its look, its parts and their numbers, its patterns and its transformations. Regular enemies
are in [enemies/](../enemies/common.md); the health gauge on screen is in [ui/hud.md](../ui/hud.md).

Sizes are in `L`, the length of the medium player ship (34 logical pixels). Offsets are logical
pixels from the boss's centre, X to the right of the screen and Y up the screen; a boss faces down
the screen, so its nose is at -Y.

## Requirements

### In the game

#### BOSS-01 — A mini boss and a final boss per level · MUST

Each level has exactly one mini boss and one final boss. They are two different boss kinds, and no
boss kind is used by two levels. Each boss kind has its own name and its own code-generated model,
themed for its world.

**Acceptance criteria**
- Given each level of every world, then its boss table names one mini boss and one final boss, two
  different kinds of the game (unit test).
- Given the bosses of a world, then no kind is used twice (unit test).
- Given every boss kind, then it has its own model and no model is left without a kind (unit test).

*Sources: GD-41, P07-R05.*

#### BOSS-02 — One boss at a time · MUST

The mini boss and the final boss arrive where [level flow](../gameplay/level-flow.md) puts them
(GAME-LEVEL-04: at the middle and at the end of the level's length); what the waves do around a
fight and how the level ends on the final boss is there too. Only one boss is fought at a time: the
next one cannot come in until the one being fought is gone.

**Acceptance criteria**
- Given a boss is being fought, then no other boss comes in until it is gone (unit test).

*Sources: P07-R06.*

#### BOSS-03 — Each boss's fight ground speed · MUST

Each boss has its own **fight ground speed**, a factor of the level's ground speed, given in its
boss file: some bosses slow the ground, at least one stops it (×0) and at least one speeds it up (a
chase). The ground eases to it as the boss arrives, holds it for as long as the boss is alive and
eases back once it is destroyed, as [level flow](../gameplay/level-flow.md) says (GAME-LEVEL-07).

**Acceptance criteria**
- Given the World 1 bosses, then their factors run from ×0 (Mesa Fortress) to ×1.5 (Storm Petrel).
- Manual validation: the change of speed is smooth, and the chase boss feels faster.

*Sources: P07-R03.*

#### BOSS-04 — A fight lasts until the boss is destroyed · MUST

A boss never leaves the screen and is never removed for being old or off screen: a fight lasts
until the boss is destroyed or the game is over. A fight lasts from the boss's arrival to the end of
its death blasts (BOSS-19).

**Acceptance criteria**
- Given a boss that is not shot at, then it stays on screen and keeps fighting.

*Sources: P07-R05, D-053.*

#### BOSS-05 — Boss music and health gauge · MUST

While a boss is fought, the boss music plays ([music](../audio/music.md)) and the boss's health
gauge shows, with its name and its rank ([HUD](../ui/hud.md)). What the gauge counts is BOSS-54.

**Acceptance criteria**
- Given a boss arrives, then the boss music starts and the gauge shows; given it is destroyed, then
  both end.

*Sources: GD-70, P07-R02.*

#### BOSS-06 — A checkpoint after the mini boss · MUST

Destroying a level's mini boss saves the level's checkpoint (GAME-LEVEL-09 in
[level flow](../gameplay/level-flow.md): its progress, the bosses passed, the weapons and the
score), and the mini boss drops a life bonus ([bonuses](../gameplay/bonuses.md)).

**Acceptance criteria**
- Given the mini boss of a level is destroyed, then a checkpoint is saved at the mini boss's
  distance with the weapons the player has then (unit test).

*Sources: P07-R08, GD-42.*

#### BOSS-07 — The boss engine and the bosses kept apart · MUST

The boss engine is game-agnostic code outside `src/game/`: a boss as an enemy made of a core and
parts that shots, collisions and bonus drops see as targets, shielding, stages, pauses, rage,
transformations, joints, turrets, roll, volley shapes, fight ground speed and health. Each concrete
boss is data (its design: parts, numbers, guns, stage patterns, rage, hidden weapons, armour
regions) and a model in `src/game/`. A stage's pattern is data, not code; a boss needs no class of
its own.

**Acceptance criteria**
- Given the code outside `src/game/`, then it names no concrete boss.
- Given a new boss, then it is added as a design and a model only.

*Sources: D-053, D-055, D-068.*

### Coming in and moving

#### BOSS-08 — Coming in · MUST

A boss appears just above the top edge (its hit circles `boss_spawn_margin` above it), centred on
the ship's reach, and comes straight down at `boss_entry_speed`, braking over the last
`boss_brake_distance` (never below a fifth of its speed) into its place in the upper part of the
screen, at its stop height (a share of the playfield's height, in its boss file). Coming in takes
about `boss_entry_time`.

**Acceptance criteria**
- Given a boss is spawned, then it is above the top edge and comes down to its stop height, braking
  as it gets there (unit test).

*Sources: P07-R05.*

#### BOSS-09 — No damage while coming in · MUST

A boss takes no damage until it is in place. While it comes in, shots that hit its core or any of
its parts spark on it and are used up, but no health is lost.

**Acceptance criteria**
- Given a boss coming in, when it is hit, then neither its core nor its parts lose health (unit
  test).
- Given a boss coming in, then shots hit all of it, core included (unit test).

*Sources: P07-R05, D-053.*

#### BOSS-10 — Moving within the ship's reach · MUST

Once in place, a boss sways left and right (a sine of its own amplitude and period) and bobs up and
down (its own amplitude and period). Its sway is cut down so that its hit circles never leave the
player ship's horizontal reach ([player ship](../gameplay/player-ship.md)); orbiting parts count at
their full reach all round.

**Acceptance criteria**
- Given a boss whose sway would take a part out of the ship's reach, then its sway is cut so that
  every hit circle stays inside it (unit test).

*Sources: P07-R05.*

#### BOSS-11 — Rolling into sideways moves · MUST

A boss rolls into its sideways moves, the side it moves to dipping: up to `boss_roll.maxDeg` at
`boss_roll.fullSpeed` across, in proportion below it, easing towards its roll `boss_roll.easePerSec`
of the way a second. The roll is in the simulation: the muzzles roll with it, so shots still leave
from the barrels; the hit circles do not turn with it.

**Acceptance criteria**
- Given a boss moving across at 60 px/s, then it rolls towards 12°, and back to level when it stops
  (unit test).
- Manual validation: the bosses lean into their sways.

*Sources: P07-R05, D-057.*

### Parts and core

#### BOSS-12 — A core and destroyable parts · MUST

A boss is one object made of a **core** and several **destroyable parts** (turrets, pods, hangars,
armour plates, limbs…), each with its own health and hit circle. Parts are attached to the core and
move with it. A player shot that hits a part damages that part only; a part at 0 health is
destroyed. The boss is destroyed when its core reaches 0 health.

**Acceptance criteria**
- Given a boss with an intact part, when shots hit that part until its health reaches 0, then that
  part is destroyed and the other parts and the core keep their health (unit test).
- Given a boss, then its parts sit at their offsets from its centre (unit test).

*Sources: P07-R01, GD-46, D-053.*

#### BOSS-13 — How many parts · MUST

A mini boss has 2 or 3 destroyable parts as it comes in; a final boss has 4 to 6. The hidden weapons
it reveals as it transforms (BOSS-38) come on top of these.

**Acceptance criteria**
- Given each mini boss and final boss design, then it has 2–3 and 4–6 parts there from the start,
  respectively.

*Sources: P07-R01.*

#### BOSS-14 — A shielded core · MUST

Some parts **shield the core**: while any of them stands (and is revealed), the core takes no
damage. Which parts shield the core is part of each boss's data; its hidden weapons shield it once
revealed. Once no shielding part is left, the core takes damage.

**Acceptance criteria**
- Given a shielding part is still there, when the core is hit, then the core's health does not
  change (unit test).
- Given every shielding part is destroyed, when the core is hit, then it loses health (unit test).
- Given a hidden shielding weapon, then it does not shield the core until it is revealed (unit
  test).

*Sources: P07-R01, D-221.*

#### BOSS-15 — Shots go through a shielded core · MUST

While a boss fights with its core shielded, the player's shots go through the core to the parts
behind it: bullets, missiles (they do not home on it) and the laser. Once no shielding part is left
(and while the boss comes in, BOSS-09), the core stops shots again. The ship still bumps into a
shielded core (BOSS-16).

**Acceptance criteria**
- Given a fighting boss with a shielding part left, then its core is not among the targets the
  player's shots can hit, and its parts are (unit test).
- Given the shield is gone, then shots hit the core and damage it (unit test).

*Sources: P07-R01, D-062.*

#### BOSS-16 — Touching a boss · MUST

The player is hurt by touching a boss's core or any of its parts that are there (not destroyed, not
hidden), with the collision damage of [lives and damage](../gameplay/lives-and-damage.md). The boss
takes no ramming damage.

**Acceptance criteria**
- Given the player touches a boss part, then the player takes the collision damage and the part
  loses no health (unit test).
- Given a part out of the ship's reach, then it is no collision (unit test).

*Sources: P07-R06, D-053.*

#### BOSS-17 — Hit flash and smoke · MUST

A part or the core that takes damage flashes white for `boss_hit_flash`. A part under
`boss_smoke_below` of its health smokes: a few grey puffs rise from it and drift back, growing and
fading, again and again.

**Acceptance criteria**
- Given a part is hit, then it shows white for about one frame.
- Given a part under half its health, then smoke rises from it until it is destroyed (unit test on
  the puffs).

*Sources: P07-R01.*

#### BOSS-18 — A destroyed part leaves no stump · MUST

A destroyed part explodes ([effects](../graphics/effects.md)) and its model is hidden: it leaves no
stump, no wound and no debris, and the boss is visibly missing it. Its smoke stops.

**Acceptance criteria**
- Given a part is destroyed, then its model is no longer shown and nothing is drawn in its place.

*Sources: P07-R01, P16-R05, D-167, D-225.*

#### BOSS-19 — Death · MUST

When its core reaches 0 health the boss dies: every part still there is destroyed with it, it stops
firing and turning its turrets, and blasts go off over its hull, one every `boss_death.every`, each
near one of its parts in turn (near the core when it has none), for `boss_death.seconds`. Then it is
removed as destroyed, with its own big explosion, and scores its points
([scoring](../gameplay/scoring.md)).

**Acceptance criteria**
- Given the core reaches 0, then the boss's parts are destroyed, it blasts over its hull for about
  2 s, then it is gone (unit test).

*Sources: P07-R01, P07-R06.*

### Stages and patterns

#### BOSS-20 — Stages · MUST

A boss goes through **stages**: stage 0 with every part there, then one stage more each time one of
its parts is destroyed (stage *k* once *k* parts are destroyed; a part that retires, BOSS-46, is not
destroyed). Each stage has its own **shooting pattern** (which weapons fire, what, how often, in
which directions), set in the boss's data. A boss has one pattern more than it has parts there from
the start; once it has lost more parts than that (its revealed weapons), it stays on its last one.

**Acceptance criteria**
- Given a boss in stage *k*, when a part is destroyed, then it is in stage *k*+1 (unit test).
- Given each boss design, then it has one stage more than its parts there from the start (unit
  test).

*Sources: P07-R04, GD-46.*

#### BOSS-21 — A new pattern at every stage · MUST

Each weapon is on a part or on the core; the weapons of a destroyed part stop for good. The parts'
volleys are the same in every stage, each stopping with its part, and the core fires something new
at every stage, so the pattern of a stage is never the pattern of the stage before it, whatever the
order the parts are destroyed in. The last stage (every part there from the start destroyed) fires a
ring or a spiral used in no earlier stage.

**Acceptance criteria**
- Given a boss and any order of destruction of its parts, then each stage's pattern differs from
  the previous one's (unit test, every boss).
- Given a part with a weapon is destroyed, then that weapon never fires again (unit test).
- Given each boss design, then its last stage's pattern is not used in an earlier stage (unit
  test).

*Sources: P07-R04, GD-46, D-055.*

#### BOSS-22 — A pause and a warning after a lost part · MUST

When a part is destroyed, the boss fires nothing for `stage_change_pause` and its charge lights (its
neon colour) strobe at `boss_stage_strobe`, so the player sees the change coming. It can still be
damaged and still moves. Then the new stage's pattern starts.

**Acceptance criteria**
- Given a part is destroyed, then the boss fires nothing for 1 s (unit test).
- Given the pause, then its charge lights strobe (unit test).

*Sources: P07-R04.*

#### BOSS-23 — What bosses fire · MUST

Boss patterns are made of volleys, each on its own timer (`every`, and `first` from the start of the
stage), fired from its piece's muzzles:
- bullets: aimed shots and aimed fans (the middle one at the player), bursts (single shots at the
  player a gap apart), fans around a preset heading, rings all around and spirals (a ring turned a
  little more at each volley);
- big, slow bullets that burst into a ring of small ones after a set time;
- homing missiles the player can shoot down;
- lasers, each with its 1 s warning line first;
- enemies launched from a part (BOSS-25).

A part may also burst into a ring of bullets when it is destroyed. Bullets, missiles and lasers are
those of [shots](../graphics/shots.md); bullet colours are style names, all in the enemy shots'
family.

**Acceptance criteria**
- Given each volley shape, then it fires as described, from the muzzle furthest along each shot's
  way (unit tests).
- Given a part that bursts when destroyed, then it fires its ring once (unit test).

*Sources: P07-R04, GD-43, GD-44, D-068.*

#### BOSS-24 — Volleys tied to another part · SHOULD

A volley may fire only while a given part stands, or only once a given part is destroyed (e.g. a
radar that makes the other guns aim). Patterns compare and turrets aim with these conditions taken
into account.

**Acceptance criteria**
- Given a volley that needs a part, when that part is destroyed, then it stops; given a volley
  after a part, then it starts once that part is destroyed (unit tests).

*Sources: D-068.*

#### BOSS-25 — Launched enemies · MUST

A part may launch regular enemies while it stands, in every stage, on its own timer: a hangar's
Hornets fly out to the side of the boss it is on, then down the Carrier's launch path; a bay's
Hornets leave side by side and dive at the player ([Hornet](../enemies/hornet.md), whatever the
world). They count among the level's spawned enemies.

**Acceptance criteria**
- Given a hangar launch, then the asked count of Hornets leaves towards the hangar's side (unit test).
- Given a bay launch, then the Hornets leave side by side, centred on the bay (unit test).

*Sources: P07-R04, D-055.*

#### BOSS-26 — The level's difficulty applies · MUST

A boss's volley timers run at the level's fire-rate factor, and its bullets fly at the level's
bullet-speed factor (both for a bullet that bursts and for the ring it bursts into), as for the
regular enemies ([enemies common](../enemies/common.md)).

**Acceptance criteria**
- Given a fire-rate factor of 2, then a volley fires twice as often (unit test).

*Sources: P07-R10, D-068.*

### Rage

#### BOSS-27 — Angry when new weapons come out · MUST

A lost part makes the boss pause (BOSS-22) but no longer angry. It is **angry** only after a
transformation (BOSS-37), when it has revealed hidden weapons: at once (any pause left from the
part that called for the transformation is cancelled, and each weapon's first volley comes
`boss_rage_first` after it opens fire, the weapons `boss_rage_stagger` apart) and for
`boss_rage_seconds` it fires only
those new weapons, `boss_rage_rate` times as often, instead of its stage's pattern, so its bullet hell
comes from them, whatever their kind (bullets, rings, missiles, lasers, a hangar's Hornets). A missile
rack fires `boss_rage_missiles` times as many missiles; a laser cannot fire faster than its warning,
its beam and `boss_rage_laser_gap` allow. Its charge lights flicker at `boss_rage_flicker` down to its
dim level. It can be damaged meanwhile. A part destroyed while it is angry pauses it (BOSS-22), and
the rage goes on afterwards; a destroyed weapon stops firing; its death stops the rage. Its angry
pattern starts afresh with each transformation.

**Acceptance criteria**
- Given a part is destroyed (no transformation), then the boss is not angry (unit test).
- Given a transformation is over, then the boss is angry for 8 s, with no pause, and fires only the
  weapons that transformation revealed, the first volleys within 1 s (unit tests).
- Given an angry boss, then each of those weapons fires 4.5 times as often, a missile rack three times
  as many missiles, and a laser at most as often as its warning, beam and gap allow (unit tests, every
  boss).

*Sources: D-063, D-221, D-256.*

### Turrets, lasers and limbs

#### BOSS-29 — Turrets turn the way they fire · MUST

A piece's guns may be on a **turret** (a pivot of its own): the turret turns at up to
`boss_turret_turn` the way its next volley goes (a burst under way first, else the volley due
soonest): at the player for aimed shots and bursts, along a fan's preset heading, and with a ring's
turn, so a turret firing a spiral spins smoothly from one volley's turn to the next and never spins
back. It keeps turning during pauses. Its muzzles turn with it, so shots leave the barrel tips and
aimed shots are aimed from there. Guns built into hulls, blades, claws or pods, missile cells and
launchers do not turn. In the model each turret is its own piece on its pivot; it flashes and hides
with its part.

**Acceptance criteria**
- Given a turret whose next volley is aimed, then it turns towards the player at most 150°/s (unit
  test).
- Given a turret firing rings, then it points at the barrel nearest the ring's next turn (unit test).
- Manual validation: every boss turret visibly turns.

*Sources: D-058, D-060.*

#### BOSS-30 — Lasers warn, then lock · MUST

A boss laser shows its warning line for 1 s, then fires its beam for its firing time. During the
warning the line follows its owner's heading; when the beam fires it keeps the heading it had then
(it is locked) and still leaves from its emitter. A laser fired from a swinging limb does not swing
while it fires.

**Acceptance criteria**
- Given a laser, then its beam fires along the heading its owner had when the warning ended (unit
  test).

*Sources: GD-43, D-072.*

#### BOSS-31 — Lasers on turrets · MUST

No boss laser turns while it fires, except a sweeper's (BOSS-40). A laser on a turret aims at the
player during its warning line at only `boss_laser_turn` (so the beam can be outrun), then holds
still while its beam fires. A sweeper's turret keeps following the player at that same rate while
its beam fires. Lasers built into a hull fire straight down.

**Acceptance criteria**
- Given a laser turret during its warning, then it turns towards the player at most 20°/s (unit
  test).
- Given its beam fires, then it holds still; given a sweeping beam, then it keeps following (unit
  tests).

*Sources: D-073, D-229.*

#### BOSS-32 — Each boss's laser in its own colour · MUST

A boss's lasers (warning line, beam, base flare) are drawn in its own neon colour folded into the
enemy shots' colour family (orange to amber, [readability](../graphics/readability.md)): a white-hot
beam core with that colour round it, fading out. Lasers of anything else take the Lancer's colour.

**Acceptance criteria**
- Given a boss's laser, then its colour is its neon folded into the enemy shots' family (unit test).

*Sources: D-072, D-231.*

#### BOSS-33 — Moving limbs · MUST

A boss may have **joints**: pivots that swing to and fro (a sine of an amplitude, a period and a
phase), each hanging on the body or on another joint, so an arm can swing at the shoulder, bend at
the elbow and turn at the wrist. A part on a joint moves with it, its hit circle and muzzles too, so
its shots leave its barrels and the player's shots hit it where it is drawn. Joints swing all the
time the boss is there. Joints are checked when the boss is built: no unknown parent, no loop, no
part both orbiting and on a joint. The model turns a node per joint by the same angles, carrying the
parts and limbs drawn on it; a limb of a part hides and flashes with it.

**Acceptance criteria**
- Given a part on a joint mid-swing, then its hit circle and its barrels' tips are where the model
  draws them (unit test).
- Given a joint hanging on an unknown joint, on itself or in a loop, then building the boss fails
  (unit test).

*Sources: D-061.*

#### BOSS-34 — Turning rings · MUST

A boss's parts may orbit its centre on a turning ring, at its spin rate: their hit circles and
muzzles turn with the ring, and the model's ring turns with them.

**Acceptance criteria**
- Given an orbiting part, then its place and its muzzles turn with the boss's spin (unit test).

*Sources: P07-R05.*

### Transformations

#### BOSS-35 — Mini bosses transform once, final bosses twice · MUST

As it loses parts, a boss **transforms** to get harder: a mini boss transforms once, a final boss
twice. Each transformation reveals 1 to 3 hidden weapons (BOSS-38), and sheds armour (BOSS-42) or
changes shape (BOSS-45).

**Acceptance criteria**
- Given each mini boss, then it transforms once; given each final boss, then twice (unit test).
- Given each transformation, then it reveals 1 to 3 armed weapons, each firing once revealed (unit
  test).

*Sources: D-221.*

#### BOSS-36 — When a boss transforms · MUST

A boss with K transformations and n parts there from the start transforms the k-th time once
ceil(k n / (K + 1)) of those parts are destroyed (half of them for a mini boss, a third and two
thirds for a final boss), unless its design names, for each transformation, the parts whose
destruction calls for it (all of them). Revealed weapons destroyed do not count. Thresholds crossed
at once give transformations one after the other. Parts broken while it comes in make it transform
once it is in place.

**Acceptance criteria**
- Given a mini boss with 3 parts, then it transforms once 2 are destroyed (unit test).
- Given a boss that transforms on named parts, then it transforms once all of them are destroyed,
  whatever else is lost (unit test).
- Given two thresholds crossed at once, then it transforms twice, one after the other (unit test).

*Sources: D-221, D-228.*

#### BOSS-37 — During a transformation · MUST

A transformation lasts `boss_transform_seconds`. Meanwhile the boss goes on moving but neither fires
nor takes damage, its charge lights strobing as in a pause. A blast goes off where each hidden
weapon comes out, and each shed armour region bursts in up to `boss_region_blasts` blasts. At its
end that transformation's weapons are revealed (they can be hit, they shield the core, they fire);
the boss then holds its fire for what is left of the pause of the part that called for it
(BOSS-22) and is angry (BOSS-27): its new weapons fire all out.

**Acceptance criteria**
- Given a boss transforming, then it fires nothing and loses no health (unit test).
- Given the transformation is over, then its new parts are live and it is angry (unit test).

*Sources: D-221, D-224.*

#### BOSS-38 — Hidden weapons · MUST

A hidden weapon is a destroyable part revealed by a transformation. Until then it cannot be hit,
does not shield the core, takes no damage, does not fire and lies folded flat out of sight. Once
revealed it shields the core and drops a bonus `hidden_weapon_drop` of the time. Its health is
`hidden_weapon_health` of the boss's sturdiest part there from the start (first or second
transformation), rounded to 10. A mini boss reveals a pair at its transformation, a final boss a
pair at each of its two (a third on the centre line for some). Its bullets are in the boss's main
bullet colour. Its kinds are kinds the boss does not fire yet, where possible.

**Acceptance criteria**
- Given a hidden part, then it is neither hit nor shields the core nor takes damage (unit test).
- Given a revealed weapon, then it fires its kind's volleys until it is destroyed (unit test).

*Sources: D-221, D-229.*

#### BOSS-39 — Never easier after a transformation · MUST

A boss never fires less after a transformation than before it: its fire rate (a bullet weighs 1, a
homing missile 2, a laser 8 and a launched enemy 2, a second), the parts that called for the
transformation counted as destroyed, never goes down from one transformation to the next, and is
higher after the last one than as it came in.

**Acceptance criteria**
- Given each boss, then its weighted fire rate as it comes in and after each transformation never
  goes down, and ends higher (unit test).

*Sources: D-221, D-229.*

#### BOSS-40 — The kinds of hidden weapon · MUST

A hidden weapon stands on a pod that tells its kind apart (octagon, square, round base, long deck,
box), and fires as its kind does (numbers in Tunable values):
- **gatling**: a three-barrelled turret following the player, firing bursts;
- **lance**: a laser lance pointing down the screen, firing a laser;
- **rack**: four missile cells, firing pairs of homing missiles;
- **orb**: a glowing emitter in a cradle, firing turning rings;
- **beam**: a cannon at the end of a rig the boss unfolds, firing a giant laser (the Scorpion's
  tail, [Scorpion](mini/1-4-scorpion.md));
- **cannon**: a big turret on a square base with one heavy barrel, firing aimed spreads of big shells;
- **mortar**: a short, wide tube tilted up on a round base, lobbing flak shells that burst into a
  ring;
- **battery**: a long, low deck with five barrels in a row, firing wide fans straight down;
- **sweeper**: a turret with two prongs and a lens, firing a laser that sweeps after the player;
- **hangar**: a box whose two doors slide apart, launching Hornets.

Its muzzles are worked out from its size and pod height, and the model is drawn from the same
numbers, so shots leave its barrels.

**Acceptance criteria**
- Given every kind, then it has its own pod and a turret or something that slides out (unit test).
- Given each kind, then it fires its volleys from the muzzles its model draws (unit tests).

*Sources: D-221, D-228, D-229.*

#### BOSS-41 — Variety of hidden weapons · MUST

Over all the bosses: no kind (the beam aside) is more than a fifth of the hidden weapons; each world
reveals at least six kinds; a final boss's second transformation reveals no kind its first did;
hangars are on final bosses only, at most one a world; at least ten bosses reveal a weapon on their
centre line.

**Acceptance criteria**
- Given every boss design, then these counts hold (unit tests).

*Sources: D-229.*

#### BOSS-42 — Shedding armour regions · MUST

At each transformation a boss sheds one or more **armour regions**. A region is a top-view outline
of the boss's design (mirrored across the centre line unless asked not to), and a piece of armour
its model draws as a part of its own, lying on the core there: at rest the boss looks as drawn, its
armour on. The core is drawn without the armour, so nothing is ever cut out of a drawing: the whole
armour is simply replaced by its broken pieces and its frame when it is shed. Each hidden weapon
lies in a region its transformation sheds (unless it rides a moving piece, BOSS-45, or sits on a
rig, BOSS-46).

**Acceptance criteria**
- Given each boss, then every transformation sheds a region and every hidden weapon lies in one its
  transformation sheds (unit test).
- Given each region, then the boss's model draws its armour, and the pieces it bursts into stay
  within the piece budget (unit test).

*Sources: D-224, D-227, D-254.*

#### BOSS-43 — How armour bursts and weapons unfold · MUST

Through a transformation (in shares of its length): the armour strains, shuddering and strobing,
until `reveal.burst`; it bursts into **pieces** thrown out, up and down, tumbling and shrinking
away, gone by `reveal.burstEnd`. The pieces are the ones the model draws for the region, else
plates cracked from the region's outline (at most `armour.chunks` a region and `armour.bossChunks`
a boss), `armour.plate` thick at the top of the armour, in the armour's own colour. Each hidden
weapon, folded flat under the armour until `reveal.swing[0]`, swings up on its hinge (its mount, or
its inner side, folded back along the hull), rising, until `reveal.swing[1]`, then slides its
barrel, cells, orb, tube, doors or turret out, overshooting a little, until `reveal.slide[1]`.
Nothing grows or shrinks into place.

**Acceptance criteria**
- Given a hidden weapon, then it stays folded away until the armour has burst and ends unfolded,
  its barrel out, at its full size (unit test).
- Given a region drawn without its own pieces, then its plates cover its outline, within the piece
  budget, in its colour (unit test).
- Manual validation: the armour bursts off and the weapons unfold out of the frame.

*Sources: D-221, D-224, D-254.*

#### BOSS-44 — The frame a shed region leaves · MUST

Where armour has burst off, a dark metal **frame** shows: a dark floor in the region's own outline,
just over the armour's lowest point, and dark metal ribs across it (`wing`: ribs across and two
spars; `shell`: a lattice; `ring`: spokes and a hoop), one rib in three with a thin neon seam, pipes
along the two longest. The frame is drawn from the region's outline unless the boss's model draws
its own. Only the floor carries a glowing outline, so the frame reads as dark metal.

**Acceptance criteria**
- Given a shed region, then its floor lies flat and dark within its outline and its ribs stay within
  it (unit test).

*Sources: D-224, D-254.*

#### BOSS-45 — Changing shape · MUST

Instead of bursting off, an armour region's piece (its drawn armour) may stay on and **move** into
a new pose as the boss transforms: a swing about a pivot (about the vertical, along the boss or across it) between two
angles, or a slide between two offsets, mirrored for a pair. It strains as armour does, then moves
between `reveal.move[0]` and `reveal.move[1]`, eased, and may leave a frame where it was drawn. A
hidden
weapon whose pod lies on a moving piece in its end pose rides it in. A part the player can hit never
stands on a piece as it moves: such parts are gone by then (the transformation names them). Two
bosses in each world change shape.

**Acceptance criteria**
- Given a moving piece, then it rests until its transformation, then moves and stays moved (unit
  test).
- Given a weapon riding a piece, then its whole pod ends up on it (unit test).
- Given every boss, then exactly eight change shape, two a world (unit test).

*Sources: D-230.*

#### BOSS-46 — Turning round and retiring parts · MUST

A transformation may turn the whole boss round by a set angle: its heading eases round over the
transformation, and its parts' places, hit circles and muzzles turn with it. A part may **retire**
at a transformation (another part takes over from it): from the start of that transformation it is
hidden, cannot be hit, is not destroyed (the stage does not move) and no longer counts in the boss's
health. A hidden weapon may sit at the end of a rig the boss unfolds instead of in an armour region.

**Acceptance criteria**
- Given a boss that turns by pi as it transforms, then at the end its parts sit at their offsets
  turned by pi (unit test).
- Given a part retiring at a transformation, then it leaves the fight as it starts, without a stage
  change (unit test).

*Sources: D-228.*

### Look

#### BOSS-47 — One Cyber-Organic creature · MUST

Every boss follows the Cyber-Organic style of the enemies ([enemies common](../enemies/common.md)):
a living biomechanical creature (or a creature-ship) with metal grafted on, its reactors glowing
organs, its lights veins and glands. It reads as one creature, not parts stuck on a box, with its
world's theme still recognisable (a coastal boss feels marine). Final bosses are larger and more
detailed than mini bosses. Some details are not symmetrical. The look is visual only: each part
keeps its position, size, hit circle and muzzles, and the patterns are unchanged.

**Acceptance criteria**
- Manual validation in the boss viewer: every boss reads as one creature of its world.
- Given each boss model, then it draws every part of its design and builds geometry for its body
  and parts (unit test).

*Sources: P16-R05, P16-R06, P07-R05.*

#### BOSS-48 — Parts read as targets · MUST

Each destroyable part is an organ, a limb or an armoured growth with a clear outline, so the player
sees what to shoot. Each part has its own glowing edge trim along its whole outline, wherever it sits
on the hull ([edge trim](../graphics/edge-trim.md)), so the player sees which parts can still be
hit.

**Acceptance criteria**
- Manual validation: every part stands out of its boss's body.

*Sources: P16-R05, P14-R04, D-220.*

#### BOSS-49 — Armour over a mechanism · MUST

Bosses look like fat armour over a complex mechanism: thick plates and grafts over a darker
mechanism or body that shows in their gaps, with surface detail (plates, seams, vents, rivets,
cables, small lights). When armour is shed, the dark metal frame beneath shows (BOSS-44).

**Acceptance criteria**
- Manual validation in the boss viewer.

*Sources: P07-R05, D-224.*

#### BOSS-50 — Colours · MUST

Every boss has one neon colour (in the boss look). Its lights (neon, veins, charge lights, edge
trim) take the nearest of the two enemy hues, bright yellow or bright green, keeping their
brightness: warm neon shows yellow, cool neon green. Its body shades (hull and flesh) keep their
colour only from moss green to ice blue; outside that window they are greyed out, so a boss's yellow
or green is its lights' ([readability](../graphics/readability.md)). Its bullets are in the enemy
shots' orange to amber family.

**Acceptance criteria**
- Given a boss's lights, then they are one of the two enemy hues (unit test).

*Sources: D-231, GD-61.*

#### BOSS-51 — One breath · SHOULD

A boss's core, parts, limbs and turrets share one breath, so the creature's veins pulse as one;
the body does not swell. The motion is visual only and runs from the frame time, so it freezes on
pause ([enemies common](../enemies/common.md)).

**Acceptance criteria**
- Given a boss model, then its pieces share one breath.

*Sources: P16-R07, D-166, D-223.*

#### BOSS-52 — A boss stays one object · MUST

At rest and after each transformation, a boss is one object: its core, the armour still on, the
frames of shed regions, its parts standing (and what slides out of its weapons) and its rigs hold
together (surfaces within `armour.hold` of each other). Nothing of it hangs in the air: the model is
drawn so (a light over a hull on a stem of its own; a part standing where a surface stays under it
once the armour is gone). The game adds no stem, pylon or beam of its own.

Turrets (on their parts) and limbs (on their joints) are not checked.

**Acceptance criteria**
- Given every boss, at rest and after each transformation, then its surfaces make one piece (unit
  test).

*Sources: D-227, D-230, D-254.*

#### BOSS-53 — Triangle budget · MUST

A mini boss model stays within `tri_budget_mini_boss` triangles and a final boss model within
`tri_budget_final_boss`. Each model is built once and shared.

**Acceptance criteria**
- Given each boss model, then its triangles are within its budget (unit test).

*Sources: P07-R05, P16-R09.*

### Health, difficulty and rewards

#### BOSS-54 — A boss's health · MUST

A boss's full health is its core's and every part's, its hidden weapons included from the start, so
the gauge never grows back. Its health left is its core's and its parts' left; a retired part's
health leaves it. The gauge marks the share of each part ([HUD](../ui/hud.md)).

**Acceptance criteria**
- Given a boss with hidden weapons, then its full health counts them from its arrival (unit test).
- Given a part loses 50 health, then the health given to the gauge goes down by 50 (unit test).

*Sources: P07-R02, D-221, D-228.*

#### BOSS-55 — Harder from level 1 to level 5 · MUST

In each world, the bosses get harder from its first level to its last, and every boss of 1-1 stays
beatable for a kid: the full health of the mini bosses goes up strictly from level 1 to level 5, and
so does that of the final bosses; each final boss has more full health than its level's mini boss;
the level's fire-rate and bullet-speed factors apply (BOSS-26).

**Acceptance criteria**
- Unit test: in each world, mini boss and final boss full health each go up strictly from level 1
  to 5, and each final boss has more than its level's mini boss.
- Manual validation: the 1-1 bosses feel easy, the 1-5 bosses clearly harder.

**Discrepancy:** with the hidden weapons counted (BOSS-54), the 1-1 final boss's full health
(Storm Petrel, 10 420) is above the 1-2 final boss's (Gull Mothership, 9 740); without them it is
below (5 770 against 5 960). The World 1 mini bosses (3 200 → 5 150) do go up. No unit test checks
this rule.

*Sources: P07-R10.*

#### BOSS-56 — Fight times · MUST

A boss's health is tuned so that a simulated player (the balanced ship, guns at level 3, always on
target, flying under the next shielding part, then the others, then the core) needs a fight time in
the ranges of its world. World 1's are in Tunable values; the other worlds' are in their world
files.

**Acceptance criteria**
- Unit test (simulation): every boss's fight, from arrival to the end of its death blasts, lasts
  within its range.

*Sources: P07-R10, D-055.*

#### BOSS-57 — Bonuses from destroyed parts · MUST

A destroyed part drops a weapon bonus with its own chance, set in its boss's data:
`part_drop_chance` for a mini boss's part, `final_part_drop_chance` for a final boss's,
`hidden_weapon_drop` for a hidden weapon. A final boss's core always drops one; a mini boss's core
drops one with the regular enemies' chance. A boss or a part never drops a life or a bomb bonus that
way. Bonuses fall from where the part was, within the ship's reach, and work as in
[bonuses](../gameplay/bonuses.md) (GAME-BONUS-04). Drops are drawn from the level's seed, so the
same fight drops the same bonuses.

**Acceptance criteria**
- Given a part with a drop chance of 1 is destroyed, then a weapon bonus appears where it was; with
  a chance of 0, none (unit tests).
- Given a final boss is destroyed, then a weapon bonus appears.
- Given the same level played twice with the same parts destroyed in the same order, then the same
  parts drop bonuses.

*Sources: P07-R07, D-055, D-221.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `boss_speed_ease` | 2 s, in and out | BOSS-03 (GAME-LEVEL-07); `src/game/config/boss_fights.py` `BOSS_FIGHT_RULES.speedEaseSeconds` |
| fight ground speed factor | ×0 to ×1.5, per boss | BOSS-03; each design's `stats.groundSpeed` |
| `health_bar_fill` | 1 s | BOSS-05; `BOSS_FIGHT_RULES.barFillSeconds` (the gauge: [HUD](../ui/hud.md)) |
| `boss_spawn_margin` | 30 px above the top edge | BOSS-08; `src/game/config/bosses/boss_kit.py` `BOSS_TIMING.spawnMargin` |
| `boss_entry_speed` | 75 px/s | BOSS-08; `BOSS_TIMING.entrySpeed` |
| `boss_brake_distance` | 60 px | BOSS-08; `BOSS_TIMING.brakeDistance` |
| `boss_entry_time` | about 3 s | BOSS-08; no damage meanwhile |
| `boss_roll` | up to 12° at 60 px/s across, easing 4 a second | BOSS-11; `BOSS_TIMING.roll` |
| `mini_boss_parts` / `final_boss_parts` | 2–3 / 4–6, hidden weapons apart | BOSS-13 |
| `boss_hit_flash` | white, 0.05 s | BOSS-17; `src/game/config/boss_look.py` `BOSS_LOOK.flash` |
| `boss_smoke_below` | 0.5 of the part's health; 3 puffs, 0.45 of its radius, 1.1 s cycle | BOSS-17; `BOSS_LOOK.smoke` |
| `boss_death` | a blast every 0.16 s for 2 s | BOSS-19; `BOSS_TIMING.death` |
| `stage_change_pause` | 1 s | BOSS-22; `BOSS_TIMING.stagePause` |
| `boss_stage_strobe` | 6 Hz | BOSS-22; `BOSS_LOOK.stageStrobeHz` |
| `boss_rage_seconds` | 8 s | BOSS-27; `BOSS_TIMING.rageSeconds` |
| `boss_rage_rate` | 4.5 × the weapons' own fire rate | BOSS-27; `BOSS_TIMING.rageRate`, `boss_build.angry_pattern` |
| `boss_rage_missiles` | 3 × the missiles of a volley | BOSS-27; `BOSS_TIMING.rageMissiles` |
| `boss_rage_first`, `boss_rage_stagger` | 0.15 s, 0.2 s per weapon | BOSS-27; `BOSS_TIMING.rageFirst`, `rageStagger` |
| `boss_rage_laser_gap` | 0.6 s between a beam's end and the next warning | BOSS-27; `BOSS_TIMING.rageLaserGap` |
| `boss_rage_flicker` | 14 Hz, down to 0.35 | BOSS-27; `BOSS_LOOK.rageFlicker` |
| `boss_turret_turn` | 150°/s | BOSS-29; `BOSS_TIMING.turretTurnDeg` |
| boss laser | 1 s warning, 12 px wide, Lancer's style recoloured | BOSS-30; `boss_kit.laser_of` |
| `boss_laser_turn` | 20°/s (warning line, sweeping beam) | BOSS-31; `BOSS_TIMING.laserTurnDeg` |
| boss missile | 140 px/s, turns 80°/s, homes 3 s, radius 5, health 10 | BOSS-23; `boss_kit.MISSILE` |
| `boss_transform_seconds` | 2.0 s | BOSS-37; `BOSS_TIMING.transformSeconds` |
| `boss_region_blasts` | 5 blasts a region at most | BOSS-37; `BOSS_TIMING.regionBlasts` |
| `hidden_weapon_health` | 0.8 (first transformation) / 1.0 (second) of the sturdiest original part | BOSS-38; written by hand in each boss's config, no code applies or checks the rule (128 of 129 hidden parts follow it on 2026-11-02; the Scorpion's tail cannon has 1100, the rule gives 580) |
| `hidden_weapon_drop` | 0.3 | BOSS-38, BOSS-57; `hidden_weapons.hidden_weapon` |
| fire-rate weights | bullet 1, missile 2, laser 8, launched enemy 2 | BOSS-39; `tests/unit/game/sim/test_boss_kinds.py` |
| gatling | bursts of 4, 0.12 s apart, 190 px/s, every 2.2 s | BOSS-40; `src/game/config/bosses/weapon_kinds.py` |
| lance | laser 1.4 s every 7.5 s; 1.9 radii long | BOSS-40; `weapon_kinds.WEAPON_SHAPE.lance` |
| rack | 2 homing missiles, 30° apart, every 6 s | BOSS-40 |
| orb | rings of 10 turning 13°, 175 px/s, every 2.6 s | BOSS-40 |
| beam | 44 px wide, 2.4 s, every 7 s | BOSS-40; `weapon_kinds.BEAM` |
| cannon | aimed spreads of 3, 12° apart, shells 150 px/s radius 7, every 2.4 s | BOSS-40; `WEAPON_FIRE.cannon` |
| mortar | 1 flak shell 110 px/s radius 8, bursting into 8 at 170 px/s after 1.1 s, every 3.2 s | BOSS-40; `WEAPON_FIRE.mortar` |
| battery | fans of 7, 9° apart, straight down, 180 px/s, every 2 s | BOSS-40; `WEAPON_FIRE.battery` |
| sweeper | sweeping laser 2 s every 8 s | BOSS-40; `WEAPON_FIRE.sweeper` |
| hangar | 2 Hornets every 7 s | BOSS-40; `WEAPON_FIRE.hangar` |
| `reveal` timeline | strain to 0.15, pieces gone by 0.6; weapons swing 0.4–0.75, slide 0.7–1.0 (overshoot 1.7); moving pieces 0.15–0.6; shudder 0.8 px, strobe 9 Hz | BOSS-43, BOSS-45; `BOSS_LOOK.reveal` |
| `armour` | 12 pieces a region, 24 a boss, plates 2.5 px thick, hold 1.2 px | BOSS-43, BOSS-52; `BOSS_LOOK.armour` |
| `frame` | floor 0.6 px over the armour's lowest point; ribs 1.6 px wide, 9 px apart, a neon seam every 3 | BOSS-44; `BOSS_LOOK.frame` |
| boss neon colours | one per boss | BOSS-50; `BOSS_LOOK.neon` |
| enemy hues | 60° (yellow), 125° (green) | BOSS-50; `src/game/config/readability.py` `READABILITY.enemyHues` |
| `tri_budget_mini_boss` / `tri_budget_final_boss` | 4 000 / 10 000 | BOSS-53; `src/game/config/enemy_look.py` `ENEMY_LOOK.budget` |
| part points | 10 % of the boss's points, rounded to 10 | BOSS-19; `src/game/config/scoring.py` `boss_part_points` |
| `part_drop_chance` / `final_part_drop_chance` | 0.5 / 0.6 | BOSS-57; `boss_kit.part`, `final_bosses.fpart` |
| `final_boss_core_drop` | 1 | BOSS-57; each final design's `coreDrop` |
| World 1 mini fight time | 25–35 s (1-1) → 40–50 s (1-5) | BOSS-56 |
| World 1 final fight time | 50–70 s (1-1) → 90–120 s (1-5) | BOSS-56 |

## Notes

- **No stump, no wound.** A destroyed part first left a burnt, sparking stump (P07-R01), then a
  wound of torn flesh, a dimmed organ, bone shards and torn plating (D-167, P16-R05); the reviewer
  had it removed (D-225).
- **Sparks on a shielded core.** P07-R01 had shots spark on a shielded core; D-053 then kept
  shielding parts out of the core's shadow. Since D-062 shots go through a shielded core, so the
  parts behind it can be hit.
- **Gaps (no test since the Python port).** No unit test checks the triangle budgets (BOSS-53, see
  D-220), the World 1 health order (BOSS-55) or the simulated fight times (BOSS-56: the simulated
  player of the TypeScript version, `tests/helpers/boss-bot.ts`, was not ported). The fight times
  were last measured before the hidden weapons (D-221) added 1 000 to 7 000 health a boss, so they
  are likely above their ranges now.
- **Drawn triangles, World 1 (scratch count, 2026-11-01):** 2 170 (Reef Warden) to 4 650
  (Overlord) for the bodies and parts as drawn, before hidden weapons, frames, stems and edge trim.
- The debug key that breaks a boss's next part (it skips hidden and retired parts and finishes a
  transformation) is in [debug options](../dev/debug-options.md).
