# Mantis Lancer

> **Area:** bosses · **Prefix:** `MB-MANTIS-LANCER` · **Related:** [common](../common.md),
> [Siege Crawler](L-4-siege-crawler.md)

The Mantis Lancer is the Lab's L-4 mini boss. **Lab boss: in the dev viewer only** (no level brings
it in; it is listed after the 40 World bosses in the dev viewer's Bosses list). A tall, narrow
praying mantis, 3.5 L long: its two raised scythes each carry a laser turret and its triangular head
a twin gun, all three shielding its core. Its scythe lasers aim at the player through their warning
lines a little out of step, so their locked beams cross and fence the player in while the head
adds aimed bursts: a laser grid to dodge between. Once both scythes are gone it sheds its thorax
plating and unfolds a pair of orbs. Shared rules are in [common](../common.md).

## Requirements

### Look

#### MB-MANTIS-LANCER-01 — Silhouette and size · MUST

Seen from above, the Mantis Lancer is a tall, narrow praying mantis, long down the screen and slim
across: a long abdomen under two folded leaf wings at the back, a plated thorax, a long neck, a
triangular head at its front (down the screen), two raptorial scythes raised forward either side of
the head, and two pairs of long, thin walking legs splayed out of the thorax.

**Acceptance criteria**
- Manual validation in the boss viewer: a mantis, its head at the front between its two raised
  scythes, its silhouette unlike any other boss's.

*Sources: user request (2026-11-05, the Lab bosses).*

#### MB-MANTIS-LANCER-02 — Body · MUST

Its body is dark, moss-tinged flesh (BOSS-50 keeps moss green): a segmented abdomen under two leaf
wings of membrane overlapping on its centre line, a green vein along each wing's midrib and its
side veins; a segmented thorax under its plating (MB-MANTIS-LANCER-05); a long neck of sinew ringed
with grafted metal collars, the plate the neck turret stands on, a green vein down it; a sinew from
each side of the neck's root out under each scythe, socketed in a dark collar; its four walking
legs jointed sinew and bone, a light on each knee; reactor sacs at its tail; a grafted plate across
the wings carrying the rotor's hatch; two running lights on the wings, off the centre line.

**Acceptance criteria**
- Manual validation: a living mantis with metal grafted on.

*Sources: user request (2026-11-05).*

#### MB-MANTIS-LANCER-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts, the shared models of [common](../common.md) (BOSS-58):
- **Scythes** (left and right, raised either side of the head): each a thick sinew femur rising to an
  armoured knee collar ringed in green, the scythe's laser turret on it (a laser emitter on a turret,
  BOSS-31), and its tibia folded forward into a crescent bone blade, its hook bent back in at the
  front, teeth along its inner edge, a green vein along its outer edge.
- **Head** (at its front): a flat triangle of flesh, a great compound eye glowing green on each back
  corner, small simple eyes, feelers sweeping back, mandibles under the mouth, and a twin gun (two
  barrels side by side on a turret) in its mouth.
- **Neck turret** (the core's): a fan turret of three barrels on the neck's plate (its aimed shots,
  aimed fans and bursts).
- **Abdomen rotor** (the core's): a rotor of twelve barrels on the plate across its wings (its last
  ring). Until its last stage it lies under an armoured hatch, an octagonal cap with a seam of green
  light round it, which bursts off as the rotor comes into use (BOSS-58), leaving a collar round the
  opening the rotor rises out of.

**Acceptance criteria**
- Given its model, then it draws both scythes, the head and every gun mount (unit test).

*Sources: user request (2026-11-05).*

#### MB-MANTIS-LANCER-04 — Lights · MUST

Green veins run down its neck, its thorax plating, its scythes and its wings; its eyes, knees,
glands and running lights glow. Its neon colour, set green, shows bright green
([common](../common.md), BOSS-50); its lasers are its neon folded into the enemy shots' family
(BOSS-32).

**Acceptance criteria**
- Given its model, then its lights are bright green.

*Sources: user request (2026-11-05).*

#### MB-MANTIS-LANCER-05 — Thorax plating · MUST

The plating of its thorax, from the wings' root to the neck's root, is the armour it sheds at its
transformation ([common](../common.md), BOSS-42): a ridged carapace drawn as a piece of its own over
the thorax (from 5.2 px to 11 px), bone ribs across it, a green vein down its spine and a gland
either side. Its region (`thorax`, mirrored) is the plating's own outline; it bursts into plates
cracked from that outline and leaves a `shell` lattice frame over the thorax. The pair of orbs lies
folded under it.

**Acceptance criteria**
- Given its design, then its one transformation sheds the thorax region and both orbs lie in it
  (unit test).
- Given its model, then it draws the thorax region's armour, and it holds together with and without
  it (unit tests).

*Sources: D-221, D-224, D-254.*

### Behaviour

#### MB-MANTIS-LANCER-06 — Coming in and moving · MUST

It comes in from the top ([common](../common.md), BOSS-08) to `stopFraction` of the playfield's
height, then sways and bobs. While it is fought the ground scrolls at ×0.6.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.6 of the level's speed and back after it.

*Sources: BOSS-03.*

#### MB-MANTIS-LANCER-07 — Parts and core · MUST

It has three parts as it comes in, all shielding its core: `scythe-left`, `scythe-right` and
`head`. The core's guns (the neck turret and the abdomen rotor) fire the core's volleys and are the
last the player destroys. The turrets turn the way they fire; the scythes' laser turrets aim at the
player only at `boss_laser_turn` through their warning lines, then hold still (BOSS-31).

**Acceptance criteria**
- Given its design, then its three parts all shield the core (unit test on its design).

*Sources: BOSS-12, BOSS-14, BOSS-58.*

#### MB-MANTIS-LANCER-08 — Stage patterns · MUST

The parts fire in every stage while they stand:
- each scythe fires its laser (1 s warning line, then a 1.6 s beam), the right one 0.6 s after the
  left, so the two beams lock from either side of the head on where the player was and cross;
- the head fires bursts of 3 green bullets at the player, its two barrels taking turns.

The core fires:
- stage 0: a single orange bullet at the player from the neck turret;
- stage 1: an aimed fan of 3, 12° apart, swept from the neck turret one bullet at a time;
- stage 2: a burst of 4 at the player, its barrels taking turns;
- stage 3 (all three parts gone): a ring of 12 green bullets from the abdomen rotor, one a barrel,
  turning 9° at each volley (a spiral), and a single aimed bullet from the neck turret.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys, each from its mount (unit test).

*Sources: BOSS-20, BOSS-21, BOSS-58.*

#### MB-MANTIS-LANCER-09 — Angry · MUST

It is angry after its transformation, when the two orbs it revealed fire all out for
`boss_rage_seconds`, `boss_rage_rate` times as often, instead of its stage's pattern
([common](../common.md), BOSS-27). A lost part does not anger it.

**Acceptance criteria**
- Given its transformation is over, then it is angry and fires only its two orbs (unit test).

*Sources: BOSS-27.*

#### MB-MANTIS-LANCER-10 — Transformation · MUST

It transforms once, when both scythes are destroyed (`transformParts`): its thorax plating bursts
off, baring a dark metal lattice, and two **orbs** unfold on it, either side of its centre line.
They shield the core and fire rings of 10 green bullets, turning, in turn.

**Acceptance criteria**
- Given both scythes destroyed, then it transforms and its two orbs are revealed (unit test).

*Sources: D-221, D-224, D-228, D-229.*

#### MB-MANTIS-LANCER-11 — Death, drops and points · MUST

Its parts drop a weapon bonus half of the time, its orbs 30 %; it drops a life bonus as a mini boss
([common](../common.md), BOSS-57). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/mantis_lancer.py` (`_MANTIS_LANCER`, `MANTIS_LANCER`) unless
named.

| Name | Value | Notes |
|------|-------|-------|
| size | 3.5 L (radius 59.5 px) | `stats.size` |
| core | health 1 450, radius 17 | `coreHealth`, `coreRadius` |
| `scythe-left`, `scythe-right` | (∓25, -46), radius 12, health 740, shield, drop 0.5 | |
| scythe lasers | (∓25, -48), 11 px high; turret, base radius 4, bore 1.7, 10 px long | `SCYTHE_LASER`, `mounts` |
| `head` | (0, -52), radius 10, health 700, shields, drop 0.5 | |
| head gun | (0, -56), 7 px high; 2 barrels 2.9 px apart, bore 1.1, 7 px long; dome radius 4.2 | `HEAD_GUN` |
| neck turret (core) | (0, -33), 9 px high; 3 barrels, bore 0.9, 6 px long; dome radius 4.4 | `mounts` `neck` |
| abdomen rotor (core) | (0, 30), 9.6 px high; 12 barrels, bore 0.8, 3.2 px long; hub radius 4.5 | `mounts` `abdomen-rotor` |
| rotor hatch | octagon of radius 6 round (0, 30), on the wings' plate; bursts as the rotor comes into use | `armour_region` `rotor-hatch` (`mount`) |
| full health | 4 810 (core 1 450, parts 2 180, orbs 1 180) | BOSS-54; the 1-4 mini boss (Scorpion) has 4 760 |
| points | 4 500; 450 a part | |
| ground speed | ×0.6 | |
| stop height | 0.72 | `stopFraction` |
| sway / bob | 55 px over 7 s / 9 px over 3.3 s | |
| scythe laser | 1.6 s beam every 5.5 s (first 2 s / 2.6 s) | `volley.laser` |
| head burst | 3 green bullets 185 px/s, 0.16 s apart, every 2.4 s (first 1.3 s) | |
| core stage 0 | 1 aimed orange bullet 175 px/s, every 3 s | neck turret |
| core stage 1 | aimed fan of 3, 12° apart, every 2.6 s | neck turret, a sweep |
| core stage 2 | burst of 4, 0.14 s apart, every 2.4 s | neck turret |
| core stage 3 | ring of 12 green turning 9°, every 1.5 s; 1 aimed orange every 2.6 s | abdomen rotor; neck turret |
| angry | the revealed orbs, BOSS-27 | `boss_build.angry_pattern` |
| transformation | both scythes destroyed | `transformParts` |
| shed region | thorax: x ±15.5 at its widest, y -27..9, `shell`, mirrored | `armour_region` `thorax` |
| orbs | (∓8, -9), radius 8, health 590, pod 7 px; rings of 10 green 175 px/s turning 13°, every 2.6 s; first 1.2 s / 2.0 s | `hidden_weapon` |
| neon | green (0.3, 1, 0.3) | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** It is registered in `BOSS_DESIGNS`, `BOSS_MODELS` and `BOSS_LOOK.neon` after the
  World bosses, and no level's boss table names it.
- **Simulated fight (2026-11-05, a part broken every 12 s):** 757 shots and 6 lasers, every one
  from a barrel's tip along it (0 off); dead at 74 s.
- **Triangles (scratch count, 2026-11-05):** about 2 860 drawn for its body, parts and armour, and
  740 for its gun mounts and orbs: about 3 600 of the 4 000 budget (BOSS-53).
