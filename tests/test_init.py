"""Tests for the Light Controller integration setup."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.core import ServiceCall

from custom_components.ha_light_controller import (
    async_setup_entry,
    async_unload_entry,
    async_reload_entry,
)
from custom_components.ha_light_controller.const import (
    DOMAIN,
    SERVICE_ENSURE_STATE,
    SERVICE_ACTIVATE_PRESET,
    SERVICE_CREATE_PRESET,
    SERVICE_DELETE_PRESET,
    SERVICE_CREATE_PRESET_FROM_CURRENT,
    CONF_PRESETS,
    ATTR_ENTITIES,
    ATTR_STATE_TARGET,
    ATTR_DEFAULT_BRIGHTNESS_PCT,
    ATTR_PRESET,
    ATTR_PRESET_NAME,
    ATTR_PRESET_ID,
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
    from custom_components.ha_light_controller.preset_manager import PresetConfig

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
        with patch(
            "custom_components.ha_light_controller.LightController"
        ) as mock_lc, patch(
            "custom_components.ha_light_controller.PresetManager"
        ) as mock_pm:
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
    async def test_setup_entry_registers_services(self, hass, config_entry):
        """Test that setup entry registers services."""
        with patch(
            "custom_components.ha_light_controller.LightController"
        ), patch(
            "custom_components.ha_light_controller.PresetManager"
        ):
            hass.config_entries.async_forward_entry_setups = AsyncMock()

            await async_setup_entry(hass, config_entry)

            # Check services were registered
            assert hass.services.async_register.call_count >= 5

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
        with patch(
            "custom_components.ha_light_controller.LightController"
        ), patch(
            "custom_components.ha_light_controller.PresetManager"
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


class TestEnsureStateService:
    """Tests for ensure_state service handler."""

    @pytest.mark.asyncio
    async def test_ensure_state_service_calls_controller(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test ensure_state service calls controller."""
        # Set up the integration using patched classes
        with patch(
            "custom_components.ha_light_controller.LightController",
            return_value=mock_controller,
        ), patch(
            "custom_components.ha_light_controller.PresetManager",
            return_value=mock_preset_manager,
        ):
            hass.config_entries.async_forward_entry_setups = AsyncMock()
            await async_setup_entry(hass, config_entry)

        # Get the service handler
        ensure_state_handler = None
        for call in hass.services.async_register.call_args_list:
            if call[0][1] == SERVICE_ENSURE_STATE:
                ensure_state_handler = call[0][2]
                break

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
        """Test activate_preset returns error when preset not found."""
        with patch(
            "custom_components.ha_light_controller.LightController",
            return_value=mock_controller,
        ), patch(
            "custom_components.ha_light_controller.PresetManager",
            return_value=mock_preset_manager,
        ):
            hass.config_entries.async_forward_entry_setups = AsyncMock()
            await async_setup_entry(hass, config_entry)

        # Get the service handler
        activate_handler = None
        for call in hass.services.async_register.call_args_list:
            if call[0][1] == SERVICE_ACTIVATE_PRESET:
                activate_handler = call[0][2]
                break

        call = MagicMock(spec=ServiceCall)
        call.data = {ATTR_PRESET: "nonexistent"}

        result = await activate_handler(call)

        assert result["success"] is False
        assert "not found" in result["message"]


class TestCreatePresetService:
    """Tests for create_preset service handler."""

    @pytest.mark.asyncio
    async def test_create_preset_missing_name(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test create_preset returns error when name missing."""
        with patch(
            "custom_components.ha_light_controller.LightController",
            return_value=mock_controller,
        ), patch(
            "custom_components.ha_light_controller.PresetManager",
            return_value=mock_preset_manager,
        ):
            hass.config_entries.async_forward_entry_setups = AsyncMock()
            await async_setup_entry(hass, config_entry)

        # Get the service handler
        create_handler = None
        for call in hass.services.async_register.call_args_list:
            if call[0][1] == SERVICE_CREATE_PRESET:
                create_handler = call[0][2]
                break

        call = MagicMock(spec=ServiceCall)
        call.data = {
            ATTR_PRESET_NAME: "",
            ATTR_ENTITIES: ["light.test"],
        }

        result = await create_handler(call)

        assert result["success"] is False
        assert "required" in result["message"]


class TestDeletePresetService:
    """Tests for delete_preset service handler."""

    @pytest.mark.asyncio
    async def test_delete_preset_missing_id(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test delete_preset returns error when ID missing."""
        with patch(
            "custom_components.ha_light_controller.LightController",
            return_value=mock_controller,
        ), patch(
            "custom_components.ha_light_controller.PresetManager",
            return_value=mock_preset_manager,
        ):
            hass.config_entries.async_forward_entry_setups = AsyncMock()
            await async_setup_entry(hass, config_entry)

        # Get the service handler
        delete_handler = None
        for call in hass.services.async_register.call_args_list:
            if call[0][1] == SERVICE_DELETE_PRESET:
                delete_handler = call[0][2]
                break

        call = MagicMock(spec=ServiceCall)
        call.data = {ATTR_PRESET_ID: ""}

        result = await delete_handler(call)

        assert result["success"] is False
        assert "required" in result["message"]

    @pytest.mark.asyncio
    async def test_delete_preset_not_found(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test delete_preset returns error when preset not found."""
        mock_preset_manager.delete_preset.return_value = False

        with patch(
            "custom_components.ha_light_controller.LightController",
            return_value=mock_controller,
        ), patch(
            "custom_components.ha_light_controller.PresetManager",
            return_value=mock_preset_manager,
        ):
            hass.config_entries.async_forward_entry_setups = AsyncMock()
            await async_setup_entry(hass, config_entry)

        # Get the service handler
        delete_handler = None
        for call in hass.services.async_register.call_args_list:
            if call[0][1] == SERVICE_DELETE_PRESET:
                delete_handler = call[0][2]
                break

        call = MagicMock(spec=ServiceCall)
        call.data = {ATTR_PRESET_ID: "nonexistent_id"}

        result = await delete_handler(call)

        assert result["success"] is False
        assert "not found" in result["message"]


class TestCreatePresetFromCurrentService:
    """Tests for create_preset_from_current service handler."""

    @pytest.mark.asyncio
    async def test_create_from_current_missing_name(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test create_preset_from_current returns error when name missing."""
        with patch(
            "custom_components.ha_light_controller.LightController",
            return_value=mock_controller,
        ), patch(
            "custom_components.ha_light_controller.PresetManager",
            return_value=mock_preset_manager,
        ):
            hass.config_entries.async_forward_entry_setups = AsyncMock()
            await async_setup_entry(hass, config_entry)

        # Get the service handler
        create_handler = None
        for call in hass.services.async_register.call_args_list:
            if call[0][1] == SERVICE_CREATE_PRESET_FROM_CURRENT:
                create_handler = call[0][2]
                break

        call = MagicMock(spec=ServiceCall)
        call.data = {
            ATTR_PRESET_NAME: "",
            ATTR_ENTITIES: ["light.test"],
        }

        result = await create_handler(call)

        assert result["success"] is False
        assert "required" in result["message"]

    @pytest.mark.asyncio
    async def test_create_from_current_missing_entities(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test create_preset_from_current returns error when entities missing."""
        with patch(
            "custom_components.ha_light_controller.LightController",
            return_value=mock_controller,
        ), patch(
            "custom_components.ha_light_controller.PresetManager",
            return_value=mock_preset_manager,
        ):
            hass.config_entries.async_forward_entry_setups = AsyncMock()
            await async_setup_entry(hass, config_entry)

        # Get the service handler
        create_handler = None
        for call in hass.services.async_register.call_args_list:
            if call[0][1] == SERVICE_CREATE_PRESET_FROM_CURRENT:
                create_handler = call[0][2]
                break

        call = MagicMock(spec=ServiceCall)
        call.data = {
            ATTR_PRESET_NAME: "Test",
            ATTR_ENTITIES: [],
        }

        result = await create_handler(call)

        assert result["success"] is False
        assert "required" in result["message"]


# =============================================================================
# Additional Service Handler Tests for Coverage
# =============================================================================


class TestEnsureStateServiceAdvanced:
    """Advanced tests for ensure_state service handler."""

    @pytest.mark.asyncio
    async def test_ensure_state_exception_handling(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test ensure_state handles exceptions gracefully."""
        mock_controller.ensure_state = AsyncMock(side_effect=Exception("Controller error"))

        with patch(
            "custom_components.ha_light_controller.LightController",
            return_value=mock_controller,
        ), patch(
            "custom_components.ha_light_controller.PresetManager",
            return_value=mock_preset_manager,
        ):
            hass.config_entries.async_forward_entry_setups = AsyncMock()
            await async_setup_entry(hass, config_entry)

        # Get the service handler
        ensure_state_handler = None
        for call in hass.services.async_register.call_args_list:
            if call[0][1] == SERVICE_ENSURE_STATE:
                ensure_state_handler = call[0][2]
                break

        call = MagicMock(spec=ServiceCall)
        call.data = {
            ATTR_ENTITIES: ["light.test"],
            ATTR_STATE_TARGET: "on",
        }

        result = await ensure_state_handler(call)

        assert result["success"] is False
        assert result["result"] == "error"
        assert "Service error" in result["message"]

    @pytest.mark.asyncio
    async def test_ensure_state_uses_config_notify_on_failure(
        self, hass, mock_controller, mock_preset_manager
    ):
        """Test ensure_state uses notify_on_failure from config options."""
        # Create config entry with notify_on_failure option
        config_entry = MagicMock()
        config_entry.entry_id = "test_entry"
        config_entry.data = {CONF_PRESETS: {}}
        config_entry.options = {"notify_on_failure": "notify.mobile_app"}
        config_entry.async_on_unload = MagicMock()
        config_entry.add_update_listener = MagicMock()

        with patch(
            "custom_components.ha_light_controller.LightController",
            return_value=mock_controller,
        ), patch(
            "custom_components.ha_light_controller.PresetManager",
            return_value=mock_preset_manager,
        ):
            hass.config_entries.async_forward_entry_setups = AsyncMock()
            await async_setup_entry(hass, config_entry)

        # Get the service handler
        ensure_state_handler = None
        for call in hass.services.async_register.call_args_list:
            if call[0][1] == SERVICE_ENSURE_STATE:
                ensure_state_handler = call[0][2]
                break

        call = MagicMock(spec=ServiceCall)
        call.data = {
            ATTR_ENTITIES: ["light.test"],
            ATTR_STATE_TARGET: "on",
        }

        await ensure_state_handler(call)

        # Verify controller was called with notify_on_failure from config
        mock_controller.ensure_state.assert_called()
        call_kwargs = mock_controller.ensure_state.call_args[1]
        assert call_kwargs["notify_on_failure"] == "notify.mobile_app"


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

        with patch(
            "custom_components.ha_light_controller.LightController",
            return_value=mock_controller,
        ), patch(
            "custom_components.ha_light_controller.PresetManager",
            return_value=mock_preset_manager,
        ):
            hass.config_entries.async_forward_entry_setups = AsyncMock()
            await async_setup_entry(hass, config_entry)

        # Get the service handler
        activate_handler = None
        for call in hass.services.async_register.call_args_list:
            if call[0][1] == SERVICE_ACTIVATE_PRESET:
                activate_handler = call[0][2]
                break

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

        with patch(
            "custom_components.ha_light_controller.LightController",
            return_value=mock_controller,
        ), patch(
            "custom_components.ha_light_controller.PresetManager",
            return_value=mock_preset_manager,
        ):
            hass.config_entries.async_forward_entry_setups = AsyncMock()
            await async_setup_entry(hass, config_entry)

        activate_handler = None
        for call in hass.services.async_register.call_args_list:
            if call[0][1] == SERVICE_ACTIVATE_PRESET:
                activate_handler = call[0][2]
                break

        call = MagicMock(spec=ServiceCall)
        call.data = {ATTR_PRESET: "My Preset"}

        result = await activate_handler(call)

        assert result["success"] is True
        mock_preset_manager.find_preset.assert_called_with("My Preset")

    @pytest.mark.asyncio
    async def test_activate_preset_exception(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test activate_preset handles exceptions."""
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

        with patch(
            "custom_components.ha_light_controller.LightController",
            return_value=mock_controller,
        ), patch(
            "custom_components.ha_light_controller.PresetManager",
            return_value=mock_preset_manager,
        ):
            hass.config_entries.async_forward_entry_setups = AsyncMock()
            await async_setup_entry(hass, config_entry)

        activate_handler = None
        for call in hass.services.async_register.call_args_list:
            if call[0][1] == SERVICE_ACTIVATE_PRESET:
                activate_handler = call[0][2]
                break

        call = MagicMock(spec=ServiceCall)
        call.data = {ATTR_PRESET: "test_preset"}

        result = await activate_handler(call)

        assert result["success"] is False
        assert "error" in result["result"]


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

        with patch(
            "custom_components.ha_light_controller.LightController",
            return_value=mock_controller,
        ), patch(
            "custom_components.ha_light_controller.PresetManager",
            return_value=mock_preset_manager,
        ):
            hass.config_entries.async_forward_entry_setups = AsyncMock()
            await async_setup_entry(hass, config_entry)

        create_handler = None
        for call in hass.services.async_register.call_args_list:
            if call[0][1] == SERVICE_CREATE_PRESET:
                create_handler = call[0][2]
                break

        call = MagicMock(spec=ServiceCall)
        call.data = {
            ATTR_PRESET_NAME: "New Preset",
            ATTR_ENTITIES: ["light.test"],
        }

        result = await create_handler(call)

        assert result["success"] is True
        assert result["result"] == "created"
        assert result["preset_id"] == "new_preset_id"
        assert result["preset_name"] == "New Preset"

    @pytest.mark.asyncio
    async def test_create_preset_exception(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test create_preset handles exceptions."""
        mock_preset_manager.create_preset = AsyncMock(side_effect=Exception("DB error"))

        with patch(
            "custom_components.ha_light_controller.LightController",
            return_value=mock_controller,
        ), patch(
            "custom_components.ha_light_controller.PresetManager",
            return_value=mock_preset_manager,
        ):
            hass.config_entries.async_forward_entry_setups = AsyncMock()
            await async_setup_entry(hass, config_entry)

        create_handler = None
        for call in hass.services.async_register.call_args_list:
            if call[0][1] == SERVICE_CREATE_PRESET:
                create_handler = call[0][2]
                break

        call = MagicMock(spec=ServiceCall)
        call.data = {
            ATTR_PRESET_NAME: "New Preset",
            ATTR_ENTITIES: ["light.test"],
        }

        result = await create_handler(call)

        assert result["success"] is False
        assert "Error creating preset" in result["message"]


class TestDeletePresetServiceAdvanced:
    """Advanced tests for delete_preset service handler."""

    @pytest.mark.asyncio
    async def test_delete_preset_success(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test delete_preset success path."""
        mock_preset_manager.delete_preset = AsyncMock(return_value=True)

        with patch(
            "custom_components.ha_light_controller.LightController",
            return_value=mock_controller,
        ), patch(
            "custom_components.ha_light_controller.PresetManager",
            return_value=mock_preset_manager,
        ):
            hass.config_entries.async_forward_entry_setups = AsyncMock()
            await async_setup_entry(hass, config_entry)

        delete_handler = None
        for call in hass.services.async_register.call_args_list:
            if call[0][1] == SERVICE_DELETE_PRESET:
                delete_handler = call[0][2]
                break

        call = MagicMock(spec=ServiceCall)
        call.data = {ATTR_PRESET_ID: "preset_to_delete"}

        result = await delete_handler(call)

        assert result["success"] is True
        assert result["result"] == "deleted"
        assert result["preset_id"] == "preset_to_delete"

    @pytest.mark.asyncio
    async def test_delete_preset_exception(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test delete_preset handles exceptions."""
        mock_preset_manager.delete_preset = AsyncMock(side_effect=Exception("DB error"))

        with patch(
            "custom_components.ha_light_controller.LightController",
            return_value=mock_controller,
        ), patch(
            "custom_components.ha_light_controller.PresetManager",
            return_value=mock_preset_manager,
        ):
            hass.config_entries.async_forward_entry_setups = AsyncMock()
            await async_setup_entry(hass, config_entry)

        delete_handler = None
        for call in hass.services.async_register.call_args_list:
            if call[0][1] == SERVICE_DELETE_PRESET:
                delete_handler = call[0][2]
                break

        call = MagicMock(spec=ServiceCall)
        call.data = {ATTR_PRESET_ID: "preset_id"}

        result = await delete_handler(call)

        assert result["success"] is False
        assert "Error deleting preset" in result["message"]


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
        mock_preset_manager.create_preset_from_current = AsyncMock(return_value=created_preset)

        with patch(
            "custom_components.ha_light_controller.LightController",
            return_value=mock_controller,
        ), patch(
            "custom_components.ha_light_controller.PresetManager",
            return_value=mock_preset_manager,
        ):
            hass.config_entries.async_forward_entry_setups = AsyncMock()
            await async_setup_entry(hass, config_entry)

        create_handler = None
        for call in hass.services.async_register.call_args_list:
            if call[0][1] == SERVICE_CREATE_PRESET_FROM_CURRENT:
                create_handler = call[0][2]
                break

        call = MagicMock(spec=ServiceCall)
        call.data = {
            ATTR_PRESET_NAME: "From Current",
            ATTR_ENTITIES: ["light.test"],
        }

        result = await create_handler(call)

        assert result["success"] is True
        assert result["result"] == "created"
        assert result["preset_id"] == "from_current_id"
        assert result["preset_name"] == "From Current"

    @pytest.mark.asyncio
    async def test_create_from_current_returns_none(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test create_preset_from_current when preset_manager returns None."""
        mock_preset_manager.create_preset_from_current = AsyncMock(return_value=None)

        with patch(
            "custom_components.ha_light_controller.LightController",
            return_value=mock_controller,
        ), patch(
            "custom_components.ha_light_controller.PresetManager",
            return_value=mock_preset_manager,
        ):
            hass.config_entries.async_forward_entry_setups = AsyncMock()
            await async_setup_entry(hass, config_entry)

        create_handler = None
        for call in hass.services.async_register.call_args_list:
            if call[0][1] == SERVICE_CREATE_PRESET_FROM_CURRENT:
                create_handler = call[0][2]
                break

        call = MagicMock(spec=ServiceCall)
        call.data = {
            ATTR_PRESET_NAME: "Test",
            ATTR_ENTITIES: ["light.test"],
        }

        result = await create_handler(call)

        assert result["success"] is False
        assert "Failed to create preset" in result["message"]

    @pytest.mark.asyncio
    async def test_create_from_current_exception(
        self, hass, config_entry, mock_controller, mock_preset_manager
    ):
        """Test create_preset_from_current handles exceptions."""
        mock_preset_manager.create_preset_from_current = AsyncMock(
            side_effect=Exception("State read error")
        )

        with patch(
            "custom_components.ha_light_controller.LightController",
            return_value=mock_controller,
        ), patch(
            "custom_components.ha_light_controller.PresetManager",
            return_value=mock_preset_manager,
        ):
            hass.config_entries.async_forward_entry_setups = AsyncMock()
            await async_setup_entry(hass, config_entry)

        create_handler = None
        for call in hass.services.async_register.call_args_list:
            if call[0][1] == SERVICE_CREATE_PRESET_FROM_CURRENT:
                create_handler = call[0][2]
                break

        call = MagicMock(spec=ServiceCall)
        call.data = {
            ATTR_PRESET_NAME: "Test",
            ATTR_ENTITIES: ["light.test"],
        }

        result = await create_handler(call)

        assert result["success"] is False
        assert "Error creating preset" in result["message"]
