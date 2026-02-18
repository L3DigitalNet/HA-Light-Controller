"""Sensor platform for Light Controller preset status."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

if TYPE_CHECKING:
    from . import LightControllerConfigEntry

from .const import (
    DOMAIN,
    PRESET_STATUS_ACTIVATING,
    PRESET_STATUS_FAILED,
    PRESET_STATUS_IDLE,
    PRESET_STATUS_SUCCESS,
)
from .preset_manager import PresetConfig, PresetManager

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LightControllerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Light Controller sensors from a config entry."""
    data = entry.runtime_data
    preset_manager = data.preset_manager

    # Track entities we've added
    added_preset_ids: set[str] = set()

    @callback
    def async_add_preset_sensors() -> None:
        """Add sensor entities for new presets."""
        # Clean up tracking for deleted presets
        added_preset_ids.intersection_update(preset_manager.presets.keys())

        new_entities: list[PresetStatusSensor] = []

        for preset_id, preset in preset_manager.presets.items():
            if preset_id not in added_preset_ids:
                entity = PresetStatusSensor(
                    hass=hass,
                    entry=entry,
                    preset_manager=preset_manager,
                    preset_id=preset_id,
                    preset=preset,
                )
                new_entities.append(entity)
                added_preset_ids.add(preset_id)
                _LOGGER.debug("Adding status sensor for preset: %s", preset.name)

        if new_entities:
            async_add_entities(new_entities)

    # Add initial sensors
    async_add_preset_sensors()

    # Register listener for preset changes
    entry.async_on_unload(preset_manager.register_listener(async_add_preset_sensors))


class PresetStatusSensor(SensorEntity):
    """Sensor entity showing the status of a Light Controller preset."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_translation_key = "preset_status"
    _attr_options = [
        PRESET_STATUS_IDLE,
        PRESET_STATUS_ACTIVATING,
        PRESET_STATUS_SUCCESS,
        PRESET_STATUS_FAILED,
    ]

    def __init__(
        self,
        hass: HomeAssistant,
        entry: LightControllerConfigEntry,
        preset_manager: PresetManager,
        preset_id: str,
        preset: PresetConfig,
    ) -> None:
        """Initialize the preset status sensor."""
        self.hass = hass
        self._entry = entry
        self._preset_manager = preset_manager
        self._preset_id = preset_id
        self._preset = preset

        # Entity attributes
        self._attr_unique_id = f"{entry.entry_id}_preset_{preset_id}_status"
        self._attr_translation_placeholders = {"name": preset.name}

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for the preset."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="Light Controller",
            manufacturer="Light Controller",
            model="Preset Manager",
        )

    @property
    def native_value(self) -> str:
        """Return the current status."""
        status = self._preset_manager.get_status(self._preset_id)
        return status.status

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        preset = self._preset_manager.get_preset(self._preset_id)
        status = self._preset_manager.get_status(self._preset_id)

        attrs: dict[str, Any] = {
            "preset_id": self._preset_id,
        }

        if preset:
            attrs["preset_name"] = preset.name
            attrs["target_state"] = preset.state
            attrs["entity_count"] = len(preset.entities)

        if status.last_activated:
            attrs["last_activated"] = status.last_activated

        if status.last_result:
            attrs["last_success"] = status.last_result.get("success", False)
            attrs["last_message"] = status.last_result.get("message", "")
            attrs["last_attempts"] = status.last_result.get("attempts", 0)

            # Format elapsed time for readability (e.g., "1.2s")
            elapsed = status.last_result.get("elapsed_seconds", 0)
            if elapsed:
                attrs["last_elapsed"] = f"{elapsed:.1f}s"

            failed_lights = status.last_result.get("failed_lights", [])
            if failed_lights:
                attrs["failed_lights"] = failed_lights
                attrs["failed_count"] = len(failed_lights)

            skipped_lights = status.last_result.get("skipped_lights", [])
            if skipped_lights:
                attrs["skipped_lights"] = skipped_lights
                attrs["skipped_count"] = len(skipped_lights)

        return attrs

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._preset_manager.get_preset(self._preset_id) is not None

    @callback
    def _handle_preset_update(self) -> None:
        """Handle preset or status updates."""
        preset = self._preset_manager.get_preset(self._preset_id)
        if preset:
            self._preset = preset
            self._attr_translation_placeholders = {"name": preset.name}
            self.async_write_ha_state()
        elif self.hass:
            self.hass.async_create_task(self.async_remove())

    async def async_added_to_hass(self) -> None:
        """Run when entity is added to hass."""
        await super().async_added_to_hass()

        # Register for updates
        self.async_on_remove(
            self._preset_manager.register_listener(self._handle_preset_update)
        )

    async def async_will_remove_from_hass(self) -> None:
        """Run when entity is being removed."""
        await super().async_will_remove_from_hass()
