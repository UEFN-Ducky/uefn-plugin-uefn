"""Materials — UEFN material create / graph / instance tools (Store plugin)."""

from __future__ import annotations

import json
from typing import Any, Optional

PLUGIN_ID = "materials"

_INTENT = (
    r"\b(material|shader|mi_|material\s*instance|base\s*color|emissive|"
    r"material\s*graph|material\s*node|blend\s*mode|two[\s-]?sided|roughness|metallic)\b"
)

# Keep in sync with listener registry + dynamic_tools._NEVER_EXPOSE.
MATERIAL_TOOL_NAMES = (
    "create_material",
    "create_material_instance",
    "duplicate_material",
    "connect_material_nodes",
    "disconnect_material_nodes",
    "connect_material_output",
    "add_material_expression",
    "delete_material_expression",
    "clear_material_expressions",
    "set_material_expression_property",
    "get_material_expression_info",
    "get_material_info",
    "set_material_flags",
    "layout_material_expressions",
    "list_material_expressions",
    "list_uefn_material_expression_classes",
    "assign_material_to_mesh",
    "set_material_instance_scalar",
    "set_material_instance_vector",
    "set_material_instance_texture",
    "recompile_material",
)


def _json(api: Any, command: str, params: dict[str, Any], *, pretty: bool = False) -> str:
    result = api.listener(command, params)
    if pretty:
        return json.dumps(result, indent=2, ensure_ascii=False, default=str)
    return json.dumps(result, ensure_ascii=False, default=str)


def register(api: Any) -> None:
    @api.tool(intent=_INTENT)
    def create_material(
        asset_name: str,
        folder: str = "",
        base_color: Optional[list[float]] = None,
        two_sided: bool = False,
        blend_mode: str = "",
        pretty: bool = False,
    ) -> str:
        """Create a material under project content_root (omit folder to auto-pin). Never /Game/Materials."""
        return _json(
            api,
            "create_material",
            {
                "asset_name": asset_name,
                "folder": folder,
                "base_color": base_color,
                "two_sided": two_sided,
                "blend_mode": blend_mode,
            },
            pretty=pretty,
        )

    @api.tool(intent=_INTENT)
    def create_material_instance(
        asset_name: str,
        parent_material_path: str,
        folder: str = "",
        pretty: bool = False,
    ) -> str:
        """Create a MaterialInstanceConstant under project content_root (omit folder to auto-pin)."""
        return _json(
            api,
            "create_material_instance",
            {
                "asset_name": asset_name,
                "parent_material_path": parent_material_path,
                "folder": folder,
            },
            pretty=pretty,
        )

    @api.tool(intent=_INTENT)
    def duplicate_material(
        source_path: str,
        asset_name: str,
        folder: str = "",
        pretty: bool = False,
    ) -> str:
        """Duplicate a material/instance under project content_root (omit folder to auto-pin)."""
        return _json(
            api,
            "duplicate_material",
            {"source_path": source_path, "asset_name": asset_name, "folder": folder},
            pretty=pretty,
        )

    @api.tool(intent=_INTENT)
    def connect_material_nodes(
        material_path: str,
        from_index: int,
        from_output: str,
        to_index: int,
        to_input: str,
        pretty: bool = False,
    ) -> str:
        """Connect two material expression nodes by index (see list_material_expressions)."""
        return _json(
            api,
            "connect_material_nodes",
            {
                "material_path": material_path,
                "from_index": from_index,
                "from_output": from_output,
                "to_index": to_index,
                "to_input": to_input,
            },
            pretty=pretty,
        )

    @api.tool(intent=_INTENT)
    def disconnect_material_nodes(
        material_path: str,
        expression_index: int,
        input_name: str = "",
        pretty: bool = False,
    ) -> str:
        """Disconnect an expression input (empty input_name = all inputs on that node when supported)."""
        return _json(
            api,
            "disconnect_material_nodes",
            {
                "material_path": material_path,
                "expression_index": expression_index,
                "input_name": input_name,
            },
            pretty=pretty,
        )

    @api.tool(intent=_INTENT)
    def connect_material_output(
        material_path: str,
        from_index: int,
        from_output: str = "",
        material_property: str = "base_color",
        pretty: bool = False,
    ) -> str:
        """Connect a node's output to a material pin (base_color, emissive_color, roughness, metallic, opacity_mask, …)."""
        return _json(
            api,
            "connect_material_output",
            {
                "material_path": material_path,
                "from_index": from_index,
                "from_output": from_output,
                "material_property": material_property,
            },
            pretty=pretty,
        )

    @api.tool(intent=_INTENT)
    def add_material_expression(
        material_path: str,
        expression_class: str,
        pos_x: int = 0,
        pos_y: int = 0,
        pretty: bool = False,
    ) -> str:
        """Add one expression node (e.g. Multiply, Sine, ScalarParameter); returns index. Finish with recompile_material."""
        return _json(
            api,
            "add_material_expression",
            {
                "material_path": material_path,
                "expression_class": expression_class,
                "pos_x": pos_x,
                "pos_y": pos_y,
            },
            pretty=pretty,
        )

    @api.tool(intent=_INTENT)
    def delete_material_expression(material_path: str, index: int, pretty: bool = False) -> str:
        """Delete one expression by index — indices SHIFT; re-run list_material_expressions."""
        return _json(
            api,
            "delete_material_expression",
            {"material_path": material_path, "index": index},
            pretty=pretty,
        )

    @api.tool(intent=_INTENT)
    def clear_material_expressions(material_path: str, pretty: bool = False) -> str:
        """Delete every expression node on a material (blank graph)."""
        return _json(api, "clear_material_expressions", {"material_path": material_path}, pretty=pretty)

    @api.tool(intent=_INTENT)
    def set_material_expression_property(
        material_path: str,
        index: int,
        property_name: str,
        value: bool | int | float | str | list[float],
        pretty: bool = False,
    ) -> str:
        """Set an editor property on an expression node; float lists auto-try LinearColor/Vector wrappers."""
        return _json(
            api,
            "set_material_expression_property",
            {
                "material_path": material_path,
                "index": index,
                "property_name": property_name,
                "value": value,
            },
            pretty=pretty,
        )

    @api.tool(intent=_INTENT)
    def get_material_expression_info(material_path: str, index: int, pretty: bool = False) -> str:
        """Dump one expression node's class and editor properties."""
        return _json(
            api,
            "get_material_expression_info",
            {"material_path": material_path, "index": index},
            pretty=pretty,
        )

    @api.tool(intent=_INTENT)
    def get_material_info(material_path: str, pretty: bool = False) -> str:
        """Material/MI summary: blend, shading, parameters, expression count, UEFN limits."""
        return _json(api, "get_material_info", {"material_path": material_path}, pretty=pretty)

    @api.tool(intent=_INTENT)
    def set_material_flags(
        material_path: str,
        two_sided: Optional[bool] = None,
        blend_mode: str = "",
        shading_model: str = "",
        pretty: bool = False,
    ) -> str:
        """Set Material flags (two_sided, blend_mode Opaque/Masked/Translucent, shading_model). Then recompile_material."""
        return _json(
            api,
            "set_material_flags",
            {
                "material_path": material_path,
                "two_sided": two_sided,
                "blend_mode": blend_mode,
                "shading_model": shading_model,
            },
            pretty=pretty,
        )

    @api.tool(intent=_INTENT)
    def layout_material_expressions(material_path: str, pretty: bool = False) -> str:
        """Auto-arrange a material's expression nodes in the graph."""
        return _json(
            api, "layout_material_expressions", {"material_path": material_path}, pretty=pretty
        )

    @api.tool(intent=_INTENT)
    def list_material_expressions(material_path: str, pretty: bool = False) -> str:
        """List a material's nodes with indices (for connect_material_nodes)."""
        return _json(
            api, "list_material_expressions", {"material_path": material_path}, pretty=pretty
        )

    @api.tool(intent=_INTENT)
    def list_uefn_material_expression_classes(pretty: bool = False) -> str:
        """UEFN-safe MaterialExpression short names available in this editor build (no Custom/HLSL)."""
        return _json(api, "list_uefn_material_expression_classes", {}, pretty=pretty)

    @api.tool(intent=_INTENT)
    def assign_material_to_mesh(
        actor_path: str,
        material_path: str,
        slot_index: int = 0,
        component_name: str = "",
        pretty: bool = False,
    ) -> str:
        """Assign a material to an actor mesh slot (StaticMesh or SkeletalMesh). Optional component_name."""
        return _json(
            api,
            "assign_material_to_mesh",
            {
                "actor_path": actor_path,
                "material_path": material_path,
                "slot_index": slot_index,
                "component_name": component_name,
            },
            pretty=pretty,
        )

    @api.tool(intent=_INTENT)
    def set_material_instance_scalar(
        material_instance_path: str, param_name: str, value: float, pretty: bool = False
    ) -> str:
        """Set a scalar parameter on a MaterialInstanceConstant."""
        return _json(
            api,
            "set_material_instance_scalar",
            {
                "material_instance_path": material_instance_path,
                "param_name": param_name,
                "value": value,
            },
            pretty=pretty,
        )

    @api.tool(intent=_INTENT)
    def set_material_instance_vector(
        material_instance_path: str, param_name: str, color: list[float], pretty: bool = False
    ) -> str:
        """Set a vector/color parameter [r,g,b,a] on a MaterialInstanceConstant."""
        return _json(
            api,
            "set_material_instance_vector",
            {
                "material_instance_path": material_instance_path,
                "param_name": param_name,
                "color": color,
            },
            pretty=pretty,
        )

    @api.tool(intent=_INTENT)
    def set_material_instance_texture(
        material_instance_path: str, param_name: str, texture_path: str, pretty: bool = False
    ) -> str:
        """Set a texture parameter on a MaterialInstanceConstant."""
        return _json(
            api,
            "set_material_instance_texture",
            {
                "material_instance_path": material_instance_path,
                "param_name": param_name,
                "texture_path": texture_path,
            },
            pretty=pretty,
        )

    @api.tool(intent=_INTENT)
    def recompile_material(material_path: str, pretty: bool = False) -> str:
        """Recompile and save a material asset. Call after any graph/flag edit."""
        return _json(api, "recompile_material", {"material_path": material_path}, pretty=pretty)

    api.log(f"materials tools registered ({len(MATERIAL_TOOL_NAMES)})")
