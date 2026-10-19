"""Level Design — Store desktop plugin (gates core tool modules)."""

from __future__ import annotations


def register(api) -> None:
    """Import gated MCP tools onto the shared FastMCP instance."""
    import backend.tools.world.level_design  # noqa: F401
    import backend.tools.world.worldgen  # noqa: F401
    import backend.tools.world.blockout_areas  # noqa: F401
    import backend.tools.world.pcg  # noqa: F401
    import backend.tools.world.fort  # noqa: F401
    api.log("leveldesign tools registered")
