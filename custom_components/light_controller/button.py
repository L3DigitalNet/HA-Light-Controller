"""Button platform for Light Controller presets."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity, ButtonDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    PRESET_STATUS_ACTIVATING,
    PRESET_STATUS_SUCCESS,
    PRESET_STATUS_FAILED,
)
from .preset_manager import PresetManager, PresetConfig

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Light Controller buttons from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    preset_manager: PresetManager = data["preset_manager"]
    controller = data["controller"]

    # Track entities we've added
    added_preset_ids: set[str] = set()
    entities: list[PresetButton] = []

    @callback
    def async_add_preset_buttons() -> None:
        """Add button entities for new presets."""
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
    entry.async_on_unload(
        preset_manager.register_listener(async_add_preset_buttons)
    )


class PresetButton(ButtonEntity):
    """Button entity to activate a Light Controller preset."""

    _attr_has_entity_name = True
    _attr_device_class = ButtonDeviceClass.IDENTIFY

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
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
        self._attr_name = f"{preset.name}"
        self._attr_icon = "mdi:lightbulb-group"

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

        # Update status to activating
        self._preset_manager.set_status(self._preset_id, PRESET_STATUS_ACTIVATING)

        # Get configured defaults from options
        options = self._entry.options

        # Build service call parameters
        # Preset values override defaults
        result = await self._controller.ensure_state(
            entities=preset.entities,
            state_target=preset.state,
            default_brightness_pct=preset.brightness_pct,
            default_rgb_color=preset.rgb_color,
            default_color_temp_kelvin=preset.color_temp_kelvin,
            default_effect=preset.effect,
            targets=preset.targets if preset.targets else None,
            transition=preset.transition,
            skip_verification=preset.skip_verification,
            # Use configured defaults for tolerances and retry
            brightness_tolerance=options.get("brightness_tolerance", 3),
            rgb_tolerance=options.get("rgb_tolerance", 10),
            kelvin_tolerance=options.get("kelvin_tolerance", 150),
            delay_after_send=options.get("delay_after_send", 2.0),
            max_retries=options.get("max_retries", 3),
            max_runtime_seconds=options.get("max_runtime_seconds", 60.0),
            use_exponential_backoff=options.get("use_exponential_backoff", False),
            max_backoff_seconds=options.get("max_backoff_seconds", 30.0),
            log_success=options.get("log_success", False),
            notify_on_failure=options.get("notify_on_failure"),
        )

        # Update status based on result
        if result.get("success", False):
            self._preset_manager.set_status(
                self._preset_id, PRESET_STATUS_SUCCESS, result
            )
            _LOGGER.info("Preset activated successfully: %s", preset.name)
        else:
            self._preset_manager.set_status(
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
            self._attr_name = f"{preset.name}"
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
