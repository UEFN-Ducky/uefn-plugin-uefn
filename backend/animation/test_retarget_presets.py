"""Retarget preset guessing: Biped, Mannequin and Mixamo (any bone prefix)."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_SRC = Path(__file__).resolve().parents[2] / "listener" / "retarget.py"

MIXAMO = ["Hips", "Spine", "Spine1", "Spine2", "Neck", "Head", "LeftShoulder", "LeftArm",
          "LeftForeArm", "LeftHand", "RightShoulder", "RightArm", "RightForeArm", "RightHand",
          "LeftUpLeg", "LeftLeg", "LeftFoot", "RightUpLeg", "RightLeg", "RightFoot"]


@pytest.fixture
def ar(monkeypatch):
    monkeypatch.setitem(sys.modules, "unreal", MagicMock(name="unreal"))
    for name, attrs in {
        "listener.dispatch": {"register": lambda *a, **k: (lambda f: f)},
        "listener.project_paths": {"pin_project_folder": lambda *a, **k: None},
        "listener.serialize": {"rotator_pyr": lambda *a, **k: None},
    }.items():
        mod = types.ModuleType(name)
        mod.__dict__.update(attrs)
        monkeypatch.setitem(sys.modules, name, mod)
    spec = importlib.util.spec_from_file_location("_retarget_under_test", _SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_guess_presets(ar):
    assert ar._guess_preset(["Bip001-Pelvis", "Bip001-Spine"]) == "biped"
    assert ar._guess_preset(["root", "pelvis", "spine_01", "upperarm_l"]) == "mannequin"
    assert ar._guess_preset(["mixamorig:" + b for b in MIXAMO]) == "mixamo"
    assert ar._guess_preset(MIXAMO) == "mixamo"
    assert ar._guess_preset(["Hips", "Spine"]) == "unknown"
    assert ar._guess_preset([]) == "unknown"


def test_mixamo_prefix_applied_to_every_chain_bone(ar):
    preset = ar.RETARGET_CHAIN_PRESETS["mixamo"]
    for prefix in ("mixamorig:", "mixamorig1:", ""):
        bones = [prefix + b for b in MIXAMO]
        assert ar._mixamo_prefix(bones) == prefix
        p = ar._with_prefix(preset, prefix)
        assert p["root"] == prefix + "Hips"
        for c in p["chains"]:
            assert c["start"] in bones and c["end"] in bones, (prefix, c)
    assert ar._with_prefix(preset, None) is preset
    names = {c["name"] for c in preset["chains"]}
    assert names == {c["name"] for c in ar.RETARGET_CHAIN_PRESETS["mannequin"]["chains"]}
