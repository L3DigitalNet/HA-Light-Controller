# VS Code Codex Instructions - HA Light Controller

## Project Type
Home Assistant Custom Integration — Light control with state verification, retries, and presets

## Environment
- Python 3.14.2 (HA 2025.2+ requires Python 3.13+)
- Home Assistant 2025.2+
- Testing: pytest + mocked homeassistant module (no running HA needed)
- Code Quality: Ruff (linter/formatter) + mypy (type checker)

## Architecture

| File | Purpose |
|------|---------|
| `__init__.py` | Entry point, service registration via loop, `_get_param()` helper |
| `controller.py` | `LightController`: expand → group → send → verify → retry |
| `preset_manager.py` | Preset CRUD, storage in `ConfigEntry.data[CONF_PRESETS]` |
| `config_flow.py` | Menu-based options flow with collapsible sections |
| `const.py` | All `CONF_*`, `ATTR_*`, `DEFAULT_*` constants |
| `button.py` / `sensor.py` | Preset button and status sensor entities |

## Core Principles

### 1. Service-Based Architecture
This integration uses services (not polling/coordinator) for light control:

```python
# Service registration via loop
services = [
    (SERVICE_ENSURE_STATE, async_handle_ensure_state, SERVICE_ENSURE_STATE_SCHEMA),
    (SERVICE_ACTIVATE_PRESET, async_handle_activate_preset, SERVICE_ACTIVATE_PRESET_SCHEMA),
]

for service_name, handler, schema in services:
    hass.services.async_register(DOMAIN, service_name, handler, schema=schema)
```

### 2. Config Flow with Options
Menu-based options flow for settings, preset creation, and preset management:

```python
class LightControllerOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        return self.async_show_menu(
            step_id="init",
            menu_options=["settings", "add_preset", "manage_presets"],
        )
```

### 3. Async-First Architecture
ALL I/O must be async:

```python
# ✅ Correct
await hass.services.async_call("light", "turn_on", service_data, blocking=True)

# ❌ Wrong - blocks event loop
time.sleep(1)
```

### 4. Full Type Hints
Use modern Python 3.13+ syntax:

```python
from __future__ import annotations
from typing import Any, Final

DOMAIN: Final = "ha_light_controller"
```

### 5. Parameter Merging Pattern
Use `_get_param()` for call data with options fallback:

```python
def _get_param(call_data: dict, options: dict, attr: str, conf: str, default: Any) -> Any:
    return call_data.get(attr, options.get(conf, default))
```

## Integration Quality Scale

**Bronze (Minimum):**
- Config flow + tests + manifest

**Silver (Reliability):**
- Error handling + availability + docs

**Gold (Complete):**
- Full async + type coverage + comprehensive tests

**Platinum (Excellence):**
- All best practices + maintenance

## Quick Commands

```bash
# Lint & fix
ruff check custom_components/ tests/ scripts/ --fix

# Format
ruff format custom_components/ tests/ scripts/

# Type check
mypy custom_components/

# Test
pytest tests/ -v

# All checks
make quality
```

## Resources
- CLAUDE.md — Extended patterns, anti-patterns, and code principles
- AGENTS.md — Full agent instructions
- resources/ — HA development skills and agent specs
