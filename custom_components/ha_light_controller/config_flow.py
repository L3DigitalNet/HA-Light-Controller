"""Config flow for Light Controller integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
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
    PRESET_NAME,
    PRESET_ENTITIES,
    PRESET_STATE,
    PRESET_BRIGHTNESS_PCT,
    PRESET_RGB_COLOR,
    PRESET_COLOR_TEMP_KELVIN,
    PRESET_TRANSITION,
    PRESET_SKIP_VERIFICATION,
)

_LOGGER = logging.getLogger(__name__)


class LightControllerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Light Controller."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Check if already configured
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title="Light Controller",
                data={},
                options={
                    CONF_DEFAULT_BRIGHTNESS_PCT: user_input.get(
                        CONF_DEFAULT_BRIGHTNESS_PCT, DEFAULT_BRIGHTNESS_PCT
                    ),
                    CONF_DEFAULT_TRANSITION: user_input.get(
                        CONF_DEFAULT_TRANSITION, DEFAULT_TRANSITION
                    ),
                    CONF_BRIGHTNESS_TOLERANCE: user_input.get(
                        CONF_BRIGHTNESS_TOLERANCE, DEFAULT_BRIGHTNESS_TOLERANCE
                    ),
                    CONF_RGB_TOLERANCE: user_input.get(
                        CONF_RGB_TOLERANCE, DEFAULT_RGB_TOLERANCE
                    ),
                    CONF_KELVIN_TOLERANCE: user_input.get(
                        CONF_KELVIN_TOLERANCE, DEFAULT_KELVIN_TOLERANCE
                    ),
                    CONF_DELAY_AFTER_SEND: user_input.get(
                        CONF_DELAY_AFTER_SEND, DEFAULT_DELAY_AFTER_SEND
                    ),
                    CONF_MAX_RETRIES: user_input.get(
                        CONF_MAX_RETRIES, DEFAULT_MAX_RETRIES
                    ),
                    CONF_MAX_RUNTIME_SECONDS: user_input.get(
                        CONF_MAX_RUNTIME_SECONDS, DEFAULT_MAX_RUNTIME_SECONDS
                    ),
                    CONF_USE_EXPONENTIAL_BACKOFF: user_input.get(
                        CONF_USE_EXPONENTIAL_BACKOFF, DEFAULT_USE_EXPONENTIAL_BACKOFF
                    ),
                    CONF_MAX_BACKOFF_SECONDS: user_input.get(
                        CONF_MAX_BACKOFF_SECONDS, DEFAULT_MAX_BACKOFF_SECONDS
                    ),
                    CONF_LOG_SUCCESS: user_input.get(
                        CONF_LOG_SUCCESS, DEFAULT_LOG_SUCCESS
                    ),
                    CONF_NOTIFY_ON_FAILURE: user_input.get(CONF_NOTIFY_ON_FAILURE, ""),
                },
            )

        # Show the setup form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_DEFAULT_BRIGHTNESS_PCT,
                        default=DEFAULT_BRIGHTNESS_PCT,
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=100,
                            step=1,
                            unit_of_measurement="%",
                            mode=selector.NumberSelectorMode.SLIDER,
                        )
                    ),
                    vol.Optional(
                        CONF_DEFAULT_TRANSITION,
                        default=DEFAULT_TRANSITION,
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0,
                            max=60,
                            step=0.5,
                            unit_of_measurement="s",
                            mode=selector.NumberSelectorMode.SLIDER,
                        )
                    ),
                }
            ),
            errors=errors,
            description_placeholders={},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Get the options flow for this handler."""
        return LightControllerOptionsFlow()


class LightControllerOptionsFlow(OptionsFlow):
    """Handle options flow for Light Controller."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options - show menu."""
        return self.async_show_menu(
            step_id="init",
            menu_options=[
                "defaults",
                "tolerances",
                "retry",
                "notifications",
                "add_preset",
                "manage_presets",
            ],
        )

    async def async_step_defaults(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle default brightness and transition settings."""
        if user_input is not None:
            new_options = {**self.config_entry.options, **user_input}
            return self.async_create_entry(title="", data=new_options)

        options = self.config_entry.options

        return self.async_show_form(
            step_id="defaults",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_DEFAULT_BRIGHTNESS_PCT,
                        default=options.get(
                            CONF_DEFAULT_BRIGHTNESS_PCT, DEFAULT_BRIGHTNESS_PCT
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=100,
                            step=1,
                            unit_of_measurement="%",
                            mode=selector.NumberSelectorMode.SLIDER,
                        )
                    ),
                    vol.Optional(
                        CONF_DEFAULT_TRANSITION,
                        default=options.get(
                            CONF_DEFAULT_TRANSITION, DEFAULT_TRANSITION
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0,
                            max=60,
                            step=0.5,
                            unit_of_measurement="s",
                            mode=selector.NumberSelectorMode.SLIDER,
                        )
                    ),
                }
            ),
        )

    async def async_step_tolerances(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle tolerance settings."""
        if user_input is not None:
            new_options = {**self.config_entry.options, **user_input}
            return self.async_create_entry(title="", data=new_options)

        options = self.config_entry.options

        return self.async_show_form(
            step_id="tolerances",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_BRIGHTNESS_TOLERANCE,
                        default=options.get(
                            CONF_BRIGHTNESS_TOLERANCE, DEFAULT_BRIGHTNESS_TOLERANCE
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0,
                            max=20,
                            step=1,
                            unit_of_measurement="%",
                            mode=selector.NumberSelectorMode.SLIDER,
                        )
                    ),
                    vol.Optional(
                        CONF_RGB_TOLERANCE,
                        default=options.get(CONF_RGB_TOLERANCE, DEFAULT_RGB_TOLERANCE),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0,
                            max=50,
                            step=1,
                            mode=selector.NumberSelectorMode.SLIDER,
                        )
                    ),
                    vol.Optional(
                        CONF_KELVIN_TOLERANCE,
                        default=options.get(
                            CONF_KELVIN_TOLERANCE, DEFAULT_KELVIN_TOLERANCE
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0,
                            max=500,
                            step=10,
                            unit_of_measurement="K",
                            mode=selector.NumberSelectorMode.SLIDER,
                        )
                    ),
                }
            ),
        )

    async def async_step_retry(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle retry and timing settings."""
        if user_input is not None:
            new_options = {**self.config_entry.options, **user_input}
            return self.async_create_entry(title="", data=new_options)

        options = self.config_entry.options

        return self.async_show_form(
            step_id="retry",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_DELAY_AFTER_SEND,
                        default=options.get(
                            CONF_DELAY_AFTER_SEND, DEFAULT_DELAY_AFTER_SEND
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0.5,
                            max=30,
                            step=0.5,
                            unit_of_measurement="s",
                            mode=selector.NumberSelectorMode.SLIDER,
                        )
                    ),
                    vol.Optional(
                        CONF_MAX_RETRIES,
                        default=options.get(CONF_MAX_RETRIES, DEFAULT_MAX_RETRIES),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=10,
                            step=1,
                            mode=selector.NumberSelectorMode.SLIDER,
                        )
                    ),
                    vol.Optional(
                        CONF_MAX_RUNTIME_SECONDS,
                        default=options.get(
                            CONF_MAX_RUNTIME_SECONDS, DEFAULT_MAX_RUNTIME_SECONDS
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=10,
                            max=300,
                            step=10,
                            unit_of_measurement="s",
                            mode=selector.NumberSelectorMode.SLIDER,
                        )
                    ),
                    vol.Optional(
                        CONF_USE_EXPONENTIAL_BACKOFF,
                        default=options.get(
                            CONF_USE_EXPONENTIAL_BACKOFF, DEFAULT_USE_EXPONENTIAL_BACKOFF
                        ),
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_MAX_BACKOFF_SECONDS,
                        default=options.get(
                            CONF_MAX_BACKOFF_SECONDS, DEFAULT_MAX_BACKOFF_SECONDS
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=5,
                            max=120,
                            step=5,
                            unit_of_measurement="s",
                            mode=selector.NumberSelectorMode.SLIDER,
                        )
                    ),
                }
            ),
        )

    async def async_step_notifications(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle notification settings."""
        if user_input is not None:
            # Handle empty notify service
            if not user_input.get(CONF_NOTIFY_ON_FAILURE):
                user_input[CONF_NOTIFY_ON_FAILURE] = ""
            new_options = {**self.config_entry.options, **user_input}
            return self.async_create_entry(title="", data=new_options)

        options = self.config_entry.options

        return self.async_show_form(
            step_id="notifications",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_LOG_SUCCESS,
                        default=options.get(CONF_LOG_SUCCESS, DEFAULT_LOG_SUCCESS),
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_NOTIFY_ON_FAILURE,
                        default=options.get(CONF_NOTIFY_ON_FAILURE, ""),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        )
                    ),
                }
            ),
        )

    async def async_step_add_preset(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle adding a new preset."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate input
            name = user_input.get(PRESET_NAME, "").strip()
            entities = user_input.get(PRESET_ENTITIES, [])

            if not name:
                errors["base"] = "name_required"
            elif not entities:
                errors["base"] = "entities_required"
            else:
                # Get preset manager from runtime_data and create preset
                if hasattr(self.config_entry, 'runtime_data') and self.config_entry.runtime_data:
                    preset_manager = self.config_entry.runtime_data.preset_manager
                    if preset_manager:
                        # Create the preset
                        await preset_manager.create_preset(
                            name=name,
                            entities=entities,
                            state=user_input.get(PRESET_STATE, "on"),
                            brightness_pct=int(user_input.get(PRESET_BRIGHTNESS_PCT, 100)),
                            rgb_color=user_input.get(PRESET_RGB_COLOR),
                            color_temp_kelvin=user_input.get(PRESET_COLOR_TEMP_KELVIN),
                            transition=float(user_input.get(PRESET_TRANSITION, 0)),
                            skip_verification=user_input.get(PRESET_SKIP_VERIFICATION, False),
                        )

                        _LOGGER.info("Created preset: %s", name)

                        # Return to menu
                        return self.async_create_entry(title="", data=self.config_entry.options)

        return self.async_show_form(
            step_id="add_preset",
            data_schema=vol.Schema(
                {
                    vol.Required(PRESET_NAME): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                    ),
                    vol.Required(PRESET_ENTITIES): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=["light", "group"],
                            multiple=True,
                        )
                    ),
                    vol.Optional(PRESET_STATE, default="on"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                selector.SelectOptionDict(value="on", label="On"),
                                selector.SelectOptionDict(value="off", label="Off"),
                            ],
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Optional(PRESET_BRIGHTNESS_PCT, default=100): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=100,
                            step=1,
                            unit_of_measurement="%",
                            mode=selector.NumberSelectorMode.SLIDER,
                        )
                    ),
                    vol.Optional(PRESET_COLOR_TEMP_KELVIN): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=2000,
                            max=6500,
                            step=100,
                            unit_of_measurement="K",
                            mode=selector.NumberSelectorMode.SLIDER,
                        )
                    ),
                    vol.Optional(PRESET_TRANSITION, default=0): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0,
                            max=60,
                            step=0.5,
                            unit_of_measurement="s",
                            mode=selector.NumberSelectorMode.SLIDER,
                        )
                    ),
                    vol.Optional(PRESET_SKIP_VERIFICATION, default=False): selector.BooleanSelector(),
                }
            ),
            errors=errors,
        )

    async def async_step_manage_presets(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle managing existing presets."""
        # Get preset manager from runtime_data
        preset_manager = None
        if hasattr(self.config_entry, 'runtime_data') and self.config_entry.runtime_data:
            preset_manager = self.config_entry.runtime_data.preset_manager

        if not preset_manager or not preset_manager.presets:
            # No presets to manage
            return self.async_show_form(
                step_id="manage_presets",
                data_schema=vol.Schema({}),
                description_placeholders={"preset_count": "0"},
                errors={"base": "no_presets"},
            )

        if user_input is not None:
            preset_id = user_input.get("preset_to_delete")
            if preset_id:
                await preset_manager.delete_preset(preset_id)
                _LOGGER.info("Deleted preset: %s", preset_id)

            return self.async_create_entry(title="", data=self.config_entry.options)

        # Build preset options
        preset_options = [
            selector.SelectOptionDict(value=pid, label=p.name)
            for pid, p in preset_manager.presets.items()
        ]

        return self.async_show_form(
            step_id="manage_presets",
            data_schema=vol.Schema(
                {
                    vol.Optional("preset_to_delete"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=preset_options,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
            description_placeholders={"preset_count": str(len(preset_manager.presets))},
        )
