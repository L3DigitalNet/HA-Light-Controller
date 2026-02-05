"""Data coordinator for the Example Device integration.

The DataUpdateCoordinator is the heart of most Home Assistant integrations.
It centralizes data fetching so that:
1. Multiple entities can share the same data without making duplicate API calls
2. Error handling and retry logic are consistent across all entities
3. Entity availability is automatically managed based on update success/failure

Think of the coordinator as a "data broker" - it fetches data from your device
on a schedule and notifies all interested entities when new data arrives.
"""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

if TYPE_CHECKING:
    from .api import ExampleDeviceApiClient, ExampleDeviceData

_LOGGER = logging.getLogger(__name__)


class ExampleDeviceCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to manage data fetching from the Example Device API.

    This coordinator:
    - Polls the device API at regular intervals
    - Stores the latest data for all entities to access
    - Handles errors and marks entities unavailable when needed
    - Notifies entities when new data is available

    The generic type parameter (dict[str, Any]) indicates the type of data
    returned by _async_update_data. Using a TypedDict or dataclass is better
    in production code for type safety.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        client: ExampleDeviceApiClient,
    ) -> None:
        """Initialize the coordinator.

        Args:
            hass: The Home Assistant instance
            client: The API client for communicating with the device
        """
        # Call the parent constructor with required parameters.
        # The name is used in logging messages.
        # update_interval determines how often _async_update_data is called.
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
            # Set to False if your data supports __eq__ comparison.
            # This avoids unnecessary entity state updates when data hasn't changed.
            always_update=False,
        )

        # Store the client for use in update methods.
        self.client = client

        # You can store additional data that's fetched once during setup.
        # This is populated in _async_setup().
        self.device_info: dict[str, Any] = {}

    async def _async_setup(self) -> None:
        """Perform one-time setup tasks.

        This method was added in Home Assistant 2024.8. It's called once
        during async_config_entry_first_refresh() before _async_update_data.

        Use this for:
        - Fetching device information that doesn't change (model, serial number)
        - Establishing persistent connections
        - Any initialization that only needs to happen once

        Errors raised here are handled the same way as in _async_update_data:
        - ConfigEntryAuthFailed triggers a reauth flow
        - Other exceptions trigger ConfigEntryNotReady
        """
        _LOGGER.debug("Performing one-time coordinator setup")

        try:
            # Fetch device info that we only need once.
            # This data won't change between updates.
            self.device_info = await self.client.async_get_device_info()
            _LOGGER.debug("Device info: %s", self.device_info)

        except AuthenticationError as err:
            # Authentication failed - user needs to re-authenticate.
            raise ConfigEntryAuthFailed("Authentication failed") from err

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch the latest data from the device.

        This is the main update method called on every polling cycle.
        It should:
        1. Fetch fresh data from the device/API
        2. Return the data in a format your entities expect
        3. Raise UpdateFailed for temporary errors (device offline)
        4. Raise ConfigEntryAuthFailed for authentication errors

        The returned data is stored in self.data and made available
        to all entities that use this coordinator.

        Returns:
            The latest device data as a dictionary

        Raises:
            UpdateFailed: When there's a temporary error (device offline, etc.)
            ConfigEntryAuthFailed: When authentication has failed/expired
        """
        try:
            # Fetch data from the device.
            # This is where you'd call your actual API client.
            data = await self.client.async_get_data()

            _LOGGER.debug("Received data update: %s", data)
            return data

        except AuthenticationError as err:
            # Authentication failed - the credentials are invalid or expired.
            # Raising ConfigEntryAuthFailed will:
            # 1. Mark the config entry as needing reauth
            # 2. Create a repair issue for the user
            # 3. Trigger the reauth flow when the user clicks "Reconfigure"
            raise ConfigEntryAuthFailed(
                "Authentication failed, please re-authenticate"
            ) from err

        except ConnectionError as err:
            # Connection failed - device is probably offline or unreachable.
            # Raising UpdateFailed will:
            # 1. Mark all entities as unavailable
            # 2. Log the error once (not on every retry)
            # 3. Continue retrying on the normal schedule
            raise UpdateFailed(
                f"Failed to connect to device: {err}"
            ) from err

        except TimeoutError as err:
            # Request timed out - treat similarly to connection error.
            raise UpdateFailed(
                f"Timeout communicating with device: {err}"
            ) from err

        except Exception as err:
            # Catch-all for unexpected errors.
            # Log the full exception for debugging.
            _LOGGER.exception("Unexpected error fetching data")
            raise UpdateFailed(
                f"Unexpected error: {err}"
            ) from err

    def get_device_data(self, device_id: str) -> dict[str, Any] | None:
        """Get data for a specific device.

        Helper method to safely access device data from the coordinator's
        stored data. Returns None if the device isn't found.

        Args:
            device_id: The unique identifier for the device

        Returns:
            The device data dictionary, or None if not found
        """
        if self.data is None:
            return None

        return self.data.get("devices", {}).get(device_id)


# Placeholder exception classes - in a real integration, these would
# come from your device library.
class AuthenticationError(Exception):
    """Raised when authentication fails."""


class ConnectionError(Exception):
    """Raised when connection to device fails."""
