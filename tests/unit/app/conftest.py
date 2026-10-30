"""Shared set-up of the app tests: the JavaScript-only helpers of `src/app/` (URL query, stored
value checks, JSON, Babylon snapshot objects) are replaced by their Python twins from
`helpers.js_shims`, so the logic around them can be tested under CPython."""

from types import SimpleNamespace
from urllib.parse import parse_qs

import pytest
from helpers import js_shims, js_window

from app import (
    debug_options,
    game_play_state,
    saved_choices,
    saved_settings,
    saved_supplies,
    saved_weapons,
)


def _supplies(raw: str):  # noqa: ANN202
    parsed = js_shims.read_supplies(raw)
    return None if parsed is None else SimpleNamespace(**parsed)


def _weapons(raw: str):  # noqa: ANN202
    parsed = js_shims.read_weapon_levels(raw)
    return None if parsed is None else SimpleNamespace(**parsed)


def _weapons_json(weapons):  # noqa: ANN001, ANN202
    return js_shims.to_json({"weapon": weapons.weapon, "levels": weapons.levels})


@pytest.fixture(autouse=True)
def js_twins(monkeypatch: pytest.MonkeyPatch) -> None:
    js_window.install(monkeypatch)
    monkeypatch.setattr(debug_options, "_query_text", js_shims.url_query)
    monkeypatch.setattr(debug_options, "_time_text", js_shims.time_number)
    monkeypatch.setattr(
        debug_options,
        "_has_key",
        lambda search, key: key in parse_qs(search.lstrip("?"), keep_blank_values=True),
    )
    monkeypatch.setattr(saved_choices, "_plain_score", js_shims.plain_score)
    monkeypatch.setattr(saved_settings, "_trimmed", lambda raw: raw.strip())
    monkeypatch.setattr(saved_settings, "_is_step_text", js_shims.step_text)
    monkeypatch.setattr(saved_settings, "_number_of", int)
    monkeypatch.setattr(saved_supplies, "_read_supplies", _supplies)
    monkeypatch.setattr(saved_supplies, "_to_json", lambda s: js_shims.to_json(vars(s)))
    monkeypatch.setattr(saved_weapons, "_read_weapon_levels", _weapons)
    monkeypatch.setattr(
        saved_weapons,
        "_to_json",
        lambda w: js_shims.to_json({"weapon": w.weapon, "levels": w.levels}),
    )
    monkeypatch.setattr(game_play_state, "js_object", js_shims.js_object)
    monkeypatch.setattr(game_play_state, "js_set", js_shims.js_set)
