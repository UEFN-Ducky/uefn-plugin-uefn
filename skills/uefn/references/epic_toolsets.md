---
description: "Every Epic UEFN MCP toolset in 42.30 with its exact tool names (30 toolsets, 388 tools) — use before unreal__describe_toolset to pick the right one"
metadata:
  order: 2
  label: "Epic toolsets catalog (42.30)"
  default_enabled: false
  load_condition: "Choosing an Epic toolset or tool name (unreal__call_tool), or the user asks what the UEFN MCP can do — Niagara, physics assets, gameplay tags, logs, data/curve tables, textures, static/skeletal meshes, widget animation, MVVM, Python enablement"
---

# Epic UEFN MCP toolsets (42.30, described live)

The server exposes three tools: `list_toolsets`, `describe_toolset`, `call_tool`
(Ducky shows them as `unreal__list_toolsets`, `unreal__describe_toolset`,
`unreal__call_tool`). Names below are exact; still call
`unreal__describe_toolset(toolset_name=…)` for argument names before the first
call to a toolset. Object arguments are `{"refPath": "<path>"}`. Rows marked
*new in skills* had no skill coverage before 42.30.

| Toolset | Tools | Tool names (`unreal__call_tool(toolset_name, tool_name, arguments)`) |
| --- | --- | --- |
| `editor_toolset.toolsets.actor.ActorTools` | 18 | `add_component`, `add_tag`, `diff`, `get_actor_bounds`, `get_actor_transform`, `get_component_actor`, `get_components`, `get_label`, `get_parent_component`, `get_root_component`, `get_tags`, `has_tag`, `look_at`, `remove_component`, `remove_tag`, `set_actor_transform`, `set_label`, `set_parent_component` |
| `editor_toolset.toolsets.asset.AssetTools` | 17 | `create_folder`, `delete`, `duplicate`, `exists`, `find_assets`, `get_asset_class`, `get_asset_tags`, `get_dependencies`, `get_metadata_tags`, `get_referencers`, `is_dirty`, `list_folders`, `load_asset`, `move`, `reload_asset`, `save_assets`, `update_metadata_tags` |
| `editor_toolset.toolsets.curve_table.CurveTableTools` (new in skills) | 10 | `add_key`, `add_row`, `create`, `diff`, `get_keys`, `import_file`, `list_rows`, `remove_row`, `rename_row`, `set_keys` |
| `editor_toolset.toolsets.data_table.DataTableTools` (new in skills) | 11 | `add_rows`, `create`, `diff`, `get_rows`, `get_schema`, `import_file`, `list_rows`, `remove_rows`, `rename_rows`, `search_row_structs`, `set_rows` |
| `editor_toolset.toolsets.material.MaterialTools` | 25 | `add_expression`, `connect_expressions`, `connect_to_output`, `create_function`, `create_material`, `create_parameter_collection`, `delete_expression`, `delete_parameter_group`, `delete_unused_expressions`, `diff_function`, `diff_material`, `disconnect_expressions`, `disconnect_from_output`, `get_expression_input_names`, `get_expression_inputs`, `get_expression_output_names`, `get_expressions`, `get_property_input`, `get_referencing_materials`, `get_statistics`, `layout_expressions`, `list_expression_classes`, `list_parameter_groups`, `recompile`, `rename_parameter_group` |
| `editor_toolset.toolsets.material_instance.MaterialInstanceTools` (new in skills) | 14 | `clear_parameters`, `create`, `diff`, `get_scalar_parameter`, `get_static_switch_parameter`, `get_texture_parameter`, `get_vector_parameter`, `list_parameters`, `set_parameter_override`, `set_parent`, `set_scalar_parameter`, `set_static_switch_parameter`, `set_texture_parameter`, `set_vector_parameter` |
| `editor_toolset.toolsets.object.ObjectTools` | 6 | `get_class`, `get_properties`, `list_properties`, `reset_properties`, `search_subclasses`, `set_properties` |
| `editor_toolset.toolsets.primitive.PrimitiveTools` (new in skills) | 4 | `add_cone`, `add_cube`, `add_cylinder`, `add_sphere` |
| `editor_toolset.toolsets.programmatic.ProgrammaticToolset` | 2 | `execute_tool_script`, `get_execution_environment` |
| `editor_toolset.toolsets.scene.SceneTools` | 28 | `add_actors_to_data_layer`, `add_to_scene_from_asset`, `add_to_scene_from_class`, `create_data_layer_asset`, `create_level`, `delete_folder`, `diff`, `find_actors`, `get_actor_asset_path`, `get_actors_in_data_layer`, `get_actors_in_folder`, `get_collision_channels`, `get_current_level`, `get_data_layers`, `get_folders`, `is_actor_hidden`, `load_actors`, `load_level`, `remove_actors_from_data_layer`, `remove_from_scene`, `rename_folder`, `replace_actors_with_asset`, `replace_actors_with_class`, `save_actor`, `set_actor_folder`, `set_actor_hidden`, `trace_world`, `unload_actors` |
| `editor_toolset.toolsets.skeletal_mesh.SkeletalMeshTools` (new in skills) | 22 | `add_socket`, `assign_physics_asset`, `get_bone_children`, `get_bone_names`, `get_bone_parent`, `get_bounds`, `get_lod_count`, `get_material`, `get_material_slots`, `get_morph_target_names`, `get_physics_asset`, `get_section_count`, `get_skeleton`, `get_socket_bone`, `get_socket_names`, `get_socket_transform`, `get_vertex_count`, `import_file`, `remove_socket`, `rename_socket`, `set_material`, `set_socket_transform` |
| `editor_toolset.toolsets.static_mesh.StaticMeshTools` (new in skills) | 16 | `generate_convex_collisions`, `generate_lods`, `get_bounds`, `get_lod_count`, `get_lod_thresholds`, `get_material`, `get_material_slots`, `get_triangle_count`, `get_vertex_count`, `import_file`, `is_nanite_enabled`, `remove_collisions`, `remove_lods`, `set_lod_thresholds`, `set_material`, `set_nanite_enabled` |
| `editor_toolset.toolsets.texture.TextureTools` (new in skills) | 4 | `export_png`, `get_size`, `import_file`, `read_texture` |
| `EditorToolset.EditorAppToolset` | 37 | `AddAssetsToCollection`, `CaptureAssetImage`, `CaptureEditorImage`, `CaptureViewport`, `CreateCollection`, `DestroyCollection`, `FocusOnActors`, `GetActiveEditorModes`, `GetAssetThumbnails`, `GetCVarValue`, `GetCameraTransform`, `GetCollectionAssets`, `GetContentBrowserPath`, `GetOpenAssets`, `GetSelectedActors`, `GetSelectedAssets`, `GetSelectedOutlinerFolders`, `GetShowFlag`, `GetVisibleActors`, `ListCollections`, `ListEditorModes`, `ListShowFlags`, `OpenEditorForAsset`, `RemoveAssetsFromCollection`, `ScreenCoordsToWorld`, `SearchCVars`, `SelectActors`, `SelectAssets`, `SelectOutlinerFolders`, `SetCVarValue`, `SetCameraTransform`, `SetContentBrowserPath`, `SetEditorMode`, `SetShowFlag`, `SetViewportViewMode`, `ShowNotification`, `WorldPosToScreenCoords` |
| `EditorToolset.LogsToolset` (new in skills) | 4 | `GetLogCategories`, `GetLogEntries`, `GetVerbosity`, `SetVerbosity` |
| `GameplayTagsToolset.GameplayTagsToolset` (new in skills) | 4 | `FindReferencersByTag`, `GetTagInfo`, `ListTags`, `ListTagsInSource` |
| `MVVMToolset.MVVMToolset` | 15 | `AddViewModelProperty`, `AddViewModelToWidget`, `CreateViewBinding`, `CreateViewEventBinding`, `FixupMVVMData`, `GetWidgetViewConfig`, `ListBindableWidgetProperties`, `ListConversionFunctions`, `ListViewModels`, `ListWidgetViewBindings`, `ListWidgetViewEvents`, `ListWidgetViewModels`, `RemoveWidgetViewBinding`, `SetBindingMode`, `SetWidgetViewConfig` |
| `NiagaraToolsets.NiagaraToolset_Assets` (new in skills) | 3 | `FindNiagaraScripts`, `GetAssetDiscoveryInfo`, `GetNiagaraScriptDigest` |
| `NiagaraToolsets.NiagaraToolset_Component` (new in skills) | 4 | `GetUserVariables`, `GetVariable`, `SetSystem`, `SetVariable` |
| `NiagaraToolsets.NiagaraToolset_Info` (new in skills) | 1 | `UEnum_Info` |
| `NiagaraToolsets.NiagaraToolset_System` | 46 | `AddEmitter`, `AddModule`, `AddRenderer`, `AddSetParameterEntry`, `AddSetParametersModule`, `AddUserVariables`, `ApplyStackIssueFix`, `CreateNiagaraSystem`, `GetAvailableDynamicInputs`, `GetDataInterfaceSchema`, `GetDynamicInputChain`, `GetDynamicInputSchema`, `GetDynamicInputSchemaFromAsset`, `GetEmitterData`, `GetEmitterInputValues`, `GetEmitterSchema`, `GetEmitterSummary`, `GetEmitterTopology`, `GetModuleInputValues`, `GetModuleSchema`, `GetModuleSchemaFromAsset`, `GetModuleTopology`, `GetRendererData`, `GetRendererSchema`, `GetScriptStackInputValues`, `GetScriptStackTopology`, `GetStackInputData`, `GetStackInputSchema`, `GetStackInputTopology`, `GetStackIssues`, `GetSystemCompileState`, `GetSystemData`, `GetSystemDependencies`, `GetSystemSchema`, `GetSystemSummary`, `GetUserVariables`, `RemoveEmitter`, `RemoveModule`, `RemoveRenderer`, `RemoveSetParameterEntry`, `RemoveUserVariables`, `SetEmitterData`, `SetModuleEnabled`, `SetRendererData`, `SetStackInputData`, `SetSystemData` |
| `PhysicsToolsets.PhysicsAssetToolset` (new in skills) | 17 | `AddBody`, `AddConstraint`, `CreateFromMesh`, `GetBodyMassScale`, `GetBodyNames`, `GetBodyPhysicsMode`, `GetBodyShapes`, `GetConstraints`, `RemoveBody`, `RemoveConstraint`, `RemoveShape`, `SetBodyMassScale`, `SetBodyPhysicsMode`, `SetBox`, `SetCapsule`, `SetConstraintLimits`, `SetSphere` |
| `UMGToolSet.UMGToolSet` | 21 | `AddUIComponent`, `AddWidget`, `CompileWidgetBlueprint`, `CreateWidgetBlueprint`, `GetNamedSlots`, `GetWidgetClassInfo`, `GetWidgetDescription`, `GetWidgetTreeDepth`, `GetWidgets`, `ListWidgetBlueprints`, `ListWidgetClasses`, `MoveUIComponent`, `MoveWidget`, `RemoveUIComponent`, `RemoveWidget`, `RenameWidget`, `ReplaceWidgetWithChild`, `ReplaceWidgetWithNamedSlot`, `ReplaceWidgetWithTemplate`, `SetNamedSlotContent`, `WrapWidgets` |
| `ValkyrieToolset.DeviceToolset` | 9 | `AddEventBinding`, `GetBindingOptions`, `GetDeviceProperties`, `ListDeviceAssets`, `ListDeviceProperties`, `ListEventBindings`, `PlaceDevice`, `RemoveEventBinding`, `SetDeviceProperty` |
| `ValkyrieToolset.EntityToolset` | 13 | `AddComponent`, `CreateEntity`, `DeleteEntity`, `FindEntities`, `GetComponentProperty`, `GetComponents`, `GetEntityTransform`, `ListComponentClasses`, `ListComponentProperties`, `ListEntityClasses`, `RemoveComponent`, `SetComponentProperty`, `SetEntityTransform` |
| `ValkyrieToolset.SessionToolset` | 8 | `GetClientLogEntries`, `GetGameState`, `GetSessionStatus`, `PushChanges`, `StartGame`, `StartSession`, `StopGame`, `StopSession` |
| `ValkyrieToolset.ValkyriePythonToolset` (new in skills) | 2 | `EnablePythonInUEFN`, `IsPythonEnabledInUEFN` |
| `ValkyrieToolset.VerseToolset` | 10 | `BuildAll`, `Copy`, `CreateDirectory`, `Delete`, `Grep`, `ListFiles`, `Move`, `ReadFile`, `Replace`, `WriteFile` |
| `VerseFieldsToolset.VerseFieldsToolset` | 7 | `AddVerseField`, `BindWidgetPropertyToVerseField`, `DuplicateVerseField`, `EditVerseField`, `GetSupportedVerseFieldTypes`, `ListVerseFields`, `RemoveVerseField` |
| `WidgetAnimationToolset.WidgetAnimationToolset` (new in skills) | 10 | `AddWidgetToAnimation`, `CreateWidgetAnimation`, `FindWidgetAnimation`, `GetWidgetAnimationBindings`, `ListWidgetAnimations`, `RemoveWidgetAnimation`, `RemoveWidgetBinding`, `RenameWidgetAnimation`, `SetWidgetAnimationDisplayLabel`, `SetWidgetAnimationLength` |

## Notes

- `ValkyrieToolset.ValkyriePythonToolset` (`IsPythonEnabledInUEFN`, `EnablePythonInUEFN`):
  the core engine Python toolsets (actor, object, scene, asset) only load once
  Python is enabled; enabling is asynchronous.
- `EditorToolset.LogsToolset.GetLogEntries(category, pattern, maxEntries)` reads the
  editor log (compile results, Content Pre-Check messages, blueprint errors).
  `ValkyrieToolset.SessionToolset.GetClientLogEntries` reads the launched client's log.
- `VerseFieldsToolset.GetSupportedVerseFieldTypes` → 42.30: bool, int, float, string,
  message, color, color_alpha, texture, material, event; event params bool/int/float
  (max 1). Details: verse `umg_verse_field_events`.
- 42.30 fix: dialogue popups no longer stall MCP progress. Ducky's Save-modal
  watchdog (`dismiss_uefn_modal`) still covers older builds and other modals.
