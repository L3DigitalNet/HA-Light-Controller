# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Git Workflow

- **All changes must be made on the `testing` branch**
- **Do NOT push to `main` without explicit permission**

## Project Overview

HA-Light-Controller is a Home Assistant custom integration providing reliable light control with state verification, automatic retries, and preset management. It ensures lights actually reach their target state after commands are sent. Distributed via HACS.

**Scope**: Focused on core light control with verification/retry and preset management. Notification feature and blueprints removed in v0.2.0.

## Environment

- **Python**: 3.12 (required by Home Assistant 2024.4+)
- **Testing**: Tests mock `homeassistant` module, no running HA instance needed

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

### Runtime Data (HA 2024.4+)

```python
@dataclass
class LightControllerData:
    controller: LightController
    preset_manager: PresetManager

entry.runtime_data = LightControllerData(...)
```

## Adding New Service Parameters

1. **const.py** - Add `ATTR_*` constant (and `CONF_*`/`DEFAULT_*` if configurable)
2. **__init__.py** - Add to voluptuous schema, use `_get_param()` helper in handler
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
