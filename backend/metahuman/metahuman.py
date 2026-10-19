"""MetaHuman UEFN tools — probe / list / inspect / assemble via listener + execute_python."""

from __future__ import annotations

import json
import logging
from typing import Any

log = logging.getLogger("uefn.plugin.metahuman")

PLUGIN_ID = "metahuman"
INTENT = r"\b(meta\s*human|metahuman|mesh\s*to\s*meta|mh\s*npc|dna)\b"

SKILL_ASSEMBLE = (
    "skill_read_subskill('metahuman', 'assemble_uefn_export') — "
    "Assembly panel → Create Full Rig → textures → Assemble with UEFN Export pipeline."
)

_CAPS_CODE = r"""
import unreal

out = {
    "available": False,
    "listener_ok": True,
    "subsystem": False,
    "subsystem_class": None,
    "can_build_api": False,
    "build_api": False,
    "uefn_pipeline_enum": False,
    "pipeline_type_names": [],
    "plugins": {},
    "hint": "",
}

# Plugin enable flags (best-effort; names vary by build).
for plug_name in (
    "MetaHumanCharacter",
    "MetaHumanCharacterEditor",
    "MetaHumanCreator",
    "MetaHuman",
    "MetaHumanAnimator",
    "MetaHumanAnimatorDepthProcessing",
):
    try:
        out["plugins"][plug_name] = bool(unreal.Paths.find_plugins(plug_name))
    except Exception:
        try:
            # Alternate: PluginManager
            pm = unreal.PluginManager.get()
            p = pm.find_plugin(plug_name) if pm else None
            out["plugins"][plug_name] = bool(p and p.is_enabled()) if p else False
        except Exception:
            out["plugins"][plug_name] = None

sub = None
sub_cls = None
for cls_name in ("MetaHumanCharacterEditorSubsystem",):
    try:
        sub_cls = getattr(unreal, cls_name, None)
        if sub_cls is not None:
            sub = unreal.get_editor_subsystem(sub_cls)
            out["subsystem_class"] = cls_name
            out["subsystem"] = sub is not None
            break
    except Exception as exc:
        out["subsystem_error"] = str(exc)[:200]

if sub is not None:
    out["can_build_api"] = hasattr(sub, "can_build_meta_human")
    out["build_api"] = hasattr(sub, "build_meta_human")

# UEFN pipeline enum
try:
    pipe = getattr(unreal, "MetaHumanDefaultPipelineType", None)
    if pipe is not None:
        names = []
        for attr in dir(pipe):
            if attr.startswith("_"):
                continue
            try:
                getattr(pipe, attr)
                names.append(attr)
            except Exception:
                pass
        out["pipeline_type_names"] = names
        out["uefn_pipeline_enum"] = any(
            n.upper() == "UEFN" or n.upper().endswith("UEFN") for n in names
        )
except Exception as exc:
    out["pipeline_error"] = str(exc)[:200]

out["available"] = bool(
    out["subsystem"] and out["build_api"] and out["uefn_pipeline_enum"]
)
if not out["available"]:
    out["hint"] = (
        "MetaHuman Python assemble API incomplete on this build. "
        "Use Creator Assembly → UEFN Export (see skill assemble_uefn_export). "
        "Enable MetaHuman Creator plugins and ensure Core Data is installed."
    )
else:
    out["hint"] = "metahuman_assemble_uefn can call build_meta_human with pipeline_type=UEFN."

result = out
"""


def _dumps(obj: Any, *, pretty: bool = False) -> str:
    if pretty:
        return json.dumps(obj, indent=2, ensure_ascii=False, default=str)
    return json.dumps(obj, ensure_ascii=False, default=str)


def _exec(api: Any, code: str, *, timeout: float = 120.0) -> dict[str, Any]:
    raw = api.listener("execute_python", {"code": code}, timeout=timeout)
    if not isinstance(raw, dict):
        return {"ok": False, "error": "bad_listener_response", "raw": str(raw)[:400]}
    stderr = str(raw.get("stderr") or "")
    if stderr.strip().startswith("STOP:"):
        return {"ok": False, "error": "blocked", "stderr": stderr.strip()[:500]}
    payload = raw.get("result")
    if isinstance(payload, dict):
        out = dict(payload)
        out.setdefault("ok", True)
        if stderr.strip():
            out["stderr"] = stderr.strip()[:500]
        return out
    return {
        "ok": False,
        "error": "no_result",
        "stdout": str(raw.get("stdout") or "")[:500],
        "stderr": stderr.strip()[:500],
        "result": payload,
    }


def _normalize_asset_path(path: str) -> str:
    p = (path or "").strip().replace("\\", "/")
    if not p:
        return ""
    if p.endswith(".uasset"):
        p = p[: -len(".uasset")]
    if not p.startswith("/"):
        # Epic MetaHuman assemblies commonly live under /Game/MetaHumans (read).
        # Everything else must be an absolute project content_root path — do not
        # invent /Game/... for new island assets (cook Disallowed reference).
        if p.startswith("MetaHumans/") or p == "MetaHumans":
            p = "/Game/" + p.lstrip("/")
        else:
            p = "/" + p.lstrip("/")
    return p


def _info_code(asset_path: str) -> str:
    # Inject path as JSON string literal.
    path_lit = json.dumps(asset_path)
    return f"""
import unreal

path = {path_lit}
out = {{"ok": False, "asset_path": path, "exists": False}}

asset = unreal.EditorAssetLibrary.load_asset(path)
if asset is None:
    out["error"] = "asset_not_found"
    result = out
else:
    cls = asset.get_class()
    cls_name = cls.get_name() if cls else type(asset).__name__
    out["class"] = cls_name
    out["exists"] = True
    out["ok"] = True
    out["name"] = asset.get_name()
    out["package"] = str(asset.get_path_name())

    # Blueprint-generated class / CDO component scan (read-only).
    components = []
    try:
        gen = None
        if hasattr(asset, "generated_class"):
            gen = asset.generated_class()
        elif cls_name.endswith("_C") or "Blueprint" in cls_name:
            gen = asset
        cdo = unreal.get_default_object(gen) if gen else None
        if cdo is not None and hasattr(cdo, "get_components_by_class"):
            try:
                comps = cdo.get_components_by_class(unreal.ActorComponent)
            except Exception:
                comps = []
            for c in comps or []:
                try:
                    cn = c.get_class().get_name() if c.get_class() else type(c).__name__
                except Exception:
                    cn = type(c).__name__
                entry = {{"class": cn, "name": c.get_name()}}
                low = cn.lower()
                if "lodsync" in low:
                    entry["kind"] = "lod_sync"
                    try:
                        entry["num_lo_ds"] = int(c.get_editor_property("num_lo_ds"))
                    except Exception:
                        pass
                elif "groom" in low:
                    entry["kind"] = "groom"
                elif "metahuman" in low:
                    entry["kind"] = "metahuman"
                components.append(entry)
    except Exception as exc:
        out["components_error"] = str(exc)[:200]
    out["components"] = components

    # Soft deps (limited)
    try:
        deps = unreal.EditorAssetLibrary.find_package_referencers_for_asset(path, False)
        out["referencer_count"] = len(list(deps) if deps else [])
    except Exception:
        pass

    # Character asset readiness hints
    out["is_metahuman_character"] = "MetaHumanCharacter" in cls_name and "Blueprint" not in cls_name
    out["looks_assembled_bp"] = "Blueprint" in cls_name or cls_name.endswith("_C")

    result = out
"""


def _can_assemble_code(asset_path: str) -> str:
    path_lit = json.dumps(asset_path)
    return f"""
import unreal

path = {path_lit}
out = {{"ok": False, "asset_path": path, "can_build": False, "ready": False}}

sub_cls = getattr(unreal, "MetaHumanCharacterEditorSubsystem", None)
if sub_cls is None:
    out["error"] = "no_subsystem_class"
    out["hint"] = {json.dumps(SKILL_ASSEMBLE)}
    result = out
else:
    try:
        sub = unreal.get_editor_subsystem(sub_cls)
    except Exception as exc:
        sub = None
        out["error"] = "subsystem_get_failed"
        out["detail"] = str(exc)[:200]
    if sub is None:
        out["hint"] = {json.dumps(SKILL_ASSEMBLE)}
        result = out
    else:
        asset = unreal.EditorAssetLibrary.load_asset(path)
        if asset is None:
            out["error"] = "asset_not_found"
            result = out
        else:
            out["class"] = asset.get_class().get_name() if asset.get_class() else type(asset).__name__
            try:
                # Prefer Text overload if present
                can = None
                if hasattr(sub, "can_build_meta_human"):
                    try:
                        can = sub.can_build_meta_human(asset, True)
                    except TypeError:
                        can = sub.can_build_meta_human(asset)
                out["can_build"] = bool(can)
                out["ready"] = bool(can)
                out["ok"] = True
                if not can:
                    out["hint"] = (
                        "Character not ready to assemble (needs Full Rig + textures). "
                        + {json.dumps(SKILL_ASSEMBLE)}
                    )
            except Exception as exc:
                out["error"] = "can_build_failed"
                out["detail"] = str(exc)[:300]
                out["hint"] = {json.dumps(SKILL_ASSEMBLE)}
            result = out
"""


def _assemble_code(asset_path: str, quality: str, name_override: str) -> str:
    path_lit = json.dumps(asset_path)
    quality_lit = json.dumps((quality or "medium").strip().lower())
    name_lit = json.dumps((name_override or "").strip())
    return f"""
import unreal

path = {path_lit}
quality_s = {quality_lit}
name_override = {name_lit}
out = {{"ok": False, "asset_path": path, "assembled": False}}

sub_cls = getattr(unreal, "MetaHumanCharacterEditorSubsystem", None)
pipe_enum = getattr(unreal, "MetaHumanDefaultPipelineType", None)
params_cls = getattr(unreal, "MetaHumanCharacterEditorBuildParameters", None)
qual_enum = getattr(unreal, "MetaHumanQualityLevel", None)

if sub_cls is None or pipe_enum is None or params_cls is None:
    out["error"] = "assemble_api_missing"
    out["hint"] = {json.dumps(SKILL_ASSEMBLE)}
    result = out
else:
    uefn_val = None
    for attr in dir(pipe_enum):
        if attr.upper() == "UEFN" or attr.upper().endswith("UEFN"):
            try:
                uefn_val = getattr(pipe_enum, attr)
                out["pipeline_attr"] = attr
                break
            except Exception:
                pass
    if uefn_val is None:
        out["error"] = "uefn_pipeline_missing"
        out["hint"] = {json.dumps(SKILL_ASSEMBLE)}
        result = out
    else:
        try:
            sub = unreal.get_editor_subsystem(sub_cls)
        except Exception as exc:
            sub = None
            out["detail"] = str(exc)[:200]
        if sub is None:
            out["error"] = "no_subsystem"
            out["hint"] = {json.dumps(SKILL_ASSEMBLE)}
            result = out
        else:
            asset = unreal.EditorAssetLibrary.load_asset(path)
            if asset is None:
                out["error"] = "asset_not_found"
                result = out
            else:
                # Character must be opened for edit on some builds — best effort.
                try:
                    unreal.AssetEditorSubsystem().open_editor_for_assets([asset])
                except Exception:
                    try:
                        unreal.EditorAssetLibrary.open_editor_for_asset(path)
                    except Exception:
                        pass

                params = params_cls()
                params.set_editor_property("pipeline_type", uefn_val)
                if name_override:
                    try:
                        params.set_editor_property("name_override", name_override)
                    except Exception:
                        pass
                if qual_enum is not None:
                    qmap = {{
                        "low": ("LOW", "Low"),
                        "medium": ("MEDIUM", "Medium"),
                        "med": ("MEDIUM", "Medium"),
                        "high": ("HIGH", "High"),
                    }}
                    keys = qmap.get(quality_s, ("MEDIUM", "Medium"))
                    qv = None
                    for k in keys:
                        if hasattr(qual_enum, k):
                            qv = getattr(qual_enum, k)
                            break
                    if qv is not None:
                        try:
                            params.set_editor_property("pipeline_quality", qv)
                            out["quality"] = quality_s
                        except Exception:
                            pass

                try:
                    if hasattr(sub, "can_build_meta_human"):
                        try:
                            ready = sub.can_build_meta_human(asset, True)
                        except TypeError:
                            ready = sub.can_build_meta_human(asset)
                        if not ready:
                            out["error"] = "not_ready"
                            out["hint"] = (
                                "can_build_meta_human returned false. "
                                + {json.dumps(SKILL_ASSEMBLE)}
                            )
                            result = out
                        else:
                            sub.build_meta_human(asset, params)
                            out["ok"] = True
                            out["assembled"] = True
                            out["message"] = "build_meta_human invoked with UEFN pipeline"
                            result = out
                    else:
                        sub.build_meta_human(asset, params)
                        out["ok"] = True
                        out["assembled"] = True
                        out["message"] = "build_meta_human invoked with UEFN pipeline (no can_build gate)"
                        result = out
                except Exception as exc:
                    out["error"] = "build_failed"
                    out["detail"] = str(exc)[:400]
                    out["hint"] = {json.dumps(SKILL_ASSEMBLE)}
                    result = out
"""


def register_tools(api: Any) -> None:
    @api.tool(name="metahuman_capabilities", intent=INTENT)
    def metahuman_capabilities(pretty: bool = False) -> str:
        """Probe MetaHuman Creator / Animator / assemble API availability in the live UEFN editor.

        Always call this before metahuman_assemble_uefn. If available is false, follow the skill
        Assembly → UEFN Export UI path instead of Python assemble.
        """
        try:
            out = _exec(api, _CAPS_CODE, timeout=60.0)
            return _dumps(out, pretty=pretty)
        except Exception as exc:
            return _dumps(
                {
                    "ok": False,
                    "available": False,
                    "error": str(exc)[:300],
                    "hint": (
                        "UEFN listener offline or execute_python failed. "
                        "Enable MetaHuman Creator in the editor and retry; "
                        "or use Assembly → UEFN Export manually."
                    ),
                },
                pretty=pretty,
            )

    @api.tool(name="metahuman_list", intent=INTENT)
    def metahuman_list(
        search: str = "MetaHuman",
        directory: str = "",
        offset: int = 0,
        limit: int = 50,
        pretty: bool = False,
    ) -> str:
        """List MetaHuman-related assets (search Content Browser by name substring).

        Empty directory = project content_root first, then /Game/MetaHumans (Epic
        assemblies). Pass an explicit project path for island-local MH.
        """
        try:
            q = (search or "").strip()
            dir_arg = (directory or "").strip()
            if not dir_arg:
                try:
                    info = api.listener("get_project_info", {})
                    root = str((info or {}).get("content_root") or "").strip()
                    if root:
                        dir_arg = root if root.endswith("/") else root + "/"
                except Exception:
                    dir_arg = ""
            if not dir_arg:
                dir_arg = "/Game/MetaHumans/"
            params: dict[str, Any] = {
                "search": q if q else "MetaHuman",
                "directory": dir_arg,
                "recursive": True,
                "offset": max(0, int(offset)),
                "limit": max(1, min(int(limit), 200)),
            }
            found = api.listener("search_assets", params)
            # Second pass under /Game/MetaHumans when first is empty and dir was project-wide.
            assets = []
            if isinstance(found, dict):
                assets = list(found.get("assets") or [])
            if not assets and not str(directory or "").strip():
                found2 = api.listener(
                    "search_assets",
                    {
                        "search": q if q else "",
                        "directory": "/Game/MetaHumans",
                        "recursive": True,
                        "offset": 0,
                        "limit": max(1, min(int(limit), 200)),
                    },
                )
                if isinstance(found2, dict) and found2.get("assets"):
                    found = found2
                    assets = list(found2.get("assets") or [])
            return _dumps(
                {
                    "ok": True,
                    "count": len(assets),
                    "assets": assets,
                    "query": params,
                    "next": "metahuman_get_info(asset_path=...) then assemble or NPC spawn skill",
                },
                pretty=pretty,
            )
        except Exception as exc:
            return _dumps({"ok": False, "error": str(exc)[:300]}, pretty=pretty)

    @api.tool(name="metahuman_get_info", intent=INTENT)
    def metahuman_get_info(asset_path: str, pretty: bool = False) -> str:
        """Inspect a MetaHuman Character or assembled Blueprint: class, components (LODSync/Groom/MH)."""
        path = _normalize_asset_path(asset_path)
        if not path:
            return _dumps({"ok": False, "error": "asset_path required"}, pretty=pretty)
        try:
            out = _exec(api, _info_code(path), timeout=60.0)
            return _dumps(out, pretty=pretty)
        except Exception as exc:
            return _dumps({"ok": False, "error": str(exc)[:300], "asset_path": path}, pretty=pretty)

    @api.tool(name="metahuman_can_assemble", intent=INTENT)
    def metahuman_can_assemble(asset_path: str, pretty: bool = False) -> str:
        """Check whether a MetaHuman Character asset is ready for UEFN Export assemble (can_build_meta_human)."""
        path = _normalize_asset_path(asset_path)
        if not path:
            return _dumps({"ok": False, "error": "asset_path required"}, pretty=pretty)
        try:
            out = _exec(api, _can_assemble_code(path), timeout=60.0)
            return _dumps(out, pretty=pretty)
        except Exception as exc:
            return _dumps(
                {
                    "ok": False,
                    "error": str(exc)[:300],
                    "asset_path": path,
                    "hint": SKILL_ASSEMBLE,
                },
                pretty=pretty,
            )

    @api.tool(name="metahuman_assemble_uefn", intent=INTENT)
    def metahuman_assemble_uefn(
        asset_path: str,
        quality: str = "medium",
        name_override: str = "",
        pretty: bool = False,
    ) -> str:
        """Assemble a MetaHuman Character with the UEFN Export pipeline (Python API when available).

        Call metahuman_capabilities first. Character must be fully rigged with textures.
        quality: low | medium | high. On failure, use Assembly UI — see skill assemble_uefn_export.
        Cloud autorigger / texture download can take minutes; this only invokes the editor build.
        """
        path = _normalize_asset_path(asset_path)
        if not path:
            return _dumps({"ok": False, "error": "asset_path required"}, pretty=pretty)
        try:
            out = _exec(
                api,
                _assemble_code(path, quality, name_override),
                timeout=180.0,
            )
            return _dumps(out, pretty=pretty)
        except Exception as exc:
            return _dumps(
                {
                    "ok": False,
                    "error": str(exc)[:300],
                    "asset_path": path,
                    "hint": SKILL_ASSEMBLE,
                },
                pretty=pretty,
            )

    api.log("metahuman MCP tools ready")


def _self_check() -> None:
    """Assert helpers produce runnable code snippets (no UEFN needed)."""
    assert "MetaHumanCharacterEditorSubsystem" in _CAPS_CODE
    assert "pipeline_type" in _assemble_code("/Game/MetaHumans/Foo", "medium", "")
    path = _normalize_asset_path("MetaHumans/Hero.uasset")
    assert path == "/Game/MetaHumans/Hero"
    info = _info_code(path)
    assert "lodsync" in info.lower() or "LODSync" in info or "lod_sync" in info
    can = _can_assemble_code(path)
    assert "can_build_meta_human" in can
    print("metahuman self-check ok")


if __name__ == "__main__":
    _self_check()
