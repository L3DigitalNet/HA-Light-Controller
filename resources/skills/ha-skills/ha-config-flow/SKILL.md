---
name: ha-config-flow
description: Generate or fix Home Assistant config flow code (config_flow.py, options flow, reauth flow, strings.json). Use when the user mentions "config flow", "options flow", "reauth", "UI setup", "configuration flow", "setup wizard", or needs to create or debug the user-facing setup experience for a Home Assistant integration.
---

# Home Assistant Config Flow Development

Config flows are **mandatory** for all new Home Assistant integrations. They provide a guided, UI-based setup experience that replaces YAML configuration. Every integration must implement at minimum `async_step_user`.

## Complete config_flow.py Template

```python
"""Config flow for {Name} integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class {Name}ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for {Name}."""

    VERSION = 1  # Increment when data schema changes

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await self._async_validate_input(user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info["unique_id"])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }),
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: dict[str, Any]
    ) -> ConfigFlowResult:
        """Handle reauth when credentials expire."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Collect new credentials for reauth."""
        errors: dict[str, str] = {}

        if user_input is not None:
            reauth_entry = self._get_reauth_entry()
            data = {**reauth_entry.data, **user_input}
            try:
                await self._async_validate_input(data)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            else:
                return self.async_update_reload_and_abort(reauth_entry, data=data)

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }),
            errors=errors,
        )

    async def _async_validate_input(self, data: dict[str, Any]) -> dict[str, Any]:
        """Validate the user input allows us to connect."""
        # Replace with actual validation against your device/service
        client = MyClient(data[CONF_HOST], data[CONF_USERNAME], data[CONF_PASSWORD])
        device_info = await client.async_get_info()
        return {"title": device_info["name"], "unique_id": device_info["serial"]}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Create the options flow."""
        return {Name}OptionsFlow(config_entry)


class {Name}OptionsFlow(OptionsFlow):
    """Handle options for {Name}."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    "scan_interval",
                    default=self.config_entry.options.get("scan_interval", 30),
                ): vol.All(vol.Coerce(int), vol.Range(min=10, max=300)),
            }),
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""

class InvalidAuth(Exception):
    """Error to indicate invalid auth."""
```

## strings.json Template

Must match every step, error, and abort reason in the config flow:

```json
{
  "config": {
    "step": {
      "user": {
        "title": "Connect to {Name}",
        "description": "Enter the connection details.",
        "data": {
          "host": "Host",
          "username": "Username",
          "password": "Password"
        },
        "data_description": {
          "host": "The IP address or hostname of your device",
          "username": "Username for authentication",
          "password": "Password for authentication"
        }
      },
      "reauth_confirm": {
        "title": "Re-authenticate",
        "description": "Your credentials have expired. Please enter new credentials.",
        "data": {
          "username": "Username",
          "password": "Password"
        }
      }
    },
    "error": {
      "cannot_connect": "Unable to connect. Check the host and ensure the device is online.",
      "invalid_auth": "Authentication failed. Check your credentials.",
      "unknown": "Unexpected error occurred."
    },
    "abort": {
      "already_configured": "This device is already configured.",
      "reauth_successful": "Re-authentication successful."
    }
  },
  "options": {
    "step": {
      "init": {
        "title": "Settings",
        "data": {
          "scan_interval": "Update interval (seconds)"
        },
        "data_description": {
          "scan_interval": "How often to poll the device (10-300 seconds)"
        }
      }
    }
  }
}
```

## Key Rules

1. **Always use `data_description`** in strings.json to give users context about each field
2. **Validate before saving** — always attempt a real connection in the config flow
3. **Set unique_id** — call `async_set_unique_id()` then `_abort_if_unique_id_configured()` to prevent duplicates
4. **Store connection data in `entry.data`**, settings/preferences in `entry.options`
5. **Implement reauth** — raise `ConfigEntryAuthFailed` in coordinator to trigger it
6. **VERSION field** — increment when changing the data schema structure, implement `async_migrate_entry` for migration
7. **Use selectors** — for advanced fields, use Home Assistant selectors for better UX

## Discovery Support (Optional)

For devices that support network discovery (Zeroconf, SSDP, DHCP, USB, Bluetooth), see [reference/discovery-methods.md](reference/discovery-methods.md) for complete implementation patterns.

Basic Zeroconf example:

```python
async def async_step_zeroconf(
    self, discovery_info: ZeroconfServiceInfo
) -> ConfigFlowResult:
    """Handle zeroconf discovery."""
    self._discovered_host = discovery_info.host
    await self.async_set_unique_id(discovery_info.properties.get("id"))
    self._abort_if_unique_id_configured(updates={CONF_HOST: self._discovered_host})
    return await self.async_step_confirm()
```

Add to manifest.json: `"zeroconf": [{"type": "_mydevice._tcp.local."}]`
