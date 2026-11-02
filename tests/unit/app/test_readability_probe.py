# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/app/readability_probe.py`."""
# adability_probe.py` (DEV-API-09): where each kind of object is on the playfield, and which of them
# is in view. The pixel reads need the render layer and are not run here.

import asyncio
import math
from types import SimpleNamespace
from typing import Any

import pytest
from helpers import js_shims
from helpers.render_fakes import FakeVector, patch_babylon

from app import readability_probe
from app.readability_probe import (
    Spot,
    _first_in_view,
    _pixel_box,
    _read_frame,
    _spots_of,
    probe_readability,
)
from config.game_play import GAME_PLAY_CONFIG
from core.math.pixel_contrast import Pixels

CFG = GAME_PLAY_CONFIG.readability_probe

# The fake screen: 4 x 4 pixels, RGBA bytes.
SIZE = 4
WHITE = [255 for _ in range(SIZE * SIZE * 4)]
BLACK = [0 if i % 4 < 3 else 255 for i in range(SIZE * SIZE * 4)]


def everything_in_view(_x: float, _y: float) -> bool:
    return True


def nothing_in_view(_x: float, _y: float) -> bool:
    return False


def test_dev_api_09_the_first_item_wholly_in_view_is_the_one_measured() -> None:
    items = [SimpleNamespace(x=500, y=500, radius=5), SimpleNamespace(x=10, y=20, radius=5)]
    spot = _first_in_view(items, lambda x, _y: x < 100, lambda item: item.radius)
    assert spot is not None
    assert (spot.x, spot.y, spot.radius) == (10, 20, 5)


def test_dev_api_09_an_item_with_its_margin_outside_the_view_is_skipped() -> None:
    items = [SimpleNamespace(x=0, y=0, radius=5)]
    assert _first_in_view(items, nothing_in_view, lambda item: item.radius) is None


def test_dev_api_09_the_spots_are_the_ship_and_the_first_of_each_kind_in_view() -> None:
    run = SimpleNamespace(
        ship=SimpleNamespace(x=100, y=50),
        enemies=SimpleNamespace(
            enemies=[SimpleNamespace(x=200, y=300, radius=12, model="gnat")],
            shots=SimpleNamespace(
                bullets=[
                    SimpleNamespace(alive=False, x=1, y=1, radius=2),
                    SimpleNamespace(alive=True, x=150, y=200, radius=3),
                ]
            ),
        ),
        shots=SimpleNamespace(
            projectiles=[
                SimpleNamespace(alive=True, x=100, y=60),  # over the ship: not measured
                SimpleNamespace(alive=True, x=110, y=200),
            ]
        ),
    )
    spots = _spots_of(run, everything_in_view)
    assert (spots.player.x, spots.player.y, spots.player.radius) == (100, 50, CFG.ship_radius)
    assert spots.enemy is not None
    assert spots.enemy.radius == 12
    # The measured enemy's model, to tell which one fails.
    assert spots.enemy_model == "gnat"
    assert spots.enemy_bullet is not None
    assert spots.enemy_bullet.radius == 3
    assert isinstance(spots.player_shot, Spot)
    assert spots.player_shot.radius == CFG.shot_radius


def test_dev_api_09_nothing_is_measured_when_nothing_is_in_view() -> None:
    run = SimpleNamespace(
        ship=SimpleNamespace(x=0, y=0),
        enemies=SimpleNamespace(
            enemies=[SimpleNamespace(x=5, y=5, radius=1)],
            shots=SimpleNamespace(bullets=[]),
        ),
        shots=SimpleNamespace(projectiles=[]),
    )
    spots = _spots_of(run, nothing_in_view)
    assert spots.enemy is None
    assert spots.enemy_bullet is None
    assert spots.player_shot is None


class FakeEngine:
    """The engine's canvas: `readPixels` gives the next image, as a promise does."""

    def __init__(self, images: list[list[int]], playfield: Any = None) -> None:
        self._images = images
        self._playfield = playfield
        self.reads: list[tuple[int, int, int, int]] = []
        # Whether the playfield was shown at each read.
        self.shown: list[bool] = []

    def getRenderWidth(self) -> int:
        return SIZE

    def getRenderHeight(self) -> int:
        return SIZE

    async def readPixels(self, x: int, y: int, width: int, height: int) -> list[int]:
        self.reads.append((x, y, width, height))
        if self._playfield is not None:
            self.shown.append(self._playfield.enabled)
        image = self._images.pop(0)
        if len(image) == 0:
            msg = "lost context"
            raise RuntimeError(msg)
        return image


class FakeCamera:
    """The active camera: its viewport, the whole screen."""

    def __init__(self) -> None:
        self.viewport = SimpleNamespace(toGlobal=lambda width, height: ("viewport", width, height))


class FakeScene:
    def __init__(self, engine: FakeEngine, camera: FakeCamera | None) -> None:
        self._engine = engine
        self.activeCamera = camera
        self.renders = 0

    def getEngine(self) -> FakeEngine:
        return self._engine

    def render(self) -> None:
        self.renders += 1

    def getTransformMatrix(self) -> str:
        return "view-projection"


class FakePlayfield:
    """The playfield layer's root: moved 1 to the right in the world."""

    def __init__(self) -> None:
        self.enabled = True

    def setEnabled(self, on: bool) -> None:
        self.enabled = on

    def getWorldMatrix(self) -> str:
        return "world"


class FakeVector3Class:
    """`BABYLON.Vector3`: the world matrix moves points 1 to the right, the projection doubles."""

    def __init__(self) -> None:
        self.projected: list[tuple[Any, ...]] = []

    def TransformCoordinates(self, point: FakeVector, world: str) -> FakeVector:
        assert world == "world"
        return FakeVector(point.x + 1, point.y, point.z)

    def Project(
        self, point: FakeVector, identity: str, transform: str, viewport: Any
    ) -> FakeVector:
        self.projected.append((identity, transform, viewport))
        return FakeVector(point.x * 2, point.y * 2, 0)


@pytest.fixture
def babylon(monkeypatch: pytest.MonkeyPatch) -> FakeVector3Class:
    """Replace the Babylon helpers and classes the probe uses, and the browser's `Math.hypot`."""
    patch_babylon(monkeypatch, readability_probe)
    vector = FakeVector3Class()
    classes = {"Vector3": vector, "Matrix": SimpleNamespace(IdentityReadOnly="identity")}
    monkeypatch.setattr(readability_probe, "babylon_class", lambda name: classes[name])
    monkeypatch.setattr(readability_probe, "js_object", js_shims.js_object)
    monkeypatch.setattr(readability_probe, "js_set", js_shims.js_set)
    monkeypatch.setattr(
        readability_probe, "window", SimpleNamespace(Math=SimpleNamespace(hypot=math.hypot))
    )
    return vector


def test_dev_api_09_a_frame_is_drawn_then_read_back_whole() -> None:
    engine = FakeEngine([WHITE])
    scene = FakeScene(engine, FakeCamera())
    frame = asyncio.run(_read_frame(scene))
    assert isinstance(frame, Pixels)
    assert (frame.width, frame.height, frame.data) == (SIZE, SIZE, WHITE)
    assert engine.reads == [(0, 0, SIZE, SIZE)]
    assert scene.renders == 1


def test_dev_api_09_a_spot_is_projected_to_a_box_of_webgl_rows(babylon: FakeVector3Class) -> None:
    scene = FakeScene(FakeEngine([]), FakeCamera())
    box = _pixel_box(scene, FakePlayfield(), Spot(1, 0.5, 1))
    # Centre (1, 0.5) -> world (2, 0.5) -> screen (4, 1); its edge (2, 0.5) -> (6, 1).
    assert (box.x, box.y, box.radius) == (4, SIZE - 1 - 1, 2)
    assert babylon.projected == [("identity", "view-projection", ("viewport", SIZE, SIZE))] * 2


def test_dev_api_09_a_box_is_at_least_one_pixel_across(babylon: FakeVector3Class) -> None:
    del babylon
    scene = FakeScene(FakeEngine([]), FakeCamera())
    assert _pixel_box(scene, FakePlayfield(), Spot(0, 0, 0.1)).radius == 1


def test_dev_api_09_a_level_without_a_camera_cannot_be_measured(
    babylon: FakeVector3Class,
) -> None:
    del babylon
    scene = FakeScene(FakeEngine([]), None)
    with pytest.raises(ValueError, match="no camera"):
        _pixel_box(scene, FakePlayfield(), Spot(0, 0, 1))


def _run_with_an_enemy() -> SimpleNamespace:
    return SimpleNamespace(
        ship=SimpleNamespace(x=1, y=0.5),
        enemies=SimpleNamespace(
            enemies=[SimpleNamespace(x=0.5, y=1, radius=0.5, model="gnat")],
            shots=SimpleNamespace(bullets=[]),
        ),
        shots=SimpleNamespace(projectiles=[]),
    )


def test_dev_api_09_the_report_compares_the_frame_with_the_background_alone(
    babylon: FakeVector3Class,
) -> None:
    """Also GFX-READ-01 (the background's brightest pixels)."""
    del babylon
    playfield = FakePlayfield()
    engine = FakeEngine([WHITE, BLACK], playfield)
    scene = FakeScene(engine, FakeCamera())
    report = asyncio.run(
        probe_readability(scene, playfield, _run_with_an_enemy(), everything_in_view, 0.1)
    )
    # The frame with the playfield, then the background without it; drawn again as it was.
    assert engine.shown == [True, False]
    assert playfield.enabled is True
    assert scene.renders == 3
    # White on black: the highest contrast there is.
    assert report["player"] == pytest.approx(21)
    assert report["enemy"] == pytest.approx(21)
    assert report["enemyModel"] == "gnat"
    assert report["enemyBullet"] is None
    assert report["playerShot"] is None
    assert report["backgroundLuminance"] == 0


def test_dev_api_09_the_playfield_is_shown_again_when_the_background_read_fails(
    babylon: FakeVector3Class,
) -> None:
    del babylon
    playfield = FakePlayfield()
    engine = FakeEngine([WHITE, []], playfield)
    scene = FakeScene(engine, FakeCamera())
    with pytest.raises(RuntimeError, match="lost context"):
        asyncio.run(probe_readability(scene, playfield, _run_with_an_enemy(), nothing_in_view, 0.1))
    assert engine.shown == [True, False]
    assert playfield.enabled is True
