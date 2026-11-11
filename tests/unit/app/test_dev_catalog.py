# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/app/dev_catalog.py` (D-199: what each dev viewer lists)."""

from types import SimpleNamespace

import pytest
from helpers.menu_game import make_game

from app import dev_catalog
from app.dev_catalog import (
    car_kinds,
    car_scale,
    dev_groups,
    dev_items,
    dev_labels,
    music_item_id,
    music_request,
)
from app.dev_catalog import dev_catalog as catalog_of
from audio.audio_bindings import AudioBindings, AudioMix, MusicRequest
from audio.audio_types import Track
from config.dev_viewer import DEV_VIEWERS


def game() -> SimpleNamespace:
    base = make_game()
    base.game_levels = [
        SimpleNamespace(id="1-1", scenery="sea"),
        SimpleNamespace(id="1-2", scenery="town"),
    ]
    base.enemy_kinds = [SimpleNamespace(id="hornet", name="Hornet", group="Tier 1")]
    base.boss_kinds = [SimpleNamespace(id="warden", name="Reef Warden")]
    base.view = SimpleNamespace(scenery={"propModels": {}}, audio=None)
    return base


def track_of(request: MusicRequest) -> Track | None:
    """One track per request, but one boss track for every level, and no `over` jingle."""
    if request.kind == "boss":
        return Track("boss-1", 120, 4, [], loop=True)
    if request.kind == "jingle":
        return (
            None
            if request.jingle == "over"
            else Track("jingle-" + str(request.jingle), 120, 4, [], loop=False)
        )
    level = request.level_id or ""
    return Track("menu" if request.kind == "menu" else "level-" + level, 120, 4, [], loop=True)


def with_audio(g: SimpleNamespace) -> SimpleNamespace:
    sounds = {"fire:guns": SimpleNamespace(name="gun-shot"), "hit": SimpleNamespace(name="hit")}
    g.view.audio = AudioBindings(track_of, {}, sounds, 20, AudioMix(1, 1), None)
    return g


@pytest.fixture(autouse=True)
def prop_kinds(monkeypatch: pytest.MonkeyPatch) -> None:
    kinds = {"sea": ["buoy", "hut"], "town": ["hut", "tower"]}
    monkeypatch.setattr(dev_catalog, "level_prop_kinds", lambda scenery: list(kinds[scenery]))
    monkeypatch.setattr(dev_catalog, "car_kinds", lambda _scenery: [])


def test_d199_the_ships_enemies_and_bosses_are_shown_over_the_first_level() -> None:
    """DEV-MENU-12."""
    g = game()
    ships = dev_items(g, "ships")
    assert [(i.id, i.label, i.host) for i in ships] == [("alpha", "Alpha", "1-1")]
    assert [(i.id, i.label, i.group) for i in dev_items(g, "enemies")] == [
        ("hornet", "Hornet", "Tier 1")
    ]
    assert [(i.id, i.label) for i in dev_items(g, "bosses")] == [("warden", "Reef Warden")]


def test_d199_each_prop_is_listed_once_over_the_first_level_that_has_it() -> None:
    """DEV-MENU-15."""
    props = dev_items(game(), "props")
    assert [(i.id, i.host) for i in props] == [("buoy", "1-1"), ("hut", "1-1"), ("tower", "1-2")]


def test_d202_the_props_are_gathered_by_the_games_prop_groups_then_the_others() -> None:
    g = game()
    g.view.scenery["propGroups"] = [
        SimpleNamespace(label="Towers", ids=["tower", "spire"]),
        SimpleNamespace(label="Sea", ids=["buoy", "tower"]),
    ]
    props = dev_items(g, "props")
    assert [(i.id, i.group, i.host) for i in props] == [
        ("tower", "Towers", "1-2"),
        ("buoy", "Sea", "1-1"),
        ("hut", "Other", "1-1"),
    ]


def test_d202_without_prop_groups_every_prop_is_in_other() -> None:
    g = game()
    g.view.scenery["propGroups"] = None
    assert {i.group for i in dev_items(g, "props")} == {"Other"}


def test_d199_the_levels_are_labelled_as_on_the_level_select() -> None:
    levels = dev_items(game(), "levels")
    assert [(i.id, i.label, i.host) for i in levels] == [
        ("1-1", "1-1", "1-1"),
        ("1-2", "1-2", "1-2"),
    ]


def test_d199_a_game_without_bosses_lists_none() -> None:
    g = game()
    g.boss_kinds = None
    assert dev_items(g, "bosses") == []


def test_d199_a_level_missing_from_the_catalog_keeps_its_id_as_label() -> None:
    g = game()
    g.game_levels.append(SimpleNamespace(id="9-9", scenery="sea"))
    assert dev_items(g, "levels")[-1].label == "9-9"


def test_d199_an_unknown_viewer_or_a_game_without_levels_is_an_error() -> None:
    with pytest.raises(ValueError, match="No dev viewer"):
        dev_items(game(), "shots")
    g = game()
    g.game_levels = []
    with pytest.raises(ValueError, match="no level"):
        dev_items(g, "ships")


def test_d199_the_catalog_and_its_labels_cover_every_viewer() -> None:
    catalog = catalog_of(game())
    assert list(catalog) == DEV_VIEWERS
    labels = dev_labels(catalog)
    assert labels["props"] == ["buoy", "hut", "tower"]
    assert labels["ships"] == ["Alpha"]
    groups = dev_groups(catalog)
    assert groups["props"] == ["Other", "Other", "Other"]
    assert groups["ships"] == [""]


def test_d209_the_cars_of_the_levels_are_listed_with_their_props(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cars = {"sea": [], "town": ["van", "hut"]}
    monkeypatch.setattr(dev_catalog, "car_kinds", lambda scenery: cars[scenery])
    monkeypatch.setattr(dev_catalog, "car_scale", lambda _scenery: 0.6)
    g = game()
    g.view.scenery["propGroups"] = [SimpleNamespace(label="Cars", ids=["van"])]
    props = dev_items(g, "props")
    assert [(i.id, i.group, i.host, i.scale) for i in props] == [
        ("van", "Cars", "1-2", 0.6),
        ("buoy", "Other", "1-1", 1),
        ("hut", "Other", "1-1", 1),
        ("tower", "Other", "1-2", 1),
    ]


def test_d209_a_level_without_cars_has_none() -> None:
    level = SimpleNamespace(props=SimpleNamespace(cars=None))
    assert car_kinds(level) == []
    level.props.cars = SimpleNamespace(kinds=["van", "truck"], scale=0.6)
    assert car_kinds(level) == ["van", "truck"]
    assert car_scale(level) == 0.6


# DEV-MENU-19, DEV-MENU-20: the sounds and the music.


def test_dev_menu_19_the_sounds_are_listed_one_per_cue_in_the_games_order() -> None:
    sounds = dev_items(with_audio(game()), "sounds")
    assert [(i.id, i.label, i.host, i.group) for i in sounds] == [
        ("fire:guns", "fire:guns", "1-1", ""),
        ("hit", "hit", "1-1", ""),
    ]


def test_dev_menu_20_the_music_lists_every_track_once_by_group_labelled_by_its_id() -> None:
    """The menu theme, each level's track, a boss track shared by the levels once, the jingles."""
    music = dev_items(with_audio(game()), "music")
    assert [(i.id, i.label, i.group) for i in music] == [
        ("menu", "menu", "Menu"),
        ("level:1-1", "level-1-1", "Levels"),
        ("level:1-2", "level-1-2", "Levels"),
        ("boss:1-1", "boss-1", "Bosses"),
        ("jingle:complete", "jingle-complete", "Jingles"),
        ("jingle:checkpoint", "jingle-checkpoint", "Jingles"),
    ]
    assert all(i.host == "1-1" for i in music)


def test_dev_menu_19_a_game_without_audio_lists_no_sound_and_no_music() -> None:
    assert dev_items(game(), "sounds") == []
    assert dev_items(game(), "music") == []
    catalog = catalog_of(game())
    assert dev_labels(catalog)["music"] == []


@pytest.mark.parametrize(
    ("request_", "item_id"),
    [
        (MusicRequest("menu", None, None), "menu"),
        (MusicRequest("level", "2-3", None), "level:2-3"),
        (MusicRequest("boss", "2-3", None), "boss:2-3"),
        (MusicRequest("jingle", None, "over"), "jingle:over"),
    ],
)
def test_dev_menu_20_a_music_item_id_names_its_request_and_reads_back(
    request_: MusicRequest, item_id: str
) -> None:
    assert music_item_id(request_) == item_id
    read = music_request(item_id)
    assert (read.kind, read.level_id, read.jingle) == (
        request_.kind,
        request_.level_id,
        request_.jingle,
    )


def test_dev_menu_20_a_request_with_no_argument_gives_an_empty_one() -> None:
    assert music_item_id(MusicRequest("level", None, None)) == "level:"
    assert music_item_id(MusicRequest("jingle", None, None)) == "jingle:"
    assert music_request("jingle").jingle is None


def test_dev_menu_13_the_enemies_are_listed_under_their_kind_s_group() -> None:
    """The enemies viewer groups the kinds by tier: a line of buttons per group."""
    g = game()
    g.enemy_kinds = [
        SimpleNamespace(id="hornet", name="Hornet", group="Tier 1"),
        SimpleNamespace(id="wasp", name="Wasp", group="Tier 2"),
    ]
    groups = dev_groups(catalog_of(g))
    assert groups["enemies"] == ["Tier 1", "Tier 2"]
