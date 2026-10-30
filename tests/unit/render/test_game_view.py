"""Unit tests of `src/render/game_view.py`: the bindings a game hands to the engine."""

from render.game_view import (
    EnemyBindings,
    EnemyShotFrame,
    GameView,
    GlowLook,
    PropGroup,
    PropTiles,
    SceneryBindings,
    ShotFrame,
)


def test_a_shot_frame_keeps_what_it_was_given() -> None:
    frame = ShotFrame(["p"], ["b"], ["i"], 0.5)
    assert (frame.projectiles, frame.beam, frame.impacts, frame.dt_seconds) == (
        ["p"],
        ["b"],
        ["i"],
        0.5,
    )


def test_an_enemy_shot_frame_keeps_bullets_missiles_and_lasers() -> None:
    frame = EnemyShotFrame(["u"], ["m"], ["l"], 0.25)
    assert (frame.bullets, frame.missiles, frame.lasers, frame.dt_seconds) == (
        ["u"],
        ["m"],
        ["l"],
        0.25,
    )


def test_a_prop_group_leaves_its_optional_fields_out_by_default() -> None:
    group = PropGroup("Rocks", ["rock-1"])
    assert group.label == "Rocks" and group.ids == ["rock-1"]
    assert group.notes is None and group.streets is None


def test_prop_tiles_pieces_are_optional() -> None:
    assert PropTiles("tile", "look").pieces is None


def test_the_game_view_keeps_its_fields_and_leaves_the_optional_ones_out() -> None:
    glow = GlowLook(0.8, 16)
    enemies = EnemyBindings({"drone": "m"}, "shots", "blasts", glow)
    scenery = SceneryBindings("camera", {"lvl": "look"}, {"rock": "m"})
    view = GameView(
        {"ship": "model"},
        2.0,
        {"gun": "renderer"},
        "backdrop",
        scenery,
        enemies,
        "bonuses",
    )

    assert view.player_ship_scale == 2.0
    assert view.enemies.glow is glow
    assert glow.blur_kernel_size == 16
    assert view.scenery.prop_groups is None and view.scenery.prop_tiles is None
    assert view.bombs is None and view.audio is None and view.outline is None
    assert enemies.set_idle_motion is None
