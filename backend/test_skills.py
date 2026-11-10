"""Every bundled skill is loadable: headers, index entries, and cross-links resolve."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

SKILLS = Path(__file__).resolve().parents[1] / "skills"
PACKS = sorted(p for p in SKILLS.iterdir() if (p / "SKILL.md").is_file())
REFS = sorted(r for p in PACKS for r in (p / "references").glob("*.md"))
LINK = re.compile(r"skill_read_subskill\(\s*(?:pack_id=)?[\"']([\w-]+)[\"']\s*,\s*(?:subskill_id=)?[\"']([\w-]+)[\"']")


def _front(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8").lstrip("﻿")
    assert text.startswith("---"), f"{path}: no frontmatter"
    head = text[3:].split("\n---", 1)
    assert len(head) == 2 and head[1].strip(), f"{path}: frontmatter not closed or body empty"
    out = {}
    for line in head[0].splitlines():
        m = re.match(r"\s*([\w_]+):\s*(.*)", line)
        if m:
            out.setdefault(m.group(1), m.group(2).strip().strip("\"'"))
    return out


def test_found_skills():
    assert PACKS and REFS


@pytest.mark.parametrize("pack", PACKS, ids=lambda p: p.name)
def test_pack_header_and_index(pack: Path):
    front = _front(pack / "SKILL.md")
    assert front.get("name") == pack.name, f"{pack.name}: name is {front.get('name')!r}"
    assert len(front.get("description", "")) >= 20, f"{pack.name}: description too short"
    # Reachable = named by SKILL.md or by another page of the pack (e.g. umg_widgets indexes umg_*).
    refs = list((pack / "references").glob("*.md"))
    texts = {r: r.read_text(encoding="utf-8") for r in refs}
    index = (pack / "SKILL.md").read_text(encoding="utf-8")
    missing = [r.stem for r in refs
               if f"`{r.stem}`" not in index and r.stem not in index
               and not any(f"`{r.stem}`" in t for o, t in texts.items() if o != r)]
    assert not missing, f"{pack.name}: no page names {missing}"


@pytest.mark.parametrize("ref", REFS, ids=lambda r: f"{r.parents[1].name}/{r.stem}")
def test_reference_header(ref: Path):
    front = _front(ref)
    assert len(front.get("description", "")) >= 20, f"{ref}: description missing or too short"


def test_cross_links_resolve():
    names = {p.name for p in PACKS}
    broken = []
    for f in [p / "SKILL.md" for p in PACKS] + REFS:
        for pack, sub in LINK.findall(f.read_text(encoding="utf-8")):
            if pack not in names:
                continue  # pack shipped by the app or another plugin
            if sub != "core" and not (SKILLS / pack / "references" / f"{sub}.md").is_file():
                broken.append(f"{f.relative_to(SKILLS)} -> {pack}/{sub}")
    assert not broken, "\n".join(broken)
