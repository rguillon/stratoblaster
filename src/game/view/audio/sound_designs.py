# Copyright (c) 2026 Renaud Guillon
"""The game's sound effects (AUD-SFX-01), all synthesised, keyed by the engine's cue (`SoundCue`).

Made to sound real rather than like a chip (D-239): cracks, thumps, whooshes and rumbles of
filtered noise and sines, metallic rings of noise through narrow filters, struck bells for the
rewards and clicks for the menus; no bare square or sawtooth sweep. Made to fit the darksynth
music and to suit a child (AUD-SFX-07). Priorities (AUD-SFX-05): the player's and the bombs' sounds
highest, the enemy shots lowest. The player's gun shots and the laser hum are mixed quieter than
hits and explosions (AUD-SFX-06).

`sound(...)` takes its optional fields (`positional`, `loop`, `hold`) as a dict, as the
The layers take a partial object.
"""

from audio.audio_types import FilterSpec, SoundDesign
from game.view.audio.sound_recipes import (
    MINIGUN,
    ExplosionSize,
    bell,
    click,
    env,
    explosion,
    flatten_layers,
    minigun,
    ring,
    rumble,
    thump,
    tone,
    whoosh,
)

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# Priorities (AUD-SFX-05).
PRIORITY = {
    "enemyShot": 0,
    "enemy": 1,
    "hit": 2,
    "weapon": 3,
    "blast": 4,
    "part": 5,
    "player": 6,
    "top": 7,
}


def sound(
    name: str,
    priority: float,
    gain: float,
    layers: list[Any],
    rest: dict[str, Any],
) -> SoundDesign:
    """Return a sound effect; `rest` holds `positional`, `loop` or `hold` (default 0)."""
    return SoundDesign(
        name,
        flatten_layers(layers),
        gain,
        priority,
        rest.get("hold", 0),
        rest.get("positional"),
        rest.get("loop"),
    )


PLAYER_WEAPONS = {
    "fire:bullet": sound(
        "gun-shot", PRIORITY["weapon"], 0.14, minigun(MINIGUN), {"positional": True}
    ),
    # A rocket leaving its tube: an ignition pop, the exhaust whoosh rising then thinning, a low
    # rumble under it.
    "fire:missile": sound(
        "missile-launch",
        PRIORITY["weapon"],
        0.3,
        [
            click(900, 0.5, 0.02),
            whoosh(400, 2600, 0.8, 0.35, 0, 0.8),
            rumble(260, 0.6, 0.3),
            tone(
                "noise",
                1,
                0.08,
                env(0.05, 0.15, 0, 0.1),
                {"delay": 0.1, "filter": FilterSpec("highpass", 3500, None, None, None)},
            ),
        ],
        {"positional": True},
    ),
    # The beam powering up: a swelling air sweep and a low surge, with a relay click.
    "beam-start:laser": sound(
        "laser-start",
        PRIORITY["weapon"],
        0.3,
        [
            click(1800, 0.4, 0.012),
            whoosh(350, 3000, 0.7, 0.2, 0, 3),
            tone(
                "sine",
                70,
                0.5,
                env(0.02, 0.18, 0, 0.08),
                {"glide_to": 150, "glide_seconds": 0.15},
            ),
        ],
        {"positional": True},
    ),
    # The beam: an electric hum of two low partials beating slowly, under a hiss of air.
    "beam:laser": sound(
        "laser-hum",
        PRIORITY["weapon"],
        0.1,
        [
            tone("sine", 55, 0.6, env(0.05, 0.1, 0.8, 0.12), {}),
            tone(
                "triangle",
                110,
                0.4,
                env(0.05, 0.1, 0.8, 0.12),
                {"detune_cents": 7, "filter": FilterSpec("lowpass", 700, None, None, None)},
            ),
            tone(
                "noise",
                1,
                0.12,
                env(0.08, 0.1, 0.8, 0.12),
                {"filter": FilterSpec("bandpass", 1600, 1.5, None, None)},
            ),
        ],
        {"loop": True},
    ),
    # A weapon racked: two mechanical clacks and a low thud, "ch-chk".
    "weapon-switch": sound(
        "weapon-switch",
        PRIORITY["player"],
        0.3,
        [
            click(2200, 0.9, 0.015),
            thump(180, 0.4, 0.05),
            click(1500, 1.2, 0.02, 0.09),
            thump(160, 0.5, 0.06, 0.09),
        ],
        {},
    ),
    # A part locking in, then two bells rising.
    "weapon-up": sound(
        "weapon-level-up",
        PRIORITY["player"],
        0.35,
        [
            click(1600, 0.9, 0.02),
            whoosh(500, 2800, 0.3, 0.2, 0, 2),
            bell([880, 1320], 0.09, 0.4),
        ],
        {},
    ),
}

ENEMY_WEAPONS = {
    # An enemy gun: a dull crack with a low body, duller than the player's minigun.
    "enemy-bullet": sound(
        "enemy-shot",
        PRIORITY["enemyShot"],
        0.16,
        [
            click(1100, 0.6, 0.015),
            rumble(600, 0.5, 0.05),
            thump(220, 0.5, 0.06),
        ],
        {"positional": True},
    ),
    # A rocket passing: its exhaust whoosh and a rumble.
    "enemy-missile": sound(
        "enemy-missile",
        PRIORITY["enemyShot"],
        0.22,
        [
            whoosh(350, 1800, 0.7, 0.35, 0, 1.2),
            rumble(220, 0.5, 0.3),
        ],
        {"positional": True},
    ),
    # The laser charging: two relay clicks over a rising, narrowing air sweep (no siren).
    "laser-warning": sound(
        "laser-warning",
        PRIORITY["enemy"],
        0.2,
        [
            click(1800, 1.5, 0.015),
            click(1800, 1.5, 0.015, 0.16),
            whoosh(300, 2400, 1.2, 0.35, 0, 3),
        ],
        {"positional": True},
    ),
    # The enemy beam: a blast of air falling in pitch, a sub thump, a rumble held while it fires.
    "laser-fire": sound(
        "enemy-laser",
        PRIORITY["enemy"],
        0.3,
        [
            whoosh(2500, 500, 0.6, 0.5, 0, 1.5),
            thump(90, 0.6, 0.3),
            tone(
                "noise",
                1,
                0.4,
                env(0.01, 0.4, 0.3, 0.15),
                {"filter": FilterSpec("lowpass", 300, 0.7, None, None)},
            ),
        ],
        {"positional": True, "hold": 0.3},
    ),
}

HITS = {
    # A shot striking metal: a crack, a short clank and a thud.
    "hit": sound(
        "hit",
        PRIORITY["hit"],
        0.3,
        [
            tone(
                "noise",
                1,
                0.6,
                env(0.001, 0.05),
                {"filter": FilterSpec("highpass", 1800, None, None, None)},
            ),
            ring(3200, 1.0, 0.06),
            thump(260, 0.5, 0.06),
        ],
        {"positional": True},
    ),
    # A shot glancing off a shield: a click and two inharmonic metallic rings.
    "hit-blocked": sound(
        "hit-shield",
        PRIORITY["hit"],
        0.28,
        [
            click(2500, 0.8, 0.01),
            ring(2900, 1.6, 0.25),
            ring(4300, 1.1, 0.18),
        ],
        {"positional": True},
    ),
    # The ship struck: a crack, a body of noise closing down, a sub thump and a rattle of metal.
    "player-hit": sound(
        "player-hit",
        PRIORITY["player"],
        0.36,
        [
            tone(
                "noise",
                1,
                0.5,
                env(0.001, 0.02, 0, 0.01),
                {"filter": FilterSpec("highpass", 1000, None, None, None)},
            ),
            tone(
                "noise",
                1,
                0.6,
                env(0.002, 0.2, 0, 0.08),
                {"filter": FilterSpec("lowpass", 250, 0.7, 900, 0.2)},
            ),
            thump(120, 0.7, 0.25),
            ring(2400, 0.7, 0.12, 0.02),
        ],
        {"positional": True},
    ),
}

# Explosion sizes (AUD-SFX-04, D-108): enemies small and large, boss parts and the player, the
# bomb and bosses.
BLAST_SMALL = ExplosionSize(0.3, 2600, 120, 0, 3)
BLAST_LARGE = ExplosionSize(0.6, 3000, 90, 0.9, 5)
BLAST_HUGE = ExplosionSize(1.1, 3400, 70, 2, 8)

DESTRUCTION = {
    "blast-small": sound(
        "explosion-small",
        PRIORITY["blast"],
        0.32,
        explosion(BLAST_SMALL, 0),
        {"positional": True},
    ),
    "blast-large": sound(
        "explosion-large",
        PRIORITY["blast"],
        0.42,
        explosion(BLAST_LARGE, 0),
        {"positional": True},
    ),
    # A large blast, then metal tearing away and falling.
    "part-destroyed": sound(
        "boss-part-destroyed",
        PRIORITY["part"],
        0.55,
        [
            explosion(BLAST_LARGE, 0),
            whoosh(2600, 500, 0.5, 0.45, 0.05, 8),
            ring(1800, 0.6, 0.3, 0.1),
        ],
        {"positional": True},
    ),
    # A chain: the core goes, then two more blasts inside the hull, over the hull's groan and a
    # deep rumble.
    "boss-destroyed": sound(
        "boss-destroyed",
        PRIORITY["top"],
        0.5,
        [
            explosion(BLAST_HUGE, 0),
            explosion(BLAST_LARGE, 0.35),
            explosion(BLAST_LARGE, 0.8),
            tone(
                "sine",
                90,
                0.3,
                env(0.01, 1.4, 0, 0.2),
                {"glide_to": 30, "glide_seconds": 1.4},
            ),
            rumble(120, 0.3, 1.6, 0.3),
        ],
        {},
    ),
}

PLAYER = {
    # The ship going down: its engine winding down (a falling air sweep and a falling low tone)
    # over a large blast.
    "life-lost": sound(
        "life-lost",
        PRIORITY["top"],
        0.45,
        [
            whoosh(2200, 300, 0.4, 0.6, 0, 2),
            tone(
                "sine",
                180,
                0.4,
                env(0.005, 0.6, 0, 0.1),
                {"glide_to": 50, "glide_seconds": 0.6},
            ),
            explosion(BLAST_LARGE, 0),
        ],
        {},
    ),
    "extra-life": sound(
        "extra-life",
        PRIORITY["top"],
        0.4,
        bell([784, 988, 1175, 1568], 0.08, 0.42),
        {},
    ),
    # A huge blast, then the pressure wave washing over and a sub-bass pressure drop.
    "bomb": sound(
        "bomb",
        PRIORITY["top"],
        0.5,
        [
            explosion(BLAST_HUGE, 0),
            whoosh(1500, 200, 0.25, 0.8, 0.05, 1.5),
            tone(
                "sine",
                50,
                0.3,
                env(0.005, 1.2, 0, 0.2),
                {"glide_to": 25, "glide_seconds": 1.2},
            ),
        ],
        {},
    ),
    "bonus:bomb": sound(
        "bomb-bonus",
        PRIORITY["player"],
        0.35,
        [thump(140, 0.5, 0.08), bell([523, 784], 0.07, 0.3)],
        {},
    ),
    # A whoosh up into a bell dyad.
    "bonus:weapon": sound(
        "weapon-bonus",
        PRIORITY["player"],
        0.35,
        [
            whoosh(500, 2500, 0.4, 0.18, 0, 2),
            bell([1047, 1568], 0.08, 0.35),
        ],
        {},
    ),
    "bonus:life": sound(
        "life-bonus",
        PRIORITY["player"],
        0.35,
        bell([784, 1175, 1568], 0.06, 0.45),
        {},
    ),
}

# The menus: clicks of a switch and a soft tap of a bell, not beeps.
MENUS = {
    "menu-move": sound(
        "menu-move",
        PRIORITY["top"],
        0.18,
        [click(3000, 1.5, 0.012)],
        {},
    ),
    "menu-confirm": sound(
        "menu-confirm",
        PRIORITY["top"],
        0.25,
        [
            click(2200, 1.0, 0.015),
            tone("sine", 1046, 0.5, env(0.002, 0.15, 0, 0.1), {}),
        ],
        {},
    ),
    "menu-back": sound(
        "menu-back",
        PRIORITY["top"],
        0.25,
        [
            click(1400, 1.0, 0.015),
            tone("sine", 523, 0.5, env(0.002, 0.15, 0, 0.1), {}),
        ],
        {},
    ),
    # A switch thrown: a clunk, its low tone falling.
    "pause": sound(
        "pause",
        PRIORITY["top"],
        0.3,
        [
            click(900, 0.6, 0.02),
            tone(
                "sine",
                220,
                0.6,
                env(0.003, 0.15, 0, 0.05),
                {"glide_to": 150, "glide_seconds": 0.15},
            ),
        ],
        {},
    ),
    # The switch thrown back: the clunk, its tone rising.
    "resume": sound(
        "resume",
        PRIORITY["top"],
        0.3,
        [
            click(900, 0.6, 0.02),
            tone(
                "sine",
                150,
                0.6,
                env(0.003, 0.15, 0, 0.05),
                {"glide_to": 220, "glide_seconds": 0.15},
            ),
        ],
        {},
    ),
    "slider": sound(
        "slider-step",
        PRIORITY["top"],
        0.4,
        [click(2400, 2.0, 0.012)],
        {},
    ),
}


def _all_sounds() -> dict[str, SoundDesign]:
    sounds: dict[str, SoundDesign] = {}
    for group in [PLAYER_WEAPONS, ENEMY_WEAPONS, HITS, DESTRUCTION, PLAYER, MENUS]:
        sounds.update(group)
    return sounds


# Every sound effect, by cue.
SOUND_DESIGNS = _all_sounds()
