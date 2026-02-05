"""Light Controller integration for Home Assistant."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from typing import TypeAlias

    from homeassistant.helpers.typing import ConfigType

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    PLATFORMS,
    SERVICE_ENSURE_STATE,
    SERVICE_ACTIVATE_PRESET,
    SERVICE_CREATE_PRESET,
    SERVICE_DELETE_PRESET,
    SERVICE_CREATE_PRESET_FROM_CURRENT,
    # Config options
    CONF_DEFAULT_BRIGHTNESS_PCT,
    CONF_DEFAULT_TRANSITION,
    CONF_BRIGHTNESS_TOLERANCE,
    CONF_RGB_TOLERANCE,
    CONF_KELVIN_TOLERANCE,
    CONF_DELAY_AFTER_SEND,
    CONF_MAX_RETRIES,
    CONF_MAX_RUNTIME_SECONDS,
    CONF_USE_EXPONENTIAL_BACKOFF,
    CONF_MAX_BACKOFF_SECONDS,
    CONF_LOG_SUCCESS,
    # Defaults
    DEFAULT_BRIGHTNESS_PCT,
    DEFAULT_TRANSITION,
    DEFAULT_BRIGHTNESS_TOLERANCE,
    DEFAULT_RGB_TOLERANCE,
    DEFAULT_KELVIN_TOLERANCE,
    DEFAULT_DELAY_AFTER_SEND,
    DEFAULT_MAX_RETRIES,
    DEFAULT_MAX_RUNTIME_SECONDS,
    DEFAULT_USE_EXPONENTIAL_BACKOFF,
    DEFAULT_MAX_BACKOFF_SECONDS,
    DEFAULT_LOG_SUCCESS,
    # Service attributes
    ATTR_ENTITIES,
    ATTR_STATE_TARGET,
    ATTR_DEFAULT_BRIGHTNESS_PCT,
    ATTR_DEFAULT_RGB_COLOR,
    ATTR_DEFAULT_COLOR_TEMP_KELVIN,
    ATTR_DEFAULT_EFFECT,
    ATTR_TARGETS,
    ATTR_BRIGHTNESS_TOLERANCE,
    ATTR_RGB_TOLERANCE,
    ATTR_KELVIN_TOLERANCE,
    ATTR_TRANSITION,
    ATTR_DELAY_AFTER_SEND,
    ATTR_MAX_RETRIES,
    ATTR_MAX_RUNTIME_SECONDS,
    ATTR_USE_EXPONENTIAL_BACKOFF,
    ATTR_MAX_BACKOFF_SECONDS,
    ATTR_SKIP_VERIFICATION,
    ATTR_LOG_SUCCESS,
    # Preset attributes
    ATTR_PRESET,
    ATTR_PRESET_NAME,
    ATTR_PRESET_ID,
    PRESET_STATUS_ACTIVATING,
    PRESET_STATUS_SUCCESS,
    PRESET_STATUS_FAILED,
)
from .controller import LightController
from .preset_manager import PresetManager

_LOGGER = logging.getLogger(__name__)

# Schema for config entry validation (empty - no YAML config)
CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)


def _get_loaded_entry(hass: HomeAssistant) -> LightControllerConfigEntry | None:
    """Get the loaded config entry for this integration.

    Returns None if no entry exists or entry is not loaded.
    """
    entries = hass.config_entries.async_entries(DOMAIN)
    for entry in entries:
        if entry.state == ConfigEntryState.LOADED:
            return entry
    return None


def _get_param(
    call_data: dict, options: dict, attr: str, conf: str, default: Any
) -> Any:
    """Get parameter from call data, falling back to options then default."""
    return call_data.get(attr, options.get(conf, default))


def _get_optional_str(
    call_data: dict, options: dict, attr: str, conf: str
) -> str | None:
    """Get optional string parameter, treating empty as None."""
    val = call_data.get(attr) or options.get(conf) or None
    return val if val else None


# Reusable RGB color validation schema
RGB_COLOR_SCHEMA = vol.All(
    vol.ExactSequence([
        vol.All(vol.Coerce(int), vol.Range(min=0, max=255)),
        vol.All(vol.Coerce(int), vol.Range(min=0, max=255)),
        vol.All(vol.Coerce(int), vol.Range(min=0, max=255)),
    ])
)


@dataclass
class LightControllerData:
    """Runtime data for the Light Controller integration."""

    controller: LightController
    preset_manager: PresetManager


if TYPE_CHECKING:
    LightControllerConfigEntry: TypeAlias = ConfigEntry[LightControllerData]
else:
    LightControllerConfigEntry = ConfigEntry

# Service schema for ensure_state
SERVICE_ENSURE_STATE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITIES): cv.entity_ids,
        vol.Optional(ATTR_STATE_TARGET, default="on"): vol.In(["on", "off"]),
        vol.Optional(ATTR_DEFAULT_BRIGHTNESS_PCT): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=100)
        ),
        vol.Optional(ATTR_DEFAULT_RGB_COLOR): RGB_COLOR_SCHEMA,
        vol.Optional(ATTR_DEFAULT_COLOR_TEMP_KELVIN): vol.All(
            vol.Coerce(int), vol.Range(min=1000, max=10000)
        ),
        vol.Optional(ATTR_DEFAULT_EFFECT): cv.string,
        vol.Optional(ATTR_TARGETS): vol.All(
            cv.ensure_list,
            [
                vol.Schema(
                    {
                        vol.Required("entity_id"): cv.entity_id,
                        vol.Optional("brightness_pct"): vol.All(
                            vol.Coerce(int), vol.Range(min=1, max=100)
                        ),
                        vol.Optional("rgb_color"): RGB_COLOR_SCHEMA,
                        vol.Optional("color_temp_kelvin"): vol.All(
                            vol.Coerce(int), vol.Range(min=1000, max=10000)
                        ),
                        vol.Optional("effect"): cv.string,
                    },
                    extra=vol.ALLOW_EXTRA,
                )
            ],
        ),
        vol.Optional(ATTR_BRIGHTNESS_TOLERANCE): vol.All(
            vol.Coerce(int), vol.Range(min=0, max=50)
        ),
        vol.Optional(ATTR_RGB_TOLERANCE): vol.All(
            vol.Coerce(int), vol.Range(min=0, max=100)
        ),
        vol.Optional(ATTR_KELVIN_TOLERANCE): vol.All(
            vol.Coerce(int), vol.Range(min=0, max=1000)
        ),
        vol.Optional(ATTR_TRANSITION): vol.All(
            vol.Coerce(float), vol.Range(min=0, max=300)
        ),
        vol.Optional(ATTR_DELAY_AFTER_SEND): vol.All(
            vol.Coerce(float), vol.Range(min=0.1, max=60)
        ),
        vol.Optional(ATTR_MAX_RETRIES): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=20)
        ),
        vol.Optional(ATTR_MAX_RUNTIME_SECONDS): vol.All(
            vol.Coerce(float), vol.Range(min=5, max=600)
        ),
        vol.Optional(ATTR_USE_EXPONENTIAL_BACKOFF): cv.boolean,
        vol.Optional(ATTR_MAX_BACKOFF_SECONDS): vol.All(
            vol.Coerce(float), vol.Range(min=1, max=300)
        ),
        vol.Optional(ATTR_SKIP_VERIFICATION): cv.boolean,
        vol.Optional(ATTR_LOG_SUCCESS): cv.boolean,
    }
)

# Service schema for activate_preset
SERVICE_ACTIVATE_PRESET_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_PRESET): cv.string,
    }
)

# Service schema for create_preset
SERVICE_CREATE_PRESET_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_PRESET_NAME): cv.string,
        vol.Required(ATTR_ENTITIES): cv.entity_ids,
        vol.Optional(ATTR_STATE_TARGET, default="on"): vol.In(["on", "off"]),
        vol.Optional(ATTR_DEFAULT_BRIGHTNESS_PCT, default=100): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=100)
        ),
        vol.Optional(ATTR_DEFAULT_RGB_COLOR): RGB_COLOR_SCHEMA,
        vol.Optional(ATTR_DEFAULT_COLOR_TEMP_KELVIN): vol.All(
            vol.Coerce(int), vol.Range(min=1000, max=10000)
        ),
        vol.Optional(ATTR_DEFAULT_EFFECT): cv.string,
        vol.Optional(ATTR_TARGETS): vol.All(cv.ensure_list),
        vol.Optional(ATTR_TRANSITION, default=0): vol.All(
            vol.Coerce(float), vol.Range(min=0, max=300)
        ),
        vol.Optional(ATTR_SKIP_VERIFICATION, default=False): cv.boolean,
    }
)

# Service schema for delete_preset
SERVICE_DELETE_PRESET_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_PRESET_ID): cv.string,
    }
)

# Service schema for create_preset_from_current
SERVICE_CREATE_PRESET_FROM_CURRENT_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_PRESET_NAME): cv.string,
        vol.Required(ATTR_ENTITIES): cv.entity_ids,
    }
)


async def async_setup(hass: HomeAssistant, config: "ConfigType") -> bool:
    """Set up the Light Controller integration.

    This registers services that will be available once a config entry is loaded.
    Services validate that a config entry exists and is loaded before executing.
    """
    # =========================================================================
    # Service: ensure_state
    # =========================================================================

    async def async_handle_ensure_state(call: ServiceCall) -> dict[str, Any]:
        """Handle the ensure_state service call."""
        entry = _get_loaded_entry(hass)
        if not entry or not entry.runtime_data:
            _LOGGER.error("Light Controller is not configured or not loaded")
            return {
                "success": False,
                "result": "error",
                "message": "Light Controller is not configured or not loaded",
            }

        controller = entry.runtime_data.controller
        options = entry.options
        data = call.data

        # Helper for getting parameters with fallback chain
        def get(attr: str, conf: str, default: Any) -> Any:
            return _get_param(data, options, attr, conf, default)

        try:
            result = await controller.ensure_state(
                entities=data.get(ATTR_ENTITIES, []),
                state_target=data.get(ATTR_STATE_TARGET, "on"),
                default_brightness_pct=get(ATTR_DEFAULT_BRIGHTNESS_PCT, CONF_DEFAULT_BRIGHTNESS_PCT, DEFAULT_BRIGHTNESS_PCT),
                default_rgb_color=data.get(ATTR_DEFAULT_RGB_COLOR),
                default_color_temp_kelvin=data.get(ATTR_DEFAULT_COLOR_TEMP_KELVIN),
                default_effect=data.get(ATTR_DEFAULT_EFFECT),
                targets=data.get(ATTR_TARGETS),
                brightness_tolerance=get(ATTR_BRIGHTNESS_TOLERANCE, CONF_BRIGHTNESS_TOLERANCE, DEFAULT_BRIGHTNESS_TOLERANCE),
                rgb_tolerance=get(ATTR_RGB_TOLERANCE, CONF_RGB_TOLERANCE, DEFAULT_RGB_TOLERANCE),
                kelvin_tolerance=get(ATTR_KELVIN_TOLERANCE, CONF_KELVIN_TOLERANCE, DEFAULT_KELVIN_TOLERANCE),
                transition=get(ATTR_TRANSITION, CONF_DEFAULT_TRANSITION, DEFAULT_TRANSITION),
                delay_after_send=get(ATTR_DELAY_AFTER_SEND, CONF_DELAY_AFTER_SEND, DEFAULT_DELAY_AFTER_SEND),
                max_retries=get(ATTR_MAX_RETRIES, CONF_MAX_RETRIES, DEFAULT_MAX_RETRIES),
                max_runtime_seconds=get(ATTR_MAX_RUNTIME_SECONDS, CONF_MAX_RUNTIME_SECONDS, DEFAULT_MAX_RUNTIME_SECONDS),
                use_exponential_backoff=get(ATTR_USE_EXPONENTIAL_BACKOFF, CONF_USE_EXPONENTIAL_BACKOFF, DEFAULT_USE_EXPONENTIAL_BACKOFF),
                max_backoff_seconds=get(ATTR_MAX_BACKOFF_SECONDS, CONF_MAX_BACKOFF_SECONDS, DEFAULT_MAX_BACKOFF_SECONDS),
                skip_verification=data.get(ATTR_SKIP_VERIFICATION, False),
                log_success=get(ATTR_LOG_SUCCESS, CONF_LOG_SUCCESS, DEFAULT_LOG_SUCCESS),
            )
            return result
        except Exception as e:
            _LOGGER.exception("Error in ensure_state service: %s", e)
            return {
                "success": False,
                "result": "error",
                "message": f"Service error: {str(e)}",
            }

    # =========================================================================
    # Service: activate_preset
    # =========================================================================

    async def async_handle_activate_preset(call: ServiceCall) -> dict[str, Any]:
        """Handle the activate_preset service call."""
        entry = _get_loaded_entry(hass)
        if not entry or not entry.runtime_data:
            _LOGGER.error("Light Controller is not configured or not loaded")
            return {
                "success": False,
                "result": "error",
                "message": "Light Controller is not configured or not loaded",
            }

        preset_manager = entry.runtime_data.preset_manager
        controller = entry.runtime_data.controller
        options = entry.options

        preset_name_or_id = call.data.get(ATTR_PRESET, "")

        preset = preset_manager.find_preset(preset_name_or_id)
        if not preset:
            _LOGGER.error("Preset not found: %s", preset_name_or_id)
            return {
                "success": False,
                "result": "error",
                "message": f"Preset not found: {preset_name_or_id}",
            }

        _LOGGER.info("Activating preset: %s", preset.name)
        await preset_manager.set_status(preset.id, PRESET_STATUS_ACTIVATING)

        try:
            result = await preset_manager.activate_preset_with_options(
                preset, controller, options
            )

            status = PRESET_STATUS_SUCCESS if result.get("success") else PRESET_STATUS_FAILED
            await preset_manager.set_status(preset.id, status, result)

            return result
        except Exception as e:
            _LOGGER.exception("Error activating preset %s: %s", preset.name, e)
            await preset_manager.set_status(preset.id, PRESET_STATUS_FAILED, {"message": str(e)})
            return {
                "success": False,
                "result": "error",
                "message": f"Error activating preset: {str(e)}",
            }

    # =========================================================================
    # Service: create_preset
    # =========================================================================

    async def async_handle_create_preset(call: ServiceCall) -> dict[str, Any]:
        """Handle the create_preset service call."""
        entry = _get_loaded_entry(hass)
        if not entry or not entry.runtime_data:
            _LOGGER.error("Light Controller is not configured or not loaded")
            return {
                "success": False,
                "result": "error",
                "message": "Light Controller is not configured or not loaded",
            }

        preset_manager = entry.runtime_data.preset_manager

        name = call.data.get(ATTR_PRESET_NAME, "")
        entities = call.data.get(ATTR_ENTITIES, [])

        if not name or not entities:
            return {
                "success": False,
                "result": "error",
                "message": "Name and entities are required",
            }

        try:
            preset = await preset_manager.create_preset(
                name=name,
                entities=entities,
                state=call.data.get(ATTR_STATE_TARGET, "on"),
                brightness_pct=call.data.get(ATTR_DEFAULT_BRIGHTNESS_PCT, 100),
                rgb_color=call.data.get(ATTR_DEFAULT_RGB_COLOR),
                color_temp_kelvin=call.data.get(ATTR_DEFAULT_COLOR_TEMP_KELVIN),
                effect=call.data.get(ATTR_DEFAULT_EFFECT),
                targets=call.data.get(ATTR_TARGETS),
                transition=call.data.get(ATTR_TRANSITION, 0),
                skip_verification=call.data.get(ATTR_SKIP_VERIFICATION, False),
            )

            _LOGGER.info("Created preset: %s (%s)", preset.name, preset.id)

            return {
                "success": True,
                "result": "created",
                "preset_id": preset.id,
                "preset_name": preset.name,
            }
        except Exception as e:
            _LOGGER.exception("Error creating preset: %s", e)
            return {
                "success": False,
                "result": "error",
                "message": f"Error creating preset: {str(e)}",
            }

    # =========================================================================
    # Service: delete_preset
    # =========================================================================

    async def async_handle_delete_preset(call: ServiceCall) -> dict[str, Any]:
        """Handle the delete_preset service call."""
        entry = _get_loaded_entry(hass)
        if not entry or not entry.runtime_data:
            _LOGGER.error("Light Controller is not configured or not loaded")
            return {
                "success": False,
                "result": "error",
                "message": "Light Controller is not configured or not loaded",
            }

        preset_manager = entry.runtime_data.preset_manager
        preset_id = call.data.get(ATTR_PRESET_ID, "")

        if not preset_id:
            return {
                "success": False,
                "result": "error",
                "message": "Preset ID is required",
            }

        try:
            success = await preset_manager.delete_preset(preset_id)

            if success:
                _LOGGER.info("Deleted preset: %s", preset_id)
                return {
                    "success": True,
                    "result": "deleted",
                    "preset_id": preset_id,
                }
            else:
                return {
                    "success": False,
                    "result": "error",
                    "message": f"Preset not found: {preset_id}",
                }
        except Exception as e:
            _LOGGER.exception("Error deleting preset: %s", e)
            return {
                "success": False,
                "result": "error",
                "message": f"Error deleting preset: {str(e)}",
            }

    # =========================================================================
    # Service: create_preset_from_current
    # =========================================================================

    async def async_handle_create_preset_from_current(call: ServiceCall) -> dict[str, Any]:
        """Handle the create_preset_from_current service call."""
        entry = _get_loaded_entry(hass)
        if not entry or not entry.runtime_data:
            _LOGGER.error("Light Controller is not configured or not loaded")
            return {
                "success": False,
                "result": "error",
                "message": "Light Controller is not configured or not loaded",
            }

        preset_manager = entry.runtime_data.preset_manager

        name = call.data.get(ATTR_PRESET_NAME, "")
        entities = call.data.get(ATTR_ENTITIES, [])

        if not name or not entities:
            return {
                "success": False,
                "result": "error",
                "message": "Name and entities are required",
            }

        try:
            preset = await preset_manager.create_preset_from_current(name, entities)

            if preset:
                _LOGGER.info("Created preset from current state: %s (%s)", preset.name, preset.id)
                return {
                    "success": True,
                    "result": "created",
                    "preset_id": preset.id,
                    "preset_name": preset.name,
                }
            else:
                return {
                    "success": False,
                    "result": "error",
                    "message": "Failed to create preset",
                }
        except Exception as e:
            _LOGGER.exception("Error creating preset from current state: %s", e)
            return {
                "success": False,
                "result": "error",
                "message": f"Error creating preset: {str(e)}",
            }

    # =========================================================================
    # Register all services
    # =========================================================================

    hass.services.async_register(
        DOMAIN, SERVICE_ENSURE_STATE, async_handle_ensure_state,
        schema=SERVICE_ENSURE_STATE_SCHEMA, supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_ACTIVATE_PRESET, async_handle_activate_preset,
        schema=SERVICE_ACTIVATE_PRESET_SCHEMA, supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_CREATE_PRESET, async_handle_create_preset,
        schema=SERVICE_CREATE_PRESET_SCHEMA, supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_DELETE_PRESET, async_handle_delete_preset,
        schema=SERVICE_DELETE_PRESET_SCHEMA, supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_CREATE_PRESET_FROM_CURRENT, async_handle_create_preset_from_current,
        schema=SERVICE_CREATE_PRESET_FROM_CURRENT_SCHEMA, supports_response=SupportsResponse.OPTIONAL,
    )

    _LOGGER.debug("Registered Light Controller services")
    return True


async def async_setup_entry(
    hass: HomeAssistant, entry: LightControllerConfigEntry
) -> bool:
    """Set up Light Controller from a config entry."""
    _LOGGER.info("Setting up Light Controller integration")

    # Initialize controller and preset manager
    controller = LightController(hass)
    preset_manager = PresetManager(hass, entry)

    # Store instances using runtime_data (HA 2024.4+ pattern)
    entry.runtime_data = LightControllerData(
        controller=controller,
        preset_manager=preset_manager,
    )

    # Forward setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Listen for options updates
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    _LOGGER.info("Light Controller integration setup complete")
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: LightControllerConfigEntry
) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading Light Controller integration")

    # Unload platforms (services remain registered in async_setup)
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant, entry: LightControllerConfigEntry
) -> None:
    """Reload config entry when options change."""
    _LOGGER.info("Reloading Light Controller due to options change")
    await hass.config_entries.async_reload(entry.entry_id)
