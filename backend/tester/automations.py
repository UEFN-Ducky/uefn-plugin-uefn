"""Pipeline tiles for live UEFN playtest."""

from __future__ import annotations

from typing import Any


def register_nodes(api: Any) -> None:
    if not hasattr(api, "register_automation_node"):
        return
    api.register_automation_node("uefn.game.start", handle_game_start)
    api.register_automation_node("uefn.player.wait", handle_player_wait)
    api.register_automation_node("uefn.player.teleport", handle_player_teleport)
    api.register_automation_node("uefn.log.expect", handle_log_expect)


def _cfg(ctx: dict[str, Any]) -> dict[str, Any]:
    return ctx.get("config") if isinstance(ctx.get("config"), dict) else {}


def handle_game_start(ctx: dict[str, Any]) -> dict[str, Any]:
    from backend.tools.tester.session_play import start_game

    return start_game()


def handle_player_wait(ctx: dict[str, Any]) -> dict[str, Any]:
    from backend.tools.tester.session_play import wait_for_player

    cfg = _cfg(ctx)
    timeout = float(cfg.get("timeout_sec") or 60.0)
    return wait_for_player(timeout_sec=timeout)


def handle_player_teleport(ctx: dict[str, Any]) -> dict[str, Any]:
    from backend.tools.tester.session_play import teleport_player

    cfg = _cfg(ctx)
    payload = ctx.get("payload") if isinstance(ctx.get("payload"), dict) else {}
    x = cfg.get("x", payload.get("x"))
    y = cfg.get("y", payload.get("y"))
    z = cfg.get("z", payload.get("z"))
    return teleport_player(
        teleporter=str(cfg.get("teleporter") or payload.get("teleporter") or ""),
        actor_label=str(cfg.get("actor_label") or payload.get("actor_label") or ""),
        x=None if x in ("", None) else float(x),
        y=None if y in ("", None) else float(y),
        z=None if z in ("", None) else float(z),
    )


def handle_log_expect(ctx: dict[str, Any]) -> dict[str, Any]:
    from backend.tools.tester.session_play import expect_log

    cfg = _cfg(ctx)
    payload = ctx.get("payload") if isinstance(ctx.get("payload"), dict) else {}
    return expect_log(
        str(cfg.get("regex") or payload.get("regex") or r"\[DUCKY-TEST\]"),
        timeout_sec=float(cfg.get("timeout_sec") or 30.0),
        since_offset=int(cfg.get("since_offset") or payload.get("log_offset") or 0),
    )
