"""_find accepts bare ids and the picker's plugin:<pid>:<id> form (Oct 28 2026: 5 of 5 apply failures)."""

import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "verse_plugin", os.path.join(os.path.dirname(__file__), "__init__.py")
)
verse_plugin = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(verse_plugin)


def test_find_accepts_plugin_prefixed_ids():
    rows = [{"id": "player_core", "plugin_id": "uefn"}, {"id": "economy", "plugin_id": "other"}]
    assert verse_plugin._find("player_core", rows) is rows[0]
    assert verse_plugin._find("plugin:uefn:player_core", rows) is rows[0]
    assert verse_plugin._find("plugin:other:player_core", rows) is None
    assert verse_plugin._find("plugin:other:economy", rows) is rows[1]
    assert verse_plugin._find("", rows) is None


if __name__ == "__main__":
    test_find_accepts_plugin_prefixed_ids()
    print("ok")
