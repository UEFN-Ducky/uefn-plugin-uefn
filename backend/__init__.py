"""UEFN — Store desktop plugin (gates core tool modules)."""

from __future__ import annotations


def register(api) -> None:
    """Import gated MCP tools onto the shared FastMCP instance."""
    import backend.tools.actors  # noqa: F401
    import backend.tools.level  # noqa: F401
    import backend.tools.level_viewport  # noqa: F401
    import backend.tools.assets  # noqa: F401
    import backend.tools.assets_pipeline  # noqa: F401
    import backend.tools.device_focused  # noqa: F401
    import backend.tools.device_editor  # noqa: F401
    import backend.tools.data_tables  # noqa: F401
    import backend.tools.editor  # noqa: F401
    import backend.tools.introspection  # noqa: F401
    import backend.tools.ai  # noqa: F401
    import backend.tools.memory  # noqa: F401
    api.log("uefn tools registered")
