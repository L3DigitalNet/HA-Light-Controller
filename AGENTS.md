# AGENTS.md

This file provides guidance to Codex when working in this repository.

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

This is a Home Assistant custom integration (`ha_light_controller`) that provides reliable light control with state verification, automatic retries, and preset management. It is distributed via HACS.

## Development Environment

This is a pure Python Home Assistant integration with no build steps.

To develop locally:

1. Copy `custom_components/ha_light_controller` to your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.
3. Enable debug logging:

   ```yaml
   logger:
     logs:
       custom_components.ha_light_controller: debug
   ```

## Architecture (Key Files)

- `custom_components/ha_light_controller/__init__.py`
  - Integration entry point. Registers services via loop, uses `_get_param()` helper for call/options merging.
- `custom_components/ha_light_controller/controller.py`
  - `LightController` implements light control, entity expansion, target grouping, verification, and retry logic.
  - `LightSettingsMixin` provides shared `to_service_data()` for `LightTarget` and `LightGroup`.
- `custom_components/ha_light_controller/preset_manager.py`
  - `PresetManager` handles preset CRUD, storage, status tracking, and `activate_preset_with_options()` for centralized preset activation.
- `custom_components/ha_light_controller/config_flow.py`
  - Config flow and options flow for UI setup. Uses collapsible sections for settings, supports preset editing and delete confirmation.
- `custom_components/ha_light_controller/button.py`
  - Preset button entities. Uses `preset_manager.activate_preset_with_options()`.
- `custom_components/ha_light_controller/sensor.py`
  - Preset status sensor entities.
- `custom_components/ha_light_controller/const.py`
  - All constants and defaults. Add new `CONF_*` and `DEFAULT_*` entries here when introducing options.

## Integration Notes

- Domain: `ha_light_controller`.
- Services: `ensure_state`, `activate_preset`, `create_preset`, `delete_preset`, `create_preset_from_current`.
- Uses `ConfigEntry` data for presets and `ConfigEntry.options` for settings.
- Entity platforms are set up via `async_forward_entry_setups`.

## Coding Guidelines

- Follow Home Assistant async patterns (`async_` methods, `await` service calls, and non-blocking I/O).
- Keep user-facing configuration in `const.py` and surfaces in `config_flow.py`.
- Prefer small, focused changes. Update tests or examples if behavior changes.
- See `CLAUDE.md` "Code Principles" section for readability and simplicity requirements.

## Tests

The integration has a comprehensive test suite using pytest. Tests are located in the `tests/` directory.

```bash
# Run all tests
pytest tests/

# Run tests with coverage
pytest tests/ --cov=custom_components/ha_light_controller

# Run a specific test file
pytest tests/test_controller.py
```

Test files:

- `test_init.py` - Integration setup and service registration
- `test_controller.py` - Light control logic and verification
- `test_config_flow.py` - Configuration and options flows
- `test_preset_manager.py` - Preset CRUD operations
- `test_button.py` - Preset button entities
- `test_sensor.py` - Preset status sensor entities
