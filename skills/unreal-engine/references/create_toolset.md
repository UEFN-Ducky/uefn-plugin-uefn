---
description: "Author or extend an Unreal Engine toolset (static AI-callable functions registered with ToolsetRegistry, exposed via unreal-mcp) in C++ (UToolsetDefinition, UFUNCTION AICallable, async results, JSON converters, RaiseScriptError, BEGIN_DEFINE_SPEC tests) or Python (@toolset_registry.tool_call, ToolCallTestCase): principles, docs rules, registration, AutomationTestToolset testing, review checklist"
metadata:
  order: 3
  label: "Authoring Unreal toolsets"
  default_enabled: false
  load_condition: "Adding, exposing or registering a tool/toolset for unreal-mcp, editing *Tools.cpp/.h/.py or a Toolsets/ folder, designing tool params/returns/struct schemas"
---

# Create Toolset

Adapted from Epic `skills/create-toolset` (MIT). A toolset is a collection of static, AI-callable functions registered with `ToolsetRegistry` and exposed through the MCP server — the way to expand what the agent can do in the editor. Skip for: calling existing tools (`core`), authoring Agent Skills (`agent_skills`), refactors that don't add or redesign a tool. UEFN islands restrict Python — this is for UE5 projects and plugins.

## Principles

- **Clean** — the simplest API that does useful domain work. Don't mirror Unreal's (often overcomplex) APIs. Test: would a technical artist understand it without reading the implementation?
- **Complete** — CRUD symmetry: set ⇒ get, create ⇒ delete. Getters without setters are fine when mutation isn't possible or useful.
- **Composable** — same types for the same kinds of operation. If `get_graph()` returns a `Graph`, `get_graph_nodes()` takes a `Graph`.
- **DRY** — no duplication within or across toolsets. `ObjectTools` already does generic UObject property get/set; don't reimplement it.

## Before you write (in order)

1. **Exists already?** Editor running → `list_toolsets`, then `describe_toolset` on anything relevant. No MCP → search for folders named `Toolsets` and read the C++ headers / Python files. Already exposed → tell the user, point to the tool, stop.
2. **More general than it sounds?** "Read Blueprint asset metadata" is really asset metadata → `AssetTools`, not `BlueprintTools`. Generic beats narrow.
3. **Domain toolset exists?** Add to it (a mesh query → `StaticMeshTools`) rather than a new one.
4. **Own plugin?** Closely related to an existing plugin → add there; a distinct domain may warrant its own plugin. Ask if it isn't obvious.
5. **Language (the user's call — help them decide).** Python is generally preferred (faster iteration, easier change).
   - **Python:** search (don't read wholesale) `<project_root>/Intermediate/PythonStub/unreal.py`. Missing → the user enables **Developer Mode** in Edit → Project Settings → Plugins → Python and restarts (recommend it proactively for any toolset work). All needed APIs present → Python. Something small missing → flag it; a minor engine tweak may still make Python better overall.
   - **C++:** when Python coverage is thin or absent.
   Summarize both and let the user choose before writing code. If neither language has the APIs, **don't work around it** — stop and tell the user so they can extend the engine. Workarounds break silently.

## Shared conventions

- Don't duplicate existing tools.
- Documentation is required at every level.
- **Real types** for params and returns (`int32`, `FVector`, `TArray<FString>`, structs). The registry serializes. JSON inside a string is a code smell; a string must really be a string.
- **Returns carry data, not status.** Normal return = success, raise = failure. Never return a bool, error string or result wrapper for errors.
- All tool methods are **static**; no instance state.
- **Tests are mandatory** for every tool.

## Documentation

Short and precise beats long. The test for every line: **could a competent reader infer this from the signature, names and types alone? Then cut it.** LLMs over-document by default — resist. Cut signature restatement (types, defaults, optionality), usage/chaining narration, worked examples of the obvious, speculation about what a field might contain. Document what the code does, not why you built it that way ("iterates subclasses directly because the asset registry misses unloaded types" is rationale, not contract). Keep: units, ranges, non-obvious encodings ("a single space-separated string"), what an empty or null result means, domain meaning the name doesn't carry.

```cpp
// Over-documented: every line restates the signature or narrates usage.
/**
 * Runs a cheat. @param CheatName The cheat name (case-insensitive), pass it to run the cheat.
 * @param Args Optional arguments; fill in the slots from the Args hint (e.g. "<float F>" -> "2.0",
 *             "<float A> <float B>" -> "1 2"). Empty string for no arguments.
 */
// Trimmed: only the non-inferable facts remain.
/**
 * Runs a cheat on the local player, as if typed into the console.
 * @param CheatName The cheat command name.
 * @param Args Arguments as a single space-separated string. Empty for none.
 */
```

- **Toolset class:** 1–3 sentences on the domain and kinds of operations. It must stand alone — an LLM often sees only the name and this, never the tools. Don't enumerate tool names.
- **Each tool:** what it does, every parameter, the return value. Meaning and units.
- **Structs:** the struct (what it represents, when used) and every field (meaning, units). `ClampMin` / `ClampMax` UPROPERTY metadata is extracted into the schema automatically — use it instead of restating constraints.

## C++

### Structure

- Derive from `UToolsetDefinition` (`ToolsetRegistry/ToolsetDefinition.h`). One toolset class per `.h` / `.cpp`.
- AI-callable tools: **static** methods with `UFUNCTION(meta = (AICallable))`; the doc comment becomes the AI-visible description.
- Private helpers: static methods without `AICallable`.

```cpp
/**
 * Snapshot of a MyThing's current state, returned by GetThingInfo.
 */
USTRUCT(BlueprintType)
struct FMyThingInfo
{
    GENERATED_BODY()

    /** How thing-like this thing is. */
    UPROPERTY(meta=(ClampMin="0.0", ClampMax="1.0")) float Thinginess;

    /** Things that belong to this thing. */
    UPROPERTY() TArray<UMyThing*> SubThings;
};

/**
 * Manages MyThings in the current level. Covers the full lifecycle of these objects:
 * querying by name, reading their state, and performing operations on them.
 */
UCLASS(BlueprintType, MinimalAPI)
class UMyToolset : public UToolsetDefinition
{
    GENERATED_BODY()

public:
    /**
     * Returns all things whose name matches the given pattern.
     * @param NamePattern Substring to match against thing names.
     * @return Matching things, or an empty array if none are found.
     */
    UFUNCTION(meta = (AICallable), Category = "MyToolset")
    static TArray<UMyThing*> FindThings(const FString& NamePattern);

    /**
     * Returns detailed info about the given thing.
     * @param Thing The thing to read state from.
     * @return The thing's current state.
     */
    UFUNCTION(meta = (AICallable), Category = "MyToolset")
    static FMyThingInfo GetThingInfo(UMyThing* Thing);

    /**
     * Performs the primary operation on the given thing.
     * @param Thing The thing to perform the operation on.
     */
    UFUNCTION(meta = (AICallable), Category = "MyToolset")
    static void DoTheThing(UMyThing* Thing);
};
```

### Async tool calls

Most tools are synchronous on the game thread. Long-running work (capturing a screenshot, waiting for an editor state change) returns a `UToolCallAsyncResult` subclass instead of the value. Many result types exist — check them before subclassing a new one. Success and failure both go through the result: `SetValue()` / `SetError()`.

```cpp
/**
 * Renders an image of the given thing.
 * @param Thing The thing to capture.
 * @return An image of the thing.
 */
UFUNCTION(meta = (AICallable), Category = "MyToolset")
static UToolCallAsyncResultImage* CaptureThingImage(UMyThing* Thing);

UToolCallAsyncResultImage* UMyToolset::CaptureThingImage(UMyThing* Thing)
{
    UToolCallAsyncResultImage* Result = NewObject<UToolCallAsyncResultImage>();

    if (!IsRenderingEnabled())
    {
        Result->SetError(TEXT("Rendering is not enabled."));
        return Result;
    }

    // Initiate the capture; call Result->SetValue(image) on completion.
    return Result;
}
```

The right implementation depends on the system — read existing toolsets for real examples first.

### Registration

Dynamic, any time; commonly module startup/shutdown (match nearby toolsets in the same plugin):

```cpp
class FMyToolsetModule : public IModuleInterface
{
    void StartupModule()
    {
        UToolsetRegistry::RegisterToolsetClass(UMyToolset::StaticClass());
    }

    void ShutdownModule()
    {
        UToolsetRegistry::UnregisterToolsetClass(UMyToolset::StaticClass());
    }
};
```

### Custom type-to-JSON converters

The registry converts all Unreal types to/from JSON automatically. Converters give extra control over one type's representation (a cleaner, more AI-friendly schema). Advanced — use only reactively, on a clear need. Built-ins:

- **`FToolsetColorConverter`** — unifies `FColor` and `FLinearColor` so the AI needn't know byte vs float.
- **`FToolsetReferenceConverter`** — UObject\* / UClass\* properties become typed soft path objects instead of raw strings.
- **`FToolsetTransformConverter`** — `FTransform` location, rotation, scale as optional fields.

New one: subclass `FToolsetJsonConverter` (`ToolsetRegistry/ToolsetJsonConverter.h`) and register it alongside the toolset. Read an existing converter in the ToolsetRegistry source first — the interface has several moving parts.

### Error handling

Raise a script error and return immediately with a null/default value:

```cpp
TArray<UMyThing*> UMyToolset::FindThings(const FString& NamePattern)
{
    if (NamePattern.IsEmpty())
    {
        UKismetSystemLibrary::RaiseScriptError(
            EScriptExceptionType::Error,
            TEXT("NamePattern must not be empty."));
        return {};
    }
}
```

### Tests

Compile first with `LiveCodingToolset.CompileLiveCoding` (blocks until done, returns MSVC diagnostics); fix errors. Each tool: at least one success test plus one test per raise path. `BEGIN_DEFINE_SPEC` / `END_DEFINE_SPEC`; reference tests live in `Plugins/Experimental/Toolsets`; place tests near the toolset following the plugin's convention.

```cpp
BEGIN_DEFINE_SPEC(
    FMyToolsetSpec,
    "AI.MyToolset",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
END_DEFINE_SPEC(FMyToolsetSpec)

void FMyToolsetSpec::Define()
{
    Describe("FindThings", [this]()
    {
        It("returns matching things", [this]()
        {
            TArray<UMyThing*> Results = UMyToolset::FindThings(TEXT("expected_name"));
            TestFalse(TEXT("Result is not empty"), Results.IsEmpty());
        });

        It("returns an empty array when no things match", [this]()
        {
            TArray<UMyThing*> Results = UMyToolset::FindThings(TEXT("nonexistent"));
            TestTrue(TEXT("Result is empty"), Results.IsEmpty());
        });

        It("raises when the name pattern is empty", [this]()
        {
            AddExpectedError(TEXT("NamePattern must not be empty"));
            UMyToolset::FindThings(TEXT(""));
        });
    });
}
```

## Python

### Structure

- Decorate with `@unreal.uclass()` and inherit `unreal.ToolsetDefinition`; one class per `.py`.
- Tools: `@toolset_registry.tool_call` then `@staticmethod`; the docstring is the AI-visible description.
- Private helpers: `@staticmethod`, `_`-prefixed, at the end of the class.
- **Type annotations are mandatory** on every parameter and return (schema generation depends on them). Use standard hints (`list[str]`, `dict[str, str]`), not `unreal.Array[str]`; the decorator converts.

```python
@unreal.uclass()
class MyToolset(unreal.ToolsetDefinition):
    """Manages MyThings in the current level. Covers the full lifecycle of these objects:
    querying by name, reading their state, and performing operations on them."""

    @toolset_registry.tool_call
    @staticmethod
    def find_things(name_pattern: str) -> list[MyThing]:
        """Returns all things whose name matches the given pattern.

        Args:
            name_pattern: Substring to match against thing names.

        Returns:
            Matching things, or an empty list if none are found.
        """
        ...

    @toolset_registry.tool_call
    @staticmethod
    def get_thing_info(thing: MyThing) -> MyThingInfo:
        """Returns detailed info about the given thing.

        Args:
            thing: The thing to read state from.

        Returns:
            The thing's current state.
        """
        ...

    @toolset_registry.tool_call
    @staticmethod
    def do_the_thing(thing: MyThing) -> None:
        """Performs the primary operation on the given thing.

        Args:
            thing: The thing to perform the operation on.
        """
        ...
```

### Registration

Never automatic. Add the class to the plugin's registration list and call it during initialization (`__init__.py` / `init_unreal.py`, next to sibling toolsets):

```python
def register_toolsets():
    unreal.ToolsetRegistry.register_toolset_class(MyToolset)

def unregister_toolsets():
    unreal.ToolsetRegistry.unregister_toolset_class(MyToolset)
```

### Error handling

Raise directly:

```python
@toolset_registry.tool_call
@staticmethod
def find_things(name_pattern: str) -> list[MyThing]:
    """Returns things whose name matches the given pattern."""
    if not name_pattern:
        raise ValueError("name_pattern must not be empty.")
```

### Tests

Extend `ToolCallTestCase`; error paths with `assertToolRaisesRuntimeError`:

```python
class MyToolsetTestCase(ToolCallTestCase):
    """Test MyToolset toolset."""

    def test_find_things_returns_matches(self):
        """Returns matching things when they exist."""
        results = MyToolset.find_things("expected_name")
        self.assertGreater(len(results), 0)

    def test_find_things_returns_empty_for_no_match(self):
        """Returns an empty list when no things match the pattern."""
        results = MyToolset.find_things("nonexistent")
        self.assertEqual(results, [])

    def test_find_things_raises_on_empty_pattern(self):
        """Raises when name_pattern is empty."""
        with self.assertToolRaisesRuntimeError():
            MyToolset.find_things("")
```

Reload the plugin's package before re-running (enable Edit → Project Settings → Plugins → Python → Enable Remote Execution):

```bash
python Engine/Plugins/Experimental/ToolsetRegistry/Content/Python/toolset_registry/tests/reload_remote.py your_plugin
```

## Testing your work

Tight loop: write → compile if needed → run → read failures → fix → repeat until green.

**Live editor (preferred; C++ and Python):**

1. `AutomationTestToolset.DiscoverTests` — required before any other test tool; skipping it gives empty results. After a Python reload pass `force_rediscover=true`.
2. `ListTests` filtered to your toolset name.
3. `RunTests` with the full test paths.
4. Poll `GetTestStatus`, then `GetTestResults` for per-test errors and warnings.

**Command line (no editor; CI; ~30 s startup):**

```bash
UnrealEditor-Cmd.exe <Project>.uproject -ExecCmds="Automation RunTests AI.MyToolset;quit" -Unattended -NullRHI
```

Use the filter prefix and flags the plugin's existing tests use.

## Review before handing off

Read the whole thing once more:

- **Duplicated boilerplate** across tools → a shared helper.
- **Incomplete coverage** — a late raise path without a test; a success case checking one scenario.
- **Duplicate functionality** vs this toolset or another.
- **API inconsistency** — parameter names/types off-convention.
- **Documentation gaps** — a vague parameter; a class doc that doesn't stand alone.
- **Documentation restating code** — type, default or call sequence; obvious examples; rationale. Cut it.
