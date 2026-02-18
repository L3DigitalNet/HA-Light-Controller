"""Tests for the Light Controller integration setup."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import ServiceCall
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError

from custom_components.ha_light_controller import (
    _get_optional_str,
    async_reload_entry,
    async_setup,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.ha_light_controller.const import (
    ATTR_DEFAULT_BRIGHTNESS_PCT,
    ATTR_ENTITIES,
    ATTR_PRESET,
    ATTR_PRESET_ID,
    ATTR_PRESET_NAME,
    ATTR_STATE_TARGET,
    SERVICE_ACTIVATE_PRESET,
    SERVICE_CREATE_PRESET,
    SERVICE_CREATE_PRESET_FROM_CURRENT,
    SERVICE_DELETE_PRESET,
    SERVICE_ENSURE_STATE,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_controller():
    """Create a mock controller."""
    controller = MagicMock()
    controller.ensure_state = AsyncMock(
        return_value={"success": True, "result": "success", "message": "Done"}
    )
    return controller


@pytest.fixture
def mock_preset_manager():
    """Create a mock preset manager."""

    manager = MagicMock()
    manager.presets = {}
    manager.get_preset = MagicMock(return_value=None)
    manager.get_preset_by_name = MagicMock(return_value=None)
    manager.find_preset = MagicMock(return_value=None)
    manager.set_status = AsyncMock()
    manager.create_preset = AsyncMock()
    manager.delete_preset = AsyncMock()
    manager.create_preset_from_current = AsyncMock()
    manager.activate_preset_with_options = AsyncMock(
        return_value={"success": True, "result": "success", "message": "Done"}
    )
    return manager


@pytest.fixture
def service_call():
    """Create a mock service call."""
    call = MagicMock(spec=ServiceCall)
    call.data = {}
    return call


# =============================================================================
# async_setup_entry Tests
# =============================================================================


class TestAsyncSetupEntry:
    """Tests for async_setup_entry."""

    @pytest.mark.asyncio
    async def test_setup_entry_creates_data(self, hass, config_entry):
        """Test that setup entry creates runtime_data."""
        with (
            patch("custom_components.ha_light_controller.LightController") as mock_lc,
            patch("custom_components.ha_light_controller.PresetManager") as mock_pm,
        ):
            mock_lc.return_value = MagicMock()
            mock_pm.return_value = MagicMock()

            # Mock async_forward_entry_setups
            hass.config_entries.async_forward_entry_setups = AsyncMock()

            result = await async_setup_entry(hass, config_entry)

            assert result is True
            assert config_entry.runtime_data is not None
            assert config_entry.runtime_data.controller is not None
            assert config_entry.runtime_data.preset_manager is not None

    @pytest.mark.asyncio
    async def test_setup_entry_does_not_register_services(self, hass, config_entry):
        """Test that setup entry does not register services (they're in async_setup)."""
        with (
            patch("custom_components.ha_light_controller.LightController"),
            patch("custom_components.ha_light_controller.PresetManager"),
        ):
            hass.config_entries.async_forward_entry_setups = AsyncMock()
            hass.services.async_register.reset_mock()

            await async_setup_entry(hass, config_entry)

            # Services should NOT be registered in async_setup_entry
            assert hass.services.async_register.call_count == 0


class TestAsyncSetup:
    """Tests for async_setup (service registration)."""

    @pytest.mark.asyncio
    async def test_setup_registers_services(self, hass):
        """Test that async_setup registers services."""
        hass.services.async_register.reset_mock()

        result = await async_setup(hass, {})

        assert result is True

        # Check services were registered
        assert hass.services.async_register.call_count == 5

        # Verify service names
        registered_services = [
            call[0][1] for call in hass.services.async_register.call_args_list
        ]
        assert SERVICE_ENSURE_STATE in registered_services
        assert SERVICE_ACTIVATE_PRESET in registered_services
        assert SERVICE_CREATE_PRESET in registered_services
        assert SERVICE_DELETE_PRESET in registered_services
        assert SERVICE_CREATE_PRESET_FROM_CURRENT in registered_services

    @pytest.mark.asyncio
    async def test_setup_entry_forwards_platforms(self, hass, config_entry):
        """Test that setup entry forwards platform setup."""
        with (
            patch("custom_components.ha_light_controller.LightController"),
            patch("custom_components.ha_light_controller.PresetManager"),
        ):
            hass.config_entries.async_forward_entry_setups = AsyncMock()

            await async_setup_entry(hass, config_entry)

            hass.config_entries.async_forward_entry_setups.assert_called_once()
            platforms = hass.config_entries.async_forward_entry_setups.call_args[0][1]
            assert "button" in platforms
            assert "sensor" in platforms


# =============================================================================
# async_unload_entry Tests
# =============================================================================


class TestAsyncUnloadEntry:
    """Tests for async_unload_entry."""

    @pytest.mark.asyncio
    async def test_unload_entry_unloads_platforms(self, hass, config_entry):
        """Test that unload entry unloads platforms."""
        hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

        result = await async_unload_entry(hass, config_entry)

        assert result is True
        hass.config_entries.async_unload_platforms.assert_called_once()

    @pytest.mark.asyncio
    async def test_unload_entry_returns_platform_result(self, hass, config_entry):
        """Test that unload entry returns platform unload result."""
        hass.config_entries.async_unload_platforms = AsyncMock(return_value=False)

        result = await async_unload_entry(hass, config_entry)

        assert result is False


# =============================================================================
# async_reload_entry Tests
# =============================================================================


class TestAsyncReloadEntry:
    """Tests for async_reload_entry."""

    @pytest.mark.asyncio
    async def test_reload_entry(self, hass, config_entry):
        """Test that reload entry triggers reload."""
        hass.config_entries.async_reload = AsyncMock()

        await async_reload_entry(hass, config_entry)

        hass.config_entries.async_reload.assert_called_once_with(config_entry.entry_id)


# =============================================================================
# Service Handler Tests
# =============================================================================


def _get_service_handler(hass, service_name):
    """Extract service handler from mock registrations."""
    for call in hass.services.async_register.call_args_list:
        if call[0][1] == service_name:
            return call[0][2]
    return None


async def _setup_services_with_entry(
    hass, config_entry, mock_controller, mock_preset_manager
):
    """Set up services and config entry for testing."""
    # Reset service registration mock
    hass.services.async_register.reset_mock()

    # Register services via async_setup
    await async_setup(hass, {})

    # Set up config entry with runtime_data
    with (
        patch(
            "custom_components.ha_light_controller.LightController",
            return_value=mock_controller,
        ),
        patch(
            "custom_components.ha_light_controller.PresetManager",
            return_value=mock_preset_manager,
        ),
    ):
        hass.config_entries.async_forward_entry_setups = AsyncMock()
        await async_setup_entry(hass, config_entry)

    # Mock async_entries to return this config entry when looking up DOMAIN
    hass.config_entries.async_entries = MagicMock(return_value=[config_entry])


class TestEnsureStateService:
    """Tests for ensure_state service handler."""

    @pytest.mark.asyncio
    async def test_ensure_state_service_calls_controller(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test ensure_state service calls controller."""
        await _setup_services_with_entry(
            hass, config_entry, mock_controller, mock_preset_manager
        )

        # Get the service handler
        ensure_state_handler = _get_service_handler(hass, SERVICE_ENSURE_STATE)
        assert ensure_state_handler is not None

        # Create a service call
        call = MagicMock(spec=ServiceCall)
        call.data = {
            ATTR_ENTITIES: ["light.test"],
            ATTR_STATE_TARGET: "on",
            ATTR_DEFAULT_BRIGHTNESS_PCT: 80,
        }

        result = await ensure_state_handler(call)

        mock_controller.ensure_state.assert_called()
        assert result["success"] is True


class TestActivatePresetService:
    """Tests for activate_preset service handler."""

    @pytest.mark.asyncio
    async def test_activate_preset_not_found(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test activate_preset raises ServiceValidationError when preset not found."""
        await _setup_services_with_entry(
            hass, config_entry, mock_controller, mock_preset_manager
        )

        activate_handler = _get_service_handler(hass, SERVICE_ACTIVATE_PRESET)

        call = MagicMock(spec=ServiceCall)
        call.data = {ATTR_PRESET: "nonexistent"}

        with pytest.raises(ServiceValidationError, match="not found"):
            await activate_handler(call)


class TestCreatePresetService:
    """Tests for create_preset service handler."""

    @pytest.mark.asyncio
    async def test_create_preset_missing_name(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test create_preset raises ServiceValidationError when name missing."""
        await _setup_services_with_entry(
            hass, config_entry, mock_controller, mock_preset_manager
        )

        create_handler = _get_service_handler(hass, SERVICE_CREATE_PRESET)

        call = MagicMock(spec=ServiceCall)
        call.data = {
            ATTR_PRESET_NAME: "",
            ATTR_ENTITIES: ["light.test"],
        }

        with pytest.raises(ServiceValidationError, match="required"):
            await create_handler(call)


class TestDeletePresetService:
    """Tests for delete_preset service handler."""

    @pytest.mark.asyncio
    async def test_delete_preset_missing_id(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test delete_preset raises ServiceValidationError when ID missing."""
        await _setup_services_with_entry(
            hass, config_entry, mock_controller, mock_preset_manager
        )

        delete_handler = _get_service_handler(hass, SERVICE_DELETE_PRESET)

        call = MagicMock(spec=ServiceCall)
        call.data = {ATTR_PRESET_ID: ""}

        with pytest.raises(ServiceValidationError, match="required"):
            await delete_handler(call)

    @pytest.mark.asyncio
    async def test_delete_preset_not_found(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test delete_preset raises ServiceValidationError when preset not found."""
        mock_preset_manager.delete_preset.return_value = False
        await _setup_services_with_entry(
            hass, config_entry, mock_controller, mock_preset_manager
        )

        delete_handler = _get_service_handler(hass, SERVICE_DELETE_PRESET)

        call = MagicMock(spec=ServiceCall)
        call.data = {ATTR_PRESET_ID: "nonexistent_id"}

        with pytest.raises(ServiceValidationError, match="not found"):
            await delete_handler(call)


class TestCreatePresetFromCurrentService:
    """Tests for create_preset_from_current service handler."""

    @pytest.mark.asyncio
    async def test_create_from_current_missing_name(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test create_preset_from_current raises when name missing."""
        await _setup_services_with_entry(
            hass, config_entry, mock_controller, mock_preset_manager
        )

        create_handler = _get_service_handler(hass, SERVICE_CREATE_PRESET_FROM_CURRENT)

        call = MagicMock(spec=ServiceCall)
        call.data = {
            ATTR_PRESET_NAME: "",
            ATTR_ENTITIES: ["light.test"],
        }

        with pytest.raises(ServiceValidationError, match="required"):
            await create_handler(call)

    @pytest.mark.asyncio
    async def test_create_from_current_missing_entities(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test create_preset_from_current raises when entities missing."""
        await _setup_services_with_entry(
            hass, config_entry, mock_controller, mock_preset_manager
        )

        create_handler = _get_service_handler(hass, SERVICE_CREATE_PRESET_FROM_CURRENT)

        call = MagicMock(spec=ServiceCall)
        call.data = {
            ATTR_PRESET_NAME: "Test",
            ATTR_ENTITIES: [],
        }

        with pytest.raises(ServiceValidationError, match="required"):
            await create_handler(call)


# =============================================================================
# Additional Service Handler Tests for Coverage
# =============================================================================


class TestEnsureStateServiceAdvanced:
    """Advanced tests for ensure_state service handler."""

    @pytest.mark.asyncio
    async def test_ensure_state_exception_handling(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test ensure_state raises HomeAssistantError on unexpected exception."""
        mock_controller.ensure_state = AsyncMock(
            side_effect=Exception("Controller error")
        )
        await _setup_services_with_entry(
            hass, config_entry, mock_controller, mock_preset_manager
        )

        ensure_state_handler = _get_service_handler(hass, SERVICE_ENSURE_STATE)

        call = MagicMock(spec=ServiceCall)
        call.data = {
            ATTR_ENTITIES: ["light.test"],
            ATTR_STATE_TARGET: "on",
        }

        with pytest.raises(HomeAssistantError, match="ensure_state"):
            await ensure_state_handler(call)


class TestActivatePresetServiceAdvanced:
    """Advanced tests for activate_preset service handler."""

    @pytest.mark.asyncio
    async def test_activate_preset_success(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test activate_preset success path."""
        from custom_components.ha_light_controller.preset_manager import PresetConfig

        # Create a mock preset
        preset = PresetConfig(
            id="test_preset",
            name="Test Preset",
            entities=["light.test"],
            brightness_pct=75,
        )
        mock_preset_manager.find_preset.return_value = preset
        await _setup_services_with_entry(
            hass, config_entry, mock_controller, mock_preset_manager
        )

        # Get the service handler
        activate_handler = _get_service_handler(hass, SERVICE_ACTIVATE_PRESET)

        call = MagicMock(spec=ServiceCall)
        call.data = {ATTR_PRESET: "test_preset"}

        result = await activate_handler(call)

        assert result["success"] is True
        mock_preset_manager.activate_preset_with_options.assert_called()
        # Verify status was set
        assert mock_preset_manager.set_status.call_count >= 2  # activating + success

    @pytest.mark.asyncio
    async def test_activate_preset_by_name(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test activate_preset finds preset by name."""
        from custom_components.ha_light_controller.preset_manager import PresetConfig

        preset = PresetConfig(
            id="test_preset",
            name="My Preset",
            entities=["light.test"],
        )
        # find_preset handles both ID and name lookup
        mock_preset_manager.find_preset.return_value = preset
        await _setup_services_with_entry(
            hass, config_entry, mock_controller, mock_preset_manager
        )

        activate_handler = _get_service_handler(hass, SERVICE_ACTIVATE_PRESET)

        call = MagicMock(spec=ServiceCall)
        call.data = {ATTR_PRESET: "My Preset"}

        result = await activate_handler(call)

        assert result["success"] is True
        mock_preset_manager.find_preset.assert_called_with("My Preset")

    @pytest.mark.asyncio
    async def test_activate_preset_exception(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test activate_preset raises HomeAssistantError on unexpected exception."""
        from custom_components.ha_light_controller.preset_manager import PresetConfig

        preset = PresetConfig(
            id="test_preset",
            name="Test Preset",
            entities=["light.test"],
        )
        mock_preset_manager.find_preset.return_value = preset
        mock_preset_manager.activate_preset_with_options = AsyncMock(
            side_effect=Exception("Controller error")
        )
        await _setup_services_with_entry(
            hass, config_entry, mock_controller, mock_preset_manager
        )

        activate_handler = _get_service_handler(hass, SERVICE_ACTIVATE_PRESET)

        call = MagicMock(spec=ServiceCall)
        call.data = {ATTR_PRESET: "test_preset"}

        with pytest.raises(HomeAssistantError, match="Error activating preset"):
            await activate_handler(call)


class TestCreatePresetServiceAdvanced:
    """Advanced tests for create_preset service handler."""

    @pytest.mark.asyncio
    async def test_create_preset_success(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test create_preset success path."""
        from custom_components.ha_light_controller.preset_manager import PresetConfig

        created_preset = PresetConfig(
            id="new_preset_id",
            name="New Preset",
            entities=["light.test"],
        )
        mock_preset_manager.create_preset = AsyncMock(return_value=created_preset)
        await _setup_services_with_entry(
            hass, config_entry, mock_controller, mock_preset_manager
        )

        create_handler = _get_service_handler(hass, SERVICE_CREATE_PRESET)

        call = MagicMock(spec=ServiceCall)
        call.data = {
            ATTR_PRESET_NAME: "New Preset",
            ATTR_ENTITIES: ["light.test"],
        }

        result = await create_handler(call)

        assert result["success"] is True
        assert result["result"] == "success"
        assert result["preset_id"] == "new_preset_id"
        assert result["preset_name"] == "New Preset"

    @pytest.mark.asyncio
    async def test_create_preset_exception(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test create_preset raises HomeAssistantError on unexpected exception."""
        mock_preset_manager.create_preset = AsyncMock(side_effect=Exception("DB error"))
        await _setup_services_with_entry(
            hass, config_entry, mock_controller, mock_preset_manager
        )

        create_handler = _get_service_handler(hass, SERVICE_CREATE_PRESET)

        call = MagicMock(spec=ServiceCall)
        call.data = {
            ATTR_PRESET_NAME: "New Preset",
            ATTR_ENTITIES: ["light.test"],
        }

        with pytest.raises(HomeAssistantError, match="Error creating preset"):
            await create_handler(call)

    @pytest.mark.asyncio
    async def test_create_preset_success_includes_standard_result_fields(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test create_preset returns standardized response fields."""
        from custom_components.ha_light_controller.preset_manager import PresetConfig

        created_preset = PresetConfig(
            id="new_preset_id",
            name="New Preset",
            entities=["light.test"],
        )
        mock_preset_manager.create_preset = AsyncMock(return_value=created_preset)
        await _setup_services_with_entry(
            hass, config_entry, mock_controller, mock_preset_manager
        )

        create_handler = _get_service_handler(hass, SERVICE_CREATE_PRESET)
        call = MagicMock(spec=ServiceCall)
        call.data = {
            ATTR_PRESET_NAME: "New Preset",
            ATTR_ENTITIES: ["light.test"],
        }

        result = await create_handler(call)

        assert result["success"] is True
        assert result["result"] == "success"
        assert result["attempts"] == 0
        assert result["total_lights"] == 0
        assert result["failed_lights"] == []
        assert result["skipped_lights"] == []
        assert result["elapsed_seconds"] == 0.0


class TestDeletePresetServiceAdvanced:
    """Advanced tests for delete_preset service handler."""

    @pytest.mark.asyncio
    async def test_delete_preset_success(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test delete_preset success path."""
        mock_preset_manager.delete_preset = AsyncMock(return_value=True)
        await _setup_services_with_entry(
            hass, config_entry, mock_controller, mock_preset_manager
        )

        delete_handler = _get_service_handler(hass, SERVICE_DELETE_PRESET)

        call = MagicMock(spec=ServiceCall)
        call.data = {ATTR_PRESET_ID: "preset_to_delete"}

        result = await delete_handler(call)

        assert result["success"] is True
        assert result["result"] == "success"
        assert result["preset_id"] == "preset_to_delete"

    @pytest.mark.asyncio
    async def test_delete_preset_exception(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test delete_preset raises HomeAssistantError on unexpected exception."""
        mock_preset_manager.delete_preset = AsyncMock(side_effect=Exception("DB error"))
        await _setup_services_with_entry(
            hass, config_entry, mock_controller, mock_preset_manager
        )

        delete_handler = _get_service_handler(hass, SERVICE_DELETE_PRESET)

        call = MagicMock(spec=ServiceCall)
        call.data = {ATTR_PRESET_ID: "preset_id"}

        with pytest.raises(HomeAssistantError, match="Error deleting preset"):
            await delete_handler(call)

    @pytest.mark.asyncio
    async def test_delete_preset_not_found_raises(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test delete_preset raises ServiceValidationError when not found."""
        mock_preset_manager.delete_preset = AsyncMock(return_value=False)
        await _setup_services_with_entry(
            hass, config_entry, mock_controller, mock_preset_manager
        )

        delete_handler = _get_service_handler(hass, SERVICE_DELETE_PRESET)
        call = MagicMock(spec=ServiceCall)
        call.data = {ATTR_PRESET_ID: "unknown"}

        with pytest.raises(ServiceValidationError, match="not found"):
            await delete_handler(call)


class TestCreatePresetFromCurrentServiceAdvanced:
    """Advanced tests for create_preset_from_current service handler."""

    @pytest.mark.asyncio
    async def test_create_from_current_success(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test create_preset_from_current success path."""
        from custom_components.ha_light_controller.preset_manager import PresetConfig

        created_preset = PresetConfig(
            id="from_current_id",
            name="From Current",
            entities=["light.test"],
            targets=[{"entity_id": "light.test", "brightness_pct": 80}],
        )
        mock_preset_manager.create_preset_from_current = AsyncMock(
            return_value=created_preset
        )
        await _setup_services_with_entry(
            hass, config_entry, mock_controller, mock_preset_manager
        )

        create_handler = _get_service_handler(hass, SERVICE_CREATE_PRESET_FROM_CURRENT)

        call = MagicMock(spec=ServiceCall)
        call.data = {
            ATTR_PRESET_NAME: "From Current",
            ATTR_ENTITIES: ["light.test"],
        }

        result = await create_handler(call)

        assert result["success"] is True
        assert result["result"] == "success"
        assert result["preset_id"] == "from_current_id"
        assert result["preset_name"] == "From Current"

    @pytest.mark.asyncio
    async def test_create_from_current_returns_none(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test create_preset_from_current raises when preset_manager returns None."""
        mock_preset_manager.create_preset_from_current = AsyncMock(return_value=None)
        await _setup_services_with_entry(
            hass, config_entry, mock_controller, mock_preset_manager
        )

        create_handler = _get_service_handler(hass, SERVICE_CREATE_PRESET_FROM_CURRENT)

        call = MagicMock(spec=ServiceCall)
        call.data = {
            ATTR_PRESET_NAME: "Test",
            ATTR_ENTITIES: ["light.test"],
        }

        with pytest.raises(HomeAssistantError, match="Failed to create preset"):
            await create_handler(call)

    @pytest.mark.asyncio
    async def test_create_from_current_exception(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test create_preset_from_current raises on unexpected exception."""
        mock_preset_manager.create_preset_from_current = AsyncMock(
            side_effect=Exception("State read error")
        )
        await _setup_services_with_entry(
            hass, config_entry, mock_controller, mock_preset_manager
        )

        create_handler = _get_service_handler(hass, SERVICE_CREATE_PRESET_FROM_CURRENT)

        call = MagicMock(spec=ServiceCall)
        call.data = {
            ATTR_PRESET_NAME: "Test",
            ATTR_ENTITIES: ["light.test"],
        }

        with pytest.raises(HomeAssistantError, match="Error creating preset"):
            await create_handler(call)


# =============================================================================
# Service Handler Edge Cases (Coverage for __init__.py gaps)
# =============================================================================


class TestServiceHandlerEdgeCases:
    """Tests for service handler edge cases to achieve full coverage."""

    @pytest.mark.asyncio
    async def test_ensure_state_no_entries(self, hass):
        """Test ensure_state raises when no config entries exist."""
        await async_setup(hass, {})

        hass.config_entries.async_entries = MagicMock(return_value=[])

        ensure_state_handler = _get_service_handler(hass, SERVICE_ENSURE_STATE)

        call = MagicMock(spec=ServiceCall)
        call.data = {
            ATTR_ENTITIES: ["light.test"],
            ATTR_STATE_TARGET: "on",
        }

        with pytest.raises(
            ServiceValidationError, match="not configured or not loaded"
        ):
            await ensure_state_handler(call)

    @pytest.mark.asyncio
    async def test_ensure_state_no_loaded_entries(self, hass, config_entry):
        """Test ensure_state raises when config entries exist but none are loaded."""
        await async_setup(hass, {})

        config_entry.state = "not_loaded"
        hass.config_entries.async_entries = MagicMock(return_value=[config_entry])

        ensure_state_handler = _get_service_handler(hass, SERVICE_ENSURE_STATE)

        call = MagicMock(spec=ServiceCall)
        call.data = {
            ATTR_ENTITIES: ["light.test"],
            ATTR_STATE_TARGET: "on",
        }

        with pytest.raises(
            ServiceValidationError, match="not configured or not loaded"
        ):
            await ensure_state_handler(call)

    @pytest.mark.asyncio
    async def test_ensure_state_runtime_data_none(self, hass, config_entry):
        """Test ensure_state raises when runtime_data is None."""
        await async_setup(hass, {})

        config_entry.state = "loaded"
        config_entry.runtime_data = None
        hass.config_entries.async_entries = MagicMock(return_value=[config_entry])

        ensure_state_handler = _get_service_handler(hass, SERVICE_ENSURE_STATE)

        call = MagicMock(spec=ServiceCall)
        call.data = {
            ATTR_ENTITIES: ["light.test"],
            ATTR_STATE_TARGET: "on",
        }

        with pytest.raises(
            ServiceValidationError, match="not configured or not loaded"
        ):
            await ensure_state_handler(call)

    @pytest.mark.asyncio
    async def test_activate_preset_runtime_data_none(self, hass, config_entry):
        """Test activate_preset raises when runtime_data is None."""
        await async_setup(hass, {})

        config_entry.state = "loaded"
        config_entry.runtime_data = None
        hass.config_entries.async_entries = MagicMock(return_value=[config_entry])

        activate_handler = _get_service_handler(hass, SERVICE_ACTIVATE_PRESET)

        call = MagicMock(spec=ServiceCall)
        call.data = {ATTR_PRESET: "test_preset"}

        with pytest.raises(
            ServiceValidationError, match="not configured or not loaded"
        ):
            await activate_handler(call)

    @pytest.mark.asyncio
    async def test_create_preset_runtime_data_none(self, hass, config_entry):
        """Test create_preset raises when runtime_data is None."""
        await async_setup(hass, {})

        config_entry.state = "loaded"
        config_entry.runtime_data = None
        hass.config_entries.async_entries = MagicMock(return_value=[config_entry])

        create_handler = _get_service_handler(hass, SERVICE_CREATE_PRESET)

        call = MagicMock(spec=ServiceCall)
        call.data = {
            ATTR_PRESET_NAME: "Test Preset",
            ATTR_ENTITIES: ["light.test"],
        }

        with pytest.raises(
            ServiceValidationError, match="not configured or not loaded"
        ):
            await create_handler(call)

    @pytest.mark.asyncio
    async def test_delete_preset_runtime_data_none(self, hass, config_entry):
        """Test delete_preset raises when runtime_data is None."""
        await async_setup(hass, {})

        config_entry.state = "loaded"
        config_entry.runtime_data = None
        hass.config_entries.async_entries = MagicMock(return_value=[config_entry])

        delete_handler = _get_service_handler(hass, SERVICE_DELETE_PRESET)

        call = MagicMock(spec=ServiceCall)
        call.data = {ATTR_PRESET_ID: "test_id"}

        with pytest.raises(
            ServiceValidationError, match="not configured or not loaded"
        ):
            await delete_handler(call)

    @pytest.mark.asyncio
    async def test_create_preset_from_current_runtime_data_none(
        self, hass, config_entry
    ):
        """Test create_preset_from_current raises when runtime_data is None."""
        await async_setup(hass, {})

        config_entry.state = "loaded"
        config_entry.runtime_data = None
        hass.config_entries.async_entries = MagicMock(return_value=[config_entry])

        create_handler = _get_service_handler(hass, SERVICE_CREATE_PRESET_FROM_CURRENT)

        call = MagicMock(spec=ServiceCall)
        call.data = {
            ATTR_PRESET_NAME: "From Current",
            ATTR_ENTITIES: ["light.test"],
        }

        with pytest.raises(
            ServiceValidationError, match="not configured or not loaded"
        ):
            await create_handler(call)

    def test_get_optional_str_empty_strings(self):
        """Test _get_optional_str with empty string handling."""
        # Test empty string in call_data
        result = _get_optional_str(
            call_data={"effect": ""},
            options={},
            attr="effect",
            conf="default_effect",
        )
        assert result is None

        # Test empty string in options
        result = _get_optional_str(
            call_data={},
            options={"default_effect": ""},
            attr="effect",
            conf="default_effect",
        )
        assert result is None

        # Test both empty strings
        result = _get_optional_str(
            call_data={"effect": ""},
            options={"default_effect": ""},
            attr="effect",
            conf="default_effect",
        )
        assert result is None

        # Test valid string value in call_data
        result = _get_optional_str(
            call_data={"effect": "strobe"},
            options={},
            attr="effect",
            conf="default_effect",
        )
        assert result == "strobe"

        # Test valid string value in options
        result = _get_optional_str(
            call_data={},
            options={"default_effect": "rainbow"},
            attr="effect",
            conf="default_effect",
        )
        assert result == "rainbow"

        # Test call_data takes precedence over options
        result = _get_optional_str(
            call_data={"effect": "strobe"},
            options={"default_effect": "rainbow"},
            attr="effect",
            conf="default_effect",
        )
        assert result == "strobe"

        # Test empty call_data falls back to options
        result = _get_optional_str(
            call_data={"effect": ""},
            options={"default_effect": "rainbow"},
            attr="effect",
            conf="default_effect",
        )
        assert result == "rainbow"
