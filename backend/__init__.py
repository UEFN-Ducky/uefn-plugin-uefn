"""UEFN — Store desktop plugin (gates core tool modules)."""

from __future__ import annotations


def register(api) -> None:
    """Import gated MCP tools onto the shared FastMCP instance."""
    import backend.tools.uefn.actors  # noqa: F401
    import backend.tools.uefn.level  # noqa: F401
    import backend.tools.uefn.level_viewport  # noqa: F401
    import backend.tools.uefn.assets  # noqa: F401
    import backend.tools.uefn.assets_pipeline  # noqa: F401
    import backend.tools.uefn.device_focused  # noqa: F401
    import backend.tools.uefn.device_editor  # noqa: F401
    import backend.tools.uefn.data_tables  # noqa: F401
    import backend.tools.uefn.editor  # noqa: F401
    import backend.tools.uefn.introspection  # noqa: F401
    import backend.tools.uefn.ai  # noqa: F401
    import backend.tools.uefn.memory  # noqa: F401
    api.log("uefn tools registered")
