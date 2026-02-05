---
name: ha-testing
description: Write tests for Home Assistant integrations using pytest and the hass fixture. Use when the user mentions "test", "pytest", "testing", "test coverage", "mock", "fixture", "conftest", or needs to write or fix tests for a Home Assistant integration. Also use when preparing an integration for core submission which requires tests.
---

# Testing Home Assistant Integrations

Automated tests are **required** for Bronze tier on the Integration Quality Scale. At minimum, you need config flow tests that verify setup succeeds and handles errors correctly.

## Test Directory Structure

```
tests/
├── conftest.py           # Shared fixtures and mocks
├── test_config_flow.py   # Config flow tests (REQUIRED)
├── test_init.py          # Setup/unload tests
├── test_sensor.py        # Sensor entity tests
├── test_switch.py        # Switch entity tests
└── test_coordinator.py   # Coordinator tests
```

## conftest.py — Shared Fixtures

```python
"""Fixtures for {Name} tests."""
from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME

from custom_components.{domain}.const import DOMAIN

MOCK_CONFIG = {
    CONF_HOST: "192.168.1.100",
    CONF_USERNAME: "admin",
    CONF_PASSWORD: "password",
}

MOCK_DEVICE_INFO = {
    "serial": "ABC123",
    "name": "Test Device",
    "model": "Model X",
    "firmware": "1.0.0",
}

MOCK_DATA = {
    "devices": {
        "device_1": {
            "name": "Living Room",
            "model": "Sensor Pro",
            "temperature": 22.5,
            "humidity": 45,
            "battery_level": 87,
            "motion_detected": False,
            "led_enabled": True,
        },
    },
}


@pytest.fixture
def mock_client() -> Generator[AsyncMock]:
    """Create a mock API client."""
    with patch(
        "custom_components.{domain}.MyClient", autospec=True
    ) as mock:
        client = mock.return_value
        client.async_get_device_info = AsyncMock(return_value=MOCK_DEVICE_INFO)
        client.async_get_data = AsyncMock(return_value=MOCK_DATA)
        client.async_set_switch = AsyncMock(return_value=True)
        yield client


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Prevent actual setup during config flow tests."""
    with patch(
        "custom_components.{domain}.async_setup_entry",
        return_value=True,
    ) as mock:
        yield mock
```

## test_config_flow.py — Config Flow Tests (REQUIRED)

```python
"""Test the {Name} config flow."""
from unittest.mock import AsyncMock

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.{domain}.const import DOMAIN

from .conftest import MOCK_CONFIG


async def test_user_flow_success(
    hass: HomeAssistant,
    mock_client: AsyncMock,
    mock_setup_entry: AsyncMock,
) -> None:
    """Test successful user config flow."""
    # Start the flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {}

    # Submit the form
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], MOCK_CONFIG
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Test Device"
    assert result["data"] == MOCK_CONFIG


async def test_user_flow_cannot_connect(
    hass: HomeAssistant,
    mock_client: AsyncMock,
    mock_setup_entry: AsyncMock,
) -> None:
    """Test config flow when device is unreachable."""
    mock_client.async_get_device_info.side_effect = ConnectionError

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], MOCK_CONFIG
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_user_flow_invalid_auth(
    hass: HomeAssistant,
    mock_client: AsyncMock,
    mock_setup_entry: AsyncMock,
) -> None:
    """Test config flow with wrong credentials."""
    mock_client.async_get_device_info.side_effect = InvalidAuth

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], MOCK_CONFIG
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}


async def test_user_flow_already_configured(
    hass: HomeAssistant,
    mock_client: AsyncMock,
    mock_setup_entry: AsyncMock,
) -> None:
    """Test flow aborts when device is already configured."""
    # Create an existing entry with the same unique ID
    entry = MockConfigEntry(domain=DOMAIN, unique_id="ABC123")
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], MOCK_CONFIG
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
```

## test_init.py — Setup/Unload Tests

```python
"""Test {Name} integration setup."""
from unittest.mock import AsyncMock

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from .conftest import MOCK_CONFIG


async def test_setup_entry(
    hass: HomeAssistant,
    mock_client: AsyncMock,
) -> None:
    """Test successful setup."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG)
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.LOADED


async def test_setup_entry_connection_error(
    hass: HomeAssistant,
    mock_client: AsyncMock,
) -> None:
    """Test setup fails gracefully on connection error."""
    mock_client.async_get_data.side_effect = ConnectionError
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG)
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.SETUP_RETRY


async def test_unload_entry(
    hass: HomeAssistant,
    mock_client: AsyncMock,
) -> None:
    """Test successful unload."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG)
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.LOADED

    await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED
```

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-homeassistant-custom-component pytest-asyncio

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_config_flow.py -v

# Run with coverage report
pytest tests/ --cov=custom_components.{domain} --cov-report=html

# Run a single test
pytest tests/test_config_flow.py::test_user_flow_success -v
```

## Key Testing Rules

1. **Config flow tests are mandatory** for Bronze tier — test success, connect failure, auth failure, and duplicate prevention at minimum
2. **Use `AsyncMock`** for all async client methods
3. **Mock the client**, not the coordinator — test the real coordinator logic with mocked external calls
4. **Use `mock_setup_entry`** in config flow tests to prevent actual integration setup
5. **Call `await hass.async_block_till_done()`** after setup to ensure all async tasks complete
6. **Assert `FlowResultType`** enum values, not string comparisons
