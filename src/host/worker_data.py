"""Plain data for the browser's worker messages (P13-R03).

`postMessage` copies its message (structured clone), and a function cannot be copied: Transcrypt
class instances carry their class as an own function property (`__class__`), so a level or a
ground posted as it is fails with "Function object could not be cloned". `to_plain` makes a copy
of the data alone: the fields of every object, with the shared references kept (a road referenced
twice is one copy, as the clone would keep it).
"""

from org.transcrypt.stubs.browser import __pragma__


def to_plain(value: object) -> object:
    """A copy of `value` as plain data: objects and arrays, without functions or class markers."""
    out: object = None
    __pragma__(
        "js",
        "{}",
        """
    var seen = new Map();
    var copy = function (v) {
        if (v === null || typeof v !== 'object') {
            return typeof v === 'function' ? undefined : v;
        }
        if (ArrayBuffer.isView(v)) {
            return v;
        }
        if (seen.has(v)) {
            return seen.get(v);
        }
        if (Array.isArray(v)) {
            var list = [];
            seen.set(v, list);
            for (var i = 0; i < v.length; i++) {
                list.push(copy(v[i]));
            }
            return list;
        }
        var obj = {};
        seen.set(v, obj);
        for (var key of Object.keys(v)) {
            if (key === '__class__' || typeof v[key] === 'function') {
                continue;
            }
            obj[key] = copy(v[key]);
        }
        return obj;
    };
    out = copy(value);
    """,
    )
    return out
