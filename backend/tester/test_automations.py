"""Tester pipeline tiles — catalog + register, no app imports."""

from __future__ import annotations

import json
from pathlib import Path

from . import automations, logs


def test_plugin_json_lists_playtest_nodes():
    data = json.loads((Path(__file__).resolve().parents[2] / "plugin.json").read_text(encoding="utf-8"))
    ids = {n["id"] for n in data["contributes"]["automations"]["nodes"]}
    assert ids == {
        "uefn.client.wait",
        "uefn.client.capture",
        "uefn.client.move",
        "uefn.game.start",
        "uefn.player.wait",
        "uefn.player.teleport",
        "uefn.log.expect",
        "uefn-logs.mark",
        "uefn-logs.wait",
        "uefn-logs.capture",
    }
    tools = set(data["contributes"]["agent.tools"]["tools"])
    assert {"uefn_logs_sources", "uefn_logs_mark", "uefn_logs_capture", "uefn_logs_wait", "uefn_logs_last"} <= tools
    for tpl in data["contributes"]["automations"]["templates"]:
        assert {n["type"] for n in tpl["graph"]["nodes"] if n["type"].startswith("uefn-logs.")} <= ids


class _LogsApi:
    plugin_id = "tester"

    def __init__(self):
        self.store: dict = {}
        self.tools: dict = {}
        self.nodes: dict = {}
        self.data = type("D", (), {"get": lambda _s, k: self.store.get(k), "put": lambda _s, k, v: self.store.__setitem__(k, v)})()
        self.changeset = type("C", (), {"record": lambda _s, **_k: None})()

    def tool(self, **_k):
        return lambda fn: self.tools.setdefault(fn.__name__, fn)

    def register_pipeline_node(self, name):
        return lambda fn: self.nodes.setdefault(name, fn)

    def log(self, _msg):
        pass


def test_logs_capture_only_lines_after_mark(tmp_path, monkeypatch):
    editor, client = tmp_path / "editor.log", tmp_path / "client.log"
    editor.write_text("LogVerse: : [ARRIVAL] old run\n", encoding="utf-8")
    monkeypatch.setattr(logs, "_sources", lambda: {"editor": str(editor), "client": str(client)})
    api = _LogsApi()
    logs.register(api)
    assert set(api.nodes) == {"uefn-logs.mark", "uefn-logs.wait", "uefn-logs.capture"}

    api.tools["uefn_logs_mark"]("run1")
    with editor.open("a", encoding="utf-8") as fh:
        fh.write("LogVerse: : [ARRIVAL] OK spawn\nLogVerse: : [ARRIVAL] FAIL gate\n")

    got = api.tools["uefn_logs_capture"](mark="run1")
    assert got["count"] == 2 and "old run" not in got["text"]
    assert got["missing_sources"] and "client" in got["missing_sources"][0]
    hit = api.tools["uefn_logs_wait"](r"OK spawn", mark="run1", timeout_sec=1)
    assert hit["found"] is True
    bad = api.tools["uefn_logs_wait"](r"never printed", mark="run1", timeout_sec=1)
    assert bad["failed"] is True and "FAIL gate" in bad["line"]


def test_register_nodes():
    names: list[str] = []

    class Api:
        def register_automation_node(self, name, _fn):
            names.append(name)

    automations.register_nodes(Api())
    assert names == [
        "uefn.game.start",
        "uefn.player.wait",
        "uefn.player.teleport",
        "uefn.log.expect",
    ]
