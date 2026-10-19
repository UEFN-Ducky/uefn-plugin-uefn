"""MetaHuman — Store desktop plugin (UEFN Creator / assemble / NPC skill + tools)."""

from __future__ import annotations

from . import metahuman

PLUGIN_ID = "metahuman"


def register(api) -> None:
    metahuman.register_tools(api)
    api.log("metahuman tools registered")
