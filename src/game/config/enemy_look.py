"""Look of the enemies (P05, GD-61), of their shots (GD-43) and of their explosions (GD-62).

Dark metallic hulls with neon lights, colourful bullets
Linear RGB, 0..1; sizes in logical pixels; durations in seconds.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.record import record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


def glow(core: Any, mid: Any, rim: Any) -> list[Any]:
    """Glow disc colours, centre to edge (black edge: soft fade with additive blending)."""
    return [core, mid, rim, [0, 0, 0]]


def times(color: Any, k: float) -> list[Any]:
    """A colour scaled by `k`."""
    return [color[0] * k, color[1] * k, color[2] * k]


def whiter(color: Any, t: float) -> list[Any]:
    """A colour `t` of the way to white."""
    return [c + (1 - c) * t for c in color]


def bullet(core: Any, color: Any) -> Any:
    """An enemy bullet's colours, centre to edge (phase 8 review).

    Its body's, a deep shade of its `color`, darker at the rim so it reads as a ball, fading out
    (`bullets.fade`), dark enough for the swirls added over it to show; its faint aura's; its two
    swirls', the smaller one whiter; and its pulsing `core`'s. All but the body are added on, so
    they end in black.
    """
    return record(
        {
            "body": [times(color, k) for k in [0.6, 0.6, 0.55, 0.45, 0.35, 0.25]],
            "halo": [times(color, 0.4), times(color, 0.2), [0, 0, 0]],
            "swirls": [
                [whiter(color, t), times(color, 0.8), times(color, 0.35), [0, 0, 0]]
                for t in [0.1, 0.4]
            ],
            "core": [core, core, times(color, 0.6), [0, 0, 0]],
        }
    )


def laser_palette(color: Any) -> Any:
    """A laser in `color` (phase 8 review): a white-hot beam core, its colour around it, fading out.

    Returns its warning line, beam and base flare colours.
    """
    return record(
        {
            "warning": [color, times(color, 0.5), [0, 0, 0]],
            "beam": [whiter(color, 0.9), color, times(color, 0.5), [0, 0, 0]],
            # A soft, roughly exponential falloff from white-hot, as the player's laser flare.
            "emitter": [
                whiter(color, 0.8),
                whiter(color, 0.5),
                color,
                times(color, 0.6),
                times(color, 0.3),
                times(color, 0.1),
                [0, 0, 0],
            ],
        }
    )


ENEMY_LOOK = record(
    {
        # Hull shades, multiplied into a dark PBR metal. The metal is `tint` of the way from white
        # to the enemy's neon colour, and glows `selfLight` of it (phase 5 review: enemies easier
        # to tell from the ground and its shadows).
        "hull": {
            "base": [0.1, 0.105, 0.12],
            "panel": [0.16, 0.16, 0.19],
            "dark": [0.045, 0.045, 0.055],
            "metallic": 0.85,
            "roughness": 0.38,
            "tint": 0.6,
            "selfLight": 0.04,
        },
        # Cyber-Organic bodies (P16-R01): dark flesh shades, multiplied into a less metallic, waxy
        # material (`metallic`, `roughness`) tinted `tint` of the way towards the enemy's neon.
        # Kept dark (under 0.2) so the enemies still stand out from the darkened ground (P14-R04).
        "flesh": {
            "crimson": [0.13, 0.035, 0.045],
            "purple": [0.085, 0.04, 0.12],
            "teal": [0.03, 0.09, 0.095],
            "sinew": [0.17, 0.08, 0.075],
            "bone": [0.19, 0.17, 0.15],
            "membrane": [0.1, 0.04, 0.07],
            "wound": [0.2, 0.02, 0.03],
            "metallic": 0.25,
            "roughness": 0.5,
            "tint": 0.35,
        },
        # Living motion (P16-R07), visual only: the body breathes (its scale pulses by `amplitude`
        # over `period`, +- `spread` per enemy), its veins pulse (from `low` to full over `period`),
        # and its wings flutter (`angle` radians at `hz`; `bigHz` for wings longer than `bigSpan`).
        "living": {
            "breathing": {"amplitude": 0.03, "period": 2.5, "spread": 0.2},
            "glow": {"period": 1.2, "low": 0.55},
            "flutter": {"hz": 6, "bigHz": 2, "bigSpan": 25, "angle": 0.16},
        },
        # Triangle budgets per tier (P16-R09).
        "budget": {
            "basic": 400,
            "veteran": 700,
            "elite": 1200,
            "miniBoss": 4000,
            "finalBoss": 10000,
        },
        # Neon colours of each enemy (P05-R01..R10, P05-R12).
        "neon": {
            "gnat": [0.1, 0.95, 1],
            "hornet": [1, 0.08, 0.1],
            "scout": [0.05, 0.9, 1],
            "strafer": [1, 0.1, 0.85],
            "weaver": [0.2, 1, 0.3],
            "spinner": [1, 0.5, 0.05],
            "lancer": [1, 0.25, 0.35],
            "rocketeer": [1, 0.12, 0.08],
            "bulwark": [0.15, 0.4, 1],
            "splitter": [0.65, 0.2, 1],
            "carrier": [1, 0.7, 0.1],
        },
        # Reactors (phase 5 review): a dark nozzle with a glowing core, and the player ships'
        # animated flame, all in the same light blue `color` on every enemy. Sizes relative to the
        # nozzle radius; the inner flame is `whiten` of the way from `color` to white. Kept light
        # (phase 5 review): an open nozzle, a flat core, 4-sided flame cones without caps and 2
        # tetrahedron puffs, about 40 triangles a reactor (about 150 before).
        "reactor": {
            # Saturated enough (0.52) to be folded into the enemy family when drawn (P14-R02).
            "color": [0.48, 0.82, 1],
            "flameSides": 4,
            "puffs": 2,
            "depth": 1.2,
            "core": 0.75,
            "flameLength": 5,
            "flameWidth": 1.5,
            "puffSize": 1.1,
            "sides": 6,
            "exhaustAlpha": 0.45,
            "flameAlpha": 0.75,
            "plasmaAlpha": 0.6,
            "whiten": 0.55,
        },
        # Rotors (the Gnat's ducted fans): blades, hub radius relative to the blades, spin.
        "rotor": {
            "blades": 2,
            "hub": 0.22,
            "spinRadPerSec": 30,
        },
        # A charging light (`Enemy.charge`) goes from `idle` to full brightness.
        "chargeIdle": 0.18,
        # Glow layer over the playfield (enemies' neon, shots).
        "glow": {"intensity": 0.6, "blurKernelSize": 24},
        "bullets": {
            # Visual radius relative to the hit radius.
            "scale": 1.6,
            # A ball of plasma: opacity of the body's centre and of each ring of its colours, so it
            # is a solid colour inside and its border fades out. Blended rather than added, so its
            # colour shows over bright snow too.
            "fade": [1, 1, 1, 0.85, 0.4, 0],
            # A faint aura added around the body, `size` times its radius, flickering by `flicker`
            # at `flickerHz`.
            "halo": {"size": 1.45, "flicker": 0.08, "flickerHz": 13},
            # Curled arms of brighter plasma added over the body (`buildSwirl`), spinning at
            # `spinRadPerSec` (opposite ways, so they churn), `size` times the body's radius, in
            # the colours of their style (`styles.*.swirls`). Each bullet starts them turned by its
            # heading, so a ring of bullets does not spin as one.
            "swirls": [
                {"size": 1, "lobes": 3, "depth": 0.55, "twist": 2.4, "spinRadPerSec": 6},
                {"size": 0.75, "lobes": 2, "depth": 0.65, "twist": -3, "spinRadPerSec": -10},
            ],
            # A white-hot glow added over its centre (phase 8 review), its radius relative to the
            # bullet's, swelling and shrinking by `amount` of it `hz` times a second as the bullet
            # flies.
            "core": {"size": 0.35, "pulse": {"hz": 2.5, "amount": 0.3}},
            "segments": 12,
            # The swirls' arms need more sides to curl smoothly.
            "swirlSegments": 24,
            "styles": {
                # Phase 14 (P14-R02, reviewer): every style in the enemy shots' warm family,
                # white-hot
                # cores round orange to yellow; the style names are kept for the enemy specs.
                "red": bullet([1, 0.95, 0.88], [1, 0.36, 0.04]),
                "magenta": bullet([1, 0.95, 0.88], [1, 0.55, 0.05]),
                "green": bullet([1, 1, 0.88], [1, 0.88, 0.1]),
                "orange": bullet([1, 0.95, 0.85], [1, 0.48, 0.02]),
                "blue": bullet([1, 0.97, 0.88], [1, 0.7, 0.08]),
                "purple": bullet([1, 0.95, 0.88], [1, 0.42, 0.1]),
            },
        },
        # Phase 10 (P10-R07): the shot style World 4's looks name (`SceneryLook.shotStyle`), for
        # red, orange and dark grounds and skies. Each bullet keeps its colours but gets a dark
        # `rim` behind it (a blended disc `size` times its radius, so a dark ring shows round the
        # ball) and a white `spark` added at its heart (`size` times its radius); laser warning
        # lines get a white core and are `warningWidth` times as wide.
        "contrast": {
            "style": "contrast",
            "rim": {
                "size": 1.3,
                "color": [0.02, 0.02, 0.04],
                "fade": [0.92, 0.92, 0.9, 0.85, 0.55, 0],
            },
            "spark": {
                "size": 0.2,
                "colors": [
                    [1, 1, 1],
                    [1, 1, 1],
                    [0.6, 0.6, 0.6],
                    [0, 0, 0],
                ],
            },
            "warningCore": 0.85,
            "warningWidth": 1.5,
        },
        "missile": {
            # Body length and radius.
            "length": 11,
            "radius": 1.8,
            # Phase 14 (P14-R02): an orange tip, in the enemy shots' family.
            "tip": [1, 0.5, 0.04],
            "flame": glow([1, 0.95, 0.7], [1, 0.45, 0.1], [0.35, 0.12, 0]),
            "flameSize": [2.6, 6],
        },
        "laser": {
            # Colour of the lasers of a style (`EnemyLaserSpec.style`) that is not a boss's: the
            # Lancer's red. A boss's lasers take its neon colour (`BOSS_LOOK.neon`, phase 8 review).
            "color": [1, 0.3, 0.4],
            # Phase 14 (P14-R02): every laser colour is moved into the enemy shots' family when
            # drawn.
            # The thin warning line, blinking at `blinkHz`, then the beam.
            "warning": {"width": 2, "blinkHz": 8},
            "beam": {
                # Visual width relative to the beam width.
                "glowWidth": 2,
                "flicker": 0.12,
                "flickerHz": 21,
            },
            # The flare at the beam's base, as the player's laser's (`SHOT_LOOK.laser.muzzle`, phase
            # 8 review): `radius` times (`baseScale` + beam width / `widthDivisor`), stretched along
            # the beam, pulsing by `pulse` at `pulseHz`, round and smooth (`segments` sides).
            "flare": {
                "radius": 12,
                "baseScale": 0.6,
                "widthDivisor": 12,
                "stretch": 1.3,
                "pulse": 0.15,
                "pulseHz": [9, 17],
                "segments": 24,
            },
        },
        # Explosions (GD-62; phase 5 review: bigger, with burning debris; phase 14, P14-R07:
        # smaller, over in `READABILITY.effectMaxDuration`, so they never hide the shots for long).
        # Sizes are relative to the hit radius of what blew up, `[min, max)` ranges are picked at
        # random per particle, `life` and `delay` in seconds, speeds in logical pixels a second,
        # `drag` per second.
        "blasts": {
            "seed": 11,
            # Missiles blow up smaller, with fewer particles.
            "missileScale": 0.6,
            # Phase 14 (P14-R07): blasts are drawn no bigger than for this hit radius, so one covers
            # at most `READABILITY.effectMaxScreenShare` of the screen (a boss part's was up to a
            # third).
            "maxRadius": 22,
            # Debris, embers and smoke wisps are full size for blasts this big (a hit radius,
            # logical pixels) and up, smaller for smaller ones (phase 5 review: small booms for tiny
            # ships).
            "fullRadius": 16,
            # Fire cools along these colours, white hot to out (black, as fire is added on).
            "heat": [
                [1, 0.97, 0.88],
                [1, 0.8, 0.4],
                [1, 0.45, 0.1],
                [0.65, 0.14, 0.03],
                [0, 0, 0],
            ],
            # A thin shock ring that races out and fades.
            "ring": {"size": 4, "life": 0.35, "segments": 32, "color": [1, 0.75, 0.45]},
            # Fireballs around the centre, one after the other, swelling as they cool. Laid over
            # what is behind them (not added on, which turns to flat white over a bright ground),
            # along `colors`, opaque for `opaque` of their life, then fading out.
            "fireball": {
                "colors": [
                    [1, 0.96, 0.75],
                    [1, 0.72, 0.22],
                    [0.95, 0.38, 0.06],
                    [0.55, 0.12, 0.03],
                    [0.18, 0.07, 0.05],
                ],
                "opaque": 0.45,
                "alpha": 0.95,
                "perRadius": 0.3,
                "count": [2, 14],
                "spread": 1.1,
                "delay": 0.12,
                "size": [1.2, 2],
                "growth": 1.5,
                "life": [0.3, 0.45],
                "drift": 40,
                "segments": 16,
            },
            # Dark smoke left by the fireballs and the burning debris, lingering.
            "smoke": {
                "size": [1, 1.6],
                "growth": 1.6,
                "life": [0.2, 0.3],
                "drift": 14,
                "alpha": 0.55,
                # Lit by the fire at first, then grey.
                "colors": [
                    [0.4, 0.22, 0.1],
                    [0.13, 0.12, 0.12],
                ],
                "segments": 12,
            },
            # Burning pieces thrown out, slowing down, trailing embers and smoke as they burn out.
            "debris": {
                "perRadius": 0.9,
                "min": 4,
                "max": 36,
                "speed": [80, 240],
                "size": [2.6, 5],
                "life": [0.3, 0.4],
                "drag": 1.8,
                # One ember every `emberEvery` seconds and one smoke wisp every `smokeEvery`, while
                # hot.
                "emberEvery": 0.025,
                "smokeEvery": 0.09,
                # Size of a smoke wisp, in logical pixels.
                "smokeSize": [4, 8],
                "segments": 8,
            },
            # Embers left behind by the debris and spat out by the blast, cooling fast.
            "embers": {
                "count": [5, 40],
                "speed": [60, 220],
                "size": [1, 2],
                "life": [0.12, 0.25],
                "drag": 4,
            },
            # At most this many particles in each layer; new ones are dropped beyond.
            "cap": 1200,
        },
    }
)
