# Copyright (c) 2026 Renaud Guillon
"""A world boss (BOSS-07), built from its design."""

import math

from core.entities.boss import Boss
from core.systems.boss_pattern import CORE, BossPattern
from core.systems.enemy_motion import approach
from game.config.bosses.boss_kit import BOSS_TIMING
from game.config.bosses.hidden_weapons import region_blasts
from game.sim.boss_build import (
    angry_pattern,
    armed_pattern,
    boss_stats,
    break_ring_ids,
    bullet_spec,
    launch_volley,
)

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import TYPE_CHECKING, Any

from core.entities.enemy import EnemyContext, EnemySpawnArea
from core.systems.boss_pattern import BossPatternSpec, VolleySource, VolleySources

if TYPE_CHECKING:
    from core.entities.boss_pieces import BossPart
    from core.systems.boss_mounts import BossMount
# A boss design is a config record (`game/config/record.py`), typed as Any there.
BossDesign = Any
# __pragma__ ("noskip")


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
    """A world boss, from its `BossDesign` (BOSS-07): it comes down from above the top edge.

    Braking into its place in the upper part of the screen (BOSS-08), then sways left and right
    (never taking its parts out of the ship's reach at the bottom of the screen, D-048, BOSS-10) and
    bobs. Each stage fires its pattern; its parts' launches go on while they stand. How each boss
    comes in and moves is its boss file's (`specs/bosses/`).
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
        # Its mounts by id, for its volleys to fire from (BOSS-58).
        self._mounts: dict[str, BossMount] = {}
        for mount in self.mounts:
            self._mounts[mount.id] = mount
        # Its angry pattern, from the weapons its last transformation revealed (BOSS-27).
        self._rage = BossPattern([])
        self._rage_form = 0
        self._fighting = 0.0
        self._launches: list[Any] = []
        for launch in design.launches or []:
            self._launches.append(launch_volley(launch))
        self._ringed: list[str] = []
        self._pattern = BossPattern(self._stage(0))
        self._bring_out(self._pattern)

    def _stage(self, stage: int) -> BossPatternSpec:
        """Return the pattern of stage `stage` (BOSS-20): its design's volleys, from their guns.

        And the parts' launches.
        """
        stages = self.design.stages
        volleys = stages[min(stage, len(stages) - 1)] or []
        result: list[Any] = []
        result.extend(self._armed(volleys))
        result.extend(self._launches)
        return result

    def _armed(self, volleys: list[Any]) -> list[Any]:
        """`volleys` from the muzzles of their guns (and turrets)."""
        return armed_pattern(self.design, volleys, self._mounts)

    def update(self, ctx: EnemyContext, dt: float) -> None:
        """Its turrets follow the player as long as it is there.

        Fire pauses included (phase 7 review, BOSS-29). They turn before it fires, so a volley
        leaves its barrels where they are drawn this frame (BOSS-58).
        """
        pattern = self._angry() if self.rage > 0 and self.pause <= 0 else self._pattern
        if self.state != "dying":
            pattern.turn_turrets(ctx, dt, self._sources())
        Boss.update(self, ctx, dt)

    def open_fire(self) -> None:
        """Put it in its place and fight at once, its first volleys due now (a dev viewer's).

        It does not come in; the volleys of its first stage fire as soon as their guns are on aim.
        """
        self.y = self.stop_y
        self.state = "fighting"
        self._pattern.open_fire()

    def enter(self, _ctx: EnemyContext, dt: float) -> bool:
        """Fly in from above the top edge, braking into the stop height."""
        entry_speed: float = BOSS_TIMING.entrySpeed
        left = self.y - self.stop_y
        # Full speed, then braking into its place over the last `brake_distance`.
        speed = max(entry_speed * 0.2, entry_speed * min(1, left / BOSS_TIMING.brakeDistance))
        self.y = approach(self.y, self.stop_y, speed * dt)
        self.spin += (self.design.spinRate or 0) * dt
        done: bool = self.y == self.stop_y
        return done

    def move(self, _ctx: EnemyContext, dt: float) -> None:
        """Advance the boss by `dt` seconds."""
        self._fighting += dt
        sway = self.design.sway
        bob = self.design.bob
        t = self._fighting
        self.x = self.center_x + self.sway_amplitude * math.sin((2 * math.pi * t) / sway.period)
        self.y = self.stop_y + bob.amplitude * math.sin((2 * math.pi * t) / bob.period)
        # Its turning ring (BOSS-34).
        self.spin += (self.design.spinRate or 0) * dt

    def update_pattern(self, ctx: EnemyContext, dt: float) -> None:
        """Run the current pattern of volleys for `dt` seconds."""
        self._pattern.step(ctx, dt, self._sources())
        self.charge = self._pattern.charge

    def _angry(self) -> BossPattern:
        """Its angry pattern: its newest weapons, fresh once it has transformed again."""
        if self._rage_form != self.form:
            self._rage_form = self.form
            self._rage = BossPattern(angry_pattern(self.design, self.form, self._mounts))
            self._bring_out(self._rage)
        return self._rage

    def update_rage(self, ctx: EnemyContext, dt: float) -> None:
        """Its bullet hell while it is angry (BOSS-27): its newest weapons firing all out.

        Its charge lights full on.
        """
        self._angry().step(ctx, dt, self._sources())
        self.charge = 1

    def on_stage_change(self, stage: int, ctx: EnemyContext) -> None:
        """Switch to the volleys of a new stage."""
        self._pattern = BossPattern(self._stage(stage))
        self._bring_out(self._pattern, ctx)
        for ring_id in break_ring_ids(self.design):
            part = self._by_id.get(ring_id)
            if part is None or not part.destroyed or ring_id in self._ringed:
                continue
            # A fuel tank bursts into a ring of bullets (BOSS-23).
            self._ringed.append(ring_id)
            ring = self.design.breakRings[ring_id]
            bullet = bullet_spec(ring.bullet)
            for k in range(ring.count):
                ctx.fire_bullet(part.x, part.y, (2 * math.pi * k) / ring.count, bullet)

    def _bring_out(self, pattern: BossPattern, ctx: EnemyContext | None = None) -> None:
        """Bring out the mounts `pattern` fires from that are not out yet (BOSS-58).

        A gun is only there once the boss uses it: the rotor of its last stage comes out then,
        bursting the hatch over it if it has one (BOSS-37).
        """
        for volley in pattern.volleys:
            mount = volley.mount
            if mount is not None and mount.shown_at is None:
                mount.shown_at = self.age
                if ctx is not None:
                    self._burst_hatches(mount.id, ctx)

    def _burst_hatches(self, mount_id: str, ctx: EnemyContext) -> None:
        """Burst the armour regions over the mount `mount_id` (`armour_region`'s `mount`)."""
        for region in self.design.armour or []:
            if region.mount == mount_id:
                for blast in region_blasts(region, BOSS_TIMING.regionBlasts):
                    ctx.explode(self.x + blast[0], self.y + blast[1], blast[2])

    def _sources(self) -> VolleySources:
        """Return the piece a volley fires from, as a function of what fires it."""

        def source(from_: str) -> VolleySource | None:
            return self._source(from_)

        return source

    def _source(self, from_: str) -> VolleySource | None:
        """Return the piece a volley fires from: the core, or its part (BOSS-21).

        The part only while it stands, once revealed.
        """
        if from_ == CORE:
            return self.core
        part = self._by_id.get(from_)
        if part is None or part.destroyed or part.hidden:
            return None
        return part

    def on_transform(self, form: int, ctx: EnemyContext) -> None:
        """Burst the armour regions it sheds at transformation `form`.

        The weapons beneath come out (BOSS-37).
        """
        for region in self.design.armour or []:
            if region.form == form and region.mount == None:
                for blast in region_blasts(region, BOSS_TIMING.regionBlasts):
                    ctx.explode(self.x + blast[0], self.y + blast[1], blast[2])
        for part in self.parts:
            if part.spec.reveal == form:
                ctx.explode(part.x, part.y, part.radius)
