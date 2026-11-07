# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/bosses/world_boss.py`: a world boss's gun mounts (BOSS-58)."""

import math
from typing import Any

import pytest
from helpers.enemy_steps import area
from helpers.fakes import FakeContext

from core.entities.muzzle import PlanePoint, RaisedPoint
from core.systems.boss_mounts import BossMount
from game.config.bosses.boss_kit import BOSS_TIMING
from game.config.bosses.final_bosses import GULL_MOTHERSHIP
from game.config.bosses.hidden_weapons import armour_region, region_blasts
from game.config.record import merge
from game.sim.boss_kinds import BOSS_DESIGNS
from game.sim.bosses.world_boss import WorldBoss

# The World 1 bosses: the mini and final boss of each of its five levels (BOSS-01).
WORLD_1 = BOSS_DESIGNS[:10]

# How close (px, radians) a shot is to a barrel's tip and way to leave it.
CLOSE = 1e-6

STEP = 1 / 30

# How long the fight stays at each stage.
STAGE_SECONDS = 16


def _same_way(a: float, b: float) -> bool:
    return abs(math.remainder(a - b, 2 * math.pi)) < CLOSE


def _near(x: float, y: float, point: PlanePoint | RaisedPoint) -> bool:
    return math.hypot(x - point.x, y - point.y) < CLOSE


class _GunCheck(FakeContext):
    """A world that checks, as each shot is fired, that it leaves one of the boss's barrels."""

    def __init__(self, boss: WorldBoss) -> None:
        super().__init__()
        self.boss = boss
        # The shots that left no barrel, by kind, and where; the mounts the others left.
        self.strays: list[tuple[str, float, float]] = []
        self.used: set[str] = set()

    def _barrels(self, kind: str) -> list[tuple[BossMount, Any, Any]]:
        """Return the barrels of its mounts of `kind` whose pieces stand, and those pieces."""
        result: list[tuple[BossMount, Any, Any]] = []
        for mount in self.boss.mounts:
            source = self.boss._source(mount.spec.piece)
            if mount.kind != kind or source is None:
                continue
            result.extend((mount, source, barrel) for barrel in mount.barrels)
        return result

    def _ring_burst(self, x: float, y: float) -> bool:
        """Whether a bullet at (`x`, `y`) is a fuel tank's ring as it bursts (not a gun's)."""
        rings = self.boss.design.breakRings or {}
        return any(
            part.spec.id in rings and part.destroyed and _near(x, y, PlanePoint(part.x, part.y))
            for part in self.boss.parts
        )

    def fire_bullet(self, x: float, y: float, heading: float, spec: Any) -> None:
        super().fire_bullet(x, y, heading, spec)
        if self._ring_burst(x, y):
            return
        for mount, source, barrel in self._barrels("gun"):
            tip = self.seen(mount.tip(source, barrel))
            if _near(x, y, tip) and _same_way(heading, mount.heading_of(source, barrel)):
                self.used.add(mount.id)
                return
        self.strays.append(("bullet", x, y))

    def fire_missile(
        self, x: float, y: float, heading: float, spec: Any, height: float = 0
    ) -> None:
        super().fire_missile(x, y, heading, spec, height)
        for mount, source, barrel in self._barrels("missile"):
            mouth = mount.tip(source, barrel)
            if _near(x, y, mouth) and height in (0, mouth.height):
                self.used.add(mount.id)
                return
        self.strays.append(("missile", x, y))

    def fire_laser(self, owner: Any, spec: Any) -> None:
        super().fire_laser(owner, spec)
        emitter = owner.emitter
        for mount, source, barrel in self._barrels("laser"):
            lens = mount.tip(source, barrel)
            same = _same_way(owner.heading, mount.heading_of(source, barrel))
            if _near(emitter.x, emitter.y, lens) and same:
                self.used.add(mount.id)
                return
        self.strays.append(("laser", emitter.x, emitter.y))


# The fights so far, by boss id: each World 1 boss is fought once for the tests that look at it.
_FIGHTS: dict[str, tuple[WorldBoss, _GunCheck]] = {}


def _fought(design: Any) -> tuple[WorldBoss, _GunCheck]:
    """Return the boss of `design` once fought (see `_fight`), and the world it fought in."""
    if design.id not in _FIGHTS:
        _FIGHTS[design.id] = _fight(design)
    return _FIGHTS[design.id]


def _fight(design: Any) -> tuple[WorldBoss, _GunCheck]:
    """Fight `design` in place: `STAGE_SECONDS` at each stage, then its next part broken.

    Until it dies.
    """
    boss = WorldBoss(design, area(width=480, height=640))
    ctx = _GunCheck(boss)
    boss.open_fire()
    t = 0.0
    for _ in range(40):
        for _ in range(int(STAGE_SECONDS / STEP)):
            t += STEP
            # The player weaves along the bottom of the screen.
            ctx.player_x = 240 + 180 * math.sin(t / 1.3)
            ctx.player_y = 60 + 30 * math.sin(t / 0.7)
            boss.age += STEP
            boss.update(ctx, STEP)
        if boss.state == "dying":
            break
        boss.break_next()
    return boss, ctx


@pytest.mark.parametrize("design", WORLD_1, ids=[d.id for d in WORLD_1])
def test_boss_58_every_shot_of_a_world_1_boss_fight_leaves_one_of_its_barrels(design: Any) -> None:
    """Also BOSS-29: its turrets' barrels point the way their shots go as they fire."""
    boss, ctx = _fought(design)
    assert boss.state == "dying"
    assert ctx.bullets or ctx.missiles or ctx.lasers
    assert ctx.strays == []


@pytest.mark.parametrize("design", WORLD_1, ids=[d.id for d in WORLD_1])
def test_boss_58_every_world_1_boss_mount_comes_out_and_fires_in_its_fight(design: Any) -> None:
    """Also WPN-03, WPN-07: a gun's barrel that fires recoils, a port that launches reloads."""
    boss, ctx = _fought(design)
    for mount in boss.mounts:
        assert mount.shown_at is not None, mount.id
        assert mount.id in ctx.used
        if mount.kind != "laser":
            assert any(barrel.fired_at is not None for barrel in mount.barrels), mount.id


def test_boss_58_open_fire_puts_the_boss_in_place_its_first_volleys_due_now() -> None:
    design = WORLD_1[0]
    boss = WorldBoss(design, area(width=480, height=640))
    assert boss.y > boss.stop_y
    boss.open_fire()
    assert (boss.y, boss.state) == (boss.stop_y, "fighting")
    ctx = FakeContext()
    for _ in range(30):
        boss.age += STEP
        boss.update(ctx, STEP)
    assert ctx.bullets


def _hatched_gull() -> Any:
    """Return the Gull Mothership with a hatch over its tail rotor, which its 4th stage uses."""
    hatch = armour_region("tail-hatch", None, [[-4, 27], [4, 27], [4, 35], [-4, 35]], "ring")
    other = armour_region("spine-hatch", None, [[-4, 7], [4, 7], [4, 15]], "ring", None, False)
    other = merge(other, {"mount": "nowhere"})
    hatch = merge(hatch, {"mount": "tail-rotor"})
    return merge(GULL_MOTHERSHIP, {"armour": [*(GULL_MOTHERSHIP.armour or []), hatch, other]})


def _rotor(boss: WorldBoss, mount_id: str) -> BossMount:
    return next(mount for mount in boss.mounts if mount.id == mount_id)


def test_boss_58_a_mount_comes_out_only_with_the_first_stage_that_fires_from_it() -> None:
    boss = WorldBoss(GULL_MOTHERSHIP, area(width=480, height=640))
    boss.age = 3.0
    rotor = _rotor(boss, "tail-rotor")
    assert rotor.shown_at is None
    assert _rotor(boss, "flak-left").shown_at == 0
    ctx = FakeContext()
    boss.on_stage_change(3, ctx)
    assert rotor.shown_at == 3.0
    boss.age = 5.0
    boss.on_stage_change(3, ctx)
    # Once out, it stays.
    assert rotor.shown_at == 3.0


def test_boss_58_a_hatch_over_a_mount_bursts_as_the_boss_first_fires_from_it() -> None:
    """Also BOSS-37: its blasts, as a transformation's armour; a hatch over another gun stays."""
    design = _hatched_gull()
    boss = WorldBoss(design, area(width=480, height=640))
    ctx = FakeContext()
    boss.on_stage_change(1, ctx)
    assert ctx.explosions == []
    boss.on_stage_change(3, ctx)
    hatch = next(region for region in design.armour if region.id == "tail-hatch")
    blasts = region_blasts(hatch, BOSS_TIMING.regionBlasts)
    assert blasts
    assert ctx.explosions == [(boss.x + b[0], boss.y + b[1], b[2]) for b in blasts]
    boss.on_stage_change(3, ctx)
    assert len(ctx.explosions) == len(blasts)


def test_boss_58_a_boss_without_armour_bursts_no_hatch() -> None:
    boss = WorldBoss(merge(GULL_MOTHERSHIP, {"armour": None}), area(width=480, height=640))
    ctx = FakeContext()
    boss.on_stage_change(3, ctx)
    assert ctx.explosions == []
    assert _rotor(boss, "tail-rotor").shown_at is not None
