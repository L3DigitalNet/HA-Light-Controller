# Copilot Instructions for HA-Light-Controller

## ⚠️ CRITICAL: Branch Policy

**ALL changes MUST be made on the `testing` branch.**

- **NEVER** push directly to `main` unless explicitly instructed by the user
- **NEVER** create commits on the `main` branch
- **ALWAYS** ensure you are on the `testing` branch before making changes
- If on `main`, switch to `testing` first: `git checkout testing`

A pre-push hook is installed to block accidental pushes to `main`. To bypass (only when explicitly instructed): `git push --no-verify origin main`

## Target Audience

Documentation and user-facing text should target **technically proficient Home Assistant users** who:

- Understand HA concepts (entities, states, services, domains, automations, scripts, scenes)
- Know HACS and custom integration installation
- Are comfortable with YAML and can read Python
- Understand Zigbee/Z-Wave and smart home networking basics

### Documentation Style

- Be concise; use technical terminology without over-explaining
- Prefer code examples over prose
- Use proper HA terminology (`entities`, `services`, `ConfigEntry`, etc.)
- Skip basic explanations (don't explain what HACS is)
- Reference parameters by name (e.g., "use the `targets` parameter")

## Project Overview

Home Assistant custom integration (`ha_light_controller`) for reliable light control with state verification, automatic retries, and preset management. Distributed via HACS.

## Architecture

### Core Components (Data Flow)

1. **[**init**.py](../custom_components/ha_light_controller/**init**.py)** - Entry point: registers 5 services, initializes `LightController` and `PresetManager`, merges call parameters with `entry.options` defaults
2. **[controller.py](../custom_components/ha_light_controller/controller.py)** - Light control logic:
   - `ensure_state()` → `_expand_entities()` → `_build_targets()` → `_group_by_settings()` → send commands → verify → retry loop
   - Key dataclasses: `LightTarget` (single light), `LightGroup` (batched lights), `OperationResult`
3. **[preset_manager.py](../custom_components/ha_light_controller/preset_manager.py)** - CRUD for presets stored in `ConfigEntry.data[CONF_PRESETS]`, listener pattern for entity updates
4. **[config_flow.py](../custom_components/ha_light_controller/config_flow.py)** - Menu-based options flow:
   - `settings` - All configuration in one page (defaults, tolerances, retry, notifications)
   - `add_preset` - Multi-step preset creation with per-entity configuration
   - `manage_presets` - Delete existing presets

### Entity Platforms

- **[button.py](../custom_components/ha_light_controller/button.py)** - `PresetButton` entities (one per preset)
- **[sensor.py](../custom_components/ha_light_controller/sensor.py)** - `PresetStatusSensor` entities tracking activation status (`idle`/`activating`/`success`/`failed`)

## Key Patterns

### Constants Convention

All `CONF_*` keys and `DEFAULT_*` values live in [const.py](../custom_components/ha_light_controller/const.py). When adding configurable options:

```python
CONF_NEW_OPTION: Final = "new_option"
DEFAULT_NEW_OPTION: Final = 10
```

### Service Parameter Merging

Service handlers merge call data with configured defaults from `entry.options`:

```python
brightness_tolerance = call.data.get(ATTR_BRIGHTNESS_TOLERANCE) or options.get(CONF_BRIGHTNESS_TOLERANCE, DEFAULT_BRIGHTNESS_TOLERANCE)
```

### Entity Expansion

`_expand_entity()` in controller.py resolves:

- `light.*` groups → individual lights
- `group.*` helper groups → member entities
- Returns only `light.` domain entities

### Dataclass-to-Dict Pattern

`PresetConfig` and other dataclasses use `from_dict()`/`to_dict()` for ConfigEntry storage. Use `PRESET_*` constants for dict keys.

### Listener Pattern for Entity Updates

`PresetManager.register_listener()` returns unsubscribe callable. Platforms use this to add/remove entities when presets change.

## Home Assistant Integration Patterns

- **Storage**: `ConfigEntry.data` for presets, `ConfigEntry.options` for settings
- **Service responses**: Use `SupportsResponse.OPTIONAL`
- **Platform setup**: `async_forward_entry_setups(hass, entry, PLATFORMS)`
- **Options reload**: `entry.add_update_listener(async_reload_entry)`
- **Device grouping**: All entities share `DeviceInfo` with `identifiers={(DOMAIN, entry.entry_id)}`

## Development

```bash
# Copy to Home Assistant for testing
cp -r custom_components/ha_light_controller /path/to/config/custom_components/

# Enable debug logging in configuration.yaml
logger:
  logs:
    custom_components.ha_light_controller: debug
```

No build steps required. Domain is `ha_light_controller`. Services: `ensure_state`, `activate_preset`, `create_preset`, `delete_preset`, `create_preset_from_current`.

## Testing

The integration has a comprehensive pytest test suite in `tests/`.

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=custom_components/ha_light_controller

# Run specific test file
pytest tests/test_controller.py -v
```

Test files: `test_init.py`, `test_controller.py`, `test_config_flow.py`, `test_preset_manager.py`, `test_button.py`, `test_sensor.py`.

## Adding Service Parameters

When adding a new parameter to a service (e.g., `ensure_state`):

1. **const.py** - Add `ATTR_*` constant and `DEFAULT_*` if configurable:

   ```python
   ATTR_NEW_PARAM: Final = "new_param"
   DEFAULT_NEW_PARAM: Final = 5
   ```

2. \***\*init**.py\*\* - Add to voluptuous schema and service handler:

   ```python
   # In SERVICE_ENSURE_STATE_SCHEMA
   vol.Optional(ATTR_NEW_PARAM): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),

   # In async_handle_ensure_state()
   new_param = call.data.get(ATTR_NEW_PARAM, options.get(CONF_NEW_PARAM, DEFAULT_NEW_PARAM))
   ```

3. **services.yaml** - Add field definition with HA selector:

   ```yaml
   new_param:
     name: New Parameter
     description: Description for UI
     selector:
       number:
         min: 0
         max: 100
         mode: slider
   ```

4. **controller.py** - Add parameter to `ensure_state()` signature and use it

## Creating Blueprints

Blueprints live in `blueprints/automation/ha_light_controller/`. Structure:

```yaml
blueprint:
  name: Blueprint Name
  description: Multi-line description
  domain: automation
  author: Light Controller
  source_url: https://github.com/L3DigitalNet/HA-Light-Controller/blueprints/...

  input:
    # Use HA selectors matching services.yaml patterns
    target_lights:
      name: Target Lights
      selector:
        entity:
          domain: light
          multiple: true

trigger:
  - platform: state
    entity_id: !input motion_sensor

action:
  - service: ha_light_controller.ensure_state
    data:
      entities: !input target_lights
      brightness_pct: !input brightness_pct
```

Reference `!input` variables from the input section. Use same selectors as `services.yaml` for consistency.

## File Naming

- Blueprints: `custom_components/ha_light_controller/blueprints/automation/ha_light_controller/*.yaml`
- Translations: `translations/en.json`, `strings.json` (for config flow)
- Service definitions: `services.yaml` with Home Assistant selector syntax

## MCP Servers

Use these MCP servers when working on this project:

- **Sequential Thinking** (`mcp_sequentialthinking_sequentialthinking`) - Use for complex multi-step tasks like adding new services, refactoring controller logic, or debugging verification failures. Helps break down problems systematically.

- **Context7** (`mcp_context7_resolve-library-id`, `mcp_context7_get-library-docs`) - Use to look up Home Assistant integration development docs, voluptuous schema patterns, or Python async patterns. Query with library IDs like `home-assistant` or `voluptuous`.
