"""verse_digest_changes: what a new Fortnite build added, removed and changed in the Verse API."""

import importlib.util
import os
import time
from pathlib import Path

_spec = importlib.util.spec_from_file_location("digest_changes", os.path.join(os.path.dirname(__file__), "digest_changes.py"))
dc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dc)

OLD_VERSE = """Verse<public> := module:
    @experimental
    # Ordered modifiers.
    modifier_stack<native><public>(t:type) := class(modifier(t)):
        AddModifier<public>(Modifier:modifier(t), Position:rational)<transacts>:cancelable = external {}

    @experimental
    timer<public> := class:
        Start<public>():void = external {}
"""
NEW_VERSE = """Verse<public> := module:
    @experimental
    # Ordered modifiers.
    modifier_stack<native><public>(t:type) := class(modifier(t)):
        AddModifier<public>(Modifier:modifier(t))<transacts>:cancelable = external {}

    timer<public> := class:
        Start<public>():void = external {}

    Perception<public> := module:
        @experimental
        sight_detector_component<native><public> := class<final_super>(component):
            @editable
            var Range<native><public>:float
"""
OLD_FORT = """Cameras<public> := module:
    fort_orbit_camera_modifier<native><public> := class<concrete>(camera_modifier):
        var CameraDistanceCentimeters<public>:float = external {}
"""
NEW_FORT = """Cameras<public> := module:
    @experimental
    fort_boom_arm_camera_modifier<native><public> := class<concrete>(camera_modifier):
        var BoomOffset<public>:vector3 = external {}
"""


def _island(root: Path, name: str, verse: str, fort: str, age_s: float) -> Path:
    folder = root / name / "Digests" / "BuiltIn"
    for rel, text in zip(dc.DIGESTS, (fort, verse, "Engine<public> := module:\n")):
        (folder / rel).parent.mkdir(parents=True, exist_ok=True)
        (folder / rel).write_text(text, encoding="utf-8")
        stamp = time.time() - age_s
        os.utime(folder / rel, (stamp, stamp))
    return folder


def test_a_new_build_lists_new_removed_changed_and_newly_publishable_names(tmp_path):
    root, history = tmp_path / "VerseProject", tmp_path / "history"
    _island(root, "OldIsland", OLD_VERSE, OLD_FORT, age_s=5000)
    _island(root, "NewIsland", NEW_VERSE, NEW_FORT, age_s=10)
    out = dc.changes(root, history)
    assert out["ok"] and out["previous_build"] and out["current"] == "NewIsland"
    assert {r["name"]: r["experimental"] for r in out["added"]} == {
        "fort_boom_arm_camera_modifier": True, "Perception": False, "sight_detector_component": True}
    assert [r["name"] for r in out["removed"]] == ["fort_orbit_camera_modifier"]
    stack = next(r for r in out["changed"] if r["name"] == "modifier_stack")
    assert "Position:rational" in stack["removed"][0] and "Position" not in stack["added"][0]
    assert out["no_longer_experimental"] == ["timer"]
    assert out["counts"] == {"added": 3, "removed": 1, "changed": 1, "no_longer_experimental": 1}

    only = dc.changes(root, history, name_filter="camera")
    assert [r["name"] for r in only["added"]] == ["fort_boom_arm_camera_modifier"] and only["changed"] == []


def test_the_previous_build_is_kept_after_uefn_rewrites_every_island(tmp_path):
    root, history = tmp_path / "VerseProject", tmp_path / "history"
    old = _island(root, "OldIsland", OLD_VERSE, OLD_FORT, age_s=5000)
    _island(root, "NewIsland", NEW_VERSE, NEW_FORT, age_s=10)
    dc.changes(root, history)
    _island(root, "OldIsland", NEW_VERSE, NEW_FORT, age_s=5)  # opened again: now the new build too
    assert dc.fingerprint(old) == dc.fingerprint(root / "NewIsland" / "Digests" / "BuiltIn")
    again = dc.changes(root, history)
    assert again["previous_build"] and [r["name"] for r in again["removed"]] == ["fort_orbit_camera_modifier"]
    assert len([p for p in history.iterdir() if p.is_dir()]) == 2


def test_one_build_or_no_digests_says_so(tmp_path):
    root, history = tmp_path / "VerseProject", tmp_path / "history"
    assert dc.changes(root, history)["ok"] is False
    _island(root, "OnlyIsland", NEW_VERSE, NEW_FORT, age_s=10)
    out = dc.changes(root, history)
    assert out["ok"] and out["previous_build"] is False and "added" not in out
