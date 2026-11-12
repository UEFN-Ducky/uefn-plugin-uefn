"""What changed in the Verse API between the Fortnite build on this PC and the one before it.

UEFN rewrites the digests (a stub of every public Verse declaration) whenever Fortnite
updates. A skill page that names an API can go stale the same day; the digest cannot. This
keeps a copy of each digest set it has seen and compares the newest with the previous one,
so an agent learns the new, removed and changed names without any skill naming a release.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
from pathlib import Path
from typing import Any

DIGESTS = ("Fortnite/Fortnite.digest.verse", "Verse/Verse.digest.verse", "UnrealEngine/UnrealEngine.digest.verse")
KEEP_SETS = 3
_DECL = re.compile(r"^(?:\([^)]*\)\s*)?(?:var(?:<\w+>)?\s+)?([A-Za-z_]\w*)(?:<[^>]*>)*\s*(?:\([^)]*\))?\s*:=\s*(class|module|interface|enum|struct)\b")


def verse_project_root() -> Path:
    base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
    return Path(base) / "UnrealEditorFortnite" / "Saved" / "VerseProject"


def history_root() -> Path:
    base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
    return Path(base) / "UEFN-Ducky" / "verse_digest_history"


def is_set(folder: Path) -> bool:
    return all((folder / rel).is_file() for rel in DIGESTS)


def fingerprint(folder: Path) -> str:
    digest = hashlib.sha1()
    for rel in DIGESTS:
        digest.update((folder / rel).read_bytes())
    return digest.hexdigest()[:16]


def _newest_time(folder: Path) -> float:
    return max((folder / rel).stat().st_mtime for rel in DIGESTS)


def island_sets(root: Path) -> list[Path]:
    """Every island's built-in digest folder, newest first."""
    found = [p for p in root.glob("*/Digests/BuiltIn") if is_set(p)] if root.is_dir() else []
    return sorted(found, key=_newest_time, reverse=True)


def remember(current: Path, history: Path) -> str:
    """Keep a copy of this digest set (once per content) and drop the oldest copies."""
    mark = fingerprint(current)
    dest = history / mark
    if not is_set(dest):
        for rel in DIGESTS:
            (dest / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(current / rel, dest / rel)
    else:
        os.utime(dest)  # most recently seen
    kept = sorted((p for p in history.iterdir() if p.is_dir() and is_set(p)), key=lambda p: p.stat().st_mtime, reverse=True)
    for old in kept[KEEP_SETS:]:
        shutil.rmtree(old, ignore_errors=True)
    return mark


def previous_set(current: Path, history: Path, islands: list[Path]) -> Path | None:
    """The newest digest set whose content differs from ``current``: a kept copy first,
    else another island's folder UEFN has not rewritten since the update."""
    mark = fingerprint(current)
    kept = sorted((p for p in history.iterdir() if p.is_dir() and is_set(p) and p.name != mark),
                  key=lambda p: p.stat().st_mtime, reverse=True) if history.is_dir() else []
    if kept:
        return kept[0]
    for other in islands:
        if other != current and fingerprint(other) != mark:
            return other
    return None


_MEMBER_NAME = re.compile(r"^(?:\([^)]*\)\.)?(?:var(?:<\w+>)?\s+)?(?:\([^)]*\))?([A-Za-z_]\w*)")


def parse(path: Path) -> tuple[dict[str, dict[str, Any]], dict[str, set[str]]]:
    """``(types, members)``: every class/module/interface/enum/struct by qualified name, and
    for each owner the declaration lines directly inside it. A type's ``experimental_members``
    names its members marked ``@experimental`` (an input action, a function)."""
    types: dict[str, dict[str, Any]] = {}
    members: dict[str, set[str]] = {}
    marked: dict[str, set[str]] = {}
    stack: list[tuple[int, str]] = []
    experimental = False
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        text = raw.strip()
        if not text:
            continue
        indent = len(raw) - len(raw.lstrip())
        while stack and stack[-1][0] >= indent:
            stack.pop()
        if text.startswith("#"):
            continue
        if text.startswith("@"):
            experimental = experimental or text.startswith("@experimental")
            continue
        if text.startswith("using "):
            continue
        owner = ".".join(name for _, name in stack)
        found = _DECL.match(text)
        if found:
            name = f"{owner}.{found.group(1)}" if owner else found.group(1)
            types[name] = {"kind": found.group(2), "experimental": experimental}
            stack.append((indent, found.group(1)))
        elif owner:
            members.setdefault(owner, set()).add(text)
            named = _MEMBER_NAME.match(text)
            if experimental and named:
                marked.setdefault(owner, set()).add(named.group(1))
        experimental = False
    for owner, names in marked.items():
        if owner in types:
            types[owner]["experimental_members"] = names
    return types, members


def _short(name: str) -> str:
    return name.rsplit(".", 1)[-1]


def compare(old: Path, new: Path, name_filter: str = "", max_results: int = 60) -> dict[str, Any]:
    """New, removed and changed declarations between two digest sets."""
    want = name_filter.strip().lower()
    cap = max(1, int(max_results))
    added: list[dict[str, Any]] = []
    removed: list[dict[str, Any]] = []
    changed: list[dict[str, Any]] = []
    publishable: list[str] = []
    for rel in DIGESTS:
        old_types, old_members = parse(old / rel)
        new_types, new_members = parse(new / rel)
        digest = rel.split("/")[0]
        for name in sorted(set(new_types) - set(old_types)):
            added.append({"name": _short(name), "kind": new_types[name]["kind"], "in": name.rsplit(".", 1)[0] if "." in name else digest,
                          "experimental": bool(new_types[name]["experimental"])})
        for name in sorted(set(old_types) - set(new_types)):
            removed.append({"name": _short(name), "kind": old_types[name]["kind"], "in": name.rsplit(".", 1)[0] if "." in name else digest})
        for name in sorted(set(new_types) & set(old_types)):
            if old_types[name]["experimental"] and not new_types[name]["experimental"]:
                publishable.append(_short(name))
            still = new_types[name].get("experimental_members", set())
            here = {m.group(1) for line in new_members.get(name, set()) if (m := _MEMBER_NAME.match(line))}
            for member in sorted(old_types[name].get("experimental_members", set())):
                if member not in still and member in here:
                    publishable.append(f"{_short(name)}.{member}")
            gone = sorted(old_members.get(name, set()) - new_members.get(name, set()))
            came = sorted(new_members.get(name, set()) - old_members.get(name, set()))
            if gone or came:
                changed.append({"name": _short(name), "kind": new_types[name]["kind"], "removed": [g[:220] for g in gone[:8]],
                                "added": [c[:220] for c in came[:8]], "more": max(0, len(gone) - 8) + max(0, len(came) - 8)})
    if want:
        def hit(row: dict[str, Any]) -> bool:
            return want in str(row.get("name", "")).lower() or want in str(row.get("in", "")).lower() or any(
                want in line.lower() for line in [*row.get("added", []), *row.get("removed", [])] if isinstance(line, str))

        added, removed, changed = [r for r in added if hit(r)], [r for r in removed if hit(r)], [r for r in changed if hit(r)]
        publishable = [n for n in publishable if want in n.lower()]
    return {
        "counts": {"added": len(added), "removed": len(removed), "changed": len(changed), "no_longer_experimental": len(publishable)},
        "added": added[:cap], "removed": removed[:cap], "changed": changed[:cap], "no_longer_experimental": publishable[:cap],
    }


def changes(root: Path | None = None, history: Path | None = None, name_filter: str = "", max_results: int = 60) -> dict[str, Any]:
    root = root or verse_project_root()
    history = history or history_root()
    islands = island_sets(root)
    if not islands:
        return {"ok": False, "error": "No Verse digests on this PC yet. Open an island in UEFN and run a Verse build, then call this again."}
    current = islands[0]
    history.mkdir(parents=True, exist_ok=True)
    before = previous_set(current, history, islands)
    if before is not None and before.parent != history:
        remember(before, history)  # UEFN rewrites that island's digests the next time it is opened
    remember(current, history)
    if before is not None and before.parent != history:
        before = history / fingerprint(before)
    if before is None:
        return {"ok": True, "previous_build": False, "current": current.parents[1].name,
                "note": "Only one Fortnite build has been seen on this PC, so there is nothing to compare yet. "
                        "The digest is still the truth: read names with get_verse_api / search_verse_digest."}
    out = compare(before, current, name_filter=name_filter, max_results=max_results)
    return {
        "ok": True, "previous_build": True, "current": current.parents[1].name, **out,
        "next": "get_verse_api(name) gives a definition with its doc comments. A removed or changed name no longer "
                "compiles as written before. `experimental: true` means islands that use it cannot be published.",
    }
