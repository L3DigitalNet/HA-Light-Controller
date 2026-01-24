"""Sensor platform for Light Controller preset status."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    PRESET_STATUS_IDLE,
    PRESET_STATUS_ACTIVATING,
    PRESET_STATUS_SUCCESS,
    PRESET_STATUS_FAILED,
)
from .preset_manager import PresetManager, PresetConfig

_LOGGER = logging.getLogger(__name__)

# Map status to icons
STATUS_ICONS = {
    PRESET_STATUS_IDLE: "mdi:lightbulb-outline",
    PRESET_STATUS_ACTIVATING: "mdi:lightbulb-on",
    PRESET_STATUS_SUCCESS: "mdi:lightbulb-on-outline",
    PRESET_STATUS_FAILED: "mdi:lightbulb-alert",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Light Controller sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    preset_manager: PresetManager = data["preset_manager"]

    # Track entities we've added
    added_preset_ids: set[str] = set()

    @callback
    def async_add_preset_sensors() -> None:
        """Add sensor entities for new presets."""
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
    entry.async_on_unload(
        preset_manager.register_listener(async_add_preset_sensors)
    )


class PresetStatusSensor(SensorEntity):
    """Sensor entity showing the status of a Light Controller preset."""

    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
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
        self._attr_name = f"{preset.name} Status"
        self._attr_icon = STATUS_ICONS.get(PRESET_STATUS_IDLE, "mdi:lightbulb-outline")

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for the preset."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="Light Controller",
            manufacturer="Light Controller",
            model="Preset Manager",
            sw_version="1.0.0",
        )

    @property
    def native_value(self) -> str:
        """Return the current status."""
        status = self._preset_manager.get_status(self._preset_id)
        return status.status

    @property
    def icon(self) -> str:
        """Return the icon based on status."""
        status = self._preset_manager.get_status(self._preset_id)
        return STATUS_ICONS.get(status.status, "mdi:lightbulb-outline")

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
            attrs["last_elapsed_seconds"] = status.last_result.get("elapsed_seconds", 0)

            failed_lights = status.last_result.get("failed_lights", [])
            if failed_lights:
                attrs["failed_lights"] = failed_lights

            skipped_lights = status.last_result.get("skipped_lights", [])
            if skipped_lights:
                attrs["skipped_lights"] = skipped_lights

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
            self._attr_name = f"{preset.name} Status"
        self.async_write_ha_state()

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
