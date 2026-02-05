"""Sensor platform for the Example Device integration.

Sensors represent read-only values from your device, such as:
- Temperature, humidity, pressure readings
- Power consumption, voltage, current
- Status values, counts, percentages
- Text states (firmware version, status messages)

This module demonstrates the key patterns for creating sensor entities:
1. Using CoordinatorEntity to automatically sync with data updates
2. Properly defining device info to group entities
3. Using SensorEntityDescription for clean, declarative entity definition
4. Implementing availability based on data presence
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import ExampleDeviceConfigEntry
from .const import DOMAIN
from .coordinator import ExampleDeviceCoordinator


@dataclass(frozen=True, kw_only=True)
class ExampleSensorEntityDescription(SensorEntityDescription):
    """Describes an Example Device sensor entity.

    This extends SensorEntityDescription with a value_fn that extracts
    the sensor's value from the coordinator's data. This pattern allows
    us to define sensors declaratively while still having custom logic
    for extracting values.
    """

    # Function to extract the value from device data.
    # Takes the device data dict and returns the sensor value.
    value_fn: Callable[[dict[str, Any]], Any]


# Define all sensors using entity descriptions.
# This declarative approach is cleaner than creating separate classes for each sensor.
SENSOR_DESCRIPTIONS: tuple[ExampleSensorEntityDescription, ...] = (
    ExampleSensorEntityDescription(
        key="temperature",
        translation_key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data.get("temperature"),
    ),
    ExampleSensorEntityDescription(
        key="humidity",
        translation_key="humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda data: data.get("humidity"),
    ),
    ExampleSensorEntityDescription(
        key="battery",
        translation_key="battery",
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda data: data.get("battery_level"),
    ),
    ExampleSensorEntityDescription(
        key="status",
        translation_key="status",
        # No device_class for text/enum sensors
        value_fn=lambda data: data.get("status"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ExampleDeviceConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Example Device sensor entities.

    This function is called by Home Assistant when setting up the sensor platform.
    It's responsible for creating all sensor entities for the config entry.

    Args:
        hass: The Home Assistant instance
        entry: The config entry being set up
        async_add_entities: Callback to register new entities
    """
    # Get the coordinator from the config entry's runtime data.
    # The coordinator was created in __init__.py during setup.
    coordinator = entry.runtime_data

    # Create sensor entities for each device known to the integration.
    # We iterate over all devices and all sensor descriptions.
    entities: list[ExampleDeviceSensor] = []

    # In this example, we assume the coordinator data contains a 'devices' dict.
    # Adjust this based on your actual data structure.
    for device_id, device_data in coordinator.data.get("devices", {}).items():
        for description in SENSOR_DESCRIPTIONS:
            # Only create the entity if the device has data for this sensor.
            # This prevents creating entities for features the device doesn't support.
            if description.value_fn(device_data) is not None:
                entities.append(
                    ExampleDeviceSensor(
                        coordinator=coordinator,
                        description=description,
                        device_id=device_id,
                    )
                )

    # Register all entities with Home Assistant.
    async_add_entities(entities)


class ExampleDeviceSensor(CoordinatorEntity[ExampleDeviceCoordinator], SensorEntity):
    """Representation of an Example Device sensor.

    This class inherits from:
    - CoordinatorEntity: Provides automatic data updates from the coordinator
    - SensorEntity: Provides the sensor-specific functionality

    The CoordinatorEntity handles:
    - Subscribing to coordinator updates
    - Triggering state updates when new data arrives
    - Managing entity availability based on coordinator status
    """

    # Use entity descriptions for configuration
    entity_description: ExampleSensorEntityDescription

    # Indicates that entity name should be based on the device name + entity name.
    # Without this, you'd get "Example Device Temperature Temperature"
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ExampleDeviceCoordinator,
        description: ExampleSensorEntityDescription,
        device_id: str,
    ) -> None:
        """Initialize the sensor.

        Args:
            coordinator: The data coordinator for this integration
            description: The entity description defining this sensor
            device_id: The unique identifier of the device this sensor belongs to
        """
        # Initialize the CoordinatorEntity - this sets up the coordinator subscription.
        super().__init__(coordinator)

        # Store the entity description (this sets self.entity_description)
        self.entity_description = description

        # Store the device ID for data lookups
        self._device_id = device_id

        # Generate a unique ID for this entity.
        # This MUST be stable across restarts - it's how HA identifies the entity.
        # Format: domain_deviceid_sensorkey
        self._attr_unique_id = f"{DOMAIN}_{device_id}_{description.key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information for this entity.

        Device info is used to:
        1. Group entities under a single device in the UI
        2. Show device details (manufacturer, model, firmware)
        3. Link the device to its identifiers for discovery

        All entities with the same 'identifiers' are grouped together.
        """
        # Get device data from the coordinator
        device_data = self.coordinator.data.get("devices", {}).get(self._device_id, {})

        return DeviceInfo(
            # Identifiers uniquely identify the device.
            # Use (domain, unique_id) format for consistency.
            identifiers={(DOMAIN, self._device_id)},
            # Human-readable name for the device
            name=device_data.get("name", f"Example Device {self._device_id}"),
            # Device metadata
            manufacturer="Example Manufacturer",
            model=device_data.get("model", "Unknown Model"),
            sw_version=device_data.get("firmware_version"),
            # Optional: If this device connects through another device (hub),
            # you can specify via_device here.
            # via_device=(DOMAIN, hub_device_id),
        )

    @property
    def available(self) -> bool:
        """Return True if the entity is available.

        An entity should be unavailable when:
        - The coordinator has failed to update (handled by CoordinatorEntity)
        - The specific device/data for this entity is missing

        This combines the coordinator's availability with entity-specific checks.
        """
        # First check if the coordinator itself is available
        if not super().available:
            return False

        # Then check if this device's data exists
        return self._device_id in self.coordinator.data.get("devices", {})

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor.

        This is called whenever Home Assistant needs the current value.
        With CoordinatorEntity, this is automatically called after each update.

        The entity_description's value_fn extracts the appropriate value
        from the device data, keeping this property clean and simple.
        """
        # Get the device data from the coordinator
        device_data = self.coordinator.data.get("devices", {}).get(self._device_id, {})

        # Use the description's value function to extract the sensor value
        return self.entity_description.value_fn(device_data)
