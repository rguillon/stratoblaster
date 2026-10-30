"""Explosions where enemies and missiles were destroyed (GD-62; phase 5 review: bigger, more
realistic): a shock ring, a cluster of fireballs, dark
smoke that lingers, and burning debris with embers and smoke wisps."""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Rgb = list[float]
__pragma__("noskip")

from core.math.rng import random_in  # noqa: E402
from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.view.enemies.organic_parts import opt  # noqa: E402

LOOK = ENEMY_LOOK.blasts
# Debris stops dropping embers and smoke after this share of its life.
BURN_LIMIT = 0.7

# The layers of an explosion, each drawn in one go.
BLAST_LAYERS = ["smoke", "rings", "fireballs", "debris", "embers"]


def ramp(colors: list[Rgb], t: float) -> Rgb:
    """The colour at `t` (0..1) along `colors`."""
    last = len(colors) - 1
    at = min(max(t, 0), 1) * last
    i = min(math.floor(at), last - 1)
    a = colors[i] if i >= 0 else [0, 0, 0]
    b = colors[i + 1]
    k = at - i
    return [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k]


class BlastSpot:
    """A disc to draw: centre, radius, and the colour it is tinted with (alpha for smoke)."""

    def __init__(self, x: float, y: float, radius: float, color: Rgb, a: float) -> None:
        self.x = x
        self.y = y
        self.radius = radius
        self.r = color[0]
        self.g = color[1]
        self.b = color[2]
        self.a = a


class Particle:
    """One particle of a layer. `age` is negative until the particle appears."""

    def __init__(  # noqa: PLR0917
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        size: float,
        life: float,
        growth: float,
        drag: float,
        ember: float,
        wisp: float,
        small: float,
        age: float,
    ) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.life = life
        self.growth = growth
        self.drag = drag
        self.ember = ember
        self.wisp = wisp
        self.small = small
        self.age = age


def spot(p: Particle, radius: float, color: Rgb, a: float = 1) -> BlastSpot:
    """A spot at the particle's place."""
    return BlastSpot(p.x, p.y, radius, color, a)


def grown(p: Particle, k: float) -> float:
    """The particle's size grown by `k` of the way to its end size."""
    return p.size * (1 + (p.growth - 1) * k)


def look_rings(p: Particle, t: float) -> BlastSpot:
    """Laid over the ground, not added on: an explosion does not light the ground (reviewer,
    2026-10-28)."""
    return spot(p, p.size * math.sqrt(t), LOOK.ring.color, (1 - t) ** 2)


def look_fireballs(p: Particle, t: float) -> BlastSpot:
    """Fireballs cool from white to deep red."""
    f = LOOK.fireball
    alpha = f.alpha * min(1, (1 - t) / (1 - f.opaque))
    return spot(p, grown(p, math.sqrt(t)), ramp(f.colors, t), alpha)


def look_smoke(p: Particle, t: float) -> BlastSpot:
    """Smoke thickens fast, then thins out as it spreads."""
    alpha = LOOK.smoke.alpha * min(1, t / 0.12) * (1 - t)
    return spot(p, grown(p, math.sqrt(t)), ramp(LOOK.smoke.colors, t * 2), alpha)


def look_debris(p: Particle, t: float) -> BlastSpot:
    """Burning debris shrinks and cools."""
    return spot(p, p.size * (1 - 0.5 * t), ramp(LOOK.heat, 0.15 + 0.75 * t))


def look_embers(p: Particle, t: float) -> BlastSpot:
    """Embers shrink and cool."""
    return spot(p, p.size * (1 - t), ramp(LOOK.heat, 0.25 + 0.75 * t))


LOOKS = {
    "rings": look_rings,
    "fireballs": look_fireballs,
    "smoke": look_smoke,
    "debris": look_debris,
    "embers": look_embers,
}


class BlastParticles:
    """Explosions where enemies and missiles were destroyed (GD-62): every layer's particles."""

    def __init__(self, random: Any) -> None:
        self.random = random
        self.layers: dict[str, list[Particle]] = {
            "smoke": [],
            "rings": [],
            "fireballs": [],
            "debris": [],
            "embers": [],
        }

    def count(self) -> int:
        """All the particles alive, in every layer."""
        total = 0
        for layer in BLAST_LAYERS:
            total += len(self.layers[layer])
        return total

    def emit(self, blast: Any) -> None:
        """Starts the explosion of `blast`."""
        scale = LOOK.missileScale if blast.kind == "missile" else 1
        # P14-R07: never bigger than for `maxRadius`.
        radius = min(blast.radius, LOOK.maxRadius) * scale
        # Pieces, embers and wisps shrink with blasts smaller than `fullRadius`.
        small = min(1, radius / LOOK.fullRadius)
        at = [blast.x, blast.y]
        self.add(
            "rings",
            {"x": at[0], "y": at[1], "size": radius * LOOK.ring.size, "life": LOOK.ring.life},
        )
        f = LOOK.fireball
        fireballs = self.count_of(radius * f.perRadius, f.count, scale)
        for i in range(fireballs):  # noqa: B007
            # The first one at the centre, at once; the others around it, later.
            k = 0 if i == 0 else 1
            d = self.direction(self.random() * radius * f.spread * k)
            fire = {
                "x": blast.x + d[0],
                "y": blast.y + d[1],
                "delay": self.random() * f.delay * k,
                "speed": f.drift,
                "dir": [d[0], d[1]],
            }
            self.fireball(fire, radius)
        d = LOOK.debris
        pieces = self.count_of(radius * d.perRadius, [d.min, d.max], scale)
        fling = 0.5 + radius / 40
        for _ in range(pieces):
            self.fling("debris", at, d, fling, LOOK.debris.drag, small)
        e = LOOK.embers
        embers = self.count_of(radius, e.count, scale)
        for _ in range(embers):
            self.fling("embers", at, e, fling, e.drag, small)

    def step(self, dt: float) -> dict[str, list[BlastSpot]]:
        """Ages everything by `dt`, drops what is over, and returns where to draw."""
        self.burn(dt)
        out: dict[str, list[BlastSpot]] = {}
        for layer in BLAST_LAYERS:
            spots: list[BlastSpot] = []
            kept: list[Particle] = []
            for p in self.layers[layer]:
                p.age += dt
                if p.age < p.life:
                    kept.append(p)
            self.layers[layer] = kept
            for p in kept:
                if p.age < 0:
                    continue
                slow = math.exp(-p.drag * dt)
                p.vx *= slow
                p.vy *= slow
                p.x += p.vx * dt
                p.y += p.vy * dt
                spots.append(LOOKS[layer](p, p.age / p.life))
            out[layer] = spots
        return out

    def burn(self, dt: float) -> None:
        """Burning debris drops embers and smoke wisps along its way while it is hot."""
        d = LOOK.debris
        for p in self.layers["debris"]:
            if p.age < 0 or p.age / p.life > BURN_LIMIT:
                continue
            p.ember -= dt
            p.wisp -= dt
            if p.ember <= 0:
                p.ember += d.emberEvery
                trail = {"speed": [5, 30], "size": LOOK.embers.size, "life": LOOK.embers.life}
                self.fling("embers", [p.x, p.y], trail, 1, LOOK.embers.drag, p.small)
            if p.wisp <= 0:
                p.wisp += d.smokeEvery
                size = random_in(self.random, d.smokeSize[0], d.smokeSize[1]) * p.small
                life = random_in(self.random, LOOK.smoke.life[0], LOOK.smoke.life[1]) * 0.6
                self.add(
                    "smoke",
                    {"x": p.x, "y": p.y, "size": size, "life": life, "growth": LOOK.smoke.growth},
                )

    def fireball(self, fire: dict[str, Any], radius: float) -> None:
        """A fireball and the smoke it leaves, a little behind it."""
        f = LOOK.fireball
        s = LOOK.smoke
        dx = fire["dir"][0]
        dy = fire["dir"][1]
        length = math.sqrt(dx * dx + dy * dy)
        if length == 0:
            length = 1
        vx = (dx / length) * fire["speed"]
        vy = (dy / length) * fire["speed"]
        size = radius * random_in(self.random, f.size[0], f.size[1])
        life = random_in(self.random, f.life[0], f.life[1])
        self.add(
            "fireballs",
            {
                "x": fire["x"],
                "y": fire["y"],
                "delay": fire["delay"],
                "vx": vx,
                "vy": vy,
                "size": size,
                "life": life,
                "growth": f.growth,
            },
        )
        # The smoke it leaves, a little behind it.
        smoke_size = radius * random_in(self.random, s.size[0], s.size[1])
        smoke_life = random_in(self.random, s.life[0], s.life[1])
        self.add(
            "smoke",
            {
                "x": fire["x"],
                "y": fire["y"],
                "delay": fire["delay"] + life * 0.35,
                "vx": (vx * s.drift) / f.drift,
                "vy": (vy * s.drift) / f.drift,
                "size": smoke_size,
                "life": smoke_life,
                "growth": s.growth,
            },
        )

    def fling(
        self,
        layer: str,
        at: list[float],
        look: Any,
        fling: float,
        drag: float,
        small: float,
    ) -> None:
        """A piece of `layer` thrown out from `at` in a random direction."""
        speed = look["speed"]
        size_range = look["size"]
        life_range = look["life"]
        v = self.direction(random_in(self.random, speed[0], speed[1]) * fling)
        self.add(
            layer,
            {
                "x": at[0],
                "y": at[1],
                "vx": v[0],
                "vy": v[1],
                "size": random_in(self.random, size_range[0], size_range[1]) * small,
                "life": random_in(self.random, life_range[0], life_range[1]),
                "drag": drag,
                "small": small,
                "ember": self.random() * LOOK.debris.emberEvery,
                "wisp": self.random() * LOOK.debris.smokeEvery,
            },
        )

    def add(self, layer: str, p: Any) -> None:
        """Adds a particle to `layer`, unless the layer is full (`cap`)."""
        items = self.layers[layer]
        if len(items) >= LOOK.cap:
            return
        delay = opt(p, "delay", 0)
        items.append(
            Particle(
                p["x"],
                p["y"],
                opt(p, "vx", 0),
                opt(p, "vy", 0),
                p["size"],
                p["life"],
                opt(p, "growth", 1),
                opt(p, "drag", 0),
                opt(p, "ember", 0),
                opt(p, "wisp", 0),
                opt(p, "small", 1),
                -delay,
            )
        )

    def direction(self, length: float) -> list[float]:
        """A vector `length` long in a random direction."""
        angle = self.random() * 2 * math.pi
        return [math.sin(angle) * length, math.cos(angle) * length]

    def count_of(self, n: float, rng: list[float], scale: float) -> int:
        """How many pieces: `n` clamped to the range `rng`, scaled, rounded, at least one."""
        clamped = min(rng[1], max(rng[0], n))
        return max(1, math.floor(clamped * scale + 0.5))
