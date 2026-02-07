# Home Assistant Integration Patterns Cookbook

This cookbook provides practical, battle-tested code patterns for common Home Assistant integration scenarios. Each pattern includes working code with explanations of **why** it works, not just what it does.

## Table of Contents

- [Authentication Patterns](#authentication-patterns)
- [Polling Strategies](#polling-strategies)
- [State Restoration](#state-restoration)
- [Error Recovery](#error-recovery)
- [Entity Organization](#entity-organization)
- [Device Discovery](#device-discovery)
- [Reauth Flow](#reauth-flow)
- [Options Flow](#options-flow)

---

## Authentication Patterns

### Pattern 1: API Key Authentication

**When to use:** Simple REST APIs with static API keys.

**Implementation:**

```python
"""API client with API key authentication."""
from __future__ import annotations

import aiohttp
from homeassistant.const import CONF_API_KEY


class APIKeyClient:
    """Client that uses API key in headers."""

    def __init__(self, host: str, api_key: str, session: aiohttp.ClientSession):
        """Initialize client."""
        self._host = host
        self._api_key = api_key
        self._session = session

    async def fetch_data(self) -> dict[str, Any]:
        """Fetch data with API key in header."""
        headers = {
            "X-API-Key": self._api_key,  # Or "Authorization": f"Bearer {self._api_key}"
            "Accept": "application/json",
        }

        async with self._session.get(
            f"https://{self._host}/api/data",
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=10),
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def close(self):
        """Close client resources."""
        # Session is managed by HA, don't close it
        pass


# In __init__.py
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from config entry."""
    session = async_get_clientsession(hass)
    client = APIKeyClient(
        entry.data[CONF_HOST],
        entry.data[CONF_API_KEY],
        session,
    )

    coordinator = MyCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True
```

**Why this works:**
- Reuses HA's aiohttp session (connection pooling)
- API key stored securely in ConfigEntry.data
- Headers set once at initialization
- Timeout prevents hanging requests

---

### Pattern 2: OAuth2 Token with Automatic Refresh

**When to use:** Cloud services requiring OAuth2 authentication with expiring tokens.

**Implementation:**

```python
"""OAuth2 client with automatic token refresh."""
from datetime import datetime, timedelta

from homeassistant.exceptions import ConfigEntryAuthFailed


class OAuth2Client:
    """Client with automatic token refresh."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        session: aiohttp.ClientSession,
    ):
        """Initialize OAuth2 client."""
        self._hass = hass
        self._config_entry = config_entry
        self._session = session
        self._token_url = "https://api.example.com/oauth/token"

    @property
    def access_token(self) -> str:
        """Get current access token."""
        return self._config_entry.data["access_token"]

    @property
    def refresh_token(self) -> str:
        """Get refresh token."""
        return self._config_entry.data["refresh_token"]

    @property
    def token_expires_at(self) -> datetime:
        """Get token expiration time."""
        return datetime.fromisoformat(self._config_entry.data["expires_at"])

    async def _ensure_valid_token(self) -> None:
        """Refresh token if expired or expiring soon."""
        # Refresh 5 minutes before expiration
        buffer = timedelta(minutes=5)

        if datetime.utcnow() >= self.token_expires_at - buffer:
            await self._refresh_access_token()

    async def _refresh_access_token(self) -> None:
        """Refresh the access token."""
        try:
            async with self._session.post(
                self._token_url,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                },
            ) as response:
                response.raise_for_status()
                data = await response.json()

            # Calculate expiration
            expires_at = datetime.utcnow() + timedelta(seconds=data["expires_in"])

            # Update config entry with new tokens
            new_data = {
                **self._config_entry.data,
                "access_token": data["access_token"],
                "refresh_token": data.get("refresh_token", self.refresh_token),
                "expires_at": expires_at.isoformat(),
            }

            self._hass.config_entries.async_update_entry(
                self._config_entry,
                data=new_data,
            )

            _LOGGER.info("Successfully refreshed OAuth2 token")

        except aiohttp.ClientError as err:
            _LOGGER.error("Failed to refresh token: %s", err)
            raise ConfigEntryAuthFailed("Token refresh failed") from err

    async def fetch_data(self) -> dict[str, Any]:
        """Fetch data with automatic token refresh."""
        await self._ensure_valid_token()

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }

        async with self._session.get(
            "https://api.example.com/data",
            headers=headers,
        ) as response:
            if response.status == 401:
                # Token invalid, trigger reauth
                raise ConfigEntryAuthFailed("Token invalid, reauth required")

            response.raise_for_status()
            return await response.json()
```

**Why this works:**
- Proactive refresh (5 min buffer) prevents auth failures
- Stores tokens securely in config entry
- Updates config entry atomically
- Raises ConfigEntryAuthFailed to trigger reauth flow
- Handles both 401 (invalid token) and refresh failures

---

### Pattern 3: Session-Based Authentication

**When to use:** Local devices with username/password that establish sessions.

**Implementation:**

```python
"""Session-based authentication client."""


class SessionClient:
    """Client with session-based authentication."""

    def __init__(self, host: str, session: aiohttp.ClientSession):
        """Initialize client."""
        self._host = host
        self._session = session
        self._authenticated = False

    async def authenticate(self, username: str, password: str) -> bool:
        """Login and establish session."""
        try:
            async with self._session.post(
                f"http://{self._host}/api/login",
                json={"username": username, "password": password},
            ) as response:
                if response.status == 401:
                    raise InvalidAuth("Invalid username or password")

                response.raise_for_status()

                # Session cookie automatically stored by aiohttp
                self._authenticated = True

                _LOGGER.info("Successfully authenticated")
                return True

        except aiohttp.ClientError as err:
            raise CannotConnect(f"Connection failed: {err}") from err

    async def fetch_data(self) -> dict[str, Any]:
        """Fetch data using session."""
        if not self._authenticated:
            raise RuntimeError("Not authenticated - call authenticate() first")

        async with self._session.get(
            f"http://{self._host}/api/data",
        ) as response:
            if response.status == 401:
                # Session expired, raise auth error
                self._authenticated = False
                raise ConfigEntryAuthFailed("Session expired")

            response.raise_for_status()
            return await response.json()

    async def logout(self) -> None:
        """Logout and clear session."""
        if not self._authenticated:
            return

        try:
            async with self._session.post(
                f"http://{self._host}/api/logout"
            ) as response:
                response.raise_for_status()
        finally:
            self._authenticated = False
```

**Why this works:**
- aiohttp automatically manages session cookies
- Explicit authentication state tracking
- Handles session expiration gracefully
- Cleanup on logout

---

## Polling Strategies

### Pattern 4: Fixed Interval with Conditional Updates

**When to use:** Devices where polling frequency should be constant but updates only happen when data changes.

**Implementation:**

```python
"""Coordinator with conditional updates."""
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator


class ConditionalCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that only updates entities when data changes."""

    def __init__(self, hass: HomeAssistant, client: APIClient):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
            always_update=False,  # Only notify entities if data changed
        )
        self.client = client
        self._last_data_hash: int | None = None

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data and check if it changed."""
        try:
            data = await self.client.fetch_data()

            # Calculate hash of data
            data_str = str(sorted(data.items()))
            current_hash = hash(data_str)

            # Compare with previous hash
            if current_hash == self._last_data_hash:
                _LOGGER.debug("Data unchanged, skipping entity updates")
                # Raise UpdateFailed to prevent entity updates
                # but coordinator remains successful
                raise UpdateFailed("Data unchanged")

            self._last_data_hash = current_hash
            _LOGGER.debug("Data changed, updating entities")
            return data

        except APIConnectionError as err:
            raise UpdateFailed(f"Connection error: {err}") from err
```

**Why this works:**
- `always_update=False` prevents unnecessary entity updates
- Hash comparison is fast and memory-efficient
- Still polls at fixed interval (device availability)
- UpdateFailed doesn't mark coordinator as failed
- Entities keep last known state when data unchanged

---

### Pattern 5: Exponential Backoff on Errors

**When to use:** Devices that may be temporarily unavailable and shouldn't be hammered with requests.

**Implementation:**

```python
"""Coordinator with exponential backoff."""


class BackoffCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator with exponential backoff on errors."""

    def __init__(self, hass: HomeAssistant, client: APIClient):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        self.client = client
        self._error_count = 0
        self._base_interval = timedelta(seconds=30)
        self._max_interval = timedelta(minutes=10)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data with backoff on errors."""
        try:
            data = await self.client.fetch_data()

            # Reset on success
            if self._error_count > 0:
                _LOGGER.info("Connection restored, resetting backoff")
                self._error_count = 0
                self.update_interval = self._base_interval

            return data

        except APIConnectionError as err:
            # Increment error count and apply backoff
            self._error_count += 1

            # Calculate new interval: base * 2^error_count
            backoff_multiplier = 2 ** min(self._error_count, 5)  # Cap at 2^5 = 32x
            new_interval = self._base_interval * backoff_multiplier

            # Clamp to max interval
            new_interval = min(new_interval, self._max_interval)

            if new_interval != self.update_interval:
                self.update_interval = new_interval
                _LOGGER.warning(
                    "Connection error #%d, backing off to %s interval",
                    self._error_count,
                    new_interval,
                )

            raise UpdateFailed(f"Connection error: {err}") from err
```

**Why this works:**
- Reduces load on failing devices
- Exponential backoff prevents request storms
- Resets immediately on success
- Capped at reasonable maximum (10 minutes)
- Logarithmic scaling (2^5 cap) prevents extreme intervals

---

## State Restoration

### Pattern 6: RestoreEntity for Sensors

**When to use:** Sensor values should persist across HA restarts.

**Implementation:**

```python
"""Sensor with state restoration."""
from homeassistant.helpers.restore_state import RestoreEntity


class RestorableSensor(CoordinatorEntity, RestoreEntity, SensorEntity):
    """Sensor that restores last state on restart."""

    def __init__(self, coordinator: MyCoordinator, device_id: str):
        """Initialize sensor."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_native_value: float | None = None

    async def async_added_to_hass(self) -> None:
        """Restore last state when added to hass."""
        await super().async_added_to_hass()

        # Restore previous state
        last_state = await self.async_get_last_state()

        if last_state is not None and last_state.state not in (
            STATE_UNKNOWN,
            STATE_UNAVAILABLE,
        ):
            try:
                self._attr_native_value = float(last_state.state)
                _LOGGER.debug(
                    "Restored %s state: %s",
                    self.entity_id,
                    self._attr_native_value,
                )
            except (ValueError, TypeError):
                _LOGGER.warning("Could not restore state: %s", last_state.state)

        # Coordinator will update with fresh data soon

    @property
    def native_value(self) -> float | None:
        """Return sensor value."""
        # Update from coordinator if available
        if self.coordinator.last_update_success:
            data = self.coordinator.data.get(self._device_id, {})
            if "value" in data:
                self._attr_native_value = data["value"]

        return self._attr_native_value
```

**Why this works:**
- Shows last known value immediately after restart
- Prevents "unavailable" flash during first update
- Validates restored state before using it
- Updates with fresh data when coordinator succeeds
- Gracefully handles invalid restored states

---

## Error Recovery

### Pattern 7: Log-Once Pattern for Repeated Errors

**When to use:** Prevent log spam from persistent connection issues.

**Implementation:**

```python
"""Coordinator with log-once error handling."""


class LogOnceCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that logs errors only once."""

    def __init__(self, hass: HomeAssistant, client: APIClient):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        self.client = client
        self._last_error_type: type[Exception] | None = None
        self._error_count = 0

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data with log-once error handling."""
        try:
            data = await self.client.fetch_data()

            # Log recovery if we had errors
            if self._last_error_type is not None:
                _LOGGER.info(
                    "Connection restored after %d failed attempts",
                    self._error_count,
                )
                self._last_error_type = None
                self._error_count = 0

            return data

        except Exception as err:
            error_type = type(err)
            self._error_count += 1

            # Log first occurrence
            if self._last_error_type != error_type:
                _LOGGER.error(
                    "Error fetching data (will only log once): %s",
                    err,
                    exc_info=True,
                )
                self._last_error_type = error_type
            else:
                # Subsequent occurrences use debug
                _LOGGER.debug(
                    "Error persists (attempt %d): %s",
                    self._error_count,
                    err,
                )

            # Log every 10th attempt at warning level
            if self._error_count % 10 == 0:
                _LOGGER.warning(
                    "Error still occurring after %d attempts: %s",
                    self._error_count,
                    err,
                )

            # Re-raise appropriate exception
            if isinstance(err, AuthenticationError):
                raise ConfigEntryAuthFailed from err
            raise UpdateFailed(f"Error: {err}") from err
```

**Why this works:**
- Logs first error at ERROR level with full traceback
- Subsequent same-type errors at DEBUG level
- Periodic reminders (every 10th) at WARNING level
- Logs recovery when connection restored
- Prevents log flooding while maintaining visibility

---

## Entity Organization

### Pattern 8: Device Registry Integration

**When to use:** Always! Groups entities by device in UI.

**Implementation:**

```python
"""Entity with proper device info."""
from homeassistant.helpers.device_registry import DeviceInfo


class MyEntity(CoordinatorEntity):
    """Entity with device registry integration."""

    _attr_has_entity_name = True  # Use device name as prefix

    def __init__(self, coordinator: MyCoordinator, device_id: str):
        """Initialize entity."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_unique_id = f"{DOMAIN}_{device_id}_{self._entity_type}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for grouping entities."""
        device_data = self.coordinator.data.get(self._device_id, {})

        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=device_data.get("name", f"Device {self._device_id}"),
            manufacturer=device_data.get("manufacturer", "Unknown"),
            model=device_data.get("model"),
            sw_version=device_data.get("firmware_version"),
            hw_version=device_data.get("hardware_version"),
            configuration_url=f"http://{device_data.get('host', '')}",
            suggested_area=device_data.get("location"),
        )

    @property
    def name(self) -> str:
        """Return entity name (appended to device name)."""
        # With _attr_has_entity_name = True:
        # Final name will be: "{device_name} {entity_name}"
        # Example: "Living Room Sensor Temperature"
        return "Temperature"
```

**Why this works:**
- Groups all entities under one device card in UI
- `_attr_has_entity_name = True` enables modern naming
- Provides rich device metadata (manufacturer, model, etc.)
- Configuration URL links to device's web interface
- Suggested area helps automatic organization

---

## Device Discovery

### Pattern 9: Network Discovery with Validation

**When to use:** Integrations that can discover devices on the network.

**Implementation:**

```python
"""Discovery flow for network devices."""
import socket


async def async_step_discovery(
    self, discovery_info: DiscoveryInfoType
) -> FlowResult:
    """Handle discovery."""
    host = discovery_info["host"]
    device_id = discovery_info["device_id"]

    # Set unique ID to prevent duplicates
    await self.async_set_unique_id(device_id)
    self._abort_if_unique_id_configured()

    # Validate device is still reachable
    try:
        device_info = await self._async_validate_discovery(host)
    except CannotConnect:
        return self.async_abort(reason="cannot_connect")

    # Show confirmation form to user
    return self.async_show_form(
        step_id="discovery_confirm",
        description_placeholders={
            "name": device_info["name"],
            "model": device_info["model"],
            "host": host,
        },
    )


async def async_step_discovery_confirm(
    self, user_input: dict[str, Any] | None = None
) -> FlowResult:
    """Confirm discovery."""
    if user_input is None:
        return self.async_show_form(step_id="discovery_confirm")

    # Create entry with discovered info
    return self.async_create_entry(
        title=self._discovered_device["name"],
        data={
            CONF_HOST: self._discovered_device["host"],
            "device_id": self._discovered_device["device_id"],
        },
    )


# Discovery helper
async def _async_validate_discovery(self, host: str) -> dict[str, Any]:
    """Validate discovered device."""
    try:
        # Check if host is reachable
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://{host}/api/info",
                timeout=aiohttp.ClientTimeout(total=5),
            ) as response:
                response.raise_for_status()
                return await response.json()
    except (aiohttp.ClientError, asyncio.TimeoutError) as err:
        raise CannotConnect(f"Cannot reach device at {host}") from err
```

**Why this works:**
- Validates device before showing to user
- Prevents duplicate entries with unique_id
- Shows device info in confirmation dialog
- Short timeout (5s) for discovery validation
- Handles unreachable devices gracefully

---

## Reauth Flow

### Pattern 10: Reauth for Expired Credentials

**When to use:** Credentials expire and need to be refreshed by user.

**Implementation:**

```python
"""Reauth flow for expired credentials."""


async def async_step_reauth(
    self, entry_data: Mapping[str, Any]
) -> FlowResult:
    """Handle reauth when credentials expire."""
    # Store entry for later update
    self._reauth_entry = self.hass.config_entries.async_get_entry(
        self.context["entry_id"]
    )

    return await self.async_step_reauth_confirm()


async def async_step_reauth_confirm(
    self, user_input: dict[str, Any] | None = None
) -> FlowResult:
    """Confirm reauth and get new credentials."""
    errors = {}

    if user_input is not None:
        try:
            # Validate new credentials
            await self._async_validate_credentials(
                self._reauth_entry.data[CONF_HOST],
                user_input[CONF_API_KEY],
            )
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except CannotConnect:
            errors["base"] = "cannot_connect"
        else:
            # Update config entry with new credentials
            self.hass.config_entries.async_update_entry(
                self._reauth_entry,
                data={
                    **self._reauth_entry.data,
                    CONF_API_KEY: user_input[CONF_API_KEY],
                },
            )

            # Reload the config entry
            await self.hass.config_entries.async_reload(
                self._reauth_entry.entry_id
            )

            return self.async_abort(reason="reauth_successful")

    return self.async_show_form(
        step_id="reauth_confirm",
        data_schema=vol.Schema({
            vol.Required(CONF_API_KEY): str,
        }),
        errors=errors,
        description_placeholders={
            "host": self._reauth_entry.data[CONF_HOST],
        },
    )
```

**Why this works:**
- Automatically triggered by ConfigEntryAuthFailed
- Preserves existing configuration (only updates credentials)
- Reloads integration after successful reauth
- Shows device info to user for context
- No data loss if reauth fails

---

## Options Flow

### Pattern 11: User-Configurable Options

**When to use:** Settings that users should be able to change without reconfiguring.

**Implementation:**

```python
"""Options flow for runtime configuration."""
from homeassistant.config_entries import OptionsFlow


class MyOptionsFlow(OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry: ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Update options
            return self.async_create_entry(title="", data=user_input)

        # Get current options (with defaults)
        current_interval = self.config_entry.options.get(
            "scan_interval",
            DEFAULT_SCAN_INTERVAL,
        )
        current_timeout = self.config_entry.options.get(
            "timeout",
            DEFAULT_TIMEOUT,
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    "scan_interval",
                    default=current_interval,
                ): vol.All(int, vol.Range(min=10, max=300)),
                vol.Required(
                    "timeout",
                    default=current_timeout,
                ): vol.All(int, vol.Range(min=5, max=60)),
                vol.Optional(
                    "enable_debug",
                    default=self.config_entry.options.get("enable_debug", False),
                ): bool,
            }),
        )


# In config_flow.py
@staticmethod
@callback
def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
    """Get the options flow."""
    return MyOptionsFlow(config_entry)


# In coordinator.py - respond to option changes
async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Update coordinator with new interval
    new_interval = entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)
    coordinator.update_interval = timedelta(seconds=new_interval)

    _LOGGER.info("Updated scan interval to %d seconds", new_interval)

    # Request immediate refresh with new settings
    await coordinator.async_request_refresh()


# In __init__.py - register update listener
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from config entry."""
    # ... setup code ...

    # Register options update listener
    entry.async_on_unload(entry.add_update_listener(async_update_listener))

    return True
```

**Why this works:**
- Users can change settings without reconfiguration
- Defaults shown if options not set
- Validation prevents invalid values
- Update listener applies changes immediately
- No integration reload needed

---

## Usage Tips

### Finding the Right Pattern

1. **Authentication** - Start with Pattern 1 (API Key), upgrade to Pattern 2 (OAuth2) only if needed
2. **Polling** - Use Pattern 4 (Conditional) for most cases, add Pattern 5 (Backoff) if devices are unreliable
3. **State** - Add Pattern 6 (Restore) for any sensor that should persist across restarts
4. **Errors** - Always implement Pattern 7 (Log-Once) to prevent log spam
5. **Devices** - Always implement Pattern 8 (Device Registry) for proper UI organization
6. **Discovery** - Add Pattern 9 if your integration can discover devices
7. **Reauth** - Implement Pattern 10 if credentials can expire
8. **Options** - Add Pattern 11 for any user-configurable behavior

### Combining Patterns

Patterns are designed to work together:

```python
# Coordinator combining multiple patterns
class MyCoordinator(
    DataUpdateCoordinator[dict[str, Any]]  # Base
):
    """Coordinator with multiple patterns."""

    def __init__(self, hass, client):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
            always_update=False,  # Pattern 4: Conditional updates
        )
        self.client = client  # Pattern 2: OAuth2 client
        self._error_count = 0  # Pattern 5: Backoff
        self._last_error_type = None  # Pattern 7: Log-once

    async def _async_update_data(self):
        """Update with multiple patterns."""
        try:
            data = await self.client.fetch_data()  # Auto-token-refresh

            # Pattern 5: Reset backoff on success
            if self._error_count > 0:
                self._error_count = 0
                self.update_interval = timedelta(seconds=30)

            # Pattern 7: Log recovery
            if self._last_error_type is not None:
                _LOGGER.info("Connection restored")
                self._last_error_type = None

            return data

        except Exception as err:
            # Pattern 7: Log-once
            if type(err) != self._last_error_type:
                _LOGGER.error("Error: %s", err)
                self._last_error_type = type(err)

            # Pattern 5: Backoff
            self._error_count += 1
            new_interval = timedelta(seconds=30 * (2 ** self._error_count))
            self.update_interval = min(new_interval, timedelta(minutes=10))

            raise UpdateFailed from err
```

---

**Remember:** These patterns are proven solutions to common problems. Use them as starting points and adapt to your specific integration needs. The "why" explanations help you understand when and how to modify them.
