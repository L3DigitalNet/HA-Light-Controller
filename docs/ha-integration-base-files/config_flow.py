"""Config flow for Example Device integration.

The config flow provides a guided, UI-based setup experience for users.
It's MANDATORY for all new integrations submitted to Home Assistant Core.

This flow:
1. Presents forms to collect user input (host, credentials, etc.)
2. Validates the input (tries to connect, authenticate)
3. Creates a config entry to store the configuration
4. Optionally supports discovery (SSDP, mDNS, DHCP, etc.)
5. Provides reauth flow when credentials expire
6. Offers options flow for post-setup configuration changes

Key concepts:
- Each "step" is a form or decision point in the flow
- Steps return either a form (to show to user) or an entry (to finalize setup)
- Errors are shown on the form for the user to correct
"""

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
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Define the schema for the user input form.
# This determines what fields are shown and their validation.
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        # Required fields - user must fill these in
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class ExampleDeviceConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Example Device.

    The ConfigFlow class provides the framework for user-driven setup.
    Each async_step_* method represents a step in the flow.
    """

    # Version of the config entry schema.
    # Increment this when you change the data structure and implement
    # a migration in async_migrate_entry (in __init__.py).
    VERSION = 1

    # Used to pass data between steps
    _discovered_host: str | None = None

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle the initial step triggered by user action.

        This is called when the user:
        1. First starts adding the integration (user_input is None)
        2. Submits the form (user_input contains their input)

        Args:
            user_input: The data submitted by the user, or None on first load

        Returns:
            A form to display or an entry to create
        """
        errors: dict[str, str] = {}

        # If we have user input, validate it
        if user_input is not None:
            try:
                # Attempt to validate the connection.
                # This prevents saving invalid configurations.
                info = await self._async_validate_input(user_input)

            except CannotConnect:
                # Connection failed - show error on the form
                errors["base"] = "cannot_connect"

            except InvalidAuth:
                # Authentication failed - show error on the form
                errors["base"] = "invalid_auth"

            except Exception:
                # Unexpected error - log it and show generic error
                _LOGGER.exception("Unexpected exception during setup")
                errors["base"] = "unknown"

            else:
                # Validation succeeded!

                # Set unique ID to prevent duplicate entries.
                # Use a stable, unique identifier from the device.
                await self.async_set_unique_id(info["unique_id"])
                self._abort_if_unique_id_configured()

                # Create the config entry.
                # title: shown in the UI
                # data: stored configuration (sensitive data like passwords)
                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )

        # Show the form (either initially or with errors)
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(
        self,
        entry_data: dict[str, Any],
    ) -> ConfigFlowResult:
        """Handle reauthorization when credentials become invalid.

        This is triggered when the integration raises ConfigEntryAuthFailed.
        It allows users to update their credentials without removing the
        integration entirely.

        Args:
            entry_data: The current config entry data

        Returns:
            A form to collect new credentials
        """
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle the reauth confirmation step.

        Collects new credentials and validates them.
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            # Get the existing entry to update
            reauth_entry = self._get_reauth_entry()

            # Merge old data with new credentials
            data = {
                **reauth_entry.data,
                CONF_USERNAME: user_input[CONF_USERNAME],
                CONF_PASSWORD: user_input[CONF_PASSWORD],
            }

            try:
                await self._async_validate_input(data)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception during reauth")
                errors["base"] = "unknown"
            else:
                # Update the existing entry with new credentials
                return self.async_update_reload_and_abort(
                    reauth_entry,
                    data=data,
                )

        # Show the reauth form (only credentials, not host)
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )

    async def _async_validate_input(
        self,
        user_input: dict[str, Any],
    ) -> dict[str, Any]:
        """Validate the user input by attempting to connect.

        This is the critical validation step that ensures the configuration
        actually works before we save it.

        Args:
            user_input: The configuration data to validate

        Returns:
            A dict with 'title' and 'unique_id' for the entry

        Raises:
            CannotConnect: If we can't connect to the device
            InvalidAuth: If authentication fails
        """
        from .api import ExampleDeviceApiClient

        # Create a client with the provided credentials
        client = ExampleDeviceApiClient(
            host=user_input[CONF_HOST],
            username=user_input[CONF_USERNAME],
            password=user_input[CONF_PASSWORD],
        )

        # Attempt to authenticate and get device info.
        # This proves the configuration is valid.
        try:
            device_info = await client.async_get_device_info()
        except Exception as err:
            # Translate library exceptions to config flow exceptions
            # In a real integration, you'd check the specific error type
            if "auth" in str(err).lower():
                raise InvalidAuth from err
            raise CannotConnect from err

        # Return info needed to create the entry
        return {
            "title": device_info.get("name", user_input[CONF_HOST]),
            "unique_id": device_info.get("serial_number", user_input[CONF_HOST]),
        }

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> ExampleDeviceOptionsFlow:
        """Get the options flow handler.

        This enables the "Configure" button on the integration card,
        allowing users to modify settings after initial setup.
        """
        return ExampleDeviceOptionsFlow(config_entry)


class ExampleDeviceOptionsFlow(OptionsFlow):
    """Handle options flow for Example Device.

    Options are settings that can be changed after initial setup,
    like polling interval, which entities to create, etc.

    Unlike config entry data, options don't require validation
    (they're typically just preferences, not connection settings).
    """

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Manage the options.

        Args:
            user_input: The submitted options, or None on first load

        Returns:
            A form to display or an entry to create
        """
        if user_input is not None:
            # Save the new options and reload the integration
            return self.async_create_entry(title="", data=user_input)

        # Build the options schema with current values as defaults
        options_schema = vol.Schema(
            {
                vol.Optional(
                    "scan_interval",
                    default=self.config_entry.options.get("scan_interval", 30),
                ): vol.All(vol.Coerce(int), vol.Range(min=10, max=300)),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
        )


# Exception classes for config flow validation
class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class InvalidAuth(Exception):
    """Error to indicate there is invalid auth."""
