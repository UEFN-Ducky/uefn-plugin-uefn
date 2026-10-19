"""UEFN — Store desktop plugin: every UEFN editor tool, workflow node and skill in one plugin.

The editor tools live in the app (gated on this plugin); the parts below bring their own
tools, listener handlers and workflow nodes. Each part was its own plugin before 1.1.0.
"""

from __future__ import annotations

# Static imports: the compiled build only ships modules it can see imported.
from . import animation, leveldesign, materials, metahuman, modeling, scenegraph, tester, verse, vfx

_PARTS = (leveldesign, modeling, vfx, scenegraph, verse, materials, animation, metahuman, tester)


def register(api) -> None:
    """Import gated MCP tools onto the shared FastMCP instance, then register each part."""
    import backend.tools.uefn.actors  # noqa: F401
    import backend.tools.uefn.level  # noqa: F401
    import backend.tools.uefn.level_viewport  # noqa: F401
    import backend.tools.uefn.assets  # noqa: F401
    import backend.tools.uefn.assets_pipeline  # noqa: F401
    import backend.tools.uefn.data_tables  # noqa: F401
    import backend.tools.uefn.editor  # noqa: F401
    import backend.tools.uefn.introspection  # noqa: F401
    import backend.tools.uefn.ai  # noqa: F401
    import backend.tools.uefn.memory  # noqa: F401
    import backend.tools.uefn.fortnite_client as fortnite_client

    fortnite_client.register_nodes(api)
    for part in _PARTS:
        # One broken part must not take every UEFN tool down (they were separate plugins).
        try:
            part.register(api)
        except Exception as exc:
            api.log(f"uefn part {part.__name__} failed to register: {exc!r}")
    api.log("uefn tools registered")
