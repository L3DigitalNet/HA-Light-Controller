"""Fixtures for Light Controller tests."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, AsyncMock
from typing import Any
from dataclasses import dataclass

import pytest


# =============================================================================
# Mock Home Assistant modules before importing custom component
# =============================================================================

# Create mock homeassistant module structure
mock_ha = MagicMock()
mock_ha.core.HomeAssistant = MagicMock
mock_ha.core.State = MagicMock
mock_ha.core.callback = lambda f: f
mock_ha.core.ServiceCall = MagicMock
mock_ha.core.SupportsResponse = MagicMock()
mock_ha.core.SupportsResponse.OPTIONAL = "optional"

mock_ha.config_entries.ConfigEntry = MagicMock
mock_ha.config_entries.ConfigFlowResult = dict

# Create proper base classes for ConfigFlow and OptionsFlow
class MockConfigFlow:
    """Mock ConfigFlow base class."""
    def __init_subclass__(cls, **kwargs):
        pass

    def async_show_form(self, **kwargs):
        return {"type": "form", **kwargs}

    def async_create_entry(self, **kwargs):
        return {"type": "create_entry", **kwargs}

    def async_show_menu(self, **kwargs):
        return {"type": "menu", **kwargs}


class MockOptionsFlow:
    """Mock OptionsFlow base class."""
    _config_entry = None

    def __init_subclass__(cls, **kwargs):
        pass

    @property
    def config_entry(self):
        """Return the config entry."""
        return self._config_entry

    def async_show_form(self, **kwargs):
        return {"type": "form", **kwargs}

    def async_create_entry(self, **kwargs):
        return {"type": "create_entry", **kwargs}

    def async_show_menu(self, **kwargs):
        return {"type": "menu", **kwargs}


mock_ha.config_entries.ConfigFlow = MockConfigFlow
mock_ha.config_entries.OptionsFlow = MockOptionsFlow

mock_ha.data_entry_flow.FlowResultType = MagicMock()
mock_ha.data_entry_flow.FlowResultType.FORM = "form"
mock_ha.data_entry_flow.FlowResultType.CREATE_ENTRY = "create_entry"
mock_ha.data_entry_flow.FlowResultType.MENU = "menu"

mock_ha.const.STATE_ON = "on"
mock_ha.const.STATE_OFF = "off"
mock_ha.const.STATE_UNAVAILABLE = "unavailable"
mock_ha.const.STATE_UNKNOWN = "unknown"

mock_ha.helpers = MagicMock()
mock_ha.helpers.config_validation = MagicMock()
mock_ha.helpers.config_validation.entity_ids = MagicMock()
mock_ha.helpers.config_validation.entity_id = MagicMock()
mock_ha.helpers.config_validation.string = MagicMock()
mock_ha.helpers.config_validation.boolean = MagicMock()
mock_ha.helpers.config_validation.ensure_list = MagicMock()
mock_ha.helpers.selector = MagicMock()
mock_ha.helpers.entity = MagicMock()
mock_ha.helpers.entity.DeviceInfo = dict
mock_ha.helpers.entity_platform = MagicMock()

# Create a proper mock for entity_registry
mock_entity_registry = MagicMock()
mock_entity_registry.async_get_entity_id = MagicMock(return_value=None)
mock_entity_registry.async_remove = MagicMock()

mock_ha.helpers.entity_registry = MagicMock()
mock_ha.helpers.entity_registry.async_get = MagicMock(return_value=mock_entity_registry)

mock_ha.components = MagicMock()
mock_ha.components.light = MagicMock()
mock_ha.components.light.DOMAIN = "light"
mock_ha.components.group = MagicMock()
mock_ha.components.group.DOMAIN = "group"
mock_ha.components.button = MagicMock()

# Create proper base classes for entities
class MockButtonEntity:
    """Mock ButtonEntity base class."""
    _attr_has_entity_name = False
    _attr_device_class = None
    _attr_unique_id = None
    _attr_name = None
    _attr_icon = None

    async def async_added_to_hass(self):
        pass

    async def async_will_remove_from_hass(self):
        pass


class MockSensorEntity:
    """Mock SensorEntity base class."""
    _attr_has_entity_name = False
    _attr_unique_id = None
    _attr_name = None
    _attr_icon = None

    async def async_added_to_hass(self):
        pass

    async def async_will_remove_from_hass(self):
        pass


class MockButtonDeviceClass:
    """Mock ButtonDeviceClass enum."""
    IDENTIFY = "identify"


mock_ha.components.button.ButtonEntity = MockButtonEntity
mock_ha.components.button.ButtonDeviceClass = MockButtonDeviceClass
mock_ha.components.sensor = MagicMock()
mock_ha.components.sensor.SensorEntity = MockSensorEntity
mock_ha.components.sensor.SensorDeviceClass = MagicMock()
mock_ha.components.sensor.SensorDeviceClass.ENUM = "enum"

# Mock voluptuous
mock_vol = MagicMock()
mock_vol.Schema = lambda x, extra=None: x
mock_vol.Required = lambda x, default=None: x
mock_vol.Optional = lambda x, default=None: x
mock_vol.All = lambda *args: args[0] if args else None
mock_vol.Coerce = lambda x: x
mock_vol.Range = lambda **kwargs: None
mock_vol.In = lambda x: x
mock_vol.ExactSequence = lambda x: x
mock_vol.ALLOW_EXTRA = "allow_extra"

# Install mocks
sys.modules["homeassistant"] = mock_ha
sys.modules["homeassistant.core"] = mock_ha.core
sys.modules["homeassistant.config_entries"] = mock_ha.config_entries
sys.modules["homeassistant.data_entry_flow"] = mock_ha.data_entry_flow
sys.modules["homeassistant.const"] = mock_ha.const
sys.modules["homeassistant.helpers"] = mock_ha.helpers
sys.modules["homeassistant.helpers.config_validation"] = mock_ha.helpers.config_validation
sys.modules["homeassistant.helpers.selector"] = mock_ha.helpers.selector
sys.modules["homeassistant.helpers.entity"] = mock_ha.helpers.entity
sys.modules["homeassistant.helpers.entity_platform"] = mock_ha.helpers.entity_platform
sys.modules["homeassistant.helpers.entity_registry"] = mock_ha.helpers.entity_registry
sys.modules["homeassistant.components"] = mock_ha.components
sys.modules["homeassistant.components.light"] = mock_ha.components.light
sys.modules["homeassistant.components.group"] = mock_ha.components.group
sys.modules["homeassistant.components.button"] = mock_ha.components.button
sys.modules["homeassistant.components.sensor"] = mock_ha.components.sensor
sys.modules["voluptuous"] = mock_vol

# Now we can import the custom component
from custom_components.ha_light_controller.const import DOMAIN, CONF_PRESETS


# =============================================================================
# Constants
# =============================================================================

STATE_ON = "on"
STATE_OFF = "off"
STATE_UNAVAILABLE = "unavailable"
STATE_UNKNOWN = "unknown"


# =============================================================================
# State mock class
# =============================================================================

@dataclass
class State:
    """Mock Home Assistant State."""
    entity_id: str
    state: str
    attributes: dict


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def hass() -> MagicMock:
    """Create a mock Home Assistant instance."""
    hass = MagicMock()
    hass.data = {}
    hass.states = MagicMock()
    hass.services = MagicMock()
    hass.config_entries = MagicMock()
    hass.async_create_task = MagicMock()

    # Make async service calls return immediately
    hass.services.async_call = AsyncMock()
    hass.config_entries.async_update_entry = MagicMock()
    hass.config_entries.async_reload = AsyncMock()
    hass.config_entries.async_forward_entry_setups = AsyncMock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

    return hass


@pytest.fixture
def config_entry() -> MagicMock:
    """Create a mock config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.data = {CONF_PRESETS: {}}
    entry.options = {}
    entry.async_on_unload = MagicMock()
    entry.add_update_listener = MagicMock()
    entry.runtime_data = None  # Will be set during async_setup_entry
    return entry


@pytest.fixture
def config_entry_with_presets() -> MagicMock:
    """Create a mock config entry with presets."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.data = {
        CONF_PRESETS: {
            "preset_1": {
                "id": "preset_1",
                "name": "Test Preset",
                "entities": ["light.test_light_1", "light.test_light_2"],
                "state": "on",
                "brightness_pct": 75,
                "rgb_color": None,
                "color_temp_kelvin": 4000,
                "effect": None,
                "targets": [],
                "transition": 1.0,
                "skip_verification": False,
            },
            "preset_2": {
                "id": "preset_2",
                "name": "Evening Scene",
                "entities": ["light.living_room"],
                "state": "on",
                "brightness_pct": 50,
                "rgb_color": [255, 200, 150],
                "color_temp_kelvin": None,
                "effect": None,
                "targets": [],
                "transition": 2.0,
                "skip_verification": False,
            },
        }
    }
    entry.options = {
        "default_brightness_pct": 100,
        "brightness_tolerance": 5,
    }
    entry.async_on_unload = MagicMock()
    entry.add_update_listener = MagicMock()
    entry.runtime_data = None  # Will be set during async_setup_entry
    return entry


def create_light_state(
    entity_id: str,
    state: str = STATE_ON,
    brightness: int = 255,
    rgb_color: tuple[int, int, int] | None = None,
    color_temp_kelvin: int | None = None,
    supported_color_modes: list[str] | None = None,
    effect: str | None = None,
    entity_ids: list[str] | None = None,
) -> State:
    """Create a mock light state."""
    attributes: dict[str, Any] = {}

    if state == STATE_ON:
        attributes["brightness"] = brightness

        if rgb_color:
            attributes["rgb_color"] = rgb_color
        if color_temp_kelvin:
            attributes["color_temp_kelvin"] = color_temp_kelvin
        if effect:
            attributes["effect"] = effect

    if supported_color_modes:
        attributes["supported_color_modes"] = supported_color_modes

    # For groups, include entity_id list
    if entity_ids:
        attributes["entity_id"] = entity_ids

    return State(entity_id, state, attributes)


@pytest.fixture
def mock_light_states(hass: MagicMock) -> dict[str, State]:
    """Set up mock light states."""
    states = {
        "light.test_light_1": create_light_state(
            "light.test_light_1",
            STATE_ON,
            brightness=255,
            supported_color_modes=["brightness", "color_temp", "rgb"],
        ),
        "light.test_light_2": create_light_state(
            "light.test_light_2",
            STATE_ON,
            brightness=200,
            rgb_color=(255, 0, 0),
            supported_color_modes=["brightness", "rgb"],
        ),
        "light.test_light_3": create_light_state(
            "light.test_light_3",
            STATE_OFF,
            supported_color_modes=["brightness"],
        ),
        "light.unavailable_light": create_light_state(
            "light.unavailable_light",
            STATE_UNAVAILABLE,
        ),
        "light.test_group": create_light_state(
            "light.test_group",
            STATE_ON,
            brightness=230,
            entity_ids=["light.test_light_1", "light.test_light_2"],
        ),
    }

    def get_state(entity_id: str) -> State | None:
        return states.get(entity_id)

    hass.states.get = get_state

    return states


@pytest.fixture
def mock_light_on(hass: MagicMock) -> State:
    """Create a single mock light that is on."""
    state = create_light_state(
        "light.single_light",
        STATE_ON,
        brightness=255,
        color_temp_kelvin=4000,
        supported_color_modes=["brightness", "color_temp"],
    )
    hass.states.get = MagicMock(return_value=state)
    return state


@pytest.fixture
def mock_light_off(hass: MagicMock) -> State:
    """Create a single mock light that is off."""
    state = create_light_state(
        "light.single_light",
        STATE_OFF,
        supported_color_modes=["brightness"],
    )
    hass.states.get = MagicMock(return_value=state)
    return state
