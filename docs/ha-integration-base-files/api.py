"""API client for the Example Device integration.

In a real integration, this would be replaced by or wrap a separate
Python library that handles communication with your device. The library
should be:
1. Published on PyPI (required for core integrations)
2. Device-agnostic (no Home Assistant dependencies)
3. Fully async for I/O operations

This example provides a mock implementation to demonstrate the
expected interface and how it integrates with the coordinator.

Key principles:
- All I/O methods should be async (async/await)
- Raise specific exceptions for different error types
- Return structured data (dataclasses or TypedDicts are recommended)
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


class ExampleDeviceApiClient:
    """API client for Example Device.

    This class handles all communication with the device.
    In a real integration, this would:
    - Manage HTTP sessions with aiohttp
    - Handle authentication token refresh
    - Parse API responses into structured data
    - Convert device-specific errors to standard exceptions
    """

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
    ) -> None:
        """Initialize the API client.

        Args:
            host: The hostname or IP address of the device
            username: The authentication username
            password: The authentication password
        """
        self._host = host
        self._username = username
        self._password = password

        # In a real implementation, you might store:
        # - An aiohttp ClientSession
        # - Authentication tokens
        # - Device connection state
        self._authenticated = False

    async def async_authenticate(self) -> bool:
        """Authenticate with the device.

        Returns:
            True if authentication succeeded

        Raises:
            AuthenticationError: If credentials are invalid
            ConnectionError: If the device is unreachable
        """
        _LOGGER.debug("Authenticating with device at %s", self._host)

        # Simulate network latency
        await asyncio.sleep(0.1)

        # Mock validation - in reality, you'd make an API call
        if self._username == "invalid":
            raise AuthenticationError("Invalid credentials")

        if self._host == "unreachable":
            raise ConnectionError("Cannot connect to device")

        self._authenticated = True
        return True

    async def async_get_device_info(self) -> dict[str, Any]:
        """Get static device information.

        This returns information that doesn't change during operation,
        such as model number, serial number, firmware version.

        Returns:
            Device information dictionary

        Raises:
            AuthenticationError: If not authenticated
            ConnectionError: If device is unreachable
        """
        if not self._authenticated:
            await self.async_authenticate()

        _LOGGER.debug("Fetching device info from %s", self._host)

        # Simulate network latency
        await asyncio.sleep(0.1)

        # Return mock device info
        # In reality, this would be parsed from an API response
        return {
            "serial_number": f"EXAMPLE-{self._host.replace('.', '-')}",
            "name": f"Example Device ({self._host})",
            "model": "Example Model X1",
            "manufacturer": "Example Manufacturer",
            "firmware_version": "1.2.3",
        }

    async def async_get_data(self) -> dict[str, Any]:
        """Get the current device data.

        This is the main data fetching method called by the coordinator.
        It returns the current state of all sensors and controls.

        Returns:
            Current device data

        Raises:
            AuthenticationError: If authentication has expired
            ConnectionError: If device is unreachable
            TimeoutError: If the request times out
        """
        if not self._authenticated:
            await self.async_authenticate()

        _LOGGER.debug("Fetching current data from %s", self._host)

        # Simulate network latency
        await asyncio.sleep(0.1)

        # Return mock data structure
        # The structure should match what your entities expect
        return {
            "devices": {
                # Each device has a unique ID as its key
                "device_1": {
                    "name": "Living Room Sensor",
                    "model": "Example Sensor Pro",
                    "firmware_version": "2.0.1",
                    # Sensor values
                    "temperature": 22.5,
                    "humidity": 45,
                    "battery_level": 87,
                    "status": "online",
                    # Binary sensor values
                    "motion_detected": False,
                    "door_open": False,
                    # Switch states
                    "led_enabled": True,
                    "night_mode": False,
                },
                "device_2": {
                    "name": "Bedroom Sensor",
                    "model": "Example Sensor Lite",
                    "firmware_version": "1.5.0",
                    "temperature": 19.8,
                    "humidity": 52,
                    "battery_level": 64,
                    "status": "online",
                    "motion_detected": True,
                    "door_open": False,
                    "led_enabled": False,
                    "night_mode": True,
                },
            }
        }

    async def async_set_switch(
        self,
        device_id: str,
        switch_key: str,
        value: bool,
    ) -> bool:
        """Set a switch value on a device.

        This demonstrates how to implement control actions.
        The coordinator should be refreshed after this to get updated state.

        Args:
            device_id: The device to control
            switch_key: Which switch to change
            value: The new switch state

        Returns:
            True if the command succeeded

        Raises:
            AuthenticationError: If authentication has expired
            ConnectionError: If device is unreachable
            CommandError: If the device rejected the command
        """
        if not self._authenticated:
            await self.async_authenticate()

        _LOGGER.debug(
            "Setting %s.%s to %s on %s",
            device_id,
            switch_key,
            value,
            self._host,
        )

        # Simulate network latency
        await asyncio.sleep(0.2)

        # In reality, you'd send a command to the device and check the response
        # Here we just return success
        return True


class AuthenticationError(Exception):
    """Exception raised when authentication fails.

    This could mean:
    - Invalid credentials provided during setup
    - Token has expired and needs refresh
    - Account has been locked or disabled
    """


class ConnectionError(Exception):
    """Exception raised when we can't connect to the device.

    This could mean:
    - Device is offline or unreachable
    - Network issues between HA and device
    - DNS resolution failed
    """


class CommandError(Exception):
    """Exception raised when a command fails.

    This could mean:
    - Device rejected the command
    - Invalid parameters
    - Device is in a state that prevents the action
    """
