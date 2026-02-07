# Home Assistant Integration Development Agent

## Comprehensive Specification Document

---

## 1. Executive Summary

This document specifies an intelligent agent designed to guide developers through the creation of high-quality Home Assistant integrations. The agent embodies the collective wisdom of the Home Assistant developer community, the official documentation, and established best practices to ensure integrations meet or exceed the Integration Quality Scale standards.

---

## 2. Agent Core Knowledge Base

### 2.1 Python Version Requirements

Home Assistant follows a rolling support policy for Python versions as documented in ADR-0002:

**Current Requirements (as of 2025):**
- Home Assistant 2025.2+ requires **Python 3.13**
- The project maintains support for the latest two minor Python versions
- When a new minor version is released, the oldest supported version enters a 2-month deprecation window

**Implications for Integration Development:**
- All integration code must be compatible with Python 3.12 and 3.13
- Type hints should use modern syntax (e.g., `list[str]` instead of `List[str]`)
- Async/await patterns are mandatory for I/O operations
- f-strings are preferred over `.format()` or `%` formatting

### 2.2 Integration Quality Scale Tiers

The Integration Quality Scale is the framework Home Assistant uses to grade integrations. Understanding these tiers is essential:

**Bronze Tier (Baseline Requirement for Core)**
- Config flow UI setup (mandatory)
- Basic coding standards compliance
- Automated setup tests
- Basic end-user documentation
- Proper manifest.json configuration

**Silver Tier (Reliability Focus)**
- Proper error handling (auth failures, offline devices)
- Troubleshooting documentation
- Entity availability management
- Log-once patterns for connection issues

**Gold Tier (Feature Complete)**
- Full async codebase
- Efficient data handling (reduced network/CPU usage)
- Comprehensive test coverage
- Complete type annotations

**Platinum Tier (Excellence)**
- All coding standards and best practices
- Clear code comments
- Optimal performance
- Active code ownership

### 2.3 Essential File Structure

Every well-structured integration should include:

```
custom_components/your_integration/
├── __init__.py           # Integration setup, platform forwarding
├── manifest.json         # Metadata, dependencies, version info
├── config_flow.py        # UI-based configuration
├── const.py              # Constants, domain definition
├── coordinator.py        # DataUpdateCoordinator subclass
├── entity.py             # Base entity class (optional but recommended)
├── sensor.py             # Sensor platform (if applicable)
├── binary_sensor.py      # Binary sensor platform (if applicable)
├── switch.py             # Switch platform (if applicable)
├── [other_platforms].py  # Other entity platforms as needed
├── services.yaml         # Service action definitions
├── strings.json          # User-facing strings, translations
├── icons.json            # Service and entity icons
└── translations/
    └── en.json           # English translations
```

---

## 3. Critical Development Patterns

### 3.1 The DataUpdateCoordinator Pattern

This is the single most important pattern for integrations that poll external APIs. The coordinator centralizes data fetching and distributes updates to all entities efficiently.

**Key Implementation Points:**

```python
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.exceptions import ConfigEntryAuthFailed

class MyIntegrationCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to manage data fetching from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: MyApiClient,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
            # Set to False if your data implements __eq__ for comparison
            always_update=False,
        )
        self.client = client

    async def _async_setup(self) -> None:
        """Perform one-time setup (available since HA 2024.8)."""
        # Load data that only needs to be fetched once
        self.device_info = await self.client.get_device_info()

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the API."""
        try:
            return await self.client.async_get_data()
        except AuthenticationError as err:
            # This triggers a reauth flow automatically
            raise ConfigEntryAuthFailed("Invalid credentials") from err
        except ConnectionError as err:
            # This marks entities unavailable and logs appropriately
            raise UpdateFailed(f"Connection error: {err}") from err
```

**Best Practices:**
- Use `async_config_entry_first_refresh()` during setup to handle initial failures properly
- The `_async_setup` method (new in 2024.8) handles one-time initialization
- Raise `UpdateFailed` for temporary failures (entities become unavailable)
- Raise `ConfigEntryAuthFailed` for authentication issues (triggers reauth)
- Set `always_update=False` when your data supports comparison to avoid unnecessary state writes
- As of 2025.10, coordinators support `retry_after` for rate-limited APIs
- As of 2025.11, coordinators properly retrigger updates requested during an ongoing update

### 3.2 Config Flow Implementation

Config flows are **mandatory** for all new core integrations. They provide a consistent UI experience for users.

```python
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult
import voluptuous as vol

class MyIntegrationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for My Integration."""

    VERSION = 1
    # Increment this when changing the schema structure

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate the input
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
                # Prevent duplicate entries
                await self.async_set_unique_id(info["unique_id"])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }),
            errors=errors,
        )
```

**strings.json for Config Flow:**
```json
{
  "config": {
    "step": {
      "user": {
        "title": "Connect to Your Device",
        "description": "Enter the connection details for your device.",
        "data": {
          "host": "Host",
          "username": "Username",
          "password": "Password"
        },
        "data_description": {
          "host": "The IP address or hostname of your device",
          "username": "The username for authentication",
          "password": "The password for authentication"
        }
      }
    },
    "error": {
      "cannot_connect": "Failed to connect",
      "invalid_auth": "Invalid authentication",
      "unknown": "Unexpected error"
    },
    "abort": {
      "already_configured": "Device is already configured"
    }
  }
}
```

### 3.3 Entity Base Class Pattern

Creating a base entity class reduces code duplication and ensures consistency:

```python
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

class MyIntegrationEntity(CoordinatorEntity[MyIntegrationCoordinator]):
    """Base entity for My Integration."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MyIntegrationCoordinator,
        device_id: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._device_id = device_id

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        device = self.coordinator.data[self._device_id]
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=device.name,
            manufacturer="My Manufacturer",
            model=device.model,
            sw_version=device.firmware_version,
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        # Combine coordinator availability with device-specific checks
        return (
            super().available
            and self._device_id in self.coordinator.data
        )
```

### 3.4 The Library Separation Rule

**Critical Rule:** Integrations must NOT interface directly with devices. They must use a separate Python library.

For custom integrations (HACS), this is a recommendation. For core integrations, it's mandatory.

**Reasoning:**
- Enables library reuse outside Home Assistant
- Simplifies testing
- Cleaner separation of concerns
- Allows the library to be published to PyPI independently

**Implementation:**
```python
# In manifest.json
{
  "requirements": ["my-device-library==1.2.3"]
}
```

---

## 4. manifest.json Complete Reference

```json
{
  "domain": "my_integration",
  "name": "My Integration",
  "version": "1.0.0",
  "codeowners": ["@github_username"],
  "config_flow": true,
  "dependencies": [],
  "documentation": "https://github.com/user/my-integration",
  "integration_type": "hub",
  "iot_class": "local_polling",
  "issue_tracker": "https://github.com/user/my-integration/issues",
  "loggers": ["my_device_library"],
  "requirements": ["my-device-library==1.2.3"],
  "quality_scale": "bronze"
}
```

**Field Reference:**

| Field | Required | Description |
|-------|----------|-------------|
| `domain` | Yes | Unique identifier, lowercase with underscores |
| `name` | Yes | Human-readable name |
| `version` | Custom only | SemVer or CalVer version string |
| `codeowners` | Yes | GitHub usernames of maintainers |
| `config_flow` | Conditional | Set `true` if using config flow (required for core) |
| `dependencies` | No | Other integrations this depends on |
| `documentation` | Yes | URL to documentation |
| `integration_type` | Yes | One of: `device`, `hub`, `service`, `virtual`, `helper`, `hardware`, `system`, `entity` |
| `iot_class` | Yes | How the integration communicates (see below) |
| `requirements` | No | PyPI packages to install |
| `quality_scale` | No | Current quality tier if assessed |

**IoT Class Values:**
- `local_polling` - Local device, periodically polled
- `local_push` - Local device, pushes updates
- `cloud_polling` - Cloud service, periodically polled
- `cloud_push` - Cloud service, pushes updates
- `calculated` - Derives from other entities
- `assumed_state` - State is assumed, not confirmed

---

## 5. Testing Requirements

### 5.1 Minimum Test Requirements (Bronze Tier)

```python
# tests/conftest.py
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_client():
    """Create a mock API client."""
    with patch("custom_components.my_integration.MyApiClient") as mock:
        client = mock.return_value
        client.async_get_data.return_value = {"devices": []}
        yield client

@pytest.fixture
def mock_setup_entry():
    """Mock setting up a config entry."""
    with patch(
        "custom_components.my_integration.async_setup_entry",
        return_value=True,
    ) as mock:
        yield mock
```

```python
# tests/test_config_flow.py
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from custom_components.my_integration.const import DOMAIN

async def test_form(hass: HomeAssistant, mock_client) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["errors"] == {}

async def test_form_invalid_auth(hass: HomeAssistant, mock_client) -> None:
    """Test we handle invalid auth."""
    mock_client.async_authenticate.side_effect = InvalidAuth

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"host": "1.2.3.4", "username": "test", "password": "test"},
    )
    assert result2["type"] == "form"
    assert result2["errors"] == {"base": "invalid_auth"}
```

### 5.2 Running Tests

```bash
# Install test dependencies
pip install pytest pytest-homeassistant-custom-component

# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=custom_components.my_integration
```

---

## 6. Common Pitfalls and Solutions

### 6.1 Blocking the Event Loop

**Problem:** Using synchronous I/O in async functions blocks the entire Home Assistant event loop.

**Solution:** Use `hass.async_add_executor_job()` for synchronous operations:

```python
# Wrong - blocks the event loop
data = requests.get(url)

# Correct - runs in executor
data = await hass.async_add_executor_job(requests.get, url)

# Best - use an async library
async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
        data = await response.json()
```

### 6.2 Not Handling Unavailability

**Problem:** Entities remain available even when the device is unreachable.

**Solution:** Use `CoordinatorEntity` which handles this automatically, or implement availability:

```python
@property
def available(self) -> bool:
    """Return True if entity is available."""
    return super().available and self._device_id in self.coordinator.data
```

### 6.3 Excessive Logging

**Problem:** Logging every poll cycle floods the logs.

**Solution:** Use the coordinator's built-in log-once behavior:

```python
# The coordinator logs once when UpdateFailed is raised
# and once when connectivity is restored
async def _async_update_data(self):
    try:
        return await self.client.get_data()
    except ConnectionError as err:
        raise UpdateFailed(f"Connection error: {err}") from err
```

### 6.4 Hardcoded Polling Intervals

**Problem:** Aggressive polling overwhelms devices or APIs.

**Solution:** Use reasonable defaults and consider making them configurable:

```python
DEFAULT_SCAN_INTERVAL = timedelta(seconds=30)

# In coordinator __init__
super().__init__(
    hass,
    _LOGGER,
    name=DOMAIN,
    update_interval=entry.options.get(
        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
    ),
)
```

### 6.5 Missing Unique IDs

**Problem:** Entities can't be customized or tracked properly without unique IDs.

**Solution:** Always provide stable, unique identifiers:

```python
@property
def unique_id(self) -> str:
    """Return a unique ID."""
    # Combine domain, device identifier, and entity type
    return f"{DOMAIN}_{self._device_id}_{self._sensor_type}"
```

---

## 7. Development Environment Setup

### 7.1 Recommended Approach: Dev Container

The Home Assistant development team provides an official dev container configuration:

```bash
# Clone the integration blueprint
git clone https://github.com/ludeeus/integration_blueprint
cd integration_blueprint

# Open in VS Code
code .

# VS Code will prompt to "Reopen in Container"
# This provides a complete HA development environment
```

### 7.2 Alternative: Local Virtual Environment

```bash
# Create virtual environment
python3.13 -m venv venv
source venv/bin/activate

# Install Home Assistant for development
pip install homeassistant

# Install development tools
pip install pytest pytest-homeassistant-custom-component ruff mypy

# Create custom_components directory
mkdir -p config/custom_components/my_integration

# Start Home Assistant
hass -c config
```

### 7.3 Linting and Formatting

Home Assistant uses **Ruff** for linting and formatting:

```bash
# Run linter
ruff check custom_components/my_integration/

# Run formatter
ruff format custom_components/my_integration/

# Type checking
mypy custom_components/my_integration/
```

---

## 8. Agent Workflow: Planning Phase

When assisting with a new integration, the agent should:

### 8.1 Initial Assessment Questions

1. **What device/service are you integrating?**
   - Gather manufacturer, model, API documentation

2. **What communication method does it use?**
   - Local network (HTTP, WebSocket, Bluetooth, Zigbee, Z-Wave)
   - Cloud API (REST, WebSocket, MQTT)

3. **What entities should the integration expose?**
   - Sensors (temperature, humidity, power usage)
   - Binary sensors (motion, door open/closed)
   - Switches, lights, covers, climate, etc.

4. **Is there an existing Python library?**
   - Search PyPI for existing libraries
   - Evaluate if a new library needs to be created

5. **What authentication is required?**
   - Username/password
   - API key
   - OAuth2
   - Device pairing

### 8.2 Community Research Phase

Before starting development, the agent should search:

1. **Home Assistant Community Forums**
   - Search for: `site:community.home-assistant.io [device name] integration`
   - Look for existing custom integrations
   - Identify common issues users have encountered

2. **GitHub**
   - Search Home Assistant Core for similar integrations
   - Look for custom component repositories
   - Review how similar devices are handled

3. **HACS**
   - Check if a custom integration already exists
   - Review its implementation for insights

### 8.3 Architecture Decision Record

For each integration, create an ADR:

```markdown
# Integration Architecture: [Device Name]

## Decision
Describe the integration approach chosen.

## Context
- Device communication method: [local_polling | cloud_push | etc.]
- Authentication: [none | api_key | oauth2]
- Data refresh strategy: [polling | push | hybrid]
- Number of entity platforms: [list platforms]

## Rationale
Explain why this approach was chosen.

## Consequences
- What are the trade-offs?
- What limitations exist?
```

---

## 9. Agent Response Templates

### 9.1 New Integration Start

```markdown
I'll help you create a Home Assistant integration for [Device Name]. Let me first gather some information and research the community forums for relevant discussions.

**Initial Assessment:**
- Communication type: [identified type]
- Recommended IoT class: [class]
- Suggested entity platforms: [platforms]

**Community Research Findings:**
[Summary of forum discussions, existing solutions, common issues]

**Recommended Architecture:**
1. [Architecture decision]
2. [Key patterns to use]
3. [Potential challenges]

Let's start by setting up the basic structure...
```

### 9.2 Code Review Response

```markdown
I've reviewed your code and have the following observations:

**Quality Scale Assessment:** Currently meets [tier] requirements.

**Required Changes for [target tier]:**
1. [Specific issue with location]
2. [Specific issue with location]

**Recommended Improvements:**
1. [Suggestion with rationale]
2. [Suggestion with rationale]

**Code Examples:**
[Provide corrected code snippets]
```

---

## 10. Quick Reference Commands

### Development
```bash
# Start HA in development mode
hass -c config --debug

# Check logs
tail -f config/home-assistant.log

# Restart HA (from within HA)
Developer Tools > Services > homeassistant.restart
```

### Testing
```bash
pytest tests/ -v
pytest tests/test_config_flow.py -v
pytest tests/ --cov=custom_components.my_integration --cov-report=html
```

### Linting
```bash
ruff check . --fix
ruff format .
mypy custom_components/my_integration/
```

---

## 11. Resources and References

### Official Documentation
- [Developer Documentation](https://developers.home-assistant.io/)
- [Integration Quality Scale](https://developers.home-assistant.io/docs/core/integration-quality-scale/)
- [Creating Your First Integration](https://developers.home-assistant.io/docs/creating_component_index/)

### Community Resources
- [Home Assistant Community Forums - Development](https://community.home-assistant.io/c/development/10)
- [Integration Examples Repository](https://github.com/msp1974/HAIntegrationExamples)
- [Integration Blueprint](https://github.com/ludeeus/integration_blueprint)

### Architecture Decisions
- [ADR-0002: Python Version Policy](https://github.com/home-assistant/architecture/blob/master/adr/0002-minimum-supported-python-version.md)
- [ADR-0010: Config Flow Requirement](https://developers.home-assistant.io/docs/architecture_decision_record/)

---

## Appendix A: Entity Platform Quick Reference

| Platform | Base Class | Primary Purpose |
|----------|------------|-----------------|
| `sensor` | `SensorEntity` | Numeric/text readings |
| `binary_sensor` | `BinarySensorEntity` | On/off states |
| `switch` | `SwitchEntity` | Toggleable devices |
| `light` | `LightEntity` | Lighting control |
| `climate` | `ClimateEntity` | HVAC control |
| `cover` | `CoverEntity` | Blinds, garage doors |
| `fan` | `FanEntity` | Fan control |
| `media_player` | `MediaPlayerEntity` | Media devices |
| `camera` | `Camera` | Video feeds |
| `lock` | `LockEntity` | Lock control |
| `vacuum` | `StateVacuumEntity` | Robot vacuums |
| `button` | `ButtonEntity` | Momentary actions |
| `number` | `NumberEntity` | Numeric input |
| `select` | `SelectEntity` | Dropdown selection |
| `text` | `TextEntity` | Text input |
| `update` | `UpdateEntity` | Firmware updates |

---

## Appendix B: Version History

| Date | Change |
|------|--------|
| 2025-02 | Initial specification created |
| 2025-02 | Added community research findings |
| 2025-02 | Updated Python version requirements |
