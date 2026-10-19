"""UEFN Logs (folded into UEFN Testing) — read the real UEFN Output Log and the Fortnite client log.

Verse Print() lines from a live session land in the UEFN Output Log as
``LogVerse: : <text>``. This plugin reads that file straight from disk so
workflows and chat agents can see exactly what the game printed.

Flow in a workflow:
  uefn-logs.mark     remember where the log ends right now (before a session)
  uefn-logs.wait     poll until a regex shows up after the mark (or a FAIL line)
  uefn-logs.capture  grab every matching line after the mark, write it to a
                     file and a ``prompt`` field so a pipeline.agent can read it
"""
from __future__ import annotations

import os
import re
import time

DEFAULT_PATTERN = r"\[ARRIVAL\]|\[PLAYERCORE\]|LogVerse: .*(Error|error|FAIL)|Script error|VerseRuntime"
TAIL_BYTES = 2_000_000


def _sources() -> dict:
    base = os.environ.get("LOCALAPPDATA", "")
    return {
        "editor": os.path.join(base, "UnrealEditorFortnite", "Saved", "Logs", "UnrealEditorFortnite.log"),
        "client": os.path.join(base, "FortniteGame", "Saved", "Logs", "FortniteGame.log"),
    }


def _pick(source: str) -> list[tuple[str, str]]:
    src = _sources()
    names = ["editor", "client"] if source in ("", "both") else [source]
    return [(n, src[n]) for n in names if n in src]


def _size(path: str) -> int:
    try:
        return os.path.getsize(path)
    except OSError:
        return -1


def _read_from(path: str, offset: int) -> str:
    size = _size(path)
    if size < 0:
        return ""
    if offset < 0 or offset > size:
        # No mark, or the log rotated (new UEFN session): read the tail.
        offset = max(0, size - TAIL_BYTES)
    with open(path, "rb") as fh:
        fh.seek(offset)
        return fh.read().decode("utf-8", errors="replace")


def register(api) -> None:
    data = api.data

    def _mark(name: str = "default") -> dict:
        marks = {n: _size(p) for n, p in _pick("both")}
        data.put(f"mark.{_key(name)}", {"name": name, "at": time.time(), "offsets": marks})
        api.changeset.record(
            command="mark", kind="mark", ident=name, facet="offsets",
            slot=f"{api.plugin_id}://mark/{_key(name)}/offsets",
        )
        return {"ok": True, "mark": name, "offsets": marks, "sources": _sources()}

    def _key(name: str) -> str:
        return re.sub(r"[^a-z0-9._-]", "-", (name or "default").lower())[:60] or "default"

    def _offsets(name: str) -> dict:
        row = data.get(f"mark.{_key(name)}") if name else None
        return (row or {}).get("offsets") or {}

    def _grep(pattern: str, source: str, mark: str, max_lines: int) -> dict:
        try:
            rx = re.compile(pattern or DEFAULT_PATTERN)
        except re.error as exc:
            return {"ok": False, "error": f"bad regex: {exc}"}
        offs = _offsets(mark)
        lines: list[str] = []
        missing: list[str] = []
        for name, path in _pick(source):
            if _size(path) < 0:
                missing.append(f"{name}: {path}")
                continue
            text = _read_from(path, int(offs.get(name, -1)))
            for line in text.splitlines():
                if rx.search(line):
                    lines.append(f"[{name}] {line.strip()}")
        if max_lines > 0 and len(lines) > max_lines:
            lines = lines[-max_lines:]
        return {"ok": True, "count": len(lines), "lines": lines, "text": "\n".join(lines),
                "missing_sources": missing, "mark": mark, "pattern": rx.pattern}

    def _capture(pattern: str = "", source: str = "both", mark: str = "default",
                 max_lines: int = 400, artifact_dir: str = "", instructions: str = "") -> dict:
        res = _grep(pattern, source, mark, max_lines)
        if not res.get("ok"):
            return res
        header = instructions or (
            "These are the UEFN Output Log lines captured from the last play session. "
            "Explain step by step what happened, point at the first [ARRIVAL] FAIL / "
            "[PLAYERCORE] TIMEOUT / Verse error, and give the concrete fix."
        )
        body = res["text"] or "(no matching log lines — the game printed nothing that matched; "\
            "check that a player actually joined and that the Verse was pushed)"
        res["prompt"] = f"{header}\n\nPattern: {res['pattern']}\n\n```log\n{body}\n```"
        if artifact_dir:
            try:
                os.makedirs(artifact_dir, exist_ok=True)
                out = os.path.join(artifact_dir, "uefn_log_capture.txt")
                with open(out, "w", encoding="utf-8") as fh:
                    fh.write(body)
                res["files"] = [out]
            except OSError as exc:
                res["file_error"] = str(exc)
        data.put("last.capture", {"at": time.time(), "count": res["count"], "text": res["text"][-20000:]})
        return res

    def _wait(pattern: str, fail_pattern: str = r"\[ARRIVAL\] FAIL|\[PLAYERCORE\] teleport TIMEOUT",
              source: str = "both", mark: str = "default", timeout_sec: float = 180.0,
              poll_sec: float = 1.0) -> dict:
        try:
            ok_rx = re.compile(pattern)
            fail_rx = re.compile(fail_pattern) if fail_pattern else None
        except re.error as exc:
            return {"ok": False, "error": f"bad regex: {exc}"}
        deadline = time.time() + max(1.0, float(timeout_sec))
        seen: list[str] = []
        while True:
            res = _grep(f"({ok_rx.pattern})" + (f"|({fail_rx.pattern})" if fail_rx else ""), source, mark, 0)
            seen = res.get("lines") or []
            hit = next((ln for ln in seen if ok_rx.search(ln)), None)
            bad = next((ln for ln in seen if fail_rx and fail_rx.search(ln)), None)
            if hit:
                return {"ok": True, "found": True, "failed": False, "line": hit, "lines": seen}
            if bad:
                return {"ok": True, "found": False, "failed": True, "line": bad, "lines": seen}
            if time.time() >= deadline:
                return {"ok": True, "found": False, "failed": False, "timed_out": True,
                        "line": "", "lines": seen}
            time.sleep(max(0.2, float(poll_sec)))

    # ---- MCP tools (chat agents) ----
    @api.tool(intent=r"\b(uefn[- ]?logs?|output log|verse print|log(s)? capture)\b")
    def uefn_logs_sources() -> dict:
        """Show which log files are read (UEFN editor log + Fortnite client log) and their sizes."""
        return {"ok": True, "sources": {n: {"path": p, "bytes": _size(p)} for n, p in _pick("both")}}

    @api.tool(intent=r"\b(uefn[- ]?logs?|output log|verse print|log(s)? capture)\b")
    def uefn_logs_mark(name: str = "default") -> dict:
        """Remember the current end of the UEFN / client logs so later captures only show new lines."""
        return _mark(name)

    @api.tool(intent=r"\b(uefn[- ]?logs?|output log|verse print|log(s)? capture)\b")
    def uefn_logs_capture(pattern: str = "", source: str = "both", mark: str = "default",
                          max_lines: int = 400) -> dict:
        """Return UEFN Output Log lines matching a regex (default: [ARRIVAL], [PLAYERCORE], Verse errors) since the mark."""
        return _capture(pattern, source, mark, max_lines)

    @api.tool(intent=r"\b(uefn[- ]?logs?|output log|verse print|log(s)? capture)\b")
    def uefn_logs_wait(pattern: str, fail_pattern: str = r"\[ARRIVAL\] FAIL|\[PLAYERCORE\] teleport TIMEOUT",
                       source: str = "both", mark: str = "default", timeout_sec: float = 180.0) -> dict:
        """Wait until a regex appears in the UEFN log after the mark; stops early on a FAIL line."""
        return _wait(pattern, fail_pattern, source, mark, timeout_sec)

    @api.tool(intent=r"\b(uefn[- ]?logs?|output log|verse print|log(s)? capture)\b")
    def uefn_logs_last() -> dict:
        """Return the last capture made by a workflow or tool."""
        return {"ok": True, "last": data.get("last.capture") or {}}

    # ---- Workflow nodes ----
    def _cfg(ctx: dict) -> dict:
        return ctx.get("config") or {}

    @api.register_pipeline_node("uefn-logs.mark")
    def node_mark(ctx: dict) -> dict:
        return _mark(str(_cfg(ctx).get("mark") or "default"))

    @api.register_pipeline_node("uefn-logs.wait")
    def node_wait(ctx: dict) -> dict:
        c = _cfg(ctx)
        return _wait(
            str(c.get("pattern") or r"\[ARRIVAL\]"),
            str(c.get("fail_pattern") if c.get("fail_pattern") is not None else r"\[ARRIVAL\] FAIL|\[PLAYERCORE\] teleport TIMEOUT"),
            str(c.get("source") or "both"),
            str(c.get("mark") or "default"),
            float(c.get("timeout_sec") or 180),
        )

    @api.register_pipeline_node("uefn-logs.capture")
    def node_capture(ctx: dict) -> dict:
        c = _cfg(ctx)
        return _capture(
            str(c.get("pattern") or ""),
            str(c.get("source") or "both"),
            str(c.get("mark") or "default"),
            int(c.get("max_lines") or 400),
            str(ctx.get("artifact_dir") or ""),
            str(c.get("instructions") or ""),
        )

    api.log("uefn-logs tools + workflow nodes registered")
