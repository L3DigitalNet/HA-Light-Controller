"""Tests for the Light Controller sensor platform."""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from unittest.mock import AsyncMock, MagicMock

from custom_components.ha_light_controller.sensor import (
    async_setup_entry,
    PresetStatusSensor,
    STATUS_ICONS,
)
from custom_components.ha_light_controller.preset_manager import (
    PresetConfig,
    PresetStatus,
)
from custom_components.ha_light_controller.const import (
    DOMAIN,
    PRESET_STATUS_IDLE,
    PRESET_STATUS_ACTIVATING,
    PRESET_STATUS_SUCCESS,
    PRESET_STATUS_FAILED,
)


@dataclass
class MockRuntimeData:
    """Mock runtime data for tests."""
    controller: MagicMock = None
    preset_manager: MagicMock = None


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
    )


@pytest.fixture
def mock_preset_manager(mock_preset):
    """Create a mock preset manager."""
    manager = MagicMock()
    manager.presets = {"test_preset_id": mock_preset}
    manager.get_preset = MagicMock(return_value=mock_preset)
    manager.get_status = MagicMock(return_value=PresetStatus())
    manager.register_listener = MagicMock(return_value=MagicMock())
    return manager


@pytest.fixture
def sensor_entity(hass, config_entry, mock_preset_manager, mock_preset):
    """Create a PresetStatusSensor entity."""
    return PresetStatusSensor(
        hass=hass,
        entry=config_entry,
        preset_manager=mock_preset_manager,
        preset_id="test_preset_id",
        preset=mock_preset,
    )


# =============================================================================
# async_setup_entry Tests
# =============================================================================


class TestAsyncSetupEntry:
    """Tests for async_setup_entry."""

    @pytest.mark.asyncio
    async def test_setup_entry_adds_sensors(
        self, hass, config_entry, mock_preset_manager
    ):
        """Test that setup entry adds sensor entities."""
        config_entry.runtime_data = MockRuntimeData(
            preset_manager=mock_preset_manager,
        )

        async_add_entities = MagicMock()
        await async_setup_entry(hass, config_entry, async_add_entities)

        async_add_entities.assert_called_once()
        entities = async_add_entities.call_args[0][0]
        assert len(entities) == 1
        assert isinstance(entities[0], PresetStatusSensor)

    @pytest.mark.asyncio
    async def test_setup_entry_registers_listener(
        self, hass, config_entry, mock_preset_manager
    ):
        """Test that setup entry registers a listener for new presets."""
        config_entry.runtime_data = MockRuntimeData(
            preset_manager=mock_preset_manager,
        )

        async_add_entities = MagicMock()
        await async_setup_entry(hass, config_entry, async_add_entities)

        mock_preset_manager.register_listener.assert_called()
        config_entry.async_on_unload.assert_called()


# =============================================================================
# PresetStatusSensor Tests
# =============================================================================


class TestPresetStatusSensor:
    """Tests for PresetStatusSensor entity."""

    def test_init(self, sensor_entity, mock_preset):
        """Test sensor initialization."""
        assert sensor_entity._preset_id == "test_preset_id"
        assert sensor_entity._preset == mock_preset
        assert sensor_entity._attr_translation_placeholders == {"name": "Test Preset"}
        assert sensor_entity._attr_translation_key == "preset_status"
        assert sensor_entity._attr_icon == STATUS_ICONS[PRESET_STATUS_IDLE]

    def test_unique_id(self, sensor_entity, config_entry):
        """Test unique ID generation."""
        expected_id = f"{config_entry.entry_id}_preset_test_preset_id_status"
        assert sensor_entity._attr_unique_id == expected_id

    def test_has_entity_name(self, sensor_entity):
        """Test has_entity_name flag."""
        assert sensor_entity._attr_has_entity_name is True

    def test_device_info(self, sensor_entity, config_entry):
        """Test device info."""
        device_info = sensor_entity.device_info
        assert (DOMAIN, config_entry.entry_id) in device_info["identifiers"]
        assert device_info["name"] == "Light Controller"


class TestPresetStatusSensorState:
    """Tests for PresetStatusSensor state values."""

    def test_native_value_idle(self, sensor_entity, mock_preset_manager):
        """Test native value when status is idle."""
        mock_preset_manager.get_status.return_value = PresetStatus(
            status=PRESET_STATUS_IDLE
        )
        assert sensor_entity.native_value == PRESET_STATUS_IDLE

    def test_native_value_activating(self, sensor_entity, mock_preset_manager):
        """Test native value when status is activating."""
        mock_preset_manager.get_status.return_value = PresetStatus(
            status=PRESET_STATUS_ACTIVATING
        )
        assert sensor_entity.native_value == PRESET_STATUS_ACTIVATING

    def test_native_value_success(self, sensor_entity, mock_preset_manager):
        """Test native value when status is success."""
        mock_preset_manager.get_status.return_value = PresetStatus(
            status=PRESET_STATUS_SUCCESS
        )
        assert sensor_entity.native_value == PRESET_STATUS_SUCCESS

    def test_native_value_failed(self, sensor_entity, mock_preset_manager):
        """Test native value when status is failed."""
        mock_preset_manager.get_status.return_value = PresetStatus(
            status=PRESET_STATUS_FAILED
        )
        assert sensor_entity.native_value == PRESET_STATUS_FAILED


class TestPresetStatusSensorIcon:
    """Tests for PresetStatusSensor icon property."""

    def test_icon_idle(self, sensor_entity, mock_preset_manager):
        """Test icon for idle status."""
        mock_preset_manager.get_status.return_value = PresetStatus(
            status=PRESET_STATUS_IDLE
        )
        assert sensor_entity.icon == "mdi:lightbulb-outline"

    def test_icon_activating(self, sensor_entity, mock_preset_manager):
        """Test icon for activating status."""
        mock_preset_manager.get_status.return_value = PresetStatus(
            status=PRESET_STATUS_ACTIVATING
        )
        assert sensor_entity.icon == "mdi:lightbulb-on"

    def test_icon_success(self, sensor_entity, mock_preset_manager):
        """Test icon for success status."""
        mock_preset_manager.get_status.return_value = PresetStatus(
            status=PRESET_STATUS_SUCCESS
        )
        assert sensor_entity.icon == "mdi:lightbulb-on-outline"

    def test_icon_failed(self, sensor_entity, mock_preset_manager):
        """Test icon for failed status."""
        mock_preset_manager.get_status.return_value = PresetStatus(
            status=PRESET_STATUS_FAILED
        )
        assert sensor_entity.icon == "mdi:lightbulb-alert"

    def test_icon_unknown_status(self, sensor_entity, mock_preset_manager):
        """Test icon for unknown status falls back to default."""
        mock_preset_manager.get_status.return_value = PresetStatus(
            status="unknown_status"
        )
        assert sensor_entity.icon == "mdi:lightbulb-outline"


class TestPresetStatusSensorAttributes:
    """Tests for PresetStatusSensor extra state attributes."""

    def test_basic_attributes(self, sensor_entity, mock_preset, mock_preset_manager):
        """Test basic extra state attributes."""
        attrs = sensor_entity.extra_state_attributes
        assert attrs["preset_id"] == "test_preset_id"
        assert attrs["preset_name"] == "Test Preset"
        assert attrs["target_state"] == "on"
        assert attrs["entity_count"] == 2

    def test_attributes_with_last_activation(self, sensor_entity, mock_preset_manager):
        """Test attributes include last activation info."""
        mock_preset_manager.get_status.return_value = PresetStatus(
            status=PRESET_STATUS_SUCCESS,
            last_activated="2024-01-15T10:30:00",
            last_result={
                "success": True,
                "message": "All lights set",
                "attempts": 2,
                "elapsed_seconds": 3.5,
            },
        )

        attrs = sensor_entity.extra_state_attributes
        assert attrs["last_activated"] == "2024-01-15T10:30:00"
        assert attrs["last_success"] is True
        assert attrs["last_message"] == "All lights set"
        assert attrs["last_attempts"] == 2
        assert attrs["last_elapsed_seconds"] == 3.5

    def test_attributes_with_failed_lights(self, sensor_entity, mock_preset_manager):
        """Test attributes include failed lights."""
        mock_preset_manager.get_status.return_value = PresetStatus(
            status=PRESET_STATUS_FAILED,
            last_result={
                "success": False,
                "message": "Some lights failed",
                "attempts": 3,
                "elapsed_seconds": 10.0,
                "failed_lights": ["light.test_1"],
                "skipped_lights": ["light.test_2"],
            },
        )

        attrs = sensor_entity.extra_state_attributes
        assert attrs["failed_lights"] == ["light.test_1"]
        assert attrs["skipped_lights"] == ["light.test_2"]

    def test_attributes_no_failed_lights_when_empty(
        self, sensor_entity, mock_preset_manager
    ):
        """Test failed_lights not included when empty."""
        mock_preset_manager.get_status.return_value = PresetStatus(
            status=PRESET_STATUS_SUCCESS,
            last_result={
                "success": True,
                "failed_lights": [],
                "skipped_lights": [],
            },
        )

        attrs = sensor_entity.extra_state_attributes
        assert "failed_lights" not in attrs
        assert "skipped_lights" not in attrs

    def test_attributes_when_preset_deleted(self, sensor_entity, mock_preset_manager):
        """Test attributes when preset no longer exists."""
        mock_preset_manager.get_preset.return_value = None

        attrs = sensor_entity.extra_state_attributes
        assert attrs["preset_id"] == "test_preset_id"
        assert "preset_name" not in attrs


class TestPresetStatusSensorAvailability:
    """Tests for PresetStatusSensor availability."""

    def test_available_when_preset_exists(self, sensor_entity, mock_preset_manager):
        """Test availability when preset exists."""
        assert sensor_entity.available is True

    def test_unavailable_when_preset_deleted(self, sensor_entity, mock_preset_manager):
        """Test availability when preset is deleted."""
        mock_preset_manager.get_preset.return_value = None
        assert sensor_entity.available is False


class TestPresetStatusSensorLifecycle:
    """Tests for PresetStatusSensor lifecycle methods."""

    @pytest.mark.asyncio
    async def test_async_added_to_hass(self, sensor_entity, mock_preset_manager):
        """Test that sensor registers listener when added to hass."""
        sensor_entity.async_on_remove = MagicMock()

        await sensor_entity.async_added_to_hass()

        mock_preset_manager.register_listener.assert_called()
        sensor_entity.async_on_remove.assert_called()

    @pytest.mark.asyncio
    async def test_async_will_remove_from_hass(self, sensor_entity):
        """Test cleanup when removed from hass."""
        # Should not raise any errors
        await sensor_entity.async_will_remove_from_hass()

    def test_handle_preset_update(self, sensor_entity, mock_preset_manager):
        """Test handling preset updates."""
        sensor_entity.async_write_ha_state = MagicMock()

        # Update the preset name
        updated_preset = PresetConfig(
            id="test_preset_id",
            name="Updated Name",
            entities=["light.test"],
        )
        mock_preset_manager.get_preset.return_value = updated_preset

        sensor_entity._handle_preset_update()

        assert sensor_entity._preset == updated_preset
        assert sensor_entity._attr_translation_placeholders == {"name": "Updated Name"}
        sensor_entity.async_write_ha_state.assert_called_once()

    def test_handle_preset_update_deleted(self, sensor_entity, mock_preset_manager):
        """Test handling when preset is deleted."""
        sensor_entity.async_write_ha_state = MagicMock()
        mock_preset_manager.get_preset.return_value = None

        sensor_entity._handle_preset_update()

        # Should still call write_ha_state even if preset deleted
        sensor_entity.async_write_ha_state.assert_called_once()


class TestStatusIcons:
    """Tests for STATUS_ICONS mapping."""

    def test_all_statuses_have_icons(self):
        """Test that all status values have icons."""
        assert PRESET_STATUS_IDLE in STATUS_ICONS
        assert PRESET_STATUS_ACTIVATING in STATUS_ICONS
        assert PRESET_STATUS_SUCCESS in STATUS_ICONS
        assert PRESET_STATUS_FAILED in STATUS_ICONS

    def test_icons_are_valid_mdi(self):
        """Test that all icons are valid mdi icons."""
        for icon in STATUS_ICONS.values():
            assert icon.startswith("mdi:")
