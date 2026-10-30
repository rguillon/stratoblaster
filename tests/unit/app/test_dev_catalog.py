"""Unit tests of `src/app/dev_catalog.py` (D-199: what each dev viewer lists)."""

from types import SimpleNamespace

import pytest
from helpers.menu_game import make_game

from app import dev_catalog
from app.dev_catalog import car_kinds, car_scale, dev_groups, dev_items, dev_labels
from app.dev_catalog import dev_catalog as catalog_of
from config.dev_viewer import DEV_VIEWERS


def game() -> SimpleNamespace:
    base = make_game()
    base.game_levels = [
        SimpleNamespace(id="1-1", scenery="sea"),
        SimpleNamespace(id="1-2", scenery="town"),
    ]
    base.enemy_kinds = [SimpleNamespace(id="gnat", name="Gnat")]
    base.boss_kinds = [SimpleNamespace(id="warden", name="Reef Warden")]
    base.view = SimpleNamespace(scenery={"propModels": {}})
    return base


@pytest.fixture(autouse=True)
def prop_kinds(monkeypatch: pytest.MonkeyPatch) -> None:
    kinds = {"sea": ["buoy", "hut"], "town": ["hut", "tower"]}
    monkeypatch.setattr(dev_catalog, "level_prop_kinds", lambda scenery: list(kinds[scenery]))
    monkeypatch.setattr(dev_catalog, "car_kinds", lambda scenery: [])


def test_d199_the_ships_enemies_and_bosses_are_shown_over_the_first_level() -> None:
    g = game()
    ships = dev_items(g, "ships")
    assert [(i.id, i.label, i.host) for i in ships] == [
        ("alpha", "Alpha", "1-1"),
        ("beta", "Beta", "1-1"),
    ]
    assert [(i.id, i.label) for i in dev_items(g, "enemies")] == [("gnat", "Gnat")]
    assert [(i.id, i.label) for i in dev_items(g, "bosses")] == [("warden", "Reef Warden")]


def test_d199_each_prop_is_listed_once_over_the_first_level_that_has_it() -> None:
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
        dev_items(game(), "sounds")
    g = game()
    g.game_levels = []
    with pytest.raises(ValueError, match="no level"):
        dev_items(g, "ships")


def test_d199_the_catalog_and_its_labels_cover_every_viewer() -> None:
    catalog = catalog_of(game())
    assert list(catalog) == DEV_VIEWERS
    labels = dev_labels(catalog)
    assert labels["props"] == ["buoy", "hut", "tower"]
    assert labels["ships"] == ["Alpha", "Beta"]
    groups = dev_groups(catalog)
    assert groups["props"] == ["Other", "Other", "Other"]
    assert groups["ships"] == ["", ""]


def test_d209_the_cars_of_the_levels_are_listed_with_their_props(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cars = {"sea": [], "town": ["van", "hut"]}
    monkeypatch.setattr(dev_catalog, "car_kinds", lambda scenery: cars[scenery])
    monkeypatch.setattr(dev_catalog, "car_scale", lambda scenery: 0.6)
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
