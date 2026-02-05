---
name: ha-coordinator
description: Implement or fix a Home Assistant DataUpdateCoordinator for centralized data fetching. Use when the user mentions "coordinator", "DataUpdateCoordinator", "polling", "data fetching", "update coordinator", "_async_update_data", "UpdateFailed", or needs to set up efficient data polling for a Home Assistant integration.
---

# Home Assistant DataUpdateCoordinator Pattern

The DataUpdateCoordinator is the most important architectural pattern for polling-based Home Assistant integrations. It centralizes data fetching, distributes updates to all entities, and handles error/retry logic automatically.

## When to Use a Coordinator

Use a DataUpdateCoordinator when your integration polls a device or API on a schedule. This covers the vast majority of integrations. Do NOT use one for push-based integrations where the device sends updates (use event subscriptions instead).

## Complete Coordinator Template

```python
"""DataUpdateCoordinator for {Name}."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class {Name}Coordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to manage data fetching."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(
                seconds=entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)
            ),
            always_update=False,  # Only notify entities when data actually changes
        )
        self.client = MyClient(
            host=entry.data["host"],
            username=entry.data["username"],
            password=entry.data["password"],
        )

    async def _async_setup(self) -> None:
        """Perform one-time initialization (Home Assistant 2024.8+).

        Called once during async_config_entry_first_refresh() before _async_update_data.
        Use for data that doesn't change: device info, serial numbers, capabilities.
        Errors here are handled identically to _async_update_data.
        """
        self.device_info = await self.client.async_get_device_info()

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the device/API.

        Called on every polling cycle. Return the data your entities need.

        Raises:
            ConfigEntryAuthFailed: Triggers reauth flow. Use for expired/invalid credentials.
            UpdateFailed: Marks entities unavailable, logs once, retries on schedule.
        """
        try:
            return await self.client.async_get_data()
        except AuthenticationError as err:
            raise ConfigEntryAuthFailed("Authentication failed") from err
        except ConnectionError as err:
            raise UpdateFailed(f"Connection error: {err}") from err
        except TimeoutError as err:
            raise UpdateFailed(f"Timeout: {err}") from err
```

## Critical Behaviors

### Error Handling

The coordinator provides three error paths:

| Exception | Effect | When to Use |
|---|---|---|
| `UpdateFailed` | Entities become unavailable, logs once, retries on schedule | Device offline, network error, timeout |
| `ConfigEntryAuthFailed` | Triggers reauth flow, stops polling | Expired token, invalid credentials |
| `ConfigEntryError` | Permanently fails the config entry | Unrecoverable configuration error |

### `always_update=False`

Set this when your data supports Python `__eq__` comparison (dicts, dataclasses, NamedTuples). This prevents unnecessary entity state writes when data hasn't changed, reducing database writes and UI updates.

### `_async_setup` (HA 2024.8+)

Replaces the old pattern of checking an initialization flag in `_async_update_data`:

```python
# OLD PATTERN (avoid)
async def _async_update_data(self):
    if not self._initialized:
        self._initialized = True
        self.static_data = await self.client.get_info()
    return await self.client.get_data()

# NEW PATTERN (use this)
async def _async_setup(self):
    self.static_data = await self.client.get_info()

async def _async_update_data(self):
    return await self.client.get_data()
```

### retry_after (HA 2025.10+)

For rate-limited APIs, include a retry delay with UpdateFailed:

```python
except RateLimitError as err:
    raise UpdateFailed(
        f"Rate limited: {err}",
        translation_key="rate_limited",
    ) from err
    # The coordinator will respect Retry-After headers when available
```

## Using the Coordinator in __init__.py

```python
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = {Name}Coordinator(hass, entry)

    # This calls _async_setup() then _async_update_data()
    # Raises ConfigEntryNotReady on failure (auto-retries)
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator for platform access
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True
```

## Using the Coordinator in Entity Platforms

```python
class MySensor(CoordinatorEntity[{Name}Coordinator], SensorEntity):
    """Sensor that automatically updates from coordinator data."""

    def __init__(self, coordinator: {Name}Coordinator, device_id: str) -> None:
        super().__init__(coordinator)  # Subscribes to coordinator updates
        self._device_id = device_id

    @property
    def native_value(self) -> float | None:
        """Return current value from coordinator data."""
        return self.coordinator.data.get("devices", {}).get(self._device_id, {}).get("temperature")

    @property
    def available(self) -> bool:
        """Entity is available when coordinator succeeds AND device data exists."""
        return super().available and self._device_id in self.coordinator.data.get("devices", {})
```

## Helper Method Pattern

Add helper methods on the coordinator for clean data access:

```python
def get_device_data(self, device_id: str) -> dict[str, Any] | None:
    """Get data for a specific device."""
    if self.data is None:
        return None
    return self.data.get("devices", {}).get(device_id)

def get_device_ids(self) -> list[str]:
    """Get all known device IDs."""
    if self.data is None:
        return []
    return list(self.data.get("devices", {}).keys())
```

## Common Mistakes

1. **Not calling `async_config_entry_first_refresh()`** — setup succeeds but no data is loaded
2. **Catching exceptions too broadly** — let `ConfigEntryAuthFailed` and `UpdateFailed` propagate
3. **Blocking I/O in `_async_update_data`** — use `await hass.async_add_executor_job()` for sync libraries
4. **Setting `always_update=True` unnecessarily** — causes excessive state writes
5. **Storing the coordinator in `hass.data`** — use `entry.runtime_data` instead (modern pattern)
