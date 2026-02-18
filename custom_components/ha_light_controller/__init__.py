"""Light Controller integration for Home Assistant."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from homeassistant.helpers.typing import ConfigType

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import config_validation as cv

from .const import (
    ATTR_BRIGHTNESS_TOLERANCE,
    ATTR_DEFAULT_BRIGHTNESS_PCT,
    ATTR_DEFAULT_COLOR_TEMP_KELVIN,
    ATTR_DEFAULT_EFFECT,
    ATTR_DEFAULT_RGB_COLOR,
    ATTR_DELAY_AFTER_SEND,
    # Service attributes
    ATTR_ENTITIES,
    ATTR_KELVIN_TOLERANCE,
    ATTR_LOG_SUCCESS,
    ATTR_MAX_BACKOFF_SECONDS,
    ATTR_MAX_RETRIES,
    ATTR_MAX_RUNTIME_SECONDS,
    # Preset attributes
    ATTR_PRESET,
    ATTR_PRESET_ID,
    ATTR_PRESET_NAME,
    ATTR_RGB_TOLERANCE,
    ATTR_SKIP_VERIFICATION,
    ATTR_STATE_TARGET,
    ATTR_TARGETS,
    ATTR_TRANSITION,
    ATTR_USE_EXPONENTIAL_BACKOFF,
    CONF_BRIGHTNESS_TOLERANCE,
    # Config options
    CONF_DEFAULT_BRIGHTNESS_PCT,
    CONF_DEFAULT_TRANSITION,
    CONF_DELAY_AFTER_SEND,
    CONF_KELVIN_TOLERANCE,
    CONF_LOG_SUCCESS,
    CONF_MAX_BACKOFF_SECONDS,
    CONF_MAX_RETRIES,
    CONF_MAX_RUNTIME_SECONDS,
    CONF_RGB_TOLERANCE,
    CONF_USE_EXPONENTIAL_BACKOFF,
    # Defaults
    DEFAULT_BRIGHTNESS_PCT,
    DEFAULT_BRIGHTNESS_TOLERANCE,
    DEFAULT_DELAY_AFTER_SEND,
    DEFAULT_KELVIN_TOLERANCE,
    DEFAULT_LOG_SUCCESS,
    DEFAULT_MAX_BACKOFF_SECONDS,
    DEFAULT_MAX_RETRIES,
    DEFAULT_MAX_RUNTIME_SECONDS,
    DEFAULT_RGB_TOLERANCE,
    DEFAULT_TRANSITION,
    DEFAULT_USE_EXPONENTIAL_BACKOFF,
    DOMAIN,
    PLATFORMS,
    PRESET_STATUS_ACTIVATING,
    PRESET_STATUS_FAILED,
    PRESET_STATUS_SUCCESS,
    RESULT_ATTEMPTS,
    RESULT_CODE,
    RESULT_CODE_ERROR,
    RESULT_CODE_SUCCESS,
    RESULT_ELAPSED_SECONDS,
    RESULT_FAILED_LIGHTS,
    RESULT_MESSAGE,
    RESULT_SKIPPED_LIGHTS,
    RESULT_SUCCESS,
    RESULT_TOTAL_LIGHTS,
    SERVICE_ACTIVATE_PRESET,
    SERVICE_CREATE_PRESET,
    SERVICE_CREATE_PRESET_FROM_CURRENT,
    SERVICE_DELETE_PRESET,
    SERVICE_ENSURE_STATE,
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
    call_data: Mapping[str, Any],
    options: Mapping[str, Any],
    attr: str,
    conf: str,
    default: Any,
) -> Any:
    """Get parameter from call data, falling back to options then default."""
    return call_data.get(attr, options.get(conf, default))


def _get_optional_str(
    call_data: Mapping[str, Any],
    options: Mapping[str, Any],
    attr: str,
    conf: str,
) -> str | None:
    """Get optional string parameter, treating empty as None."""
    val = call_data.get(attr) or options.get(conf) or None
    return val if val else None


def _service_response(
    *,
    success: bool,
    result_code: str,
    message: str,
    attempts: int = 0,
    total_lights: int = 0,
    failed_lights: list[str] | None = None,
    skipped_lights: list[str] | None = None,
    elapsed_seconds: float = 0.0,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build standardized service response payload."""
    response: dict[str, Any] = {
        RESULT_SUCCESS: success,
        RESULT_CODE: result_code,
        RESULT_MESSAGE: message,
        RESULT_ATTEMPTS: attempts,
        RESULT_TOTAL_LIGHTS: total_lights,
        RESULT_FAILED_LIGHTS: failed_lights or [],
        RESULT_SKIPPED_LIGHTS: skipped_lights or [],
        RESULT_ELAPSED_SECONDS: elapsed_seconds,
    }
    if extra:
        response.update(extra)
    return response


# Reusable RGB color validation schema
RGB_COLOR_SCHEMA = vol.All(
    vol.ExactSequence(
        [
            vol.All(vol.Coerce(int), vol.Range(min=0, max=255)),
            vol.All(vol.Coerce(int), vol.Range(min=0, max=255)),
            vol.All(vol.Coerce(int), vol.Range(min=0, max=255)),
        ]
    )
)

TARGET_OVERRIDE_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_id,
        vol.Optional("state"): vol.In(["on", "off"]),
        vol.Optional("brightness_pct"): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=100)
        ),
        vol.Optional("rgb_color"): RGB_COLOR_SCHEMA,
        vol.Optional("color_temp_kelvin"): vol.All(
            vol.Coerce(int), vol.Range(min=1000, max=10000)
        ),
        vol.Optional("effect"): cv.string,
        vol.Optional("transition"): vol.All(
            vol.Coerce(float), vol.Range(min=0, max=300)
        ),
    }
)
TARGET_OVERRIDES_SCHEMA = vol.All(cv.ensure_list, [TARGET_OVERRIDE_SCHEMA])


@dataclass
class LightControllerData:
    """Runtime data for the Light Controller integration."""

    controller: LightController
    preset_manager: PresetManager


type LightControllerConfigEntry = ConfigEntry[LightControllerData]

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
        vol.Optional(ATTR_TARGETS): TARGET_OVERRIDES_SCHEMA,
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
        vol.Optional(ATTR_TARGETS): TARGET_OVERRIDES_SCHEMA,
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


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:  # noqa: C901
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
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="not_configured",
            )

        controller = entry.runtime_data.controller
        options = entry.options
        data = call.data

        # Helper for getting parameters with fallback chain
        def get(attr: str, conf: str, default: Any) -> Any:
            return _get_param(data, options, attr, conf, default)

        try:
            return await controller.ensure_state(
                entities=data.get(ATTR_ENTITIES, []),
                state_target=data.get(ATTR_STATE_TARGET, "on"),
                default_brightness_pct=get(
                    ATTR_DEFAULT_BRIGHTNESS_PCT,
                    CONF_DEFAULT_BRIGHTNESS_PCT,
                    DEFAULT_BRIGHTNESS_PCT,
                ),
                default_rgb_color=data.get(ATTR_DEFAULT_RGB_COLOR),
                default_color_temp_kelvin=data.get(ATTR_DEFAULT_COLOR_TEMP_KELVIN),
                default_effect=data.get(ATTR_DEFAULT_EFFECT),
                targets=data.get(ATTR_TARGETS),
                brightness_tolerance=get(
                    ATTR_BRIGHTNESS_TOLERANCE,
                    CONF_BRIGHTNESS_TOLERANCE,
                    DEFAULT_BRIGHTNESS_TOLERANCE,
                ),
                rgb_tolerance=get(
                    ATTR_RGB_TOLERANCE, CONF_RGB_TOLERANCE, DEFAULT_RGB_TOLERANCE
                ),
                kelvin_tolerance=get(
                    ATTR_KELVIN_TOLERANCE,
                    CONF_KELVIN_TOLERANCE,
                    DEFAULT_KELVIN_TOLERANCE,
                ),
                transition=get(
                    ATTR_TRANSITION, CONF_DEFAULT_TRANSITION, DEFAULT_TRANSITION
                ),
                delay_after_send=get(
                    ATTR_DELAY_AFTER_SEND,
                    CONF_DELAY_AFTER_SEND,
                    DEFAULT_DELAY_AFTER_SEND,
                ),
                max_retries=get(
                    ATTR_MAX_RETRIES, CONF_MAX_RETRIES, DEFAULT_MAX_RETRIES
                ),
                max_runtime_seconds=get(
                    ATTR_MAX_RUNTIME_SECONDS,
                    CONF_MAX_RUNTIME_SECONDS,
                    DEFAULT_MAX_RUNTIME_SECONDS,
                ),
                use_exponential_backoff=get(
                    ATTR_USE_EXPONENTIAL_BACKOFF,
                    CONF_USE_EXPONENTIAL_BACKOFF,
                    DEFAULT_USE_EXPONENTIAL_BACKOFF,
                ),
                max_backoff_seconds=get(
                    ATTR_MAX_BACKOFF_SECONDS,
                    CONF_MAX_BACKOFF_SECONDS,
                    DEFAULT_MAX_BACKOFF_SECONDS,
                ),
                skip_verification=data.get(ATTR_SKIP_VERIFICATION, False),
                log_success=get(
                    ATTR_LOG_SUCCESS, CONF_LOG_SUCCESS, DEFAULT_LOG_SUCCESS
                ),
            )
        except (HomeAssistantError, ServiceValidationError):
            raise
        except Exception as e:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="ensure_state_error",
                translation_placeholders={"error": str(e)},
            ) from e

    # =========================================================================
    # Service: activate_preset
    # =========================================================================

    async def async_handle_activate_preset(call: ServiceCall) -> dict[str, Any]:
        """Handle the activate_preset service call."""
        entry = _get_loaded_entry(hass)
        if not entry or not entry.runtime_data:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="not_configured",
            )

        preset_manager = entry.runtime_data.preset_manager
        controller = entry.runtime_data.controller
        options = entry.options

        preset_name_or_id = call.data.get(ATTR_PRESET, "")

        preset = preset_manager.find_preset(preset_name_or_id)
        if not preset:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="preset_not_found",
                translation_placeholders={"preset": preset_name_or_id},
            )

        _LOGGER.info("Activating preset: %s", preset.name)
        await preset_manager.set_status(preset.id, PRESET_STATUS_ACTIVATING)

        try:
            result = await preset_manager.activate_preset_with_options(
                preset, controller, options
            )

            status = (
                PRESET_STATUS_SUCCESS if result.get("success") else PRESET_STATUS_FAILED
            )
            await preset_manager.set_status(preset.id, status, result)

            return result
        except (HomeAssistantError, ServiceValidationError):
            raise
        except Exception as e:
            await preset_manager.set_status(
                preset.id, PRESET_STATUS_FAILED, {"message": str(e)}
            )
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="activate_preset_error",
                translation_placeholders={
                    "preset_name": preset.name,
                    "error": str(e),
                },
            ) from e

    # =========================================================================
    # Service: create_preset
    # =========================================================================

    async def async_handle_create_preset(call: ServiceCall) -> dict[str, Any]:
        """Handle the create_preset service call."""
        entry = _get_loaded_entry(hass)
        if not entry or not entry.runtime_data:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="not_configured",
            )

        preset_manager = entry.runtime_data.preset_manager

        name = call.data.get(ATTR_PRESET_NAME, "")
        entities = call.data.get(ATTR_ENTITIES, [])

        if not name or not entities:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="name_entities_required",
            )

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

            return _service_response(
                success=True,
                result_code=RESULT_CODE_SUCCESS,
                message=f"Created preset: {preset.name}",
                extra={
                    "preset_id": preset.id,
                    "preset_name": preset.name,
                },
            )
        except (HomeAssistantError, ServiceValidationError):
            raise
        except Exception as e:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="create_preset_error",
                translation_placeholders={"error": str(e)},
            ) from e

    # =========================================================================
    # Service: delete_preset
    # =========================================================================

    async def async_handle_delete_preset(call: ServiceCall) -> dict[str, Any]:
        """Handle the delete_preset service call."""
        entry = _get_loaded_entry(hass)
        if not entry or not entry.runtime_data:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="not_configured",
            )

        preset_manager = entry.runtime_data.preset_manager
        preset_id = call.data.get(ATTR_PRESET_ID, "")

        if not preset_id:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="preset_id_required",
            )

        try:
            success = await preset_manager.delete_preset(preset_id)

            if not success:
                raise ServiceValidationError(
                    translation_domain=DOMAIN,
                    translation_key="preset_not_found",
                    translation_placeholders={"preset": preset_id},
                )

            _LOGGER.info("Deleted preset: %s", preset_id)
            return _service_response(
                success=True,
                result_code=RESULT_CODE_SUCCESS,
                message=f"Deleted preset: {preset_id}",
                extra={"preset_id": preset_id},
            )
        except (HomeAssistantError, ServiceValidationError):
            raise
        except Exception as e:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="delete_preset_error",
                translation_placeholders={"error": str(e)},
            ) from e

    # =========================================================================
    # Service: create_preset_from_current
    # =========================================================================

    async def async_handle_create_preset_from_current(
        call: ServiceCall,
    ) -> dict[str, Any]:
        """Handle the create_preset_from_current service call."""
        entry = _get_loaded_entry(hass)
        if not entry or not entry.runtime_data:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="not_configured",
            )

        preset_manager = entry.runtime_data.preset_manager

        name = call.data.get(ATTR_PRESET_NAME, "")
        entities = call.data.get(ATTR_ENTITIES, [])

        if not name or not entities:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="name_entities_required",
            )

        try:
            preset = await preset_manager.create_preset_from_current(name, entities)

            if not preset:
                raise HomeAssistantError(
                    translation_domain=DOMAIN,
                    translation_key="preset_create_failed",
                )

            _LOGGER.info(
                "Created preset from current state: %s (%s)", preset.name, preset.id
            )
            return _service_response(
                success=True,
                result_code=RESULT_CODE_SUCCESS,
                message=f"Created preset from current state: {preset.name}",
                extra={
                    "preset_id": preset.id,
                    "preset_name": preset.name,
                },
            )
        except (HomeAssistantError, ServiceValidationError):
            raise
        except Exception as e:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="create_from_current_error",
                translation_placeholders={"error": str(e)},
            ) from e

    # =========================================================================
    # Register all services
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
