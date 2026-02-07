# Security Best Practices for Home Assistant Integrations

Security is critical for Home Assistant integrations. This guide provides patterns and practices to protect user credentials, prevent vulnerabilities, and handle sensitive data properly.

## Table of Contents

- [Credential Storage](#credential-storage)
- [API Key & Token Handling](#api-key--token-handling)
- [Network Security](#network-security)
- [Input Validation](#input-validation)
- [Logging Security](#logging-security)
- [Authentication Patterns](#authentication-patterns)
- [Common Vulnerabilities](#common-vulnerabilities)
- [Security Checklist](#security-checklist)

---

## Credential Storage

### ✅ DO: Use ConfigEntry.data for Credentials

Store all credentials in the config entry, which is encrypted at rest:

```python
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_USERNAME, CONF_PASSWORD

async def async_step_user(self, user_input=None):
    """Handle user step."""
    if user_input is not None:
        # Credentials stored securely in config entry
        return self.async_create_entry(
            title=user_input[CONF_USERNAME],
            data={
                CONF_USERNAME: user_input[CONF_USERNAME],
                CONF_PASSWORD: user_input[CONF_PASSWORD],
                CONF_API_KEY: user_input[CONF_API_KEY],
            },
        )
```

### ✅ DO: Use Password Input Type in Config Flow

Mark sensitive fields as secrets in your schema:

```python
import voluptuous as vol
from homeassistant.const import CONF_API_KEY, CONF_PASSWORD

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_API_KEY): str,      # Will be masked in UI
    vol.Required(CONF_PASSWORD): str,     # Will be masked in UI
})

# In config_flow.py
return self.async_show_form(
    step_id="user",
    data_schema=DATA_SCHEMA,
)
```

**Home Assistant automatically masks** fields named with these constants:
- `CONF_PASSWORD`
- `CONF_API_KEY`
- `CONF_TOKEN`
- `CONF_ACCESS_TOKEN`

### ❌ DON'T: Store Credentials in Options

Options are for non-sensitive configuration:

```python
# ❌ WRONG - Credentials in options
entry.options = {
    "api_key": "secret123",  # DON'T DO THIS
    "update_interval": 30,
}

# ✅ CORRECT - Credentials in data, settings in options
entry.data = {
    "api_key": "secret123",  # Encrypted
}
entry.options = {
    "update_interval": 30,   # User-configurable setting
}
```

### ❌ DON'T: Store Credentials in Attributes

Never expose credentials as entity attributes:

```python
# ❌ WRONG - API key visible in entity attributes
@property
def extra_state_attributes(self):
    return {
        "api_key": self.api_key,  # DON'T DO THIS
        "last_update": self.last_update,
    }

# ✅ CORRECT - Only non-sensitive data
@property
def extra_state_attributes(self):
    return {
        "last_update": self.last_update,
        "firmware_version": self.firmware,
    }
```

---

## API Key & Token Handling

### Token Refresh Pattern

For OAuth2 and other token-based authentication:

```python
from datetime import datetime, timedelta
from homeassistant.exceptions import ConfigEntryAuthFailed

class APIClient:
    """API client with automatic token refresh."""

    async def _ensure_valid_token(self):
        """Refresh token if expired."""
        if self._token_expires_at <= datetime.utcnow():
            try:
                await self._refresh_token()
            except AuthenticationError as err:
                # Trigger reauth flow
                raise ConfigEntryAuthFailed from err

    async def _refresh_token(self):
        """Refresh access token."""
        response = await self._session.post(
            TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": self._refresh_token,
                "client_id": CLIENT_ID,
            },
        )
        data = await response.json()

        # Update stored tokens in config entry
        self.hass.config_entries.async_update_entry(
            self.config_entry,
            data={
                **self.config_entry.data,
                "access_token": data["access_token"],
                "refresh_token": data["refresh_token"],
                "expires_at": datetime.utcnow() + timedelta(
                    seconds=data["expires_in"]
                ),
            },
        )
```

### Proactive Token Rotation

Rotate tokens before they expire:

```python
# ✅ GOOD - Refresh 5 minutes before expiration
REFRESH_BUFFER = timedelta(minutes=5)

if self._token_expires_at <= datetime.utcnow() + REFRESH_BUFFER:
    await self._refresh_token()
```

### API Key Storage

Store API keys in config entry data:

```python
from homeassistant.const import CONF_API_KEY

# In __init__.py setup
api_key = entry.data[CONF_API_KEY]
client = APIClient(hass, api_key)
```

---

## Network Security

### ✅ DO: Always Use HTTPS

```python
import aiohttp

# ✅ CORRECT - HTTPS for external APIs
API_URL = "https://api.example.com"

async with aiohttp.ClientSession() as session:
    async with session.get(API_URL) as response:
        data = await response.json()
```

### ✅ DO: Validate SSL Certificates

```python
import aiohttp
import ssl

# ✅ CORRECT - Verify SSL certificates
ssl_context = ssl.create_default_context()

async with aiohttp.ClientSession(
    connector=aiohttp.TCPConnector(ssl=ssl_context)
) as session:
    async with session.get(url) as response:
        return await response.json()
```

### ⚠️ CAUTION: Disabling SSL Verification

Only disable SSL verification for local devices with self-signed certificates, and make it user-configurable:

```python
import ssl
from homeassistant.const import CONF_VERIFY_SSL

# Allow users to disable SSL verification for local devices
verify_ssl = entry.data.get(CONF_VERIFY_SSL, True)

if verify_ssl:
    ssl_context = ssl.create_default_context()
else:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    _LOGGER.warning(
        "SSL certificate verification is disabled. "
        "This is insecure and should only be used for local devices."
    )
```

### Handle SSL Errors Gracefully

```python
from aiohttp import ClientSSLError
from homeassistant.helpers.update_coordinator import UpdateFailed

try:
    data = await self.api.fetch_data()
except ClientSSLError as err:
    raise UpdateFailed(
        f"SSL certificate verification failed: {err}. "
        "Check your SSL configuration."
    ) from err
```

---

## Input Validation

### Validate All User Inputs

Always validate data from users and external APIs:

```python
import voluptuous as vol
from homeassistant.const import CONF_HOST

# Define validation schema
CONFIG_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): vol.All(str, vol.Length(min=1, max=253)),
    vol.Required("port"): vol.All(int, vol.Range(min=1, max=65535)),
    vol.Optional("timeout", default=30): vol.All(
        int, vol.Range(min=5, max=300)
    ),
})

# In config_flow.py
async def async_step_user(self, user_input=None):
    """Handle user step."""
    errors = {}

    if user_input is not None:
        try:
            # Validate input
            validated = CONFIG_SCHEMA(user_input)
        except vol.Invalid as err:
            errors["base"] = "invalid_input"
            _LOGGER.error("Invalid input: %s", err)
        else:
            # Proceed with validated data
            return self.async_create_entry(
                title=validated[CONF_HOST],
                data=validated,
            )
```

### Sanitize External Data

Never trust data from external APIs:

```python
from typing import Any

def sanitize_device_name(name: str) -> str:
    """Sanitize device name from API."""
    # Remove potentially dangerous characters
    sanitized = "".join(c for c in name if c.isalnum() or c in " -_")
    # Limit length
    return sanitized[:50]

async def _async_update_data(self) -> dict[str, Any]:
    """Fetch and sanitize data."""
    raw_data = await self.api.fetch_data()

    return {
        device_id: {
            "name": sanitize_device_name(device["name"]),
            "value": float(device["value"]),  # Ensure correct type
        }
        for device_id, device in raw_data.items()
    }
```

### Prevent Path Traversal

When handling file paths from user input:

```python
from pathlib import Path

def validate_filename(filename: str) -> bool:
    """Validate filename for path traversal."""
    # ✅ Prevent ../../../etc/passwd
    path = Path(filename)

    # Check for path traversal attempts
    if ".." in path.parts:
        raise ValueError("Path traversal detected")

    # Ensure relative path
    if path.is_absolute():
        raise ValueError("Absolute paths not allowed")

    return True
```

---

## Logging Security

### ❌ DON'T: Log Credentials or Tokens

Never log sensitive data:

```python
import logging

_LOGGER = logging.getLogger(__name__)

# ❌ WRONG - Logs credentials
_LOGGER.debug("Authenticating with credentials: %s", credentials)
_LOGGER.info("API key: %s", api_key)

# ✅ CORRECT - No sensitive data
_LOGGER.debug("Authenticating user: %s", username)
_LOGGER.info("API request to endpoint: %s", endpoint)
```

### Mask Sensitive Data in Logs

If you must log URLs or data structures with credentials:

```python
def mask_credentials(url: str) -> str:
    """Mask credentials in URL."""
    from urllib.parse import urlparse, urlunparse

    parsed = urlparse(url)

    if parsed.password:
        # Replace password with ***
        netloc = f"{parsed.username}:***@{parsed.hostname}"
        if parsed.port:
            netloc += f":{parsed.port}"

        masked = parsed._replace(netloc=netloc)
        return urlunparse(masked)

    return url

# Usage
_LOGGER.debug("API URL: %s", mask_credentials(api_url))
```

### Use Debug Logging Appropriately

```python
# ✅ CORRECT - Debug logs for troubleshooting
_LOGGER.debug("Fetching data from device %s", device_id)
_LOGGER.debug("Response status: %s", response.status)

# Detailed debug without credentials
_LOGGER.debug(
    "API response headers: %s",
    {k: v for k, v in response.headers.items() if k != "Authorization"},
)
```

---

## Authentication Patterns

### Pattern 1: API Key Authentication

```python
from homeassistant.const import CONF_API_KEY

class APIClient:
    """Client with API key authentication."""

    def __init__(self, api_key: str):
        """Initialize client."""
        self._api_key = api_key
        self._session = aiohttp.ClientSession(
            headers={"X-API-Key": api_key}  # Header-based auth
        )

    async def fetch_data(self):
        """Fetch data with API key."""
        async with self._session.get(API_URL) as response:
            response.raise_for_status()
            return await response.json()
```

### Pattern 2: OAuth2 Authentication

```python
from homeassistant.helpers import config_entry_oauth2_flow

class OAuth2FlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler,
    domain=DOMAIN,
):
    """Handle OAuth2 flow."""

    DOMAIN = DOMAIN

    @property
    def logger(self):
        """Return logger."""
        return _LOGGER

    @property
    def extra_authorize_data(self):
        """Extra data for authorization."""
        return {"scope": "read write"}
```

### Pattern 3: Session-Based Authentication

```python
class SessionClient:
    """Client with session-based authentication."""

    async def login(self, username: str, password: str):
        """Login and establish session."""
        async with self._session.post(
            f"{self._base_url}/login",
            json={"username": username, "password": password},
        ) as response:
            if response.status != 200:
                raise AuthenticationError("Invalid credentials")

            # Session cookie stored automatically by aiohttp
            self._authenticated = True

    async def fetch_data(self):
        """Fetch data (requires active session)."""
        if not self._authenticated:
            raise AuthenticationError("Not authenticated")

        async with self._session.get(f"{self._base_url}/data") as response:
            return await response.json()
```

---

## Common Vulnerabilities

### 1. SQL Injection (If Using Databases)

```python
# ❌ WRONG - Vulnerable to SQL injection
query = f"SELECT * FROM devices WHERE name = '{device_name}'"

# ✅ CORRECT - Use parameterized queries
query = "SELECT * FROM devices WHERE name = ?"
cursor.execute(query, (device_name,))
```

### 2. Command Injection (If Executing Commands)

```python
import shlex

# ❌ WRONG - Vulnerable to command injection
os.system(f"ping {hostname}")

# ✅ CORRECT - Use subprocess with list arguments
import subprocess
subprocess.run(["ping", "-c", "1", hostname], check=True)
```

### 3. XML External Entity (XXE) Attack

```python
import defusedxml.ElementTree as ET

# ✅ CORRECT - Use defusedxml instead of standard xml
tree = ET.parse(xml_file)
```

### 4. Insecure Deserialization

```python
import json

# ❌ WRONG - Using pickle with untrusted data
import pickle
data = pickle.loads(untrusted_data)  # DON'T DO THIS

# ✅ CORRECT - Use JSON for untrusted data
data = json.loads(untrusted_data)
```

### 5. Hardcoded Secrets

```python
# ❌ WRONG - Hardcoded credentials
API_KEY = "sk_live_abc123xyz"  # DON'T DO THIS

# ✅ CORRECT - Load from config entry
api_key = config_entry.data[CONF_API_KEY]
```

---

## Security Checklist

Use this checklist before releasing your integration:

### Credential Security
- [ ] Credentials stored in `ConfigEntry.data` (not options)
- [ ] Password fields use `CONF_PASSWORD`, `CONF_API_KEY`, or similar
- [ ] No credentials in entity attributes
- [ ] No credentials in debug logs
- [ ] Token refresh implemented (if applicable)

### Network Security
- [ ] HTTPS used for all external API calls
- [ ] SSL certificates validated (or user-configurable)
- [ ] SSL errors handled gracefully with clear messages
- [ ] Timeouts configured for all network requests

### Input Validation
- [ ] All user inputs validated with voluptuous schemas
- [ ] External API data sanitized before use
- [ ] Path traversal attacks prevented
- [ ] Type validation on all external data

### Logging Security
- [ ] No credentials logged at any log level
- [ ] Sensitive data masked in URLs/logs
- [ ] Debug logging doesn't expose secrets
- [ ] Error messages don't reveal system internals

### Authentication
- [ ] Authentication errors raise `ConfigEntryAuthFailed`
- [ ] Reauth flow implemented for expired credentials
- [ ] Session management secure (if applicable)
- [ ] No plaintext credential transmission

### General Security
- [ ] No hardcoded secrets in code
- [ ] Dependencies reviewed for known vulnerabilities
- [ ] No dangerous deserialization (pickle) of untrusted data
- [ ] Command injection prevented (if executing commands)
- [ ] XML parsing uses defusedxml (if parsing XML)

---

## Resources

- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **Home Assistant Security**: https://www.home-assistant.io/docs/configuration/securing/
- **Python Security Best Practices**: https://python.readthedocs.io/en/stable/library/security_warnings.html
- **aiohttp Security**: https://docs.aiohttp.org/en/stable/client_advanced.html#ssl-control-for-tcp-sockets

## Reporting Security Issues

If you discover a security vulnerability in your integration:

1. **Do not** open a public issue
2. **Email** the maintainer privately
3. **Provide** details: affected versions, exploit details, potential impact
4. **Wait** for fix before public disclosure
5. **Credit** researcher after fix (if they want credit)

---

**Remember:** Security is not optional. Protect your users' credentials and data with the same care you'd want for your own.
