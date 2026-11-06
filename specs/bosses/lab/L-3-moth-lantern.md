# Moth Lantern

> **Area:** bosses · **Prefix:** `MB-MOTH-LANTERN` · **Related:** [common](../common.md),
> [Leviathan Spine](L-3-leviathan-spine.md)

**Lab boss: in the dev viewer only.** It is listed after the 40 game bosses in the dev viewer's
Bosses list, and no level brings it in.

The Moth Lantern is the mini boss of Lab level L-3: a huge moth, 4 L across, its broad, soft wings
folded back at rest. An eye-spot gun on each forewing fans bullets that cross under it, and its long
glowing lantern abdomen lobs big, slow spore shells that burst into rings and drift over the screen.
Once both eye-spots are gone its wings swing open wide (it changes shape, BOSS-45) and a lance rides
in on each forewing. Shared rules are in [common](../common.md).

## Requirements

### Look

#### MB-MOTH-LANTERN-01 — Silhouette and size · MUST

Seen from above, the Moth Lantern is a moth, its head down the screen: a furry head with two great
compound eyes and two feathered antennae curving out ahead of it, a broad furry thorax, broad
forewings swept back over its hindwings at rest (about 4 L from tip to tip), and behind them a long,
segmented, glowing abdomen: the lantern. With its wings open it is about 5 L across, its four wings
spread like a moth pinned flat.

**Acceptance criteria**
- Manual validation in the boss viewer: a moth, wings folded back at rest and spread wide once it
  has transformed, its lantern trailing behind.

*Sources: Lab boss request (2026-11-05).*

#### MB-MOTH-LANTERN-02 — Body and wings · MUST

Its head and thorax are domed hides (slate, graphite) with tufts of sinew fur on the thorax and a
fur collar behind the head; its forelegs, middle and hind legs are folded under it; plates are
grafted on its shoulders and a metal coupling rings the root of its abdomen. Each wing is a soft
membrane with a darker, furry base, glowing veins fanning out from its root, a fringe of scales
along its outer margin and a grafted hinge knuckle at its root; each forewing has a ring of light
round its eye-spot, each hindwing a great eye-spot (a ring of light round a dark iris and a glowing
pupil), hidden under the forewing at rest and bared as the wings open.

**Acceptance criteria**
- Manual validation: one moth creature with grafted metal, its wings soft and veined.

*Sources: BOSS-47, BOSS-49.*

#### MB-MOTH-LANTERN-03 — Its parts and guns · MUST

Every shot leaves one of its gun mounts (BOSS-58):
- **Eye-spots** (left and right, on the forewings): each a swollen eye standing on its wing's
  eye-spot ring, a glowing iris round a turret of three barrels side by side (its pupil), sweeping
  its fans.
- **Lantern** (its abdomen, behind it): a glowing body under dark, pinched carapace plates, the
  light showing between them and along its flanks, grafted metal bands and a great glowing bulb at
  its tip; on its back a mortar (a single fat barrel in a cradle on a turntable) lobs its spore
  shells.
- **Maw turret** (the core's, on its head): three barrels side by side (its aimed shots and bursts).
- **Thorax rotor** (the core's): twelve barrels round a hub on its thorax (its last ring). Until its
  last stage it lies under an armoured hatch, an octagonal cap with a seam of light round it; as the
  rotor comes into use the hatch bursts off (BOSS-58), leaving a collar, and the rotor rises out.

**Acceptance criteria**
- Given its model, then it draws both eye-spots, the lantern and every gun mount.

*Sources: BOSS-48, BOSS-58.*

#### MB-MOTH-LANTERN-04 — Lights · MUST

Its veins, the rings of its eye-spots, its compound eyes, the lit edge of its forewings and its
lantern glow. Its neon colour, set lilac, shows bright green (BOSS-50).

**Acceptance criteria**
- Given its model, then its lights are bright green.

*Sources: BOSS-50.*

#### MB-MOTH-LANTERN-05 — Its wings change shape · MUST

Its four wings are moving pieces (BOSS-45), drawn spread open: at rest each forewing is swung back
50° about the front of its root and each hindwing 20° about its own, the forewing over the
hindwing; at its transformation they swing forward into their open pose and stay there. They leave
no frame. The thorax hatch is a shed region of its own (BOSS-58).

**Acceptance criteria**
- Given its design, then its transformation moves the forewings and hindwings, each pair mirrored,
  and its lances ride the forewings (unit tests on the moving regions).
- Given its model, then it draws each wing, and it holds together at rest and once they have moved.

*Sources: BOSS-42, BOSS-45, BOSS-52.*

### Behaviour

#### MB-MOTH-LANTERN-06 — Coming in and moving · MUST

It comes in from the top (BOSS-08) to `stopFraction` of the playfield's height, then sways slowly
and bobs quickly, a drifting flutter. While it is fought the ground scrolls at ×0.5.

**Acceptance criteria**
- Given the fight, then the ground eases to ×0.5 of the level's speed and back after it.

*Sources: BOSS-03, BOSS-10.*

#### MB-MOTH-LANTERN-07 — Parts and core · MUST

It has three parts as it comes in, all shielding its core: `eye-left`, `eye-right` and `lantern`.
The core's guns (the maw turret and the thorax rotor) fire the core's volleys and are the last the
player destroys.

**Acceptance criteria**
- Given its design, then its three parts all shield the core.

*Sources: BOSS-12, BOSS-14.*

#### MB-MOTH-LANTERN-08 — Stage patterns · MUST

In every stage while they stand, each eye-spot sweeps a fan of 5 magenta bullets, 12° apart, its
heading turned 8° across the centre line (the left one's to the screen's right, the right one's to
its left), so the two fans cross under it, the two in turn; the lantern lobs a big, slow spore shell
at the player, which bursts into a ring of 10 after 1.5 s, the rings drifting over the screen. The
core fires:
- stage 0: an aimed purple bullet;
- stage 1: an aimed fan of 3, 10° apart, swept;
- stage 2: a burst of 4 at the player;
- stage 3 (all three parts gone): a ring of 12 from the thorax rotor, one bullet a barrel, turning a
  little at each volley (a spiral), and an aimed magenta bullet.

**Acceptance criteria**
- Given each stage, then the core fires that stage's volleys; each shot leaves a barrel (a fight in
  the simulation).

*Sources: BOSS-21, BOSS-23, BOSS-58.*

#### MB-MOTH-LANTERN-09 — Angry · MUST

After its transformation it is angry (BOSS-27): its two lances fire all out, as often as their
warning, beam and gap allow, for `boss_rage_seconds`. It has no angry pattern of its own.

**Acceptance criteria**
- Given its transformation is over, then it is angry and fires only its two lances.

*Sources: BOSS-27.*

#### MB-MOTH-LANTERN-10 — Transformation · MUST

It transforms once, when both eye-spots are destroyed (named, so that no part the player can hit
stands on a wing as it moves): its wings swing open wide and a **lance** rides in on each forewing,
on the pod it unfolds there, pointing down the screen. They shield the core and fire their lasers,
in turn.

**Acceptance criteria**
- Given both eye-spots destroyed, then it transforms, its wings swing open and its two lances are
  revealed on the forewings.

*Sources: BOSS-35, BOSS-36, BOSS-45.*

#### MB-MOTH-LANTERN-11 — Death, drops and points · MUST

Its parts drop a weapon bonus half of the time, its lances 30 %; it drops a life bonus as a mini
boss (BOSS-57). It scores the points of Tunable values.

**Acceptance criteria**
- Given its design, then its parts' drop chances and its points are those of Tunable values.

*Sources: BOSS-57.*

## Tunable values

All in `src/game/config/bosses/lab/moth_lantern.py` (`_MOTH_LANTERN`, `MOTH_LANTERN`) unless named;
its model in `src/game/view/bosses/lab/moth_lantern_model.py` and `moth_lantern_wings.py`.

| Name | Value | Notes |
|------|-------|-------|
| size | 4 L (radius 68 px) | `stats.size` |
| core | health 1 150, radius 16 | |
| `eye-left`, `eye-right` | (∓36.2, 9.9), radius 12, health 650, shield, drop 0.5 | on the folded forewings: the eye-spot (52, -20) of the open wing swung back 50° |
| eye-spot turrets | 12.4 px high; 3 barrels 2.9 px apart, bore 1.1, 7 px long; dome radius 4.6 | `EYE_GUN` |
| `lantern` | (0, 42), radius 15, health 720, shield, drop 0.5 | abdomen from y 20 to 66 |
| spore mortar | (0, 34), 13.2 px high; 1 barrel, bore 3.4, 4.5 px long; turntable radius 6; axis 0.8 of it | `SPORE_MORTAR` (`style` `mortar`) |
| maw turret (core) | (0, -38), 8.4 px high; 3 barrels 2.6 px apart, bore 1, 6 px long; dome radius 4.5 | `mounts` `maw` |
| thorax rotor (core) | (0, -12), 13.6 px high; 12 barrels, bore 0.8, 3.2 px long; hub radius 4.5 | `mounts` `thorax-rotor` |
| rotor hatch | octagon of radius 6.5 round (0, -12), the cap 12.2–15 px | `armour_region` `rotor-hatch` (`mount`) |
| full health | 4 330 (core 1 150, parts 2 020, lances 1 160) | BOSS-54 |
| points | 4 000; 400 a part | |
| ground speed | ×0.5 | |
| stop height | 0.73 | `stopFraction` |
| sway / bob | 55 px over 9 s / 10 px over 2.6 s | |
| eye-spot fans | 5, 12° apart, heading ∓8° across, magenta 175 px/s, every 3 s (first 1 s / 2.5 s) | a sweep |
| spore shell | 1 aimed, purple, radius 8, 80 px/s, bursting after 1.5 s into 10 magenta at 140 px/s; every 2.8 s (first 1.8 s) | `SPORE` (`bursting`) |
| core stage 0 | aimed 1, purple 185 px/s, every 3 s | maw |
| core stage 1 | aimed 3, 10° apart, every 2.6 s | maw, a sweep |
| core stage 2 | burst of 4, 0.14 s apart, every 2 s | maw |
| core stage 3 | ring of 12 turning 8°, every 1.6 s; aimed magenta every 2.4 s | rotor; maw |
| weighted fire rate | 4.0 as it comes in, 4.5 after its transformation | BOSS-39 |
| transformation | `eye-left` and `eye-right` destroyed | `transformParts` |
| forewings (moving region) | the open forewing: x 12..85, y -38..0; membrane 6–8.2 px; swing about the vertical at (±12, -22, 6) from 50° back to 0; mirrored; no frame | `moving_region`, `swing`; `heights` from 6 px |
| hindwings (moving region) | the open hindwing: x 13..66, y -6..40; membrane 4.4–6 px; swing about the vertical at (±13, -6, 4) from 20° back to 0; mirrored; no frame | |
| lances | (∓62, -24) on the open forewings, radius 8, health 580, pod on the wing from 8 to 11 px, purple; first 1.2 s / 2.0 s | ride the forewings |
| neon | lilac (0.85, 0.5, 1), shown green | `BOSS_LOOK.neon` |

## Notes

- **Lab boss.** No level, world file or music cue names it; its fight time and its place in a
  world's health order (BOSS-55, BOSS-56) are not set. Its health is about that of the 1-3 mini boss
  (Dust Devil, 4 090).
- **Simulated fight** (a part broken every 12 s, scratch tool, 2026-11-05): 339 shots, every one
  from a barrel, along it; it dies at about 74 s.
