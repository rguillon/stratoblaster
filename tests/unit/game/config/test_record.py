# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/record.py`."""

from game.config.record import concat, field, fields_of, merge, record


def test_record_fields_read_as_attributes_and_missing_fields_read_as_none() -> None:
    """ENG-160: read by attribute in CPython as in the browser."""
    r = record({"a": 1, "nested": {"b": 2}})
    assert r.a == 1
    assert r.nested.b == 2
    assert r.absent is None


def test_record_keeps_dicts_inside_lists_as_records() -> None:
    r = record({"rows": [{"x": 3}]})
    assert r.rows[0].x == 3


def test_merge_sets_extra_fields_over_a_copy_of_the_base() -> None:
    base = {"a": 1, "b": 2}
    out = merge(base, {"b": 3, "c": 4})
    assert (out.a, out.b, out.c) == (1, 3, 4)
    assert base == {"a": 1, "b": 2}


def test_merge_with_no_extra_is_a_copy() -> None:
    assert merge({"a": 1}, None).a == 1


def test_concat_joins_lists_into_a_new_list() -> None:
    a = [1]
    assert concat(a, [2, 3], []) == [1, 2, 3]
    assert a == [1]


def test_field_reads_a_key_or_the_default() -> None:
    assert field({"k": 5}, "k", 0) == 5
    assert field({"k": 5}, "missing", 9) == 9
    assert field(record({"k": 5}), "k", 0) == 5


def test_fields_of_copies_the_fields_of_a_record_or_of_an_object() -> None:
    r = record({"a": 1, "b": {"c": 2}})
    fields = fields_of(r)
    assert fields == {"a": 1, "b": {"c": 2}}
    fields["a"] = 5
    assert r.a == 1

    class Plain:
        def __init__(self) -> None:
            self.x = 3
            self.y = "y"

    assert fields_of(Plain()) == {"x": 3, "y": "y"}
