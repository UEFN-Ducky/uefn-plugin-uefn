---
description: "Every Epic UEFN MCP toolset in 43.00 with its exact tool names (56 toolsets, 826 tools) and the 42.40 → 43.00 renames — use before unreal__describe_toolset to pick the right one"
metadata:
  order: 2
  label: "Epic toolsets catalog (43.00)"
  default_enabled: false
  load_condition: "Choosing an Epic toolset or tool name (unreal__call_tool), or the user asks what the UEFN MCP can do — level/actors, assets, Niagara, PCG, Sequencer, profiling/Insights, scene capture, prefabs, physics assets, gameplay tags, logs, data/curve tables, textures, meshes, UMG/MVVM, MetaSound, Python"
---

# Epic UEFN MCP toolsets (43.00, described live)

Described live in UEFN 43.00 on Nov 1 2026 (`unreal__list_toolsets` + `unreal__describe_toolset`
on every toolset): **56 toolsets, 826 tools** (42.40: 30 / 388).

The server exposes three tools: `list_toolsets`, `describe_toolset`, `call_tool`
(Ducky shows them as `unreal__list_toolsets`, `unreal__describe_toolset`,
`unreal__call_tool`). Names below are exact; still call
`unreal__describe_toolset(toolset_name=…)` for argument names before the first
call to a toolset. Object arguments are `{"refPath": "<path>"}`.
`execute_tool_script` cannot call `describe_toolset` (top-level tool, not in its registry).

## 42.40 → 43.00 renames (old names fail)

The Python-backed `editor_toolset.toolsets.*` toolsets with snake_case tools became native
`EditorToolset.*` toolsets with PascalCase tools.

| 42.40 | 43.00 | Change |
| --- | --- | --- |
| `editor_toolset.toolsets.actor.ActorTools` | `EditorToolset.ActorToolset` | PascalCase; + `GetCanonicalActorState`, `GetComponentTransform`, `SetComponentTransform` |
| `editor_toolset.toolsets.asset.AssetTools` | `EditorToolset.AssetToolset` | `save_assets` → `SaveAsset`; + `FixUpRedirectors`, `ValidateAssets`, `GetAssetContentRoots`, `GetVirtualPaths`, user asset tags |
| `editor_toolset.toolsets.scene.SceneTools` | `EditorToolset.LevelToolset` | `add_to_scene_from_class` → `AddToSceneFromClass` (same rule: place `/Game/Creative/**` `…_C` classes from class, never from asset) |
| `editor_toolset.toolsets.{curve_table,data_table,material,material_instance,object,primitive,skeletal_mesh,texture}` | `EditorToolset.{CurveTable,DataTable,Material,MaterialInstance,Object,Primitive,SkeletalMesh,Texture}Toolset` | PascalCase, same tools |
| `editor_toolset.toolsets.static_mesh.StaticMeshTools` | `EditorToolset.StaticMeshToolset` | `is_nanite_enabled` → `IsNaniteMesh`; + collision complexity, quality-level min LOD |
| `EditorToolset.EditorAppToolset` | same | − `GetCVarValue`, `SearchCVars`, `SetCVarValue`; + `GetAssetEditorSelection`, `SelectAssetEditorObjects`, `GetPivotLocation`, `SetPivotLocation` |
| `EditorToolset.LogsToolset` | `ConsoleToolset.LogsToolset` | moved |
| `UMGToolSet.UMGToolSet` | same | `GetWidgetDescription`, `GetWidgetTreeDepth` moved to `WidgetStaticAnalysisToolset` (`DescribeWidget`, `GetWidgetTreeDepth`); + `GetContainerWidgetNavigationDoc` |
| `MVVMToolset.MVVMToolset` | same | 15 → 27: view conditions, conversion-function args, event-binding literals |
| `ValkyrieToolset.DeviceToolset` | `ValkyrieFortniteToolset.DeviceToolset` | + classic device options: `ListClassicDeviceOptions`, `GetClassicDeviceOptionValues`, `SetClassicDeviceOption` |
| `ValkyrieToolset.SessionToolset` | `ValkyrieFortniteToolset.SessionToolset` | + `GetVerseOutput` |
| `ValkyrieToolset.EntityToolset` | same | + `RenameEntity`, `ReparentEntity` |
| `ValkyrieToolset.ValkyriePythonToolset` | same | `IsPythonEnabledInUEFN` / `EnablePythonInUEFN` → `IsPythonReadyForMainProject` / `EnablePythonForMainProject` |
| `ValkyrieToolset.VerseToolset` | `VerseToolset.VerseToolset` | + `FileTree` |

**New in 43.00:** AgentSkill, AIAssistant, CurveAtlas, SoundWave, MetaSound authoring, PCG +
PCGSpatial, BeaconClients, 7 Sequencer toolsets (`animation_toolset.toolsets.*`), Prefab,
Geometry, PythonScripting, SpatialProfiler, SceneCapture, Insights (Target / TimingProfiler /
MemorySnapshot), UMGDebug, WidgetStaticAnalysis, FortPlayer. No IK Retargeter toolset.

## Catalog

| Toolset | Tools | Tool names (`unreal__call_tool(toolset_name, tool_name, arguments)`) |
| --- | --- | --- |
| `ToolsetRegistry.AgentSkillToolset` | 4 | `CreateSkill`, `GetSkills`, `ListSkills`, `UpdateSkill` |
| `AIAssistantEditor.AIAssistantToolset` | 2 | `GetDockedContext`, `GetProjectContext` |
| `ConsoleToolset.LogsToolset` | 4 | `GetLogCategories`, `GetLogEntries`, `GetVerbosity`, `SetVerbosity` |
| `EditorToolset.ActorToolset` | 21 | `AddComponent`, `AddTag`, `Diff`, `GetActorBounds`, `GetActorTransform`, `GetCanonicalActorState`, `GetComponentActor`, `GetComponentTransform`, `GetComponents`, `GetLabel`, `GetParentComponent`, `GetRootComponent`, `GetTags`, `HasTag`, `LookAt`, `RemoveComponent`, `RemoveTag`, `SetActorTransform`, `SetComponentTransform`, `SetLabel`, `SetParentComponent` |
| `EditorToolset.AssetToolset` | 24 | `AddUserAssetTags`, `CreateFolder`, `Delete`, `Duplicate`, `Exists`, `FindAssets`, `FixUpRedirectors`, `GetAssetClass`, `GetAssetContentRoots`, `GetAssetTags`, `GetDependencies`, `GetMetadataTags`, `GetReferencers`, `GetUserAssetTags`, `GetVirtualPaths`, `IsDirty`, `ListFolders`, `LoadAsset`, `Move`, `ReloadAsset`, `RemoveUserAssetTags`, `SaveAsset`, `UpdateMetadataTags`, `ValidateAssets` |
| `EditorToolset.CurveAtlasToolset` | 13 | `AddGradient`, `CreateAtlas`, `CreateGradient`, `GetAlphaStops`, `GetChannelKeys`, `GetColorStops`, `GetGradients`, `RemoveGradient`, `SampleGradient`, `SetAlphaStops`, `SetChannelKeys`, `SetColorStops`, `SetGradients` |
| `EditorToolset.CurveTableToolset` | 10 | `AddKey`, `AddRow`, `Create`, `Diff`, `GetKeys`, `ImportFile`, `ListRows`, `RemoveRow`, `RenameRow`, `SetKeys` |
| `EditorToolset.DataTableToolset` | 11 | `AddRows`, `Create`, `Diff`, `GetRows`, `GetSchema`, `ImportFile`, `ListRows`, `RemoveRows`, `RenameRows`, `SearchRowStructs`, `SetRows` |
| `EditorToolset.EditorAppToolset` | 38 | `AddAssetsToCollection`, `CaptureAssetImage`, `CaptureEditorImage`, `CaptureViewport`, `CreateCollection`, `DestroyCollection`, `FocusOnActors`, `GetActiveEditorModes`, `GetAssetEditorSelection`, `GetAssetThumbnails`, `GetCameraTransform`, `GetCollectionAssets`, `GetContentBrowserPath`, `GetOpenAssets`, `GetPivotLocation`, `GetSelectedActors`, `GetSelectedAssets`, `GetSelectedOutlinerFolders`, `GetShowFlag`, `GetVisibleActors`, `ListCollections`, `ListEditorModes`, `ListShowFlags`, `OpenEditorForAsset`, `RemoveAssetsFromCollection`, `ScreenCoordsToWorld`, `SelectActors`, `SelectAssetEditorObjects`, `SelectAssets`, `SelectOutlinerFolders`, `SetCameraTransform`, `SetContentBrowserPath`, `SetEditorMode`, `SetPivotLocation`, `SetShowFlag`, `SetViewportViewMode`, `ShowNotification`, `WorldPosToScreenCoords` |
| `EditorToolset.LevelToolset` | 28 | `AddActorsToDataLayer`, `AddToSceneFromAsset`, `AddToSceneFromClass`, `CreateDataLayerAsset`, `CreateLevel`, `DeleteFolder`, `Diff`, `FindActors`, `GetActorAssetPath`, `GetActorsInDataLayer`, `GetActorsInFolder`, `GetCollisionChannels`, `GetCurrentLevel`, `GetDataLayers`, `GetFolders`, `IsActorHidden`, `LoadActors`, `LoadLevel`, `RemoveActorsFromDataLayer`, `RemoveFromScene`, `RenameFolder`, `ReplaceActorsWithAsset`, `ReplaceActorsWithClass`, `SaveActor`, `SetActorFolder`, `SetActorHidden`, `TraceWorld`, `UnloadActors` |
| `EditorToolset.MaterialInstanceToolset` | 14 | `ClearParameters`, `Create`, `Diff`, `GetScalarParameter`, `GetStaticSwitchParameter`, `GetTextureParameter`, `GetVectorParameter`, `ListParameters`, `SetParameterOverride`, `SetParent`, `SetScalarParameter`, `SetStaticSwitchParameter`, `SetTextureParameter`, `SetVectorParameter` |
| `EditorToolset.MaterialToolset` | 25 | `AddExpression`, `ConnectExpressions`, `ConnectToOutput`, `CreateFunction`, `CreateMaterial`, `CreateParameterCollection`, `DeleteExpression`, `DeleteParameterGroup`, `DeleteUnusedExpressions`, `DiffFunction`, `DiffMaterial`, `DisconnectExpressions`, `DisconnectFromOutput`, `GetExpressionInputNames`, `GetExpressionInputs`, `GetExpressionOutputNames`, `GetExpressions`, `GetPropertyInput`, `GetReferencingMaterials`, `GetStatistics`, `LayoutExpressions`, `ListExpressionClasses`, `ListParameterGroups`, `Recompile`, `RenameParameterGroup` |
| `EditorToolset.ObjectToolset` | 6 | `GetClass`, `GetProperties`, `ListProperties`, `ResetProperties`, `SearchSubclasses`, `SetProperties` |
| `EditorToolset.PrimitiveToolset` | 4 | `AddCone`, `AddCube`, `AddCylinder`, `AddSphere` |
| `EditorToolset.SkeletalMeshToolset` | 22 | `AddSocket`, `AssignPhysicsAsset`, `GetBoneChildren`, `GetBoneNames`, `GetBoneParent`, `GetBounds`, `GetLodCount`, `GetMaterial`, `GetMaterialSlots`, `GetMorphTargetNames`, `GetPhysicsAsset`, `GetSectionCount`, `GetSkeleton`, `GetSocketBone`, `GetSocketNames`, `GetSocketTransform`, `GetVertexCount`, `ImportFile`, `RemoveSocket`, `RenameSocket`, `SetMaterial`, `SetSocketTransform` |
| `EditorToolset.SoundWaveToolset` | 1 | `ImportFile` |
| `EditorToolset.StaticMeshToolset` | 22 | `GenerateConvexCollisions`, `GenerateLods`, `GetBounds`, `GetCollisionComplexity`, `GetLodCount`, `GetLodThresholds`, `GetMaterial`, `GetMaterialSlots`, `GetQualityLevelMinLod`, `GetQualityLevelMinLodDefault`, `GetTriangleCount`, `GetVertexCount`, `ImportFile`, `IsNaniteMesh`, `RemoveCollisions`, `RemoveLods`, `SetCollisionComplexity`, `SetLodThresholds`, `SetMaterial`, `SetNaniteEnabled`, `SetQualityLevelMinLod`, `SetQualityLevelMinLodDefault` |
| `EditorToolset.TextureToolset` | 4 | `ExportPng`, `GetSize`, `ImportFile`, `ReadTexture` |
| `GameplayTagsToolset.GameplayTagsToolset` | 4 | `FindReferencersByTag`, `GetTagInfo`, `ListTags`, `ListTagsInSource` |
| `MetaSoundToolset.MetaSoundAuthoringToolset` | 8 | `AttachBuilderToAsset`, `BuildToAsset`, `CommitBuilderToAsset`, `CreatePatchPresetBuilder`, `CreateSourcePresetBuilder`, `DetachBuilderFromAsset`, `FindMetaSoundAssets`, `SetDefaults` |
| `MVVMToolset.MVVMToolset` | 27 | `AddViewCondition`, `AddViewModelProperty`, `AddViewModelToWidget`, `ClearConversionFunctionArgumentPath`, `CreateViewBinding`, `CreateViewEventBinding`, `FixupMVVMData`, `GetWidgetViewConfig`, `ListBindableWidgetProperties`, `ListBindingConversionOptions`, `ListClassBindableFields`, `ListConversionFunctions`, `ListPropertyPathBindableFields`, `ListViewConditions`, `ListViewModels`, `ListWidgetViewBindings`, `ListWidgetViewEventBindings`, `ListWidgetViewEvents`, `ListWidgetViewModels`, `RemoveViewCondition`, `RemoveWidgetViewBinding`, `SetBindingMode`, `SetConversionFunctionArgumentLiteral`, `SetEventBindingArgumentLiteral`, `SetViewConditionOperation`, `SetWidgetViewBindingEnabled`, `SetWidgetViewConfig` |
| `VerseToolset.VerseToolset` | 11 | `BuildAll`, `Copy`, `CreateDirectory`, `Delete`, `FileTree`, `Grep`, `ListFiles`, `Move`, `ReadFile`, `Replace`, `WriteFile` |
| `NiagaraToolsets.NiagaraToolset_Info` | 1 | `UEnum_Info` |
| `NiagaraToolsets.NiagaraToolset_Component` | 4 | `GetUserVariables`, `GetVariable`, `SetSystem`, `SetVariable` |
| `NiagaraToolsets.NiagaraToolset_System` | 46 | `AddEmitter`, `AddModule`, `AddRenderer`, `AddSetParameterEntry`, `AddSetParametersModule`, `AddUserVariables`, `ApplyStackIssueFix`, `CreateNiagaraSystem`, `GetAvailableDynamicInputs`, `GetDataInterfaceSchema`, `GetDynamicInputChain`, `GetDynamicInputSchema`, `GetDynamicInputSchemaFromAsset`, `GetEmitterData`, `GetEmitterInputValues`, `GetEmitterSchema`, `GetEmitterSummary`, `GetEmitterTopology`, `GetModuleInputValues`, `GetModuleSchema`, `GetModuleSchemaFromAsset`, `GetModuleTopology`, `GetRendererData`, `GetRendererSchema`, `GetScriptStackInputValues`, `GetScriptStackTopology`, `GetStackInputData`, `GetStackInputSchema`, `GetStackInputTopology`, `GetStackIssues`, `GetSystemCompileState`, `GetSystemData`, `GetSystemDependencies`, `GetSystemSchema`, `GetSystemSummary`, `GetUserVariables`, `RemoveEmitter`, `RemoveModule`, `RemoveRenderer`, `RemoveSetParameterEntry`, `RemoveUserVariables`, `SetEmitterData`, `SetModuleEnabled`, `SetRendererData`, `SetStackInputData`, `SetSystemData` |
| `NiagaraToolsets.NiagaraToolset_Assets` | 3 | `FindNiagaraScripts`, `GetAssetDiscoveryInfo`, `GetNiagaraScriptDigest` |
| `PhysicsToolsets.PhysicsAssetToolset` | 17 | `AddBody`, `AddConstraint`, `CreateFromMesh`, `GetBodyMassScale`, `GetBodyNames`, `GetBodyPhysicsMode`, `GetBodyShapes`, `GetConstraints`, `RemoveBody`, `RemoveConstraint`, `RemoveShape`, `SetBodyMassScale`, `SetBodyPhysicsMode`, `SetBox`, `SetCapsule`, `SetConstraintLimits`, `SetSphere` |
| `VerseFieldsToolset.VerseFieldsToolset` | 7 | `AddVerseField`, `BindWidgetPropertyToVerseField`, `DuplicateVerseField`, `EditVerseField`, `GetSupportedVerseFieldTypes`, `ListVerseFields`, `RemoveVerseField` |
| `PCGToolset.PCGToolset` | 30 | `AddCommentBox`, `AddNode`, `AddSubgraphNode`, `ConnectNodePins`, `CreateGraph`, `DisconnectNodePins`, `DrawSpline`, `ExecuteGraphInstance`, `GetGraphDescription`, `GetGraphInstanceParams`, `GetGraphSchema`, `GetGraphStructure`, `GetNativeNodeSchema`, `GetNodeDataView`, `GetNodeInfo`, `ListAvailableSubgraphs`, `ListGraphInstances`, `ListNativeNodes`, `RemoveCommentBox`, `RemoveGraphParams`, `RemoveNode`, `RepositionNode`, `ResetGraphInstanceParams`, `SetGraphDescription`, `SetGraphInstanceParams`, `SetGraphParams`, `SetNodeComment`, `SpawnGraphInstance`, `UpdateCommentBox`, `UpdateNode` |
| `PCGToolset.PCGSpatialToolset` | 1 | `RunPCGInstantGraph` (call directly, not from `execute_tool_script`) |
| `ValkyrieFortniteToolset.BeaconClientsToolset` | 1 | `ListClients` |
| `animation_toolset.toolsets.sequencer.SequencerTools` | 143 | bindings, folders, tracks, sections, marked frames, playback/view/work ranges, camera cuts, play/pause/playhead; e.g. `create_level_sequence`, `open_sequence`, `add_actors`, `add_spawnable_from_class`, `add_track_to_binding`, `add_section`, `set_section_range`, `create_camera`, `set_camera_cut_binding`, `set_playback_range`, `play`, `bake_transform` (full list: `unreal__describe_toolset`) |
| `animation_toolset.toolsets.keyframing.SequencerKeyframingTools` | 22 | `add_key_bool`, `add_key_float`, `add_key_integer`, `add_key_string`, `bake_channel_keys`, `close_curve_editor`, `curve_editor_empty_selection`, `curve_editor_select_keys`, `get_channel_names`, `get_curve_editor_selected_keys`, `get_default_value`, `get_keys`, `get_keys_by_index`, `get_selected_channels`, `get_selected_key_channels`, `is_curve_editor_open`, `is_curve_shown`, `open_curve_editor`, `remove_key_at_frame`, `select_channels`, `set_default_value`, `show_curve` |
| `animation_toolset.toolsets.controlrig_sequencer.SequencerControlRigTools` | 71 | control-rig tracks, controls get/set (`get_transform`, `set_transform`, `key_controls`, `key_controls_at_frames`), anim layers, spaces (`bake_space`, `set_space`), `bake_to_control_rig`, `load_anim_into_rig`, `import_fbx_to_rig`, `mirror_selected_controls`, `tween_control_rig`, `snap_control_rig` |
| `animation_toolset.toolsets.outliner.SequencerOutlinerTools` | 22 | `expand_all_outliner_nodes`, `get_deactivated_nodes`, `get_locked_nodes`, `get_muted_nodes`, `get_node_label`, `get_outliner_children`, `get_outliner_paths`, `get_outliner_selection`, `get_outliner_tree`, `get_pinned_nodes`, `get_sections_for_nodes`, `get_soloed_nodes`, `is_node_expanded`, `is_node_expanded_by_path`, `set_node_deactivated`, `set_node_expanded`, `set_node_locked`, `set_node_muted`, `set_node_pinned`, `set_node_solo`, `set_nodes_expanded_by_path`, `set_outliner_selection` |
| `animation_toolset.toolsets.conditions.SequencerConditionTools` | 9 | `clear_section_condition`, `clear_track_condition`, `clear_track_row_condition`, `get_section_condition`, `get_track_condition`, `get_track_row_condition`, `set_section_condition`, `set_track_condition`, `set_track_row_condition` |
| `animation_toolset.toolsets.custom_bindings.SequencerCustomBindingTools` | 7 | `convert_to_custom_binding`, `convert_to_possessable`, `convert_to_spawnable`, `get_custom_binding_objects`, `get_custom_binding_type`, `get_custom_bindings_of_type`, `save_default_spawnable_state` |
| `animation_toolset.toolsets.import_export.SequencerImportExportTools` | 5 | `export_anim_sequence`, `get_linked_anim_sequences`, `get_linked_level_sequence`, `import_fbx`, `link_anim_sequence` |
| `ValkyrieToolset.ValkyriePythonToolset` | 2 | `EnablePythonForMainProject`, `IsPythonReadyForMainProject` |
| `ValkyrieToolset.EntityToolset` | 15 | `AddComponent`, `CreateEntity`, `DeleteEntity`, `FindEntities`, `GetComponentProperty`, `GetComponents`, `GetEntityTransform`, `ListComponentClasses`, `ListComponentProperties`, `ListEntityClasses`, `RemoveComponent`, `RenameEntity`, `ReparentEntity`, `SetComponentProperty`, `SetEntityTransform` |
| `ValkyrieToolset.PrefabToolset` | 8 | `ApplyPrefabEdits`, `BreakPrefabInstance`, `CreatePrefab`, `CreatePrefabFromEntities`, `GetPrefab`, `GetPrefabForEntity`, `GetPrefabOverrides`, `ResetPrefabInstance` |
| `geometry_toolset.geometry_ops.GeometryTools` | 6 | `append_box`, `append_cone`, `append_cylinder`, `append_disc`, `append_sphere`, `append_torus` |
| `editor_toolset.toolsets.programmatic.ProgrammaticToolset` | 2 | `execute_tool_script`, `get_execution_environment` |
| `editor_toolset.toolsets.python_scripting.PythonScriptingTools` | 5 | `execute_python`, `get_symbol`, `grep_stubs`, `read_me`, `search_symbols` |
| `SpatialProfilerToolset.ProfilerToolset` | 15 | `AcquireSource`, `ClearSamples`, `GetMetricHotspots`, `GetMetricStats`, `GetMonitorPerformanceEnabled`, `GetSamplingStatus`, `ListClients`, `ListMetrics`, `ListSources`, `OpenProfiler`, `ReleaseSource`, `RevealMetric`, `SetEnabledMetrics`, `StartSampling`, `StopSampling` |
| `ValkyrieFortniteToolset.SessionToolset` | 9 | `GetClientLogEntries`, `GetGameState`, `GetSessionStatus`, `GetVerseOutput`, `PushChanges`, `StartGame`, `StartSession`, `StopGame`, `StopSession` |
| `ValkyrieFortniteToolset.DeviceToolset` | 12 | `AddEventBinding`, `GetBindingOptions`, `GetClassicDeviceOptionValues`, `GetDeviceProperties`, `ListClassicDeviceOptions`, `ListDeviceAssets`, `ListDeviceProperties`, `ListEventBindings`, `PlaceDevice`, `RemoveEventBinding`, `SetClassicDeviceOption`, `SetDeviceProperty` |
| `SceneCaptureToolset.SceneCaptureToolset` | 8 | `Capture`, `CaptureActiveEditorView`, `CaptureGameViewport`, `DescribeMode`, `GetActiveEditorView`, `ListModes`, `ListViews`, `ListWorlds` |
| `InsightsToolset.InsightsTargetToolset` | 3 | `ListCaptures`, `ListSavedCaptures`, `ListTargets` |
| `InsightsToolset.TimingProfilerToolset` | 5 | `CanCapture`, `GetCaptureStatus`, `GetRecordedChannels`, `StartCapture`, `StopCapture` |
| `InsightsToolset.MemorySnapshotToolset` | 2 | `CanSnapshot`, `TakeSnapshot` |
| `UMGToolSet.UMGToolSet` | 20 | `AddUIComponent`, `AddWidget`, `CompileWidgetBlueprint`, `CreateWidgetBlueprint`, `GetContainerWidgetNavigationDoc`, `GetNamedSlots`, `GetWidgetClassInfo`, `GetWidgets`, `ListWidgetBlueprints`, `ListWidgetClasses`, `MoveUIComponent`, `MoveWidget`, `RemoveUIComponent`, `RemoveWidget`, `RenameWidget`, `ReplaceWidgetWithChild`, `ReplaceWidgetWithNamedSlot`, `ReplaceWidgetWithTemplate`, `SetNamedSlotContent`, `WrapWidgets` |
| `UMGToolSet.UMGDebugToolSet` | 6 | `ClearWidgetLifetimeLog`, `GetWidgetLifetimeEvents`, `GetWidgetLifetimeLogStatus`, `ShowWidgetLifetimeLogWindow`, `StartWidgetLifetimeLogging`, `StopWidgetLifetimeLogging` |
| `WidgetStaticAnalysisToolset.WidgetStaticAnalysisToolset` | 5 | `DescribeWidget`, `GetViewModelConnectionMap`, `GetWidgetConnectionMap`, `GetWidgetTreeDepth`, `TraceWidgetPropertyOverrides` |
| `WidgetAnimationToolset.WidgetAnimationToolset` | 10 | `AddWidgetToAnimation`, `CreateWidgetAnimation`, `FindWidgetAnimation`, `GetWidgetAnimationBindings`, `ListWidgetAnimations`, `RemoveWidgetAnimation`, `RemoveWidgetBinding`, `RenameWidgetAnimation`, `SetWidgetAnimationDisplayLabel`, `SetWidgetAnimationLength` |
| `FortGameplayToolset.FortPlayerToolset` | 1 | `GetLocalPlayerState` |
| **Total** | **826** | |

## Notes

- **PCG how-to:** Epic skill `/PCGToolset/Skills/Skill_PCGGraphGeneration.Skill_PCGGraphGeneration_C`
  (`ToolsetRegistry.AgentSkillToolset.GetSkills`) + leveldesign `procedural_generation`. PCGToolset has no
  `DuplicateGraph` or singular `SetGraphParam` (Epic's skill names both): use
  `EditorToolset.AssetToolset.Duplicate` and `SetGraphParams` instead.
- **PCG refs are objects:** `{"graph": {"refPath": "/<root>/F/G.G"}}`; node refs are
  `"<graph path>:<nodeName>"`.

- `ValkyrieToolset.ValkyriePythonToolset` (`IsPythonReadyForMainProject`,
  `EnablePythonForMainProject`): Python-backed toolsets (Sequencer, Geometry, PythonScripting,
  Programmatic) need Python enabled for the main project; enabling is asynchronous.
- `ConsoleToolset.LogsToolset.GetLogEntries(category, pattern, maxEntries)` reads the
  editor log (compile results, Content Pre-Check messages, blueprint errors).
  `ValkyrieFortniteToolset.SessionToolset.GetClientLogEntries` reads the launched client's log;
  `GetVerseOutput` reads Verse `Print` output.
- Profiling (`SpatialProfilerToolset`, `InsightsToolset.*`) needs a running session; order:
  `ListClients`/`ListTargets` (retry once, discovery is async) → acquire/`CanCapture` → sample/capture → stop.
- `VerseFieldsToolset.GetSupportedVerseFieldTypes` → 42.30: bool, int, float, string,
  message, color, color_alpha, texture, material, event; event params bool/int/float
  (max 1). Details: verse `umg_verse_field_events`.
- 42.30 fix: dialogue popups no longer stall MCP progress. Ducky's Save-modal
  watchdog (`dismiss_uefn_modal`) still covers older builds and other modals.
