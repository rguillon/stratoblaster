# Enemy and boss weapons

> **Area:** Enemies and bosses · **Prefix:** `WPN` · **Related:** [common rules](common.md),
> [boss rules](../bosses/common.md), [shots](../graphics/shots.md),
> [Reef Warden](../bosses/mini/1-1-reef-warden.md), [Overlord](../bosses/final/1-5-overlord.md)

Every weapon of every enemy and boss is one of three things the player learns to read at a glance:
a **gun** (a barrel that recoils and fires bullets), a **laser** (the Overlord's beam) and a
**missile launcher** (a hexagonal hole in a barrel). The Reef Warden's cannons are the model of a
gun. Nothing is fired from a hull, a joint or a point of the body that is not one of these three.

This file is the shared rule; each enemy's and boss's own file says where its guns, lasers and
launchers stand. It is delivered in slices (D-268): the shared mechanics first, then the enemies,
then the mini bosses, then the final bosses; the requirements below hold for a kind once its slice
is done, and `Slice` says which one.

## Requirements

### Guns

#### WPN-01 — A bullet comes out of a barrel · MUST

Every bullet an enemy or a boss fires leaves a **barrel**: a drawn tube with a pose, its tip's
position (seen through the tilted camera, ENM-21) and the direction it points. The bullet starts
exactly at the tip and flies exactly along the barrel's direction at the instant it is fired: no
bullet is aimed from the body's centre, none is given a heading its barrel does not have.

**Acceptance criteria**
- Given any gun, then each bullet's start equals its barrel's tip and its heading equals its barrel's
  heading, to 0.01 px and 0.0001 rad (unit test, every kind).
- Given a boss's piece, then every gun it has is a barrel of the piece's model (unit test).

*Sources: owner request 2026-11-04, ENM-21, BOSS-29.*

#### WPN-02 — A barrel points before it fires · MUST

A gun that aims (at the player, along a fan's heading, with a ring's turn) is a barrel on a pivot
(a turret) or a barrel fixed on the body with its own angle. It fires only once the barrel points
within `barrel_aim_tolerance` of the way the volley goes; a fixed barrel is chosen for the way it
already points. Fans, rings and spirals are fired by **several barrels**, one per shot of the volley
(a hub of radial barrels, or a bank of barrels on a turret that turns between volleys), each shot
leaving its own barrel (WPN-01).

**Acceptance criteria**
- Given a due aimed volley and a barrel pointing elsewhere, then nothing is fired until the barrel
  points within the tolerance (unit test).
- Given a ring of N bullets, then N barrels fire one each (unit test).

*Sources: owner request 2026-11-04, BOSS-29.*

#### WPN-03 — A barrel recoils · MUST

When a barrel fires, it is thrown back along its own axis by `barrel_recoil` (a share of its length)
and slides forward again over `barrel_recoil_seconds`, eased out. It is the barrel that moves, not
the bullet's start: the bullet leaves the tip where it was at the instant of firing (WPN-01). A
burst's barrels recoil each time they fire; a twin or a bank recoils the barrel that fired. The
recoil is held in the simulation (`Barrel.recoil`, 1 at firing down to 0), so the same state moves
the drawn barrel and can be tested.

**Acceptance criteria**
- Given a barrel that fires, then its recoil is 1 at that age and 0 after `barrel_recoil_seconds`,
  never negative (unit test).
- Given a barrel firing again before it is back, then the recoil restarts at 1 (unit test).
- Given a model, then each of its barrels is its own mesh that slides back by recoil × the recoil
  distance (unit test on the model's barrel nodes).
- Manual validation: every gun visibly kicks when it fires.

*Sources: owner request 2026-11-04.*

#### WPN-04 — Enemies have guns, not bare hulls · MUST

An enemy that fires bullets carries drawn barrels (a Strafer: three on each side). Its config's
muzzles are its barrels' tips and directions (ENM-21 becomes WPN-01 for them).

**Acceptance criteria**
- Given each enemy kind that fires bullets, then its model draws a barrel at each muzzle (unit
  test).

*Sources: owner request 2026-11-04. Slice: enemies (bullets: done, D-270; missiles and lasers: with WPN-06 to WPN-09).*

#### WPN-05 — Every boss shot comes from a gun · MUST

Every bullet, ring, fan, burst or flak shell a boss fires leaves a barrel of one of its pieces. A
piece that fired from its hull, a blade, a claw or a pod (BOSS-29: "guns built into hulls...") gets
barrels there.

**Acceptance criteria**
- Given every boss, then each of its bullet volleys names the barrels it leaves from, and the model
  draws them (unit test over every boss).

*Sources: owner request 2026-11-04. Slice: mini bosses, final bosses.*

### Lasers

#### WPN-06 — Every laser looks like the Overlord's · MUST

Every laser of an enemy or a boss (the Lancer's, the Prism's, the bosses') has the Overlord's look:
the same warning line, the same beam of a white-hot core inside a wide halo, the same flare at its
emitter, the same widths per `style`. Only its colour stays its owner's (BOSS-32; the Lancer's red).
A laser leaves a **lens at the end of a barrel**, which does not recoil.

**Acceptance criteria**
- Given the lasers of two different owners, then their warning, beam and flare meshes use the same
  shapes and falloffs and differ in colour only (unit test).
- Manual validation: the Lancer's, the Prism's and a mini boss's laser read as the Overlord's.

*Sources: owner request 2026-11-04, BOSS-32. Slice: lasers (done, D-271).*

### Missile launchers

#### WPN-07 — A hexagonal hole in a barrel · MUST

Every missile is launched from a **hexagonal port**: a hexagon-bored hole in the end of a barrel (a
short thick one for a rack, a long one for a mortar). The bore is **wider than the rocket** (its
inner radius clears the drawn missile) and the tube is wider than the bore, all along the launcher.
The port is **hollow**: a dark well with a glowing rim (or none, when its launcher is lit along its
sides instead, as the Rocketeer's), open at the top. Its rocket waits in the well
while it is loaded; from the moment it is launched the port is empty, and the next rocket rises
back into the well over `missile_reload_seconds` (seen from `missile_reload_show` of that time on).

**Acceptance criteria**
- Given each missile launcher, then its model has a hexagonal port at its muzzle (unit test).
- Given the missiles of every launcher, then the bore's inner radius exceeds the drawn missile's
  radius and the tube's exceeds the bore's (unit test).
- Given a port, then nothing covers its mouth, and its rocket is a piece of its own (unit test).
- Given each missile enemy's model, then no face crosses its bore between the well's floor and
  its mouth: the tube behind a port stops where the well starts (unit test).
- Given a launcher that has just launched, then its port's rocket is hidden, then rises back and is
  in place after `missile_reload_seconds`; a launcher the simulation does not report (a boss's, until
  WPN-05) is always loaded (unit test).
- Given a missile fired, then it starts at the port's centre with the port's direction (unit test).

*Sources: owner request 2026-11-04. Slice: missiles (done, D-271).*

#### WPN-08 — The missile leaves the port before it turns · MUST

A missile flies straight out of its port, along the port's direction, for `missile_launch_seconds`
before it begins to turn toward the player (homing, `homing_seconds` counted from then on). It never
turns inside or beside the launcher.

**Acceptance criteria**
- Given a missile fired, then its heading is the port's for `missile_launch_seconds`, whatever the
  player's position (unit test).
- Given a missile in that time, then its homing time has not started to run (unit test).

*Sources: owner request 2026-11-04.*

#### WPN-09 — Upward silos curve over to the player's plane · MUST

A silo that points up (out of the plane of play, towards the camera) fires its missile up first; the
missile then **arcs over**: it climbs for `missile_climb_seconds`, curves in a half loop of radius
`missile_arc_radius` to the playfield's plane (its height falls to 0) pointed along the way it will
fly, and only then tracks the player (WPN-08's homing). The arc is drawn: the missile grows and
shrinks with its height as the camera sees it.

**Acceptance criteria**
- Given a missile from an upward silo, then its height rises, falls to 0 after `missile_climb_seconds`
  + the arc, and it homes only from then on (unit test).
- Given the missile in its climb, then the player's shots and body do not hit it, and it does not hit
  the player (it is not on the plane yet; unit test).
- Manual validation: the arc reads as a missile turning over before it hunts.

*Sources: owner request 2026-11-04.*

## Tunable values

| Name | Value | Notes |
|------|-------|-------|
| `barrel_aim_tolerance` | 6° | as BOSS-29's `boss_turret_aim_tolerance` |
| `barrel_recoil` | 0.35 of the barrel's length | WPN-03 |
| `barrel_recoil_seconds` | 0.5 s | WPN-03; the slide back is instant, the return eased out |
| `missile_launch_seconds` | 0.25 s | WPN-08 |
| `missile_climb_seconds` | 0.3 s | WPN-09 |
| `missile_arc_radius` | 40 px | WPN-09 |
| `missile_reload_seconds` | 1.2 s | WPN-07; the port is empty, then the rocket rises back |
| `missile_reload_show` | 0.35 of it | WPN-07; the rocket is hidden before |

## Notes

- Requested by the owner on 2026-11-04 so that a weapon is recognised at once: guns recoil, lasers are
  the Overlord's, missiles come out of hexagonal ports. Decisions in D-268 to D-270.
- Fans and rings come from rotating multi-barrel turrets (owner's choice), not from a barrel that
  fires in several directions.
- The laser colour stays each owner's (owner's choice): the look is shared, the tint is not.
