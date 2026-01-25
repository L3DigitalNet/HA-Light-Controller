"""Preset manager for Light Controller integration."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable
import uuid

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback

from .const import (
    CONF_PRESETS,
    PRESET_ID,
    PRESET_NAME,
    PRESET_ENTITIES,
    PRESET_STATE,
    PRESET_BRIGHTNESS_PCT,
    PRESET_RGB_COLOR,
    PRESET_COLOR_TEMP_KELVIN,
    PRESET_EFFECT,
    PRESET_TARGETS,
    PRESET_TRANSITION,
    PRESET_SKIP_VERIFICATION,
    PRESET_STATUS_IDLE,
    PRESET_STATUS_SUCCESS,
    PRESET_STATUS_FAILED,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class PresetConfig:
    """Configuration for a single preset."""

    id: str
    name: str
    entities: list[str]
    state: str = "on"
    brightness_pct: int = 100
    rgb_color: list[int] | None = None
    color_temp_kelvin: int | None = None
    effect: str | None = None
    targets: list[dict[str, Any]] = field(default_factory=list)
    transition: float = 0.0
    skip_verification: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PresetConfig":
        """Create a PresetConfig from a dictionary."""
        return cls(
            id=data.get(PRESET_ID, str(uuid.uuid4())),
            name=data.get(PRESET_NAME, "Unnamed Preset"),
            entities=data.get(PRESET_ENTITIES, []),
            state=data.get(PRESET_STATE, "on"),
            brightness_pct=data.get(PRESET_BRIGHTNESS_PCT, 100),
            rgb_color=data.get(PRESET_RGB_COLOR),
            color_temp_kelvin=data.get(PRESET_COLOR_TEMP_KELVIN),
            effect=data.get(PRESET_EFFECT),
            targets=data.get(PRESET_TARGETS, []),
            transition=data.get(PRESET_TRANSITION, 0.0),
            skip_verification=data.get(PRESET_SKIP_VERIFICATION, False),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            PRESET_ID: self.id,
            PRESET_NAME: self.name,
            PRESET_ENTITIES: self.entities,
            PRESET_STATE: self.state,
            PRESET_BRIGHTNESS_PCT: self.brightness_pct,
            PRESET_RGB_COLOR: self.rgb_color,
            PRESET_COLOR_TEMP_KELVIN: self.color_temp_kelvin,
            PRESET_EFFECT: self.effect,
            PRESET_TARGETS: self.targets,
            PRESET_TRANSITION: self.transition,
            PRESET_SKIP_VERIFICATION: self.skip_verification,
        }

    def to_slug(self) -> str:
        """Generate a slug from the preset name."""
        # Convert to lowercase, replace spaces with underscores, remove special chars
        slug = self.name.lower()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[\s-]+", "_", slug)
        return slug


@dataclass
class PresetStatus:
    """Runtime status of a preset."""

    status: str = PRESET_STATUS_IDLE
    last_result: dict[str, Any] | None = None
    last_activated: str | None = None


class PresetManager:
    """Manages preset storage and operations."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the preset manager."""
        self.hass = hass
        self.entry = entry
        self._presets: dict[str, PresetConfig] = {}
        self._status: dict[str, PresetStatus] = {}
        self._listeners: list[Callable] = []

        # Load presets from config entry
        self._load_presets()

    def _load_presets(self) -> None:
        """Load presets from config entry data."""
        presets_data = self.entry.data.get(CONF_PRESETS, {})

        for preset_id, preset_data in presets_data.items():
            try:
                preset = PresetConfig.from_dict(preset_data)
                self._presets[preset_id] = preset
                self._status[preset_id] = PresetStatus()
                _LOGGER.debug("Loaded preset: %s (%s)", preset.name, preset_id)
            except Exception as e:
                _LOGGER.error("Error loading preset %s: %s", preset_id, e)

        _LOGGER.info("Loaded %d presets", len(self._presets))

    async def _save_presets(self) -> None:
        """Save presets to config entry data."""
        presets_data = {
            preset_id: preset.to_dict()
            for preset_id, preset in self._presets.items()
        }

        # Update config entry data
        new_data = {**self.entry.data, CONF_PRESETS: presets_data}
        self.hass.config_entries.async_update_entry(self.entry, data=new_data)

        _LOGGER.debug("Saved %d presets", len(presets_data))

        # Notify listeners
        await self._notify_listeners()

    async def _notify_listeners(self) -> None:
        """Notify all registered listeners of preset changes."""
        for listener in self._listeners:
            try:
                listener()
            except Exception as e:
                _LOGGER.error("Error notifying listener: %s", e)

    @callback
    def register_listener(self, listener: Callable) -> Callable:
        """Register a listener for preset changes. Returns unsubscribe function."""
        self._listeners.append(listener)

        def unsubscribe() -> None:
            if listener in self._listeners:
                self._listeners.remove(listener)

        return unsubscribe

    @property
    def presets(self) -> dict[str, PresetConfig]:
        """Get all presets."""
        return self._presets.copy()

    def get_preset(self, preset_id: str) -> PresetConfig | None:
        """Get a preset by ID."""
        return self._presets.get(preset_id)

    def get_preset_by_name(self, name: str) -> PresetConfig | None:
        """Get a preset by name (case-insensitive)."""
        name_lower = name.lower()
        for preset in self._presets.values():
            if preset.name.lower() == name_lower:
                return preset
        return None

    def get_status(self, preset_id: str) -> PresetStatus:
        """Get the status of a preset."""
        return self._status.get(preset_id, PresetStatus())

    def set_status(
        self,
        preset_id: str,
        status: str,
        result: dict[str, Any] | None = None,
    ) -> None:
        """Update the status of a preset."""
        if preset_id not in self._status:
            self._status[preset_id] = PresetStatus()

        self._status[preset_id].status = status
        if result is not None:
            self._status[preset_id].last_result = result

        if status in [PRESET_STATUS_SUCCESS, PRESET_STATUS_FAILED]:
            self._status[preset_id].last_activated = datetime.now().isoformat()

        # Trigger entity updates
        self.hass.async_create_task(self._notify_listeners())

    async def create_preset(
        self,
        name: str,
        entities: list[str],
        state: str = "on",
        brightness_pct: int = 100,
        rgb_color: list[int] | None = None,
        color_temp_kelvin: int | None = None,
        effect: str | None = None,
        targets: list[dict[str, Any]] | None = None,
        transition: float = 0.0,
        skip_verification: bool = False,
    ) -> PresetConfig:
        """Create a new preset."""
        preset_id = str(uuid.uuid4())

        preset = PresetConfig(
            id=preset_id,
            name=name,
            entities=entities,
            state=state,
            brightness_pct=brightness_pct,
            rgb_color=rgb_color,
            color_temp_kelvin=color_temp_kelvin,
            effect=effect,
            targets=targets or [],
            transition=transition,
            skip_verification=skip_verification,
        )

        self._presets[preset_id] = preset
        self._status[preset_id] = PresetStatus()

        await self._save_presets()

        _LOGGER.info("Created preset: %s (%s)", name, preset_id)
        return preset

    async def update_preset(
        self, preset_id: str, **kwargs: Any
    ) -> PresetConfig | None:
        """Update an existing preset."""
        if preset_id not in self._presets:
            _LOGGER.warning("Preset not found: %s", preset_id)
            return None

        preset = self._presets[preset_id]

        # Update fields
        for key, value in kwargs.items():
            if hasattr(preset, key) and key != "id":
                setattr(preset, key, value)

        await self._save_presets()

        _LOGGER.info("Updated preset: %s", preset_id)
        return preset

    async def delete_preset(self, preset_id: str) -> bool:
        """Delete a preset."""
        if preset_id not in self._presets:
            _LOGGER.warning("Preset not found: %s", preset_id)
            return False

        preset = self._presets.pop(preset_id)
        self._status.pop(preset_id, None)

        await self._save_presets()

        _LOGGER.info("Deleted preset: %s (%s)", preset.name, preset_id)
        return True

    async def create_preset_from_current(
        self, name: str, entities: list[str]
    ) -> PresetConfig | None:
        """Create a preset from the current state of entities."""
        if not entities:
            _LOGGER.warning("No entities provided for preset creation")
            return None

        targets: list[dict[str, Any]] = []

        for entity_id in entities:
            state = self.hass.states.get(entity_id)
            if not state:
                continue

            target: dict[str, Any] = {"entity_id": entity_id}

            if state.state == "on":
                attrs = state.attributes

                # Brightness
                if "brightness" in attrs:
                    brightness = attrs["brightness"]
                    target["brightness_pct"] = round((brightness / 255) * 100)

                # RGB color
                if "rgb_color" in attrs:
                    target["rgb_color"] = list(attrs["rgb_color"])

                # Color temperature
                if "color_temp_kelvin" in attrs:
                    target["color_temp_kelvin"] = attrs["color_temp_kelvin"]
                elif "color_temperature_kelvin" in attrs:
                    target["color_temp_kelvin"] = attrs["color_temperature_kelvin"]

                # Effect
                if "effect" in attrs and attrs["effect"] not in [None, "none", "None"]:
                    target["effect"] = attrs["effect"]

            targets.append(target)

        # Determine overall state
        states = [self.hass.states.get(e) for e in entities]
        any_on = any(s and s.state == "on" for s in states)

        # Create preset
        preset = await self.create_preset(
            name=name,
            entities=entities,
            state="on" if any_on else "off",
            targets=targets if any_on else [],
        )

        _LOGGER.info(
            "Created preset from current state: %s with %d entities",
            name,
            len(entities),
        )

        return preset
