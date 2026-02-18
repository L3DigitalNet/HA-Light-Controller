"""Diagnostics support for Light Controller integration."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_PRESETS


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    presets_data = entry.data.get(CONF_PRESETS, {})

    return {
        "config_entry_data": {k: v for k, v in entry.data.items() if k != CONF_PRESETS},
        "options": dict(entry.options),
        "preset_count": len(presets_data),
        "presets": {
            pid: {
                "name": p.get("name", "unknown"),
                "entity_count": len(p.get("entities", [])),
                "state": p.get("state", "unknown"),
                "has_targets": bool(p.get("targets")),
                "skip_verification": p.get("skip_verification", False),
            }
            for pid, p in presets_data.items()
        },
    }
