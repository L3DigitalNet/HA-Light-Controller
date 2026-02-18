"""Tests for the Light Controller button platform."""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.ha_light_controller.button import (
    PresetButton,
    async_setup_entry,
)
from custom_components.ha_light_controller.const import (
    DOMAIN,
    PRESET_STATUS_ACTIVATING,
    PRESET_STATUS_FAILED,
    PRESET_STATUS_SUCCESS,
)
from custom_components.ha_light_controller.preset_manager import (
    PresetConfig,
    PresetStatus,
)


@dataclass
class MockRuntimeData:
    """Mock runtime data for tests."""

    controller: MagicMock
    preset_manager: MagicMock


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_preset():
    """Create a mock preset."""
    return PresetConfig(
        id="test_preset_id",
        name="Test Preset",
        entities=["light.test_1", "light.test_2"],
        state="on",
        brightness_pct=75,
        rgb_color=[255, 200, 100],
        color_temp_kelvin=None,
        effect=None,
        targets=[],
        transition=1.5,
        skip_verification=False,
    )


@pytest.fixture
def mock_preset_manager(mock_preset):
    """Create a mock preset manager."""
    manager = MagicMock()
    manager.presets = {"test_preset_id": mock_preset}
    manager.get_preset = MagicMock(return_value=mock_preset)
    manager.get_status = MagicMock(return_value=PresetStatus())
    manager.set_status = AsyncMock()
    manager.register_listener = MagicMock(return_value=MagicMock())
    manager.activate_preset_with_options = AsyncMock(
        return_value={"success": True, "result": "success"}
    )
    return manager


@pytest.fixture
def mock_controller():
    """Create a mock controller."""
    controller = MagicMock()
    controller.ensure_state = AsyncMock(
        return_value={"success": True, "result": "success"}
    )
    return controller


@pytest.fixture
def button_entity(
    hass, config_entry, mock_preset_manager, mock_controller, mock_preset
):
    """Create a PresetButton entity."""
    return PresetButton(
        hass=hass,
        entry=config_entry,
        preset_manager=mock_preset_manager,
        controller=mock_controller,
        preset_id="test_preset_id",
        preset=mock_preset,
    )


# =============================================================================
# async_setup_entry Tests
# =============================================================================


class TestAsyncSetupEntry:
    """Tests for async_setup_entry."""

    @pytest.mark.asyncio
    async def test_setup_entry_adds_buttons(
        self, hass, config_entry, mock_preset_manager, mock_controller
    ):
        """Test that setup entry adds button entities."""
        config_entry.runtime_data = MockRuntimeData(
            controller=mock_controller,
            preset_manager=mock_preset_manager,
        )

        async_add_entities = MagicMock()
        await async_setup_entry(hass, config_entry, async_add_entities)

        async_add_entities.assert_called_once()
        entities = async_add_entities.call_args[0][0]
        assert len(entities) == 1
        assert isinstance(entities[0], PresetButton)

    @pytest.mark.asyncio
    async def test_setup_entry_registers_listener(
        self, hass, config_entry, mock_preset_manager, mock_controller
    ):
        """Test that setup entry registers a listener for new presets."""
        config_entry.runtime_data = MockRuntimeData(
            controller=mock_controller,
            preset_manager=mock_preset_manager,
        )

        async_add_entities = MagicMock()
        await async_setup_entry(hass, config_entry, async_add_entities)

        mock_preset_manager.register_listener.assert_called()
        config_entry.async_on_unload.assert_called()


# =============================================================================
# PresetButton Tests
# =============================================================================


class TestPresetButton:
    """Tests for PresetButton entity."""

    def test_init(self, button_entity, mock_preset):
        """Test button initialization."""
        assert button_entity._preset_id == "test_preset_id"
        assert button_entity._preset == mock_preset
        assert button_entity._attr_translation_placeholders == {"name": "Test Preset"}
        assert button_entity._attr_translation_key == "preset"
        # Icon is now a dynamic property based on preset state
        assert button_entity.icon == "mdi:lightbulb-group"

    def test_icon_off_preset(
        self, hass, config_entry, mock_preset_manager, mock_controller
    ):
        """Test icon for preset with state='off'."""
        preset = PresetConfig(
            id="off_preset",
            name="Turn Off",
            entities=["light.test"],
            state="off",
            brightness_pct=0,
        )
        mock_preset_manager.get_preset.return_value = preset

        button = PresetButton(
            hass=hass,
            entry=config_entry,
            preset_manager=mock_preset_manager,
            controller=mock_controller,
            preset_id="off_preset",
            preset=preset,
        )

        assert button.icon == "mdi:lightbulb-group-off"

    def test_unique_id(self, button_entity, config_entry):
        """Test unique ID generation."""
        expected_id = f"{config_entry.entry_id}_preset_test_preset_id_button"
        assert button_entity._attr_unique_id == expected_id

    def test_device_class(self, button_entity):
        """Test device class is not set (None)."""
        assert (
            not hasattr(button_entity, "_attr_device_class")
            or button_entity._attr_device_class is None
        )

    def test_has_entity_name(self, button_entity):
        """Test has_entity_name flag."""
        assert button_entity._attr_has_entity_name is True

    def test_device_info(self, button_entity, config_entry):
        """Test device info."""
        device_info = button_entity.device_info
        assert (DOMAIN, config_entry.entry_id) in device_info["identifiers"]
        assert device_info["name"] == "Light Controller"

    def test_available_when_preset_exists(self, button_entity, mock_preset_manager):
        """Test availability when preset exists."""
        assert button_entity.available is True

    def test_unavailable_when_preset_deleted(self, button_entity, mock_preset_manager):
        """Test availability when preset is deleted."""
        mock_preset_manager.get_preset.return_value = None
        assert button_entity.available is False


class TestPresetButtonAttributes:
    """Tests for PresetButton extra state attributes."""

    def test_extra_state_attributes_basic(self, button_entity, mock_preset):
        """Test basic extra state attributes."""
        attrs = button_entity.extra_state_attributes
        assert attrs["preset_id"] == "test_preset_id"
        assert attrs["entities"] == ["light.test_1", "light.test_2"]
        assert attrs["state"] == "on"
        assert attrs["brightness_pct"] == 75

    def test_extra_state_attributes_with_rgb(self, button_entity, mock_preset):
        """Test extra state attributes include RGB color."""
        attrs = button_entity.extra_state_attributes
        assert attrs["rgb_color"] == [255, 200, 100]

    def test_extra_state_attributes_no_rgb(
        self, hass, config_entry, mock_preset_manager, mock_controller
    ):
        """Test extra state attributes when no RGB color."""
        preset = PresetConfig(
            id="no_rgb",
            name="No RGB",
            entities=["light.test"],
            brightness_pct=50,
            color_temp_kelvin=4000,
        )
        mock_preset_manager.get_preset.return_value = preset

        button = PresetButton(
            hass=hass,
            entry=config_entry,
            preset_manager=mock_preset_manager,
            controller=mock_controller,
            preset_id="no_rgb",
            preset=preset,
        )

        attrs = button.extra_state_attributes
        assert "rgb_color" not in attrs
        assert attrs["color_temp_kelvin"] == 4000

    def test_extra_state_attributes_with_effect(
        self, hass, config_entry, mock_preset_manager, mock_controller
    ):
        """Test extra state attributes include effect."""
        preset = PresetConfig(
            id="with_effect",
            name="With Effect",
            entities=["light.test"],
            brightness_pct=100,
            effect="rainbow",
        )
        mock_preset_manager.get_preset.return_value = preset

        button = PresetButton(
            hass=hass,
            entry=config_entry,
            preset_manager=mock_preset_manager,
            controller=mock_controller,
            preset_id="with_effect",
            preset=preset,
        )

        attrs = button.extra_state_attributes
        assert attrs["effect"] == "rainbow"

    def test_extra_state_attributes_with_targets(
        self, hass, config_entry, mock_preset_manager, mock_controller
    ):
        """Test extra state attributes include target count."""
        preset = PresetConfig(
            id="with_targets",
            name="With Targets",
            entities=["light.test_1", "light.test_2"],
            brightness_pct=100,
            targets=[
                {"entity_id": "light.test_1", "brightness_pct": 50},
                {"entity_id": "light.test_2", "brightness_pct": 75},
            ],
        )
        mock_preset_manager.get_preset.return_value = preset

        button = PresetButton(
            hass=hass,
            entry=config_entry,
            preset_manager=mock_preset_manager,
            controller=mock_controller,
            preset_id="with_targets",
            preset=preset,
        )

        attrs = button.extra_state_attributes
        assert attrs["target_count"] == 2

    def test_extra_state_attributes_with_last_result(
        self, button_entity, mock_preset_manager
    ):
        """Test extra state attributes include last activation result."""
        mock_preset_manager.get_status.return_value = PresetStatus(
            status=PRESET_STATUS_SUCCESS,
            last_result={"result": "success", "message": "Done"},
            last_activated="2024-01-15T10:30:00",
        )

        attrs = button_entity.extra_state_attributes
        assert attrs["last_result"] == "success"
        assert attrs["last_activated"] == "2024-01-15T10:30:00"

    def test_extra_state_attributes_empty_when_preset_deleted(
        self, button_entity, mock_preset_manager
    ):
        """Test extra state attributes are empty when preset is deleted."""
        mock_preset_manager.get_preset.return_value = None
        attrs = button_entity.extra_state_attributes
        assert attrs == {}


class TestPresetButtonPress:
    """Tests for PresetButton press functionality."""

    @pytest.mark.asyncio
    async def test_press_activates_preset(
        self, button_entity, mock_controller, mock_preset_manager, mock_preset
    ):
        """Test that pressing the button activates the preset."""
        await button_entity.async_press()

        mock_preset_manager.activate_preset_with_options.assert_called_once()
        call_args = mock_preset_manager.activate_preset_with_options.call_args[0]
        assert call_args[0] == mock_preset  # preset
        assert call_args[1] == mock_controller  # controller

    @pytest.mark.asyncio
    async def test_press_sets_status_activating(
        self, button_entity, mock_preset_manager
    ):
        """Test that pressing sets status to activating."""
        await button_entity.async_press()

        # First call should be to set activating status
        first_call = mock_preset_manager.set_status.call_args_list[0]
        assert first_call[0][0] == "test_preset_id"
        assert first_call[0][1] == PRESET_STATUS_ACTIVATING

    @pytest.mark.asyncio
    async def test_press_sets_status_success(
        self, button_entity, mock_controller, mock_preset_manager
    ):
        """Test that successful activation sets status to success."""
        mock_preset_manager.activate_preset_with_options.return_value = {
            "success": True,
            "result": "success",
        }

        await button_entity.async_press()

        # Second call should be to set success status
        last_call = mock_preset_manager.set_status.call_args_list[-1]
        assert last_call[0][0] == "test_preset_id"
        assert last_call[0][1] == PRESET_STATUS_SUCCESS

    @pytest.mark.asyncio
    async def test_press_sets_status_failed(
        self, button_entity, mock_controller, mock_preset_manager
    ):
        """Test that failed activation sets status to failed."""
        mock_preset_manager.activate_preset_with_options.return_value = {
            "success": False,
            "result": "failed",
            "message": "Lights unreachable",
        }

        await button_entity.async_press()

        # Second call should be to set failed status
        last_call = mock_preset_manager.set_status.call_args_list[-1]
        assert last_call[0][0] == "test_preset_id"
        assert last_call[0][1] == PRESET_STATUS_FAILED

    @pytest.mark.asyncio
    async def test_press_with_deleted_preset(
        self, button_entity, mock_preset_manager, mock_controller
    ):
        """Test pressing when preset has been deleted."""
        mock_preset_manager.get_preset.return_value = None

        await button_entity.async_press()

        # Should not call ensure_state
        mock_controller.ensure_state.assert_not_called()

    @pytest.mark.asyncio
    async def test_press_uses_preset_rgb_color(
        self, button_entity, mock_preset_manager, mock_preset
    ):
        """Test that preset with RGB color is passed to activate."""
        await button_entity.async_press()

        # Verify the preset with RGB color was passed
        call_args = mock_preset_manager.activate_preset_with_options.call_args[0]
        assert call_args[0].rgb_color == [255, 200, 100]

    @pytest.mark.asyncio
    async def test_press_uses_preset_transition(
        self, button_entity, mock_preset_manager, mock_preset
    ):
        """Test that preset with transition is passed to activate."""
        await button_entity.async_press()

        # Verify the preset with transition was passed
        call_args = mock_preset_manager.activate_preset_with_options.call_args[0]
        assert call_args[0].transition == 1.5

    @pytest.mark.asyncio
    async def test_press_uses_configured_options(
        self, hass, mock_preset_manager, mock_controller, mock_preset
    ):
        """Test that configured options are passed to activate."""
        config_entry = MagicMock()
        config_entry.entry_id = "test_entry"
        config_entry.options = {
            "brightness_tolerance": 10,
            "max_retries": 5,
        }

        button = PresetButton(
            hass=hass,
            entry=config_entry,
            preset_manager=mock_preset_manager,
            controller=mock_controller,
            preset_id="test_preset_id",
            preset=mock_preset,
        )

        await button.async_press()

        # Verify options were passed
        call_args = mock_preset_manager.activate_preset_with_options.call_args[0]
        assert call_args[2] == config_entry.options


class TestPresetButtonLifecycle:
    """Tests for PresetButton lifecycle methods."""

    @pytest.mark.asyncio
    async def test_async_added_to_hass(self, button_entity, mock_preset_manager):
        """Test that button registers listener when added to hass."""
        button_entity.async_on_remove = MagicMock()

        await button_entity.async_added_to_hass()

        mock_preset_manager.register_listener.assert_called()
        button_entity.async_on_remove.assert_called()

    @pytest.mark.asyncio
    async def test_async_will_remove_from_hass(self, button_entity):
        """Test cleanup when removed from hass."""
        # Should not raise any errors
        await button_entity.async_will_remove_from_hass()

    def test_handle_preset_update(self, button_entity, mock_preset_manager):
        """Test handling preset updates."""
        button_entity.async_write_ha_state = MagicMock()

        # Update the preset name
        updated_preset = PresetConfig(
            id="test_preset_id",
            name="Updated Name",
            entities=["light.test"],
        )
        mock_preset_manager.get_preset.return_value = updated_preset

        button_entity._handle_preset_update()

        assert button_entity._preset == updated_preset
        assert button_entity._attr_translation_placeholders == {"name": "Updated Name"}
        button_entity.async_write_ha_state.assert_called_once()

    def test_handle_preset_update_deleted(
        self, button_entity, mock_preset_manager, hass
    ):
        """Test handling when preset is deleted schedules self-removal."""
        button_entity.async_write_ha_state = MagicMock()
        button_entity.async_remove = AsyncMock()
        mock_preset_manager.get_preset.return_value = None

        button_entity._handle_preset_update()

        # Should NOT call write_ha_state when preset is deleted
        button_entity.async_write_ha_state.assert_not_called()
        # Should schedule self-removal via async_create_task
        hass.async_create_task.assert_called_once()
