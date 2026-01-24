"""Light Controller integration for Home Assistant."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
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
    CONF_NOTIFY_ON_FAILURE,
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
    ATTR_NOTIFY_ON_FAILURE,
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

# Service schema for ensure_state
SERVICE_ENSURE_STATE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITIES): cv.entity_ids,
        vol.Optional(ATTR_STATE_TARGET, default="on"): vol.In(["on", "off"]),
        vol.Optional(ATTR_DEFAULT_BRIGHTNESS_PCT): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=100)
        ),
        vol.Optional(ATTR_DEFAULT_RGB_COLOR): vol.All(
            vol.ExactSequence([
                vol.All(vol.Coerce(int), vol.Range(min=0, max=255)),
                vol.All(vol.Coerce(int), vol.Range(min=0, max=255)),
                vol.All(vol.Coerce(int), vol.Range(min=0, max=255)),
            ])
        ),
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
                        vol.Optional("rgb_color"): vol.All(
                            vol.ExactSequence([
                                vol.All(vol.Coerce(int), vol.Range(min=0, max=255)),
                                vol.All(vol.Coerce(int), vol.Range(min=0, max=255)),
                                vol.All(vol.Coerce(int), vol.Range(min=0, max=255)),
                            ])
                        ),
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
        vol.Optional(ATTR_NOTIFY_ON_FAILURE): cv.string,
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
        vol.Optional(ATTR_DEFAULT_RGB_COLOR): vol.All(
            vol.ExactSequence([
                vol.All(vol.Coerce(int), vol.Range(min=0, max=255)),
                vol.All(vol.Coerce(int), vol.Range(min=0, max=255)),
                vol.All(vol.Coerce(int), vol.Range(min=0, max=255)),
            ])
        ),
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


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Light Controller from a config entry."""
    _LOGGER.info("Setting up Light Controller integration")

    # Initialize controller and preset manager
    controller = LightController(hass)
    preset_manager = PresetManager(hass, entry)

    # Store instances
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "controller": controller,
        "preset_manager": preset_manager,
        "entry": entry,
    }

    # Get configured options (defaults)
    options = entry.options

    # =========================================================================
    # Service: ensure_state
    # =========================================================================

    async def async_handle_ensure_state(call: ServiceCall) -> dict[str, Any]:
        """Handle the ensure_state service call."""
        entities = call.data.get(ATTR_ENTITIES, [])
        state_target = call.data.get(ATTR_STATE_TARGET, "on")

        brightness_pct = call.data.get(
            ATTR_DEFAULT_BRIGHTNESS_PCT,
            options.get(CONF_DEFAULT_BRIGHTNESS_PCT, DEFAULT_BRIGHTNESS_PCT),
        )

        rgb_color = call.data.get(ATTR_DEFAULT_RGB_COLOR)
        color_temp_kelvin = call.data.get(ATTR_DEFAULT_COLOR_TEMP_KELVIN)
        effect = call.data.get(ATTR_DEFAULT_EFFECT)
        targets = call.data.get(ATTR_TARGETS)

        brightness_tolerance = call.data.get(
            ATTR_BRIGHTNESS_TOLERANCE,
            options.get(CONF_BRIGHTNESS_TOLERANCE, DEFAULT_BRIGHTNESS_TOLERANCE),
        )
        rgb_tolerance = call.data.get(
            ATTR_RGB_TOLERANCE,
            options.get(CONF_RGB_TOLERANCE, DEFAULT_RGB_TOLERANCE),
        )
        kelvin_tolerance = call.data.get(
            ATTR_KELVIN_TOLERANCE,
            options.get(CONF_KELVIN_TOLERANCE, DEFAULT_KELVIN_TOLERANCE),
        )

        transition = call.data.get(
            ATTR_TRANSITION,
            options.get(CONF_DEFAULT_TRANSITION, DEFAULT_TRANSITION),
        )
        delay_after_send = call.data.get(
            ATTR_DELAY_AFTER_SEND,
            options.get(CONF_DELAY_AFTER_SEND, DEFAULT_DELAY_AFTER_SEND),
        )
        max_retries = call.data.get(
            ATTR_MAX_RETRIES,
            options.get(CONF_MAX_RETRIES, DEFAULT_MAX_RETRIES),
        )
        max_runtime_seconds = call.data.get(
            ATTR_MAX_RUNTIME_SECONDS,
            options.get(CONF_MAX_RUNTIME_SECONDS, DEFAULT_MAX_RUNTIME_SECONDS),
        )
        use_exponential_backoff = call.data.get(
            ATTR_USE_EXPONENTIAL_BACKOFF,
            options.get(CONF_USE_EXPONENTIAL_BACKOFF, DEFAULT_USE_EXPONENTIAL_BACKOFF),
        )
        max_backoff_seconds = call.data.get(
            ATTR_MAX_BACKOFF_SECONDS,
            options.get(CONF_MAX_BACKOFF_SECONDS, DEFAULT_MAX_BACKOFF_SECONDS),
        )

        skip_verification = call.data.get(ATTR_SKIP_VERIFICATION, False)
        log_success = call.data.get(
            ATTR_LOG_SUCCESS,
            options.get(CONF_LOG_SUCCESS, DEFAULT_LOG_SUCCESS),
        )

        notify_on_failure = call.data.get(ATTR_NOTIFY_ON_FAILURE)
        if notify_on_failure is None:
            config_notify = options.get(CONF_NOTIFY_ON_FAILURE, "")
            if config_notify:
                notify_on_failure = config_notify

        result = await controller.ensure_state(
            entities=entities,
            state_target=state_target,
            default_brightness_pct=brightness_pct,
            default_rgb_color=rgb_color,
            default_color_temp_kelvin=color_temp_kelvin,
            default_effect=effect,
            targets=targets,
            brightness_tolerance=brightness_tolerance,
            rgb_tolerance=rgb_tolerance,
            kelvin_tolerance=kelvin_tolerance,
            transition=transition,
            delay_after_send=delay_after_send,
            max_retries=max_retries,
            max_runtime_seconds=max_runtime_seconds,
            use_exponential_backoff=use_exponential_backoff,
            max_backoff_seconds=max_backoff_seconds,
            skip_verification=skip_verification,
            log_success=log_success,
            notify_on_failure=notify_on_failure,
        )

        return result

    # =========================================================================
    # Service: activate_preset
    # =========================================================================

    async def async_handle_activate_preset(call: ServiceCall) -> dict[str, Any]:
        """Handle the activate_preset service call."""
        preset_name_or_id = call.data.get(ATTR_PRESET, "")

        # Find preset by name or ID
        preset = preset_manager.get_preset(preset_name_or_id)
        if not preset:
            preset = preset_manager.get_preset_by_name(preset_name_or_id)

        if not preset:
            _LOGGER.error("Preset not found: %s", preset_name_or_id)
            return {
                "success": False,
                "result": "error",
                "message": f"Preset not found: {preset_name_or_id}",
            }

        _LOGGER.info("Activating preset: %s", preset.name)

        # Update status
        preset_manager.set_status(preset.id, PRESET_STATUS_ACTIVATING)

        # Execute
        result = await controller.ensure_state(
            entities=preset.entities,
            state_target=preset.state,
            default_brightness_pct=preset.brightness_pct,
            default_rgb_color=preset.rgb_color,
            default_color_temp_kelvin=preset.color_temp_kelvin,
            default_effect=preset.effect,
            targets=preset.targets if preset.targets else None,
            transition=preset.transition,
            skip_verification=preset.skip_verification,
            brightness_tolerance=options.get(CONF_BRIGHTNESS_TOLERANCE, DEFAULT_BRIGHTNESS_TOLERANCE),
            rgb_tolerance=options.get(CONF_RGB_TOLERANCE, DEFAULT_RGB_TOLERANCE),
            kelvin_tolerance=options.get(CONF_KELVIN_TOLERANCE, DEFAULT_KELVIN_TOLERANCE),
            delay_after_send=options.get(CONF_DELAY_AFTER_SEND, DEFAULT_DELAY_AFTER_SEND),
            max_retries=options.get(CONF_MAX_RETRIES, DEFAULT_MAX_RETRIES),
            max_runtime_seconds=options.get(CONF_MAX_RUNTIME_SECONDS, DEFAULT_MAX_RUNTIME_SECONDS),
            use_exponential_backoff=options.get(CONF_USE_EXPONENTIAL_BACKOFF, DEFAULT_USE_EXPONENTIAL_BACKOFF),
            max_backoff_seconds=options.get(CONF_MAX_BACKOFF_SECONDS, DEFAULT_MAX_BACKOFF_SECONDS),
            log_success=options.get(CONF_LOG_SUCCESS, DEFAULT_LOG_SUCCESS),
            notify_on_failure=options.get(CONF_NOTIFY_ON_FAILURE),
        )

        # Update status
        status = PRESET_STATUS_SUCCESS if result.get("success") else PRESET_STATUS_FAILED
        preset_manager.set_status(preset.id, status, result)

        return result

    # =========================================================================
    # Service: create_preset
    # =========================================================================

    async def async_handle_create_preset(call: ServiceCall) -> dict[str, Any]:
        """Handle the create_preset service call."""
        name = call.data.get(ATTR_PRESET_NAME, "")
        entities = call.data.get(ATTR_ENTITIES, [])

        if not name or not entities:
            return {
                "success": False,
                "result": "error",
                "message": "Name and entities are required",
            }

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

    # =========================================================================
    # Service: delete_preset
    # =========================================================================

    async def async_handle_delete_preset(call: ServiceCall) -> dict[str, Any]:
        """Handle the delete_preset service call."""
        preset_id = call.data.get(ATTR_PRESET_ID, "")

        if not preset_id:
            return {
                "success": False,
                "result": "error",
                "message": "Preset ID is required",
            }

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

    # =========================================================================
    # Service: create_preset_from_current
    # =========================================================================

    async def async_handle_create_preset_from_current(call: ServiceCall) -> dict[str, Any]:
        """Handle the create_preset_from_current service call."""
        name = call.data.get(ATTR_PRESET_NAME, "")
        entities = call.data.get(ATTR_ENTITIES, [])

        if not name or not entities:
            return {
                "success": False,
                "result": "error",
                "message": "Name and entities are required",
            }

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

    # =========================================================================
    # Register services
    # =========================================================================

    hass.services.async_register(
        DOMAIN,
        SERVICE_ENSURE_STATE,
        async_handle_ensure_state,
        schema=SERVICE_ENSURE_STATE_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_ACTIVATE_PRESET,
        async_handle_activate_preset,
        schema=SERVICE_ACTIVATE_PRESET_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_CREATE_PRESET,
        async_handle_create_preset,
        schema=SERVICE_CREATE_PRESET_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_DELETE_PRESET,
        async_handle_delete_preset,
        schema=SERVICE_DELETE_PRESET_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_CREATE_PRESET_FROM_CURRENT,
        async_handle_create_preset_from_current,
        schema=SERVICE_CREATE_PRESET_FROM_CURRENT_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

    # =========================================================================
    # Forward setup to platforms
    # =========================================================================

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Listen for options updates
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    _LOGGER.info("Light Controller integration setup complete")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading Light Controller integration")

    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Unregister services
        hass.services.async_remove(DOMAIN, SERVICE_ENSURE_STATE)
        hass.services.async_remove(DOMAIN, SERVICE_ACTIVATE_PRESET)
        hass.services.async_remove(DOMAIN, SERVICE_CREATE_PRESET)
        hass.services.async_remove(DOMAIN, SERVICE_DELETE_PRESET)
        hass.services.async_remove(DOMAIN, SERVICE_CREATE_PRESET_FROM_CURRENT)

        # Remove data
        hass.data[DOMAIN].pop(entry.entry_id, None)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN, None)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options change."""
    _LOGGER.info("Reloading Light Controller due to options change")
    await hass.config_entries.async_reload(entry.entry_id)
