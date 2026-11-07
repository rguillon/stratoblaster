# Carapace Drum

> **Area:** bosses · **Prefix:** `MB-CARAPACE-DRUM` · **Related:** [common](../common.md),
> [Tri-Wing Hydra](L-1-tri-wing-hydra.md)

The Carapace Drum is the mini boss of the Lab's level L-1: a squat barnacle drum seen from above,
3 L across, a domed shelled lid round its operculum on a thick turning rim. Its rim carries three
barnacle rotor pods 120° apart which fire rings of bullets, spiralling as the rim turns: a
bullet-curtain boss. All three pods shield its core. Once two of them are gone it sheds its lid's
armour and unfolds a pair of cannons. Shared rules are in [common](../common.md).

**Lab boss: in the dev viewer only.** It is listed after the 40 World bosses in the dev viewer's
Bosses list; no level brings it in.

## Requirements

### Look

#### MB-CARAPACE-DRUM-01 — Silhouette and size · MUST

Seen from above, the Carapace Drum is round and squat, 3 L across, with no nose to speak of: a
solid drum under a domed lid, sunk into a thick ring rim (no spokes, no gap between rim and drum)
that carries three barnacle cones 120° apart. Only the mouth turret on its front shoulder and the
eyes under it tell its front.

**Acceptance criteria**
- Manual validation in the boss viewer: a round shelled drum on a thick ring carrying three
  barnacles, clearly not the Dust Devil's open jelly with its spoked ring.

*Sources: Lab request (2026-11-05: "create 5 new mini bosses and 5 new final bosses").*

#### MB-CARAPACE-DRUM-02 — Body · MUST

Its drum is dark sinew, its sloping shoulder clad in leaning bone shell plates with dark flesh
between them (BOSS-49); the operculum (a slate hub ringed with light) stands from the middle of its
top, where its lid leaves a hole. A plate grafted on its front shoulder seats the mouth turret, a
cluster of three eyes under it, reactor sacs at its tail and glands on its flanks. The turning rim
is a thick graphite ring of barnacle plates: riveted plates on its top between the pods, bone spurs
out of its edge, an aqua vein along its lip.

**Acceptance criteria**
- Manual validation: one living barnacle creature under grafted armour, its rim turning.

*Sources: Lab request.*

#### MB-CARAPACE-DRUM-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts, the shared models of [common](../common.md) (BOSS-58):
- **Rotor pods** (`pod-1` at the front, `pod-2` and `pod-3`, on the rim, BOSS-34): each a barnacle
  cone of leaning bone wall plates round a crater, a vein ring at its foot, a spawn sac on its outer
  side; in the crater a rotor with six barrels (its rings).
- **Mouth turret** (the core's): a gun turret with three barrels side by side on the plate on its
  front shoulder (its fans, aimed spreads, bursts and aimed shots).
- **Crown rotor** (the core's): a rotor with twelve barrels on the operculum (its last stage's
  ring). Until then it lies under a hatch, an octagonal armoured cap with a seam of aqua light; the
  hatch bursts off as the rotor comes into use (BOSS-58), leaving a collar, and the rotor rises out.

**Acceptance criteria**
- Given its model, then it draws the three pods and every gun mount (unit test).

*Sources: Lab request.*

#### MB-CARAPACE-DRUM-04 — Lights · MUST

Aqua veins run over its shoulder, its lid and its rim's lip; its eyes, glands and the operculum's
ring glow. Its neon colour, set aqua, shows bright green ([common](../common.md), BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright green.

*Sources: Lab request.*

#### MB-CARAPACE-DRUM-05 — The lid · MUST

Its domed lid is the armour it sheds at its transformation (BOSS-42): a shell of revolution from
its rim (radius 23, sunk into the drum's top at 9 px) up to the operculum (radius 7, about 16 px),
bone ribs radiating down it, riveted plates between them and an aqua vein down each side. Its
region, `lid`, is a half-ring from 7 to 23 px out and its mirror image; it bursts into plates
cracked from that outline and leaves a `ring` frame (spokes and a hoop) on the drum's top. The pair
of cannons lies folded under it.

**Acceptance criteria**
- Given its design, then its one transformation sheds the lid and both cannons lie in it (unit test).
- Given its model, then it draws the lid, and it holds together with and without it (unit tests).

*Sources: Lab request, D-254.*

### Behaviour

#### MB-CARAPACE-DRUM-06 — Coming in and moving · MUST

It comes in from the top ([common](../common.md), BOSS-08) to `stopFraction` of the playfield's
height, then sways and bobs, its rim turning all the while at `spinRate`. While it is fought the
ground scrolls at ×0.5.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.5 of the level's speed and back after it.

*Sources: Lab request.*

#### MB-CARAPACE-DRUM-07 — Parts and core · MUST

It has three parts as it comes in, all shielding its core: `pod-1`, `pod-2` and `pod-3`, orbiting
on its rim. Each pod's rotor fires a ring of six green bullets, the three in turn, each ring turned
a little more than the last (a spiral), the whole turning with the rim. The core's guns (the mouth
turret and the crown rotor) fire the core's volleys and are the last the player destroys.

**Acceptance criteria**
- Given its design, then its three parts all shield the core and orbit (unit test on its design).

*Sources: Lab request.*

#### MB-CARAPACE-DRUM-08 — Stage patterns · MUST

The pods fire their rings in every stage while they stand. The core fires:
- stage 0: a fan of 3 blue bullets straight down, swept from the mouth turret;
- stage 1: an aimed spread of 3, swept the same way;
- stage 2: a burst of 4 at the player and a fan of 5 straight down;
- stage 3 (all three pods gone): a ring of 12 from the crown rotor turning 11° a volley (a
  spiral, its first ring), and a single aimed shot from the mouth turret.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys (BOSS-21 unit tests).

*Sources: Lab request.*

#### MB-CARAPACE-DRUM-09 — Angry · MUST

It is angry after its transformation: the two cannons it revealed fire all out for
`boss_rage_seconds`, `boss_rage_rate` times as often, instead of its stage's pattern
([common](../common.md), BOSS-27).

**Acceptance criteria**
- Given its transformation is over, then it is angry and fires only its two cannons (unit test).

*Sources: Lab request, D-256.*

#### MB-CARAPACE-DRUM-10 — Transformation · MUST

It transforms once, when two of its pods are destroyed: its lid's armour bursts off, baring a dark
metal ring frame round the operculum, and two **cannons** unfold on the drum's top, either side of
the operculum. They shield the core and sweep aimed spreads of 3 big blue shells, in turn.

**Acceptance criteria**
- Given two pods destroyed, then it transforms and its two cannons are revealed (unit test on its
  thresholds).

*Sources: Lab request, D-221, D-229.*

#### MB-CARAPACE-DRUM-11 — Death, drops and points · MUST

Its pods drop a weapon bonus half of the time, its cannons 30 %; it drops a life bonus as a mini
boss ([common](../common.md), BOSS-57). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: Lab request.*

## Tunable values

All in `src/game/config/bosses/lab/carapace_drum.py` (`_CARAPACE_DRUM`, `CARAPACE_DRUM`); its model
in `src/game/view/bosses/lab/carapace_drum_model.py`.

| Name | Value | Notes |
|------|-------|-------|
| size | 3 L (radius 51 px) | `stats.size` |
| core | health 900, radius 20 | `coreHealth`, `coreRadius` |
| `pod-1`, `pod-2`, `pod-3` | 40 px out at 0°, 120°, 240° from the nose (`pod-1` at (0, -40)), radius 13, health 500, shield, orbit, drop 0.5 | `POD_SPOTS` |
| pod rotors | 6 barrels, bore 0.9, 4 px long, hub radius 4, 10.5 px high in the crater | `POD_ROTOR`, `mounts` |
| mouth turret (core) | (0, -26), 9.4 px high; 3 barrels 2.9 px apart, bore 1.1, 5 px long; dome radius 5 | `mounts` `mouth` |
| crown rotor (core) | (0, 0), 17.4 px high; 12 barrels, bore 0.8, 3.5 px long; hub radius 5 | `mounts` `crown-rotor` |
| crown hatch | octagon of radius 6.5 round (0, 0), the cap from 16.8 px to 19.8 px; bursts as the rotor comes into use | `armour_region` `crown-hatch` (`mount`) |
| full health | 3 200 | BOSS-54 |
| points | 3 000; 300 a part | |
| ground speed | ×0.5 | |
| stop height | 0.72 | `stopFraction` |
| sway / bob | 55 px over 9 s / 6 px over 4 s | |
| rim spin | 0.45 rad/s | `spinRate` |
| pod rings | 6 green bullets 165 px/s, turning 14°, every 2.4 s (first 0.6 s / 1.4 s / 2.2 s) | one bullet a barrel |
| core stage 0 | fan of 3, 12° apart, blue 180 px/s, every 3 s | mouth turret, a sweep |
| core stage 1 | aimed 3, 12° apart, every 2.6 s | a sweep |
| core stage 2 | burst of 4, 0.15 s apart, every 2.2 s; fan of 5, 12° apart, every 2.6 s | |
| core stage 3 | ring of 12 green, turning 11°, every 1.6 s; aimed 1 blue every 2.8 s | crown rotor; mouth turret |
| angry | the revealed cannons, BOSS-27 | `boss_build.angry_pattern` |
| transformation | 2 pods destroyed | default threshold |
| lid (shed) | a half-ring from 7 to 23 px out and its mirror image, `ring`; the lid 8.4–16.4 px | `armour_region` `lid` |
| cannons | (∓14.5, 3), radius 8, health 400, pod on the drum's top from 9 px to 12 px, blue; first 1.2 s / 2.0 s; spreads of 3 shells, 12° apart, every 2.4 s | `hidden_weapon` |
| fire rate (BOSS-39) | 8.5 weighted shots a second as it comes in, 8.7 after its transformation | |
| neon | aqua (0.2, 1, 0.8), shown green | `BOSS_LOOK.neon` |

## Notes

- Its parts orbit, as the Dust Devil's blade pods do; it tells itself apart from that boss by its
  closed, solid round body and thick plated rim (the Dust Devil is an open bell on a thin spoked
  ring) and by its lid, which reveals cannons instead of orbs.
