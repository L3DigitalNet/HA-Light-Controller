"""Button platform for Light Controller presets."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

if TYPE_CHECKING:
    from . import LightControllerConfigEntry

from .const import (
    DOMAIN,
    PRESET_STATUS_ACTIVATING,
    PRESET_STATUS_FAILED,
    PRESET_STATUS_SUCCESS,
)
from .preset_manager import PresetConfig, PresetManager

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 0  # No I/O; entities are locally managed


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LightControllerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Light Controller buttons from a config entry."""
    data = entry.runtime_data
    preset_manager = data.preset_manager
    controller = data.controller

    # Track entities we've added
    added_preset_ids: set[str] = set()

    @callback
    def async_add_preset_buttons() -> None:
        """Add button entities for new presets."""
        # Clean up tracking for deleted presets
        added_preset_ids.intersection_update(preset_manager.presets.keys())

        new_entities: list[PresetButton] = []

        for preset_id, preset in preset_manager.presets.items():
            if preset_id not in added_preset_ids:
                entity = PresetButton(
                    hass=hass,
                    entry=entry,
                    preset_manager=preset_manager,
                    controller=controller,
                    preset_id=preset_id,
                    preset=preset,
                )
                new_entities.append(entity)
                added_preset_ids.add(preset_id)
                _LOGGER.debug("Adding button for preset: %s", preset.name)

        if new_entities:
            async_add_entities(new_entities)

    # Add initial buttons
    async_add_preset_buttons()

    # Register listener for preset changes
    entry.async_on_unload(preset_manager.register_listener(async_add_preset_buttons))


class PresetButton(ButtonEntity):
    """Button entity to activate a Light Controller preset."""

    _attr_has_entity_name = True
    _attr_translation_key = "preset"

    def __init__(
        self,
        hass: HomeAssistant,
        entry: LightControllerConfigEntry,
        preset_manager: PresetManager,
        controller: Any,
        preset_id: str,
        preset: PresetConfig,
    ) -> None:
        """Initialize the preset button."""
        self.hass = hass
        self._entry = entry
        self._preset_manager = preset_manager
        self._controller = controller
        self._preset_id = preset_id
        self._preset = preset

        # Entity attributes
        self._attr_unique_id = f"{entry.entry_id}_preset_{preset_id}_button"
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
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        preset = self._preset_manager.get_preset(self._preset_id)
        if not preset:
            return {}

        attrs = {
            "preset_id": self._preset_id,
            "entities": preset.entities,
            "state": preset.state,
            "brightness_pct": preset.brightness_pct,
        }

        if preset.rgb_color:
            attrs["rgb_color"] = preset.rgb_color
        if preset.color_temp_kelvin:
            attrs["color_temp_kelvin"] = preset.color_temp_kelvin
        if preset.effect:
            attrs["effect"] = preset.effect
        if preset.targets:
            attrs["target_count"] = len(preset.targets)

        # Add last activation result
        status = self._preset_manager.get_status(self._preset_id)
        if status.last_result:
            attrs["last_result"] = status.last_result.get("result", "unknown")
        if status.last_activated:
            attrs["last_activated"] = status.last_activated

        return attrs

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._preset_manager.get_preset(self._preset_id) is not None

    async def async_press(self) -> None:
        """Handle button press - activate the preset."""
        preset = self._preset_manager.get_preset(self._preset_id)
        if not preset:
            _LOGGER.error("Preset not found: %s", self._preset_id)
            return

        _LOGGER.info("Activating preset: %s", preset.name)
        await self._preset_manager.set_status(self._preset_id, PRESET_STATUS_ACTIVATING)

        result = await self._preset_manager.activate_preset_with_options(
            preset, self._controller, self._entry.options
        )

        if result.get("success", False):
            await self._preset_manager.set_status(
                self._preset_id, PRESET_STATUS_SUCCESS, result
            )
            _LOGGER.info("Preset activated successfully: %s", preset.name)
        else:
            await self._preset_manager.set_status(
                self._preset_id, PRESET_STATUS_FAILED, result
            )
            _LOGGER.warning(
                "Preset activation failed: %s - %s",
                preset.name,
                result.get("message", "Unknown error"),
            )

    @callback
    def _handle_preset_update(self) -> None:
        """Handle preset updates."""
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
