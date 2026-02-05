---
name: ha-integration-scaffold
description: Scaffold a new Home Assistant integration with correct file structure, manifest, and boilerplate. Use when creating a new Home Assistant custom component, custom integration, or when the user says "scaffold", "create integration", "new integration", "custom component", or "Home Assistant integration".
---

# Home Assistant Integration Scaffolding

When scaffolding a Home Assistant integration, always generate the complete file structure with properly configured boilerplate. Every integration must follow the patterns below.

## Required File Structure

```
custom_components/{domain}/
├── __init__.py           # Entry point: async_setup_entry, async_unload_entry
├── manifest.json         # Integration metadata (REQUIRED)
├── config_flow.py        # UI-based configuration (REQUIRED for new integrations)
├── const.py              # Domain constant, platform list, defaults
├── coordinator.py        # DataUpdateCoordinator subclass
├── entity.py             # Base entity class (recommended)
├── strings.json          # User-facing strings for config flow and entities
├── translations/
│   └── en.json           # English translations (copy of strings.json)
└── [platform].py         # One file per entity platform (sensor.py, switch.py, etc.)
```

## manifest.json Template

Always generate with ALL required fields:

```json
{
  "domain": "{domain_name}",
  "name": "{Human Readable Name}",
  "version": "1.0.0",
  "codeowners": ["@{github_username}"],
  "config_flow": true,
  "dependencies": [],
  "documentation": "https://github.com/{user}/{repo}",
  "integration_type": "{hub|device|service}",
  "iot_class": "{local_polling|local_push|cloud_polling|cloud_push|calculated}",
  "issue_tracker": "https://github.com/{user}/{repo}/issues",
  "requirements": []
}
```

**Field rules:**
- `domain`: lowercase, underscores only, must match folder name
- `version`: SemVer format, required for custom integrations
- `integration_type`: "hub" for gateways to multiple devices, "device" for single device, "service" for cloud services
- `iot_class`: must accurately describe how the integration communicates
- `config_flow`: always `true` for new integrations — YAML-only configuration is not permitted

## __init__.py Template

```python
"""The {Name} integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import {Name}Coordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]  # Add platforms as needed

type {Name}ConfigEntry = ConfigEntry[{Name}Coordinator]


async def async_setup_entry(hass: HomeAssistant, entry: {Name}ConfigEntry) -> bool:
    """Set up {Name} from a config entry."""
    coordinator = {Name}Coordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: {Name}ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
```

## const.py Template

```python
"""Constants for the {Name} integration."""
from typing import Final

DOMAIN: Final = "{domain}"
DEFAULT_SCAN_INTERVAL = 30
```

## Python Version Requirements

- Home Assistant 2025.2+ requires **Python 3.13**
- Use modern type syntax: `list[str]` not `List[str]`, `dict[str, Any]` not `Dict[str, Any]`
- Use `from __future__ import annotations` in every file
- All I/O must be async

## Critical Rules

1. **Config flow is mandatory** — never suggest YAML-only configuration
2. **Library separation** — device communication belongs in a separate PyPI library (required for core, recommended for custom)
3. **DataUpdateCoordinator** — always use for polling integrations
4. **Unique IDs** — every entity must have a stable unique_id
5. **Device info** — group entities under devices using DeviceInfo with identifiers

## Additional resources

- For config flow details, see the `ha-config-flow` skill
- For coordinator patterns, see the `ha-coordinator` skill
- For entity platform details, see the `ha-entity-platforms` skill
- For testing guidance, see the `ha-testing` skill
