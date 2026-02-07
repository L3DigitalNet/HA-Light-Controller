# Copilot Instructions

## ⚠️ Branch Policy

**ALL changes MUST be made on the `testing` branch.** Never push to `main` without explicit permission.

## Project Overview

Home Assistant custom integration (`ha_light_controller`) providing light control with state verification, automatic retries, and preset management. Distributed via HACS.

## Architecture

| File                      | Purpose                                                           |
| ------------------------- | ----------------------------------------------------------------- |
| `__init__.py`             | Entry point, service registration via loop, `_get_param()` helper |
| `controller.py`           | `LightController`: expand → group → send → verify → retry         |
| `preset_manager.py`       | Preset CRUD, storage in `ConfigEntry.data[CONF_PRESETS]`          |
| `config_flow.py`          | Menu-based options flow with collapsible sections                 |
| `const.py`                | All `CONF_*`, `ATTR_*`, `DEFAULT_*` constants                     |
| `button.py` / `sensor.py` | Preset button and status sensor entities                          |

## Key Patterns

### Constants in `const.py`

```python
CONF_NEW_OPTION: Final = "new_option"
DEFAULT_NEW_OPTION: Final = 10
ATTR_NEW_PARAM: Final = "new_param"
```

### Parameter Merging via `_get_param()`

```python
brightness_tolerance = _get_param(data, options, ATTR_BRIGHTNESS_TOLERANCE, CONF_BRIGHTNESS_TOLERANCE, DEFAULT_BRIGHTNESS_TOLERANCE)
```

### Adding New Service Parameters

1. `const.py` — Add `ATTR_*` (and `CONF_*`/`DEFAULT_*` if configurable)
2. `__init__.py` — Add to schema, use `_get_param()` in handler
3. `services.yaml` — Add field definition with HA selector
4. `controller.py` — Add to `ensure_state()` signature if needed

## Commands

```bash
pytest                                        # All tests
pytest tests/test_controller.py               # Specific file
pytest --cov=custom_components/ha_light_controller  # With coverage
```

## Testing

Tests mock the entire `homeassistant` module in `tests/conftest.py`. No running HA instance required. Key fixtures: `hass`, `config_entry`, `mock_light_states`, `create_light_state()`.

## Code Style

- Flat over nested (max 3 levels)
- All I/O must be async or use `hass.async_add_executor_job()`
- Delete unused code; no commented-out code or compatibility shims
- Target HA users who understand entities, services, and YAML

## See Also

For comprehensive guidance, see the source documentation:

- [AGENTS.md](../AGENTS.md) — Full agent instructions, architecture details, and coding guidelines
- [CLAUDE.md](../CLAUDE.md) — Extended patterns, anti-patterns, and code principles
