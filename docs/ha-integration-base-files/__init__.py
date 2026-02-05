"""The Example Device integration.

This is the main entry point for the integration. It handles:
1. Setting up the integration when a config entry is created
2. Forwarding setup to individual platforms (sensor, switch, etc.)
3. Unloading the integration when it's removed

The key pattern here is using a DataUpdateCoordinator to centralize
data fetching and distribute updates to all entities efficiently.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN, PLATFORMS
from .coordinator import ExampleDeviceCoordinator

if TYPE_CHECKING:
    from .api import ExampleDeviceApiClient

# Set up logging for this integration.
# Use _LOGGER (with underscore) as per HA convention.
_LOGGER = logging.getLogger(__name__)

# Define the platforms this integration supports.
# This could also be imported from const.py for centralization.
PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.SWITCH]

# Type alias for the config entry with runtime data.
# This provides type hints for the coordinator stored in the entry.
type ExampleDeviceConfigEntry = ConfigEntry[ExampleDeviceCoordinator]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ExampleDeviceConfigEntry,
) -> bool:
    """Set up Example Device from a config entry.

    This function is called when:
    - The integration is first configured (after config flow completes)
    - Home Assistant starts up and loads existing config entries
    - The integration is reloaded

    Args:
        hass: The Home Assistant instance
        entry: The config entry being set up

    Returns:
        True if setup succeeded, raises exception otherwise
    """
    # Create the API client using stored configuration.
    # In a real integration, this would be your device library.
    from .api import ExampleDeviceApiClient

    client = ExampleDeviceApiClient(
        host=entry.data[CONF_HOST],
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
    )

    # Create the coordinator that will manage data updates.
    # The coordinator centralizes polling and distributes data to entities.
    coordinator = ExampleDeviceCoordinator(hass, client)

    # Perform the first data refresh.
    # This method handles errors appropriately:
    # - Raises ConfigEntryNotReady on connection failures (triggers retry)
    # - Raises ConfigEntryAuthFailed on auth failures (triggers reauth flow)
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        # Log the error for debugging, then re-raise for HA to handle
        _LOGGER.error("Failed to initialize Example Device: %s", err)
        raise ConfigEntryNotReady(f"Failed to connect: {err}") from err

    # Store the coordinator in the config entry's runtime_data.
    # This makes it available to platforms during their setup.
    # Using runtime_data (instead of hass.data) is the modern pattern.
    entry.runtime_data = coordinator

    # Forward the setup to all platforms (sensor, switch, etc.).
    # This calls each platform's async_setup_entry function.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register an update listener to handle options changes.
    # This allows users to modify settings without removing/re-adding.
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ExampleDeviceConfigEntry,
) -> bool:
    """Unload a config entry.

    This is called when:
    - The user removes the integration
    - The integration is reloaded
    - Home Assistant is shutting down

    It's important to clean up any resources (connections, subscriptions, etc.)
    """
    # Unload all platforms first.
    # This removes all entities and cleans up their resources.
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_update_options(
    hass: HomeAssistant,
    entry: ExampleDeviceConfigEntry,
) -> None:
    """Handle options update.

    Called when the user modifies integration options through the UI.
    The cleanest way to apply changes is often to reload the entire entry.
    """
    await hass.config_entries.async_reload(entry.entry_id)
