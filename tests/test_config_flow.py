"""Tests for the Light Controller config flow."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.config_entries import ConfigEntry
from homeassistant.data_entry_flow import FlowResultType

from custom_components.ha_light_controller.config_flow import (
    LightControllerConfigFlow,
    LightControllerOptionsFlow,
)
from custom_components.ha_light_controller.const import (
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
    PRESET_NAME,
    PRESET_ENTITIES,
    PRESET_STATE,
    PRESET_BRIGHTNESS_PCT,
)


# =============================================================================
# ConfigFlow Tests
# =============================================================================


class TestLightControllerConfigFlow:
    """Tests for the initial config flow."""

    @pytest.mark.asyncio
    async def test_step_user_form(self, hass):
        """Test that the user step shows a form."""
        flow = LightControllerConfigFlow()
        flow.hass = hass
        flow.context = {}

        result = await flow.async_step_user()

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"
        assert result["errors"] == {}

    @pytest.mark.asyncio
    async def test_step_user_creates_entry(self, hass):
        """Test that submitting the form creates an entry."""
        flow = LightControllerConfigFlow()
        flow.hass = hass
        flow.context = {}

        # Mock the unique ID methods
        flow.async_set_unique_id = AsyncMock()
        flow._abort_if_unique_id_configured = MagicMock()

        result = await flow.async_step_user(
            user_input={
                CONF_DEFAULT_BRIGHTNESS_PCT: 80,
                CONF_DEFAULT_TRANSITION: 1.5,
            }
        )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == "Light Controller"
        assert result["data"] == {}
        assert result["options"][CONF_DEFAULT_BRIGHTNESS_PCT] == 80
        assert result["options"][CONF_DEFAULT_TRANSITION] == 1.5

    @pytest.mark.asyncio
    async def test_step_user_uses_defaults(self, hass):
        """Test that missing values use defaults."""
        flow = LightControllerConfigFlow()
        flow.hass = hass
        flow.context = {}

        flow.async_set_unique_id = AsyncMock()
        flow._abort_if_unique_id_configured = MagicMock()

        result = await flow.async_step_user(user_input={})

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["options"][CONF_DEFAULT_BRIGHTNESS_PCT] == DEFAULT_BRIGHTNESS_PCT
        assert result["options"][CONF_DEFAULT_TRANSITION] == DEFAULT_TRANSITION

    def test_async_get_options_flow(self):
        """Test that options flow handler is returned."""
        entry = MagicMock(spec=ConfigEntry)
        flow = LightControllerConfigFlow.async_get_options_flow(entry)
        assert isinstance(flow, LightControllerOptionsFlow)


# =============================================================================
# OptionsFlow Tests
# =============================================================================


class TestLightControllerOptionsFlow:
    """Tests for the options flow."""

    @pytest.fixture
    def options_flow(self, config_entry):
        """Create an options flow instance."""
        flow = LightControllerOptionsFlow()
        flow._config_entry = config_entry
        return flow

    @pytest.mark.asyncio
    async def test_step_init_shows_menu(self, options_flow, hass):
        """Test that init step shows menu."""
        options_flow.hass = hass

        result = await options_flow.async_step_init()

        assert result["type"] == FlowResultType.MENU
        assert "defaults" in result["menu_options"]
        assert "tolerances" in result["menu_options"]
        assert "retry" in result["menu_options"]
        assert "notifications" in result["menu_options"]
        assert "add_preset" in result["menu_options"]
        assert "manage_presets" in result["menu_options"]

    @pytest.mark.asyncio
    async def test_step_defaults_form(self, options_flow, hass):
        """Test defaults step shows form."""
        options_flow.hass = hass

        result = await options_flow.async_step_defaults()

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "defaults"

    @pytest.mark.asyncio
    async def test_step_defaults_saves(self, options_flow, hass):
        """Test defaults step saves options."""
        options_flow.hass = hass

        result = await options_flow.async_step_defaults(
            user_input={
                CONF_DEFAULT_BRIGHTNESS_PCT: 90,
                CONF_DEFAULT_TRANSITION: 2.0,
            }
        )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["data"][CONF_DEFAULT_BRIGHTNESS_PCT] == 90
        assert result["data"][CONF_DEFAULT_TRANSITION] == 2.0

    @pytest.mark.asyncio
    async def test_step_tolerances_form(self, options_flow, hass):
        """Test tolerances step shows form."""
        options_flow.hass = hass

        result = await options_flow.async_step_tolerances()

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "tolerances"

    @pytest.mark.asyncio
    async def test_step_tolerances_saves(self, options_flow, hass):
        """Test tolerances step saves options."""
        options_flow.hass = hass

        result = await options_flow.async_step_tolerances(
            user_input={
                CONF_BRIGHTNESS_TOLERANCE: 5,
                CONF_RGB_TOLERANCE: 15,
                CONF_KELVIN_TOLERANCE: 200,
            }
        )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["data"][CONF_BRIGHTNESS_TOLERANCE] == 5
        assert result["data"][CONF_RGB_TOLERANCE] == 15
        assert result["data"][CONF_KELVIN_TOLERANCE] == 200

    @pytest.mark.asyncio
    async def test_step_retry_form(self, options_flow, hass):
        """Test retry step shows form."""
        options_flow.hass = hass

        result = await options_flow.async_step_retry()

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "retry"

    @pytest.mark.asyncio
    async def test_step_retry_saves(self, options_flow, hass):
        """Test retry step saves options."""
        options_flow.hass = hass

        result = await options_flow.async_step_retry(
            user_input={
                CONF_DELAY_AFTER_SEND: 3.0,
                CONF_MAX_RETRIES: 5,
                CONF_MAX_RUNTIME_SECONDS: 120.0,
                CONF_USE_EXPONENTIAL_BACKOFF: True,
                CONF_MAX_BACKOFF_SECONDS: 60.0,
            }
        )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["data"][CONF_DELAY_AFTER_SEND] == 3.0
        assert result["data"][CONF_MAX_RETRIES] == 5
        assert result["data"][CONF_USE_EXPONENTIAL_BACKOFF] is True

    @pytest.mark.asyncio
    async def test_step_notifications_form(self, options_flow, hass):
        """Test notifications step shows form."""
        options_flow.hass = hass

        result = await options_flow.async_step_notifications()

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "notifications"

    @pytest.mark.asyncio
    async def test_step_notifications_saves(self, options_flow, hass):
        """Test notifications step saves options."""
        options_flow.hass = hass

        result = await options_flow.async_step_notifications(
            user_input={
                CONF_LOG_SUCCESS: True,
                CONF_NOTIFY_ON_FAILURE: "notify.mobile_app",
            }
        )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["data"][CONF_LOG_SUCCESS] is True
        assert result["data"][CONF_NOTIFY_ON_FAILURE] == "notify.mobile_app"

    @pytest.mark.asyncio
    async def test_step_notifications_empty_notify(self, options_flow, hass):
        """Test notifications step handles empty notify service."""
        options_flow.hass = hass

        result = await options_flow.async_step_notifications(
            user_input={
                CONF_LOG_SUCCESS: False,
                CONF_NOTIFY_ON_FAILURE: "",
            }
        )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["data"][CONF_NOTIFY_ON_FAILURE] == ""


class TestOptionsFlowAddPreset:
    """Tests for the add_preset options flow step."""

    @pytest.fixture
    def options_flow_with_manager(self, config_entry, hass):
        """Create options flow with mock preset manager."""
        flow = LightControllerOptionsFlow()
        flow._config_entry = config_entry
        flow.hass = hass

        # Set up mock preset manager in runtime_data
        preset_manager = MagicMock()
        preset_manager.create_preset = AsyncMock()

        runtime_data = MagicMock()
        runtime_data.preset_manager = preset_manager
        config_entry.runtime_data = runtime_data

        return flow, preset_manager

    @pytest.mark.asyncio
    async def test_step_add_preset_form(self, options_flow_with_manager):
        """Test add_preset step shows form."""
        flow, _ = options_flow_with_manager

        result = await flow.async_step_add_preset()

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "add_preset"

    @pytest.mark.asyncio
    async def test_step_add_preset_creates(self, options_flow_with_manager):
        """Test add_preset step creates preset."""
        flow, preset_manager = options_flow_with_manager

        result = await flow.async_step_add_preset(
            user_input={
                PRESET_NAME: "New Preset",
                PRESET_ENTITIES: ["light.test"],
                PRESET_STATE: "on",
                PRESET_BRIGHTNESS_PCT: 75,
            }
        )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        preset_manager.create_preset.assert_called_once()

    @pytest.mark.asyncio
    async def test_step_add_preset_validates_name(self, options_flow_with_manager):
        """Test add_preset validates name is required."""
        flow, _ = options_flow_with_manager

        result = await flow.async_step_add_preset(
            user_input={
                PRESET_NAME: "",
                PRESET_ENTITIES: ["light.test"],
            }
        )

        assert result["type"] == FlowResultType.FORM
        assert result["errors"]["base"] == "name_required"

    @pytest.mark.asyncio
    async def test_step_add_preset_validates_entities(self, options_flow_with_manager):
        """Test add_preset validates entities are required."""
        flow, _ = options_flow_with_manager

        result = await flow.async_step_add_preset(
            user_input={
                PRESET_NAME: "Test",
                PRESET_ENTITIES: [],
            }
        )

        assert result["type"] == FlowResultType.FORM
        assert result["errors"]["base"] == "entities_required"


class TestOptionsFlowManagePresets:
    """Tests for the manage_presets options flow step."""

    @pytest.fixture
    def options_flow_with_presets(self, config_entry_with_presets, hass):
        """Create options flow with mock preset manager containing presets."""
        flow = LightControllerOptionsFlow()
        flow._config_entry = config_entry_with_presets
        flow.hass = hass

        # Create mock preset manager with actual presets
        from custom_components.ha_light_controller.preset_manager import PresetConfig

        preset_manager = MagicMock()
        preset_manager.presets = {
            "preset_1": PresetConfig(
                id="preset_1",
                name="Test Preset",
                entities=["light.test"],
            ),
            "preset_2": PresetConfig(
                id="preset_2",
                name="Another Preset",
                entities=["light.other"],
            ),
        }
        preset_manager.delete_preset = AsyncMock()

        runtime_data = MagicMock()
        runtime_data.preset_manager = preset_manager
        config_entry_with_presets.runtime_data = runtime_data

        return flow, preset_manager

    @pytest.fixture
    def options_flow_no_presets(self, config_entry, hass):
        """Create options flow with empty preset manager."""
        flow = LightControllerOptionsFlow()
        flow._config_entry = config_entry
        flow.hass = hass

        preset_manager = MagicMock()
        preset_manager.presets = {}

        runtime_data = MagicMock()
        runtime_data.preset_manager = preset_manager
        config_entry.runtime_data = runtime_data

        return flow

    @pytest.mark.asyncio
    async def test_step_manage_presets_form(self, options_flow_with_presets):
        """Test manage_presets shows form with presets."""
        flow, _ = options_flow_with_presets

        result = await flow.async_step_manage_presets()

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "manage_presets"
        assert "preset_count" in result["description_placeholders"]
        assert result["description_placeholders"]["preset_count"] == "2"

    @pytest.mark.asyncio
    async def test_step_manage_presets_no_presets(self, options_flow_no_presets):
        """Test manage_presets handles no presets."""
        flow = options_flow_no_presets

        result = await flow.async_step_manage_presets()

        assert result["type"] == FlowResultType.FORM
        assert result["errors"]["base"] == "no_presets"

    @pytest.mark.asyncio
    async def test_step_manage_presets_deletes(self, options_flow_with_presets):
        """Test manage_presets can delete preset."""
        flow, preset_manager = options_flow_with_presets

        result = await flow.async_step_manage_presets(
            user_input={"preset_to_delete": "preset_1"}
        )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        preset_manager.delete_preset.assert_called_once_with("preset_1")

    @pytest.mark.asyncio
    async def test_step_manage_presets_no_delete(self, options_flow_with_presets):
        """Test manage_presets with no delete selection."""
        flow, preset_manager = options_flow_with_presets

        result = await flow.async_step_manage_presets(user_input={})

        assert result["type"] == FlowResultType.CREATE_ENTRY
        preset_manager.delete_preset.assert_not_called()
