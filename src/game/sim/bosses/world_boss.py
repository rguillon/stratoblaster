"""A world boss (P07-R05), built from its design, ported from `game/sim/bosses/world-boss.ts`."""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.entities.boss import Boss
from core.systems.boss_pattern import CORE, BossPattern
from core.systems.enemy_motion import approach
from game.config.bosses.boss_kit import BOSS_TIMING
from game.sim.boss_build import (
    armed_pattern,
    boss_stats,
    break_ring_ids,
    bullet_spec,
    launch_volley,
)

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from core.entities.boss_pieces import BossPart  # noqa: E402
from core.entities.enemy import EnemyContext, EnemySpawnArea  # noqa: E402
from core.systems.boss_pattern import BossPatternSpec, VolleySource, VolleySources  # noqa: E402

__pragma__("noskip")

# A boss design is a config record (`game/config/record.py`), typed as Any there.
__pragma__("skip")
BossDesign = Any
__pragma__("noskip")


def _sign(value: float) -> int:
    """`Math.sign`."""
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def boss_half_width(design: BossDesign) -> float:
    """How far its hit circles reach left and right of its centre (orbiting parts all around)."""
    stats = design.stats
    most: float = stats.coreRadius
    for p in stats.parts:
        reach = math.hypot(p.x, p.y) if p.orbits else abs(p.x)
        most = max(most, reach + p.radius)
    return most


def _boss_top(design: BossDesign) -> float:
    """How far its hit circles reach above its centre."""
    stats = design.stats
    most: float = stats.coreRadius
    for p in stats.parts:
        reach = math.hypot(p.x, p.y) if p.orbits else p.y
        most = max(most, reach + p.radius)
    return most


class WorldBoss(Boss):
    """A World 1 boss (P07-R05), from its `BossDesign`: it comes down from above the top edge,
    braking into its place in the upper part of the screen, then sways left and right (never taking
    its parts out of the ship's reach at the bottom of the screen, D-048) and bobs. Each stage fires
    its pattern; its parts' launches go on while they stand.
    """

    def __init__(self, design: BossDesign, area: EnemySpawnArea) -> None:
        low, high = (0, area.width) if area.top_range is None else area.top_range
        y = area.height + _boss_top(design) + BOSS_TIMING.spawnMargin
        super().__init__((low + high) / 2, y, boss_stats(design))
        self.design = design
        self.center_x = (low + high) / 2
        self.stop_y: float = design.stopFraction * area.height
        # How far it sways: its design's, or less to keep its parts within reach.
        self.sway_amplitude = max(
            0, min(design.sway.amplitude, (high - low) / 2 - boss_half_width(design))
        )
        self._by_id: dict[str, BossPart] = {}
        for part in self.parts:
            self._by_id[part.spec.id] = part
        # Its angry pattern, fresh after each destroyed part (phase 7 review).
        self._rage = BossPattern([])
        self._fighting = 0.0
        self._launches: list[Any] = []
        for launch in design.launches or []:
            piece = self._by_id.get(launch["from"])
            x: float = piece.spec.x if piece is not None else 1
            self._launches.append(launch_volley(launch, _sign(x) or 1))
        self._ringed: list[str] = []
        self._pattern = BossPattern(self._stage(0))

    def _stage(self, stage: int) -> BossPatternSpec:
        """The pattern of stage `stage`: its design's volleys, from their guns, and the parts'
        launches.
        """
        stages = self.design.stages
        volleys = stages[min(stage, len(stages) - 1)] or []
        result: list[Any] = []
        result.extend(self._armed(volleys))
        result.extend(self._launches)
        return result

    def _armed(self, volleys: list[Any]) -> list[Any]:
        """`volleys` from the muzzles of their guns (and turrets)."""
        return armed_pattern(self.design, volleys)

    def update(self, ctx: EnemyContext, dt: float) -> None:
        """Its turrets follow the player as long as it is there, fire pauses included (phase 7
        review).
        """
        Boss.update(self, ctx, dt)
        pattern = self._rage if self.rage > 0 and self.pause <= 0 else self._pattern
        if self.state != "dying":
            pattern.turn_turrets(ctx, dt, self._sources())

    def enter(self, _ctx: EnemyContext, dt: float) -> bool:
        entry_speed: float = BOSS_TIMING.entrySpeed
        left = self.y - self.stop_y
        # Full speed, then braking into its place over the last `brake_distance`.
        speed = max(entry_speed * 0.2, entry_speed * min(1, left / BOSS_TIMING.brakeDistance))
        self.y = approach(self.y, self.stop_y, speed * dt)
        self.spin += (self.design.spinRate or 0) * dt
        done: bool = self.y == self.stop_y
        return done

    def move(self, _ctx: EnemyContext, dt: float) -> None:
        self._fighting += dt
        sway = self.design.sway
        bob = self.design.bob
        t = self._fighting
        self.x = self.center_x + self.sway_amplitude * math.sin((2 * math.pi * t) / sway.period)
        self.y = self.stop_y + bob.amplitude * math.sin((2 * math.pi * t) / bob.period)
        self.spin += (self.design.spinRate or 0) * dt

    def update_pattern(self, ctx: EnemyContext, dt: float) -> None:
        self._pattern.step(ctx, dt, self._sources())
        self.charge = self._pattern.charge

    def update_rage(self, ctx: EnemyContext, dt: float) -> None:
        """Its bullet hell while it is angry (phase 7 review): its charge lights full on."""
        self._rage.step(ctx, dt, self._sources())
        self.charge = 1

    def on_stage_change(self, stage: int, ctx: EnemyContext) -> None:
        self._pattern = BossPattern(self._stage(stage))
        self._rage = BossPattern(self._armed(self.design.rage or []))
        for ring_id in break_ring_ids(self.design):
            part = self._by_id.get(ring_id)
            if part is None or not part.destroyed or ring_id in self._ringed:
                continue
            # A fuel tank bursts into a ring of bullets (P07-R05).
            self._ringed.append(ring_id)
            ring = self.design.breakRings[ring_id]
            bullet = bullet_spec(ring.bullet)
            for k in range(ring.count):
                ctx.fire_bullet(part.x, part.y, (2 * math.pi * k) / ring.count, bullet)

    def _sources(self) -> VolleySources:
        """The piece a volley fires from, as a function of what fires it."""

        def source(from_: str) -> VolleySource | None:
            return self._source(from_)

        return source

    def _source(self, from_: str) -> VolleySource | None:
        """The piece a volley fires from: the core, or its part while that part stands."""
        if from_ == CORE:
            return self.core
        part = self._by_id.get(from_)
        if part is None or part.destroyed:
            return None
        return part
