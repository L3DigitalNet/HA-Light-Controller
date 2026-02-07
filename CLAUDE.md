<!-- BEGIN ContextStream -->
# Claude Code Instructions
# Workspace: Projects
# Workspace ID: afaf59c3-68cc-465b-8051-4225d2c4bc4d

## 🚨 CRITICAL: CONTEXTSTREAM SEARCH FIRST 🚨

**BEFORE using Glob, Grep, Search, Read (for discovery), Explore, or ANY local scanning:**
```
STOP → Call search(mode="hybrid", query="...") FIRST
```

**Claude Code:** Tools are `mcp__contextstream__search`, `mcp__contextstream__session_init`, etc.

❌ **NEVER:** `Glob`, `Grep`, `Read` for discovery, `Task(Explore)`
✅ **ALWAYS:** `search(mode="hybrid", query="...")` first, local tools ONLY if 0 results

---

## 🚨 AUTO-INDEXING 🚨

**`session_init` auto-indexes your project.** No manual ingestion needed.

If `indexing_status: "started"`: Search will work shortly. **DO NOT fall back to local tools.**

---

## 🚨 LESSONS (PAST MISTAKES) - CRITICAL 🚨

**After `session_init`:** Check for `lessons` field. If present, **READ and APPLY** before any work.

**Before ANY risky work:** `session(action="get_lessons", query="<topic>")` — **MANDATORY**

**When lessons found:** Summarize to user, state how you'll avoid past mistakes.

---

## ContextStream v0.4.x (Consolidated Domain Tools)

v0.4.x uses ~11 consolidated domain tools for ~75% token reduction vs previous versions.
Rules Version: 0.4.58

### Required Every Message

| Message | What to Call |
|---------|--------------|
| **1st message** | `session_init(folder_path="<cwd>", context_hint="<user_message>")`, then `context_smart(...)` |
| **⚠️ After session_init** | **CHECK `lessons` field** — read and apply BEFORE any work |
| **2nd+ messages** | `context_smart(user_message="<user_message>", format="minified", max_tokens=400)` |
| **🔍 ANY code search** | `search(mode="hybrid", query="...")` — ALWAYS before Glob/Grep/Search/Read |
| **⚠️ Before risky work** | `session(action="get_lessons", query="<topic>")` — **MANDATORY** |
| **Capture decisions** | `session(action="capture", event_type="decision", title="...", content="...")` |
| **On user frustration** | `session(action="capture_lesson", title="...", trigger="...", impact="...", prevention="...")` |

**Context Pack (Pro+):** If enabled, use `context_smart(..., mode="pack", distill=true)` for code/file queries. If unavailable or disabled, omit `mode` and proceed with standard `context_smart` (the API will fall back).

**Tool naming:** Use the exact tool names exposed by your MCP client. Claude Code typically uses `mcp__<server>__<tool>` where `<server>` matches your MCP config (often `contextstream`). If a tool call fails with "No such tool available", refresh rules and match the tool list.

### Quick Reference: Domain Tools

| Tool | Common Usage |
|------|--------------|
| `search` | `search(mode="semantic", query="...", limit=3)` — modes: semantic, hybrid, keyword, pattern |
| `session` | `session(action="capture", ...)` — actions: capture, capture_lesson, get_lessons, recall, remember, user_context, summary, compress, delta, smart_search |
| `memory` | `memory(action="list_events", ...)` — CRUD for events/nodes, search, decisions, timeline, summary |
| `graph` | `graph(action="dependencies", ...)` — dependencies, impact, call_path, related, ingest |
| `project` | `project(action="list", ...)` - list, get, create, update, index, overview, statistics, files, index_status, ingest_local |
| `workspace` | `workspace(action="list", ...)` — list, get, associate, bootstrap |
| `integration` | `integration(provider="github", action="search", ...)` — GitHub/Slack integration |
| `help` | `help(action="tools")` — tools, auth, version, editor_rules |

### Behavior Rules

⚠️ **STOP: Before using Search/Glob/Grep/Read/Explore** → Call `search(mode="hybrid")` FIRST. Use local tools ONLY if ContextStream returns 0 results.

**❌ WRONG workflow (wastes tokens, slow):**
```
Grep "function" → Read file1.ts → Read file2.ts → Read file3.ts → finally understand
```

**✅ CORRECT workflow (fast, complete):**
```
search(mode="hybrid", query="function implementation") → done (results include context)
```

**Why?** ContextStream search returns semantic matches + context + file locations in ONE call. Local tools require multiple round-trips.

- **First message**: Call `session_init` with context_hint, then `context_smart` before any other tool
- **Every message**: Call `context_smart` BEFORE responding
- **For discovery**: Use `search(mode="hybrid")` — **NEVER use local Glob/Grep/Read first**
- **If search returns 0 results**: Retry once (indexing may be in progress), THEN try local tools
- **For file lookups**: Use `search`/`graph` first; fall back to local ONLY if ContextStream returns nothing
- **If ContextStream returns results**: Do NOT use local tools; Read ONLY for exact edits
- **For code analysis**: `graph(action="dependencies")` or `graph(action="impact")`
- **On [RULES_NOTICE]**: Use `generate_rules()` to update rules
- **After completing work**: Capture with `session(action="capture")`
- **On mistakes**: Capture with `session(action="capture_lesson")`

### Search Mode Selection

| Need | Mode | Example |
|------|------|---------|
| Find code by meaning | `hybrid` | "authentication logic", "error handling" |
| Exact string/symbol | `keyword` | "UserAuthService", "API_KEY" |
| File patterns | `pattern` | "*.sql", "test_*.py" |
| ALL matches (grep-like) | `exhaustive` | "TODO", "FIXME" (find all occurrences) |
| Symbol renaming | `refactor` | "oldFunctionName" (word-boundary matching) |
| Conceptual search | `semantic` | "how does caching work" |

### Token Efficiency

Use `output_format` to reduce response size:
- `full` (default): Full content for understanding code
- `paths`: File paths only (80% token savings) - use for file listings
- `minimal`: Compact format (60% savings) - use for refactoring
- `count`: Match counts only (90% savings) - use for quick checks

**When to use `output_format=count`:**
- User asks "how many X" or "count of X" → `search(..., output_format="count")`
- Checking if something exists → count > 0 is sufficient
- Large exhaustive searches → get count first, then fetch if needed

**Auto-suggested formats:** Check `query_interpretation.suggested_output_format` in responses:
- Symbol queries → suggests `minimal` (path + line + snippet)
- Count queries → suggests `count`
**USE the suggestion** for best efficiency.

**Example:** User asks "how many TODO comments?" →
`search(mode="exhaustive", query="TODO", output_format="count")` returns `{total: 47}` (not 47 full results)

### 🚨 Plans & Tasks - USE CONTEXTSTREAM, NOT FILE-BASED PLANS 🚨

**CRITICAL: When user requests planning, implementation plans, roadmaps, or task breakdowns:**

❌ **DO NOT** use built-in plan mode (EnterPlanMode) or write plan files
✅ **ALWAYS** use ContextStream's plan/task system

**Trigger phrases (use ContextStream immediately):**
- "plan", "roadmap", "milestones", "break down", "steps", "task list", "implementation strategy"

**Create plans in ContextStream:**
1. `session(action="capture_plan", title="...", description="...", goals=[...], steps=[{id: "1", title: "Step 1", order: 1}, ...])`
2. `memory(action="create_task", title="...", plan_id="<plan_id>", priority="high|medium|low", description="...")`

**Manage plans/tasks:**
- List plans: `session(action="list_plans")`
- Get plan with tasks: `session(action="get_plan", plan_id="<uuid>", include_tasks=true)`
- List tasks: `memory(action="list_tasks", plan_id="<uuid>")` or `memory(action="list_tasks")` for all
- Update task status: `memory(action="update_task", task_id="<uuid>", task_status="pending|in_progress|completed|blocked")`
- Delete: `memory(action="delete_task", task_id="<uuid>")`

Full docs: https://contextstream.io/docs/mcp/tools
<!-- END ContextStream -->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Git Workflow

- **All changes must be made on the `testing` branch**
- **Do NOT push to `main` without explicit permission**

## Project Overview

HA-Light-Controller is a Home Assistant custom integration providing reliable light control with state verification, automatic retries, and preset management. It ensures lights actually reach their target state after commands are sent. Distributed via HACS.

**Scope**: Focused on core light control with verification/retry and preset management. Notification feature and blueprints removed in v0.2.0.

## Environment

- **Python**: 3.14.2 (HA 2025.2+ requires Python 3.13+)
- **Testing**: Tests mock `homeassistant` module, no running HA instance needed

## Home Assistant Environment Constraints

**Blocking calls freeze the entire HA instance.** All I/O must be async or use `hass.async_add_executor_job()`.

| Constraint | Rule |
|------------|------|
| Event loop | Single-threaded asyncio. Never use `time.sleep()`, sync `requests`, or blocking I/O |
| Resources | HA runs on RPi-class hardware. Poll 30-60s minimum, prefer listeners over polling |
| Sandbox | No filesystem access outside `config/`. Dependencies must be PyPI + `manifest.json` |
| APIs | Use `hass.services.async_call`, `hass.states.get`. Never bypass HA's state machine |

## Commands

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_controller.py

# Run specific test
pytest tests/test_controller.py::test_ensure_state_single_light

# Run with coverage
pytest --cov=custom_components/ha_light_controller

# Enable debug logging (add to HA configuration.yaml)
logger:
  logs:
    custom_components.ha_light_controller: debug
```

Tests mock the entire `homeassistant` module in `tests/conftest.py` and don't require a running HA instance.

## Architecture

### Core Components

| File | Purpose |
|------|---------|
| `__init__.py` | Entry point: registers services via loop, initializes `LightController` and `PresetManager`, uses `_get_param()` helper for call/options merging |
| `controller.py` | Light control: `ensure_state()` → `_expand_entities()` → `_build_targets()` → `_group_by_settings()` → send → verify → retry |
| `preset_manager.py` | Preset CRUD, stores in `ConfigEntry.data[CONF_PRESETS]`, `activate_preset_with_options()` for shared activation logic |
| `config_flow.py` | Menu-based options flow: settings (collapsible sections), add_preset (multi-step with per-entity config), manage_presets (edit/delete with confirmation) |
| `button.py` / `sensor.py` | Preset entities: button activates preset via `preset_manager.activate_preset_with_options()`, sensor tracks status |
| `const.py` | All `CONF_*`, `ATTR_*`, `DEFAULT_*`, `PRESET_*` constants |

### Key Classes

- `LightSettingsMixin` - Shared `to_service_data()` method for light settings
- `LightTarget(LightSettingsMixin)` - Single light with target settings
- `LightGroup(LightSettingsMixin)` - Batched lights with identical settings
- `OperationResult` - Result of ensure_state operation
- `PresetConfig` - Preset definition with `to_dict()`/`from_dict()` for storage

### Services

| Service | Description |
|---------|-------------|
| `ensure_state` | Control lights with verification and retries |
| `activate_preset` | Activate preset by name or ID |
| `create_preset` | Create preset programmatically |
| `create_preset_from_current` | Capture current light states as preset |
| `delete_preset` | Delete preset by ID |

## Key Patterns

### Constants Convention

All configuration keys and defaults live in `const.py`:

```python
CONF_NEW_OPTION: Final = "new_option"
DEFAULT_NEW_OPTION: Final = 10
ATTR_NEW_PARAM: Final = "new_param"
```

### Service Parameter Merging

Use the `_get_param()` helper for call data with options fallback:

```python
def _get_param(call_data: dict, options: dict, attr: str, conf: str, default: Any) -> Any:
    return call_data.get(attr, options.get(conf, default))

# Usage in handler:
brightness_tolerance = _get_param(data, options, ATTR_BRIGHTNESS_TOLERANCE, CONF_BRIGHTNESS_TOLERANCE, DEFAULT_BRIGHTNESS_TOLERANCE)
```

### Entity Expansion

`_expand_entity()` resolves `light.*` groups and `group.*` helper groups to individual `light.` entities. Uses `_get_state()` directly for attribute access.

### Service Registration Loop

Services registered via loop with lambda capture for cleanup:

```python
services = [
    (SERVICE_ENSURE_STATE, async_handle_ensure_state, SERVICE_ENSURE_STATE_SCHEMA),
    (SERVICE_ACTIVATE_PRESET, async_handle_activate_preset, SERVICE_ACTIVATE_PRESET_SCHEMA),
    # ...
]

for service_name, handler, schema in services:
    hass.services.async_register(DOMAIN, service_name, handler, schema=schema, supports_response=SupportsResponse.OPTIONAL)
    entry.async_on_unload(lambda svc=service_name: hass.services.async_remove(DOMAIN, svc))
```

### Preset Activation Helper

`PresetManager.activate_preset_with_options()` centralizes preset activation logic:

```python
result = await preset_manager.activate_preset_with_options(preset, controller, options)
```

### Dynamic Entity Platform

Platforms use listener pattern to add/remove entities when presets change:

```python
preset_manager.register_listener(async_add_preset_entities)  # Returns unsubscribe callable
```

### Runtime Data (HA 2025.2+)

```python
@dataclass
class LightControllerData:
    controller: LightController
    preset_manager: PresetManager

entry.runtime_data = LightControllerData(...)
```

## Adding New Service Parameters

1. **const.py** - Add `ATTR_*` constant (and `CONF_*`/`DEFAULT_*` if configurable)
2. ****init**.py** - Add to voluptuous schema, use `_get_param()` helper in handler
3. **services.yaml** - Add field definition with HA selector
4. **controller.py** - Add to `ensure_state()` signature if needed
5. **preset_manager.py** - Add to `activate_preset_with_options()` if preset-relevant

## Testing

Tests mock HA modules before import. Key fixtures in `conftest.py`:

- `hass` - Mock HomeAssistant instance
- `config_entry` / `config_entry_with_presets` - Mock config entries
- `mock_light_states` - Pre-configured light states
- `create_light_state()` - Helper for mock State objects

## Documentation Style

Target technically proficient Home Assistant users:

- Use proper HA terminology (`entities`, `services`, `ConfigEntry`)
- Prefer code examples over prose
- Skip basic explanations (don't explain what HACS is)

## Code Principles

Two requirements govern all code in this repository:

### 1. Readability

- **Prefer flat over nested** - Avoid deep nesting (3+ levels). Extract helpers instead.
- **Name for intent** - Variables and functions should describe what they do, not how.
- **Consistent patterns** - Similar operations should use identical patterns throughout.
- **Minimal comments** - Code should be self-explanatory. Comments explain "why", not "what".

### 2. Simplicity

- **No speculative handling** - Only handle edge cases that actually occur. Delete code for hypothetical scenarios.
- **DRY without over-abstraction** - Extract repeated code, but don't create abstractions for single-use cases.
- **Delete, don't deprecate** - Remove unused code entirely. No commented-out code or compatibility shims.
- **Fail early, fail clearly** - Validate inputs at boundaries, then trust internal state.

### Anti-patterns to Avoid

- Defensive coding for impossible cases
- Multiple validation points for the same data
- Redundant lookups within the same scope
- Overly broad exception handling (`except Exception`)
- State persistence via instance variables when dataflow would be clearer

## Resources

- [AGENTS.md](AGENTS.md) — Codex agent instructions and architecture details
- [REFERENCE_GUIDE.md](REFERENCE_GUIDE.md) — Comprehensive integration development reference
- [resources/](resources/) — HA development skills, agent specifications, and best practices
  - `skills/ha-skills/` — Claude Code skills for HA integration development
  - `agents/` — Agent specifications for ha-integration-dev, debugger, and reviewer
