"""Assert-based smoke for MetaHuman plugin helpers (no UEFN / no frameworks)."""

from __future__ import annotations

from .metahuman import (
    INTENT,
    _assemble_code,
    _can_assemble_code,
    _CAPS_CODE,
    _info_code,
    _normalize_asset_path,
)


def test_normalize_asset_path() -> None:
    assert _normalize_asset_path("MetaHumans/Hero.uasset") == "/Game/MetaHumans/Hero"
    assert _normalize_asset_path("/Game/MetaHumans/Hero") == "/Game/MetaHumans/Hero"
    assert _normalize_asset_path("VideoTest/MetaHumans/Hero") == "/VideoTest/MetaHumans/Hero"
    assert _normalize_asset_path("") == ""


def test_caps_code_mentions_subsystem() -> None:
    assert "MetaHumanCharacterEditorSubsystem" in _CAPS_CODE
    assert "UEFN" in _CAPS_CODE


def test_assemble_code_sets_uefn_pipeline() -> None:
    code = _assemble_code("/Game/MetaHumans/Hero", "high", "HeroUEFN")
    assert "pipeline_type" in code
    assert "build_meta_human" in code
    assert "HeroUEFN" in code


def test_can_assemble_and_info() -> None:
    path = "/Game/MetaHumans/Hero"
    assert "can_build_meta_human" in _can_assemble_code(path)
    assert path in _info_code(path)


def test_intent_matches_metahuman() -> None:
    import re

    assert re.search(INTENT, "create a MetaHuman NPC", re.I)
    assert re.search(INTENT, "mesh to meta human", re.I)


if __name__ == "__main__":
    test_normalize_asset_path()
    test_caps_code_mentions_subsystem()
    test_assemble_code_sets_uefn_pipeline()
    test_can_assemble_and_info()
    test_intent_matches_metahuman()
    print("ok")
