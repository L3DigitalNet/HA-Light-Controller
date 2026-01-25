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
    PRESET_SKIP_VERIFICATION,
    PRESET_TRANSITION,
    PRESET_COLOR_MODE,
    PRESET_COLOR_TEMP_KELVIN,
    PRESET_RGB_COLOR,
    COLOR_MODE_NONE,
    COLOR_MODE_COLOR_TEMP,
    COLOR_MODE_RGB,
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
        assert "settings" in result["menu_options"]
        assert "add_preset" in result["menu_options"]
        assert "manage_presets" in result["menu_options"]

    @pytest.mark.asyncio
    async def test_step_settings_form(self, options_flow, hass):
        """Test settings step shows form with all configuration options."""
        options_flow.hass = hass

        result = await options_flow.async_step_settings()

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "settings"

    @pytest.mark.asyncio
    async def test_step_settings_saves(self, options_flow, hass):
        """Test settings step saves all options."""
        options_flow.hass = hass

        result = await options_flow.async_step_settings(
            user_input={
                CONF_DEFAULT_BRIGHTNESS_PCT: 90,
                CONF_DEFAULT_TRANSITION: 2.0,
                CONF_BRIGHTNESS_TOLERANCE: 5,
                CONF_RGB_TOLERANCE: 15,
                CONF_KELVIN_TOLERANCE: 200,
                CONF_DELAY_AFTER_SEND: 3.0,
                CONF_MAX_RETRIES: 5,
                CONF_MAX_RUNTIME_SECONDS: 120.0,
                CONF_USE_EXPONENTIAL_BACKOFF: True,
                CONF_MAX_BACKOFF_SECONDS: 60.0,
                CONF_LOG_SUCCESS: True,
                CONF_NOTIFY_ON_FAILURE: "notify.mobile_app",
            }
        )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["data"][CONF_DEFAULT_BRIGHTNESS_PCT] == 90
        assert result["data"][CONF_DEFAULT_TRANSITION] == 2.0
        assert result["data"][CONF_BRIGHTNESS_TOLERANCE] == 5
        assert result["data"][CONF_RGB_TOLERANCE] == 15
        assert result["data"][CONF_KELVIN_TOLERANCE] == 200
        assert result["data"][CONF_DELAY_AFTER_SEND] == 3.0
        assert result["data"][CONF_MAX_RETRIES] == 5
        assert result["data"][CONF_USE_EXPONENTIAL_BACKOFF] is True
        assert result["data"][CONF_LOG_SUCCESS] is True
        assert result["data"][CONF_NOTIFY_ON_FAILURE] == "notify.mobile_app"

    @pytest.mark.asyncio
    async def test_step_settings_empty_notify(self, options_flow, hass):
        """Test settings step handles empty notify service."""
        options_flow.hass = hass

        result = await options_flow.async_step_settings(
            user_input={
                CONF_DEFAULT_BRIGHTNESS_PCT: 100,
                CONF_DEFAULT_TRANSITION: 1.0,
                CONF_LOG_SUCCESS: False,
                CONF_NOTIFY_ON_FAILURE: "",
            }
        )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["data"][CONF_NOTIFY_ON_FAILURE] == ""


class TestOptionsFlowAddPreset:
    """Tests for the add_preset options flow steps (multi-step flow)."""

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

        # Mock hass.states.get for friendly name lookup
        mock_state = MagicMock()
        mock_state.attributes = {"friendly_name": "Test Light"}
        hass.states.get = MagicMock(return_value=mock_state)

        return flow, preset_manager

    @pytest.mark.asyncio
    async def test_step_add_preset_form(self, options_flow_with_manager):
        """Test add_preset step shows form with name, entities, and skip_verification."""
        flow, _ = options_flow_with_manager

        result = await flow.async_step_add_preset()

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "add_preset"

    @pytest.mark.asyncio
    async def test_step_add_preset_goes_to_entity_menu(self, options_flow_with_manager):
        """Test add_preset step proceeds to preset_entity_menu after valid input."""
        flow, _ = options_flow_with_manager

        result = await flow.async_step_add_preset(
            user_input={
                PRESET_NAME: "New Preset",
                PRESET_ENTITIES: ["light.test"],
                PRESET_SKIP_VERIFICATION: False,
            }
        )

        # Should go to entity menu, not create entry directly
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "preset_entity_menu"
        # Verify preset data was stored
        assert flow._preset_data[PRESET_NAME] == "New Preset"
        assert flow._preset_data[PRESET_ENTITIES] == ["light.test"]

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

    @pytest.mark.asyncio
    async def test_step_preset_entity_menu_shows_actions(self, options_flow_with_manager):
        """Test preset_entity_menu shows available actions."""
        flow, _ = options_flow_with_manager
        # Set up preset data as if we came from add_preset
        flow._preset_data = {
            PRESET_NAME: "Test Preset",
            PRESET_ENTITIES: ["light.test"],
            PRESET_SKIP_VERIFICATION: False,
            "targets": {},
        }

        result = await flow.async_step_preset_entity_menu()

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "preset_entity_menu"
        assert "preset_name" in result["description_placeholders"]
        assert result["description_placeholders"]["preset_name"] == "Test Preset"

    @pytest.mark.asyncio
    async def test_step_preset_entity_menu_requires_configuration(self, options_flow_with_manager):
        """Test preset_entity_menu requires at least one entity to be configured."""
        flow, _ = options_flow_with_manager
        flow._preset_data = {
            PRESET_NAME: "Test Preset",
            PRESET_ENTITIES: ["light.test"],
            PRESET_SKIP_VERIFICATION: False,
            "targets": {},  # No entities configured yet
        }

        result = await flow.async_step_preset_entity_menu(
            user_input={"action": "save"}
        )

        assert result["type"] == FlowResultType.FORM
        assert result["errors"]["base"] == "configure_at_least_one"

    @pytest.mark.asyncio
    async def test_step_select_entity_to_configure(self, options_flow_with_manager):
        """Test select_entity_to_configure shows entity list."""
        flow, _ = options_flow_with_manager
        flow._preset_data = {
            PRESET_NAME: "Test Preset",
            PRESET_ENTITIES: ["light.test1", "light.test2"],
            PRESET_SKIP_VERIFICATION: False,
            "targets": {},
        }

        result = await flow.async_step_select_entity_to_configure()

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "select_entity_to_configure"

    @pytest.mark.asyncio
    async def test_step_configure_entity_form(self, options_flow_with_manager):
        """Test configure_entity shows form for entity settings."""
        flow, _ = options_flow_with_manager
        flow._preset_data = {
            PRESET_NAME: "Test Preset",
            PRESET_ENTITIES: ["light.test"],
            PRESET_SKIP_VERIFICATION: False,
            "targets": {},
        }
        flow._configuring_entity = "light.test"

        result = await flow.async_step_configure_entity()

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "configure_entity"
        assert "entity_name" in result["description_placeholders"]

    @pytest.mark.asyncio
    async def test_step_configure_entity_saves_on_state(self, options_flow_with_manager):
        """Test configure_entity saves 'on' state configuration."""
        flow, _ = options_flow_with_manager
        flow._preset_data = {
            PRESET_NAME: "Test Preset",
            PRESET_ENTITIES: ["light.test"],
            PRESET_SKIP_VERIFICATION: False,
            "targets": {},
        }
        flow._configuring_entity = "light.test"

        result = await flow.async_step_configure_entity(
            user_input={
                PRESET_STATE: "on",
                PRESET_TRANSITION: 1.5,
                PRESET_BRIGHTNESS_PCT: 75,
                PRESET_COLOR_MODE: COLOR_MODE_COLOR_TEMP,
                PRESET_COLOR_TEMP_KELVIN: 4000,
            }
        )

        # Should return to entity menu
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "preset_entity_menu"
        # Verify target was stored
        assert "light.test" in flow._preset_data["targets"]
        target = flow._preset_data["targets"]["light.test"]
        assert target["state"] == "on"
        assert target["brightness_pct"] == 75
        assert target["color_temp_kelvin"] == 4000
        assert target["transition"] == 1.5

    @pytest.mark.asyncio
    async def test_step_configure_entity_saves_off_state(self, options_flow_with_manager):
        """Test configure_entity saves 'off' state without brightness/color."""
        flow, _ = options_flow_with_manager
        flow._preset_data = {
            PRESET_NAME: "Test Preset",
            PRESET_ENTITIES: ["light.test"],
            PRESET_SKIP_VERIFICATION: False,
            "targets": {},
        }
        flow._configuring_entity = "light.test"

        result = await flow.async_step_configure_entity(
            user_input={
                PRESET_STATE: "off",
                PRESET_TRANSITION: 2.0,
                PRESET_BRIGHTNESS_PCT: 100,  # Should be ignored for off state
                PRESET_COLOR_MODE: COLOR_MODE_NONE,
            }
        )

        assert result["type"] == FlowResultType.FORM
        target = flow._preset_data["targets"]["light.test"]
        assert target["state"] == "off"
        assert "brightness_pct" not in target  # Not saved for off state
        assert "color_temp_kelvin" not in target

    @pytest.mark.asyncio
    async def test_step_configure_entity_rgb_color(self, options_flow_with_manager):
        """Test configure_entity saves RGB color configuration."""
        flow, _ = options_flow_with_manager
        flow._preset_data = {
            PRESET_NAME: "Test Preset",
            PRESET_ENTITIES: ["light.test"],
            PRESET_SKIP_VERIFICATION: False,
            "targets": {},
        }
        flow._configuring_entity = "light.test"

        result = await flow.async_step_configure_entity(
            user_input={
                PRESET_STATE: "on",
                PRESET_TRANSITION: 0,
                PRESET_BRIGHTNESS_PCT: 80,
                PRESET_COLOR_MODE: COLOR_MODE_RGB,
                PRESET_RGB_COLOR: [255, 128, 64],
            }
        )

        target = flow._preset_data["targets"]["light.test"]
        assert target["rgb_color"] == [255, 128, 64]

    @pytest.mark.asyncio
    async def test_step_add_more_entities(self, options_flow_with_manager):
        """Test add_more_entities adds entities to preset."""
        flow, _ = options_flow_with_manager
        flow._preset_data = {
            PRESET_NAME: "Test Preset",
            PRESET_ENTITIES: ["light.test1"],
            PRESET_SKIP_VERIFICATION: False,
            "targets": {},
        }

        result = await flow.async_step_add_more_entities(
            user_input={"new_entities": ["light.test2", "light.test3"]}
        )

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "preset_entity_menu"
        assert "light.test2" in flow._preset_data[PRESET_ENTITIES]
        assert "light.test3" in flow._preset_data[PRESET_ENTITIES]

    @pytest.mark.asyncio
    async def test_step_add_more_entities_no_duplicates(self, options_flow_with_manager):
        """Test add_more_entities doesn't add duplicate entities."""
        flow, _ = options_flow_with_manager
        flow._preset_data = {
            PRESET_NAME: "Test Preset",
            PRESET_ENTITIES: ["light.test1"],
            PRESET_SKIP_VERIFICATION: False,
            "targets": {},
        }

        await flow.async_step_add_more_entities(
            user_input={"new_entities": ["light.test1", "light.test2"]}
        )

        # light.test1 should only appear once
        assert flow._preset_data[PRESET_ENTITIES].count("light.test1") == 1
        assert "light.test2" in flow._preset_data[PRESET_ENTITIES]

    @pytest.mark.asyncio
    async def test_step_remove_entity(self, options_flow_with_manager):
        """Test remove_entity removes entity from preset."""
        flow, _ = options_flow_with_manager
        flow._preset_data = {
            PRESET_NAME: "Test Preset",
            PRESET_ENTITIES: ["light.test1", "light.test2"],
            PRESET_SKIP_VERIFICATION: False,
            "targets": {"light.test1": {"entity_id": "light.test1", "state": "on"}},
        }

        result = await flow.async_step_remove_entity(
            user_input={"entity_to_remove": "light.test1"}
        )

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "preset_entity_menu"
        assert "light.test1" not in flow._preset_data[PRESET_ENTITIES]
        assert "light.test1" not in flow._preset_data["targets"]

    @pytest.mark.asyncio
    async def test_step_remove_entity_prevents_last_removal(self, options_flow_with_manager):
        """Test cannot remove last entity from preset."""
        flow, _ = options_flow_with_manager
        flow._preset_data = {
            PRESET_NAME: "Test Preset",
            PRESET_ENTITIES: ["light.test1"],  # Only one entity
            PRESET_SKIP_VERIFICATION: False,
            "targets": {},
        }

        result = await flow.async_step_preset_entity_menu(
            user_input={"action": "remove"}
        )

        assert result["type"] == FlowResultType.FORM
        assert result["errors"]["base"] == "cannot_remove_last"

    @pytest.mark.asyncio
    async def test_create_preset_from_data(self, options_flow_with_manager):
        """Test _create_preset_from_data creates preset with configured targets."""
        flow, preset_manager = options_flow_with_manager
        flow._preset_data = {
            PRESET_NAME: "Test Preset",
            PRESET_ENTITIES: ["light.test1", "light.test2"],
            PRESET_SKIP_VERIFICATION: True,
            "targets": {
                "light.test1": {"entity_id": "light.test1", "state": "on", "brightness_pct": 75},
                "light.test2": {"entity_id": "light.test2", "state": "off"},
            },
        }

        result = await flow._create_preset_from_data()

        assert result["type"] == FlowResultType.CREATE_ENTRY
        preset_manager.create_preset.assert_called_once()
        call_kwargs = preset_manager.create_preset.call_args.kwargs
        assert call_kwargs["name"] == "Test Preset"
        assert len(call_kwargs["targets"]) == 2
        assert call_kwargs["skip_verification"] is True


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
