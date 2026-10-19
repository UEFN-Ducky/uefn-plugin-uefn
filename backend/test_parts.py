"""UEFN is one plugin made of parts: each part registers, nothing is listed twice, every skill ships."""

from __future__ import annotations

import json
from pathlib import Path

from . import _PARTS

_ROOT = Path(__file__).resolve().parents[1]


def test_every_part_registers_and_manifest_is_clean():
    assert all(callable(getattr(p, "register", None)) for p in _PARTS)
    tools = json.loads((_ROOT / "plugin.json").read_text(encoding="utf-8"))["contributes"]["agent.tools"]["tools"]
    assert len(tools) == len(set(tools))
    skills = sorted(p.name for p in (_ROOT / "skills").iterdir() if p.is_dir())
    assert len(skills) == 16 and all((_ROOT / "skills" / s / "SKILL.md").is_file() for s in skills)
