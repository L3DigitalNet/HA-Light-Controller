# Fix Preset Configuration Gaps Implementation Plan

> ✅ **STATUS: COMPLETED** (implemented in v0.2.1)
>
> **Implementation:**
> - Commits 787e429 through 3ab3816 (2026-01-31) completed all 8 tasks
> - LightTarget now has `state` and `transition` fields with proper defaults
> - Per-entity state and transition overrides fully functional
> - Mixed on/off states in single preset supported via `_send_commands_per_target()`
> - Preset creation derives state/transition from per-entity configs
> - Full test coverage added for new functionality
>
> **Note:**
> This plan was created and executed on 2026-01-31 alongside the scope simplification work (v0.2.0). The implementation completed all tasks as specified, adding per-entity state and transition support to the backend to match the UI capabilities.

---

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix 4 gaps where per-entity preset configuration is collected by UI but not used by controller.

**Architecture:** Add `state` and `transition` fields to `LightTarget` dataclass, modify `_build_targets()` to read these from overrides, update `_send_commands()` to handle per-entity state splitting, and fix `_create_preset_from_data()` to derive preset-level state/transition from per-entity configs.

**Tech Stack:** Python, Home Assistant integration framework, pytest

---

## Background

The UI allows users to configure per-entity state (on/off) and transition for each light in a preset. However:
1. `LightTarget` doesn't have `state` or `transition` fields
2. `_build_targets()` ignores `state` and `transition` from overrides
3. `_create_preset_from_data()` hardcodes `state="on"` and `transition=0.0`

## Design Decision: Per-Entity State Handling

When a preset has mixed per-entity states (some lights "on", some "off"), the controller needs to:
1. Split targets into two groups: on-targets and off-targets
2. Send turn_on commands to on-targets
3. Send turn_off commands to off-targets

This is a significant architectural change to `ensure_state()` which currently assumes all lights have the same target state.

---

## Task 1: Add state and transition fields to LightTarget

**Files:**
- Modify: `custom_components/ha_light_controller/controller.py:128-136`
- Test: `tests/test_controller.py`

**Step 1: Write failing test for LightTarget with state field**

Add to `tests/test_controller.py` after the existing LightTarget tests (around line 150):

```python
class TestLightTargetStateAndTransition:
    """Tests for LightTarget state and transition fields."""

    def test_light_target_default_state_on(self):
        """Test LightTarget defaults to state='on'."""
        target = LightTarget(entity_id="light.test")
        assert target.state == "on"

    def test_light_target_custom_state_off(self):
        """Test LightTarget with state='off'."""
        target = LightTarget(entity_id="light.test", state="off")
        assert target.state == "off"

    def test_light_target_default_transition_none(self):
        """Test LightTarget defaults to transition=None."""
        target = LightTarget(entity_id="light.test")
        assert target.transition is None

    def test_light_target_custom_transition(self):
        """Test LightTarget with custom transition."""
        target = LightTarget(entity_id="light.test", transition=2.5)
        assert target.transition == 2.5
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_controller.py::TestLightTargetStateAndTransition -v`
Expected: FAIL with "LightTarget() got an unexpected keyword argument 'state'"

**Step 3: Add state and transition fields to LightTarget**

In `custom_components/ha_light_controller/controller.py`, update `LightTarget` (lines 128-136):

```python
@dataclass
class LightTarget(LightSettingsMixin):
    """Target settings for a single light."""

    entity_id: str
    brightness_pct: int = 100
    rgb_color: list[int] | None = None
    color_temp_kelvin: int | None = None
    effect: str | None = None
    state: str = "on"  # NEW: per-entity target state
    transition: float | None = None  # NEW: per-entity transition
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_controller.py::TestLightTargetStateAndTransition -v`
Expected: PASS

**Step 5: Run full test suite**

Run: `pytest tests/test_controller.py -v`
Expected: All tests PASS (existing tests should still work with defaults)

**Step 6: Commit**

```bash
git add custom_components/ha_light_controller/controller.py tests/test_controller.py
git commit -m "feat: add state and transition fields to LightTarget

- LightTarget now has state field (default 'on')
- LightTarget now has transition field (default None)
- Existing behavior unchanged due to defaults"
```

---

## Task 2: Update _build_targets to read state and transition from overrides

**Files:**
- Modify: `custom_components/ha_light_controller/controller.py:281-308`
- Test: `tests/test_controller.py`

**Step 1: Write failing test for _build_targets with state/transition overrides**

Add to `tests/test_controller.py` in `TestLightControllerTargetBuilding` class (around line 450):

```python
    def test_build_targets_with_state_override(self, hass, mock_light_states):
        """Test building targets with per-entity state override."""
        controller = LightController(hass)
        overrides = {
            "light.test_light_1": {
                "entity_id": "light.test_light_1",
                "state": "off",
            }
        }
        targets = controller._build_targets(
            members=["light.test_light_1", "light.test_light_2"],
            overrides=overrides,
            default_brightness_pct=100,
            default_rgb_color=None,
            default_color_temp_kelvin=None,
            default_effect=None,
        )
        # First light has state override
        assert targets[0].state == "off"
        # Second light uses default
        assert targets[1].state == "on"

    def test_build_targets_with_transition_override(self, hass, mock_light_states):
        """Test building targets with per-entity transition override."""
        controller = LightController(hass)
        overrides = {
            "light.test_light_1": {
                "entity_id": "light.test_light_1",
                "transition": 3.0,
            }
        }
        targets = controller._build_targets(
            members=["light.test_light_1", "light.test_light_2"],
            overrides=overrides,
            default_brightness_pct=100,
            default_rgb_color=None,
            default_color_temp_kelvin=None,
            default_effect=None,
        )
        # First light has transition override
        assert targets[0].transition == 3.0
        # Second light uses default
        assert targets[1].transition is None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_controller.py::TestLightControllerTargetBuilding::test_build_targets_with_state_override -v`
Expected: FAIL - state will be "on" (default) instead of "off"

**Step 3: Update _build_targets to read state and transition**

In `custom_components/ha_light_controller/controller.py`, update `_build_targets()` (lines 281-308):

```python
    def _build_targets(
        self,
        members: list[str],
        overrides: dict[str, dict[str, Any]],
        default_brightness_pct: int,
        default_rgb_color: list[int] | None,
        default_color_temp_kelvin: int | None,
        default_effect: str | None,
        default_state: str = "on",  # NEW parameter
        default_transition: float | None = None,  # NEW parameter
    ) -> list[LightTarget]:
        """Build LightTarget objects for each member."""
        targets: list[LightTarget] = []

        for entity_id in members:
            override = overrides.get(entity_id, {})

            target = LightTarget(
                entity_id=entity_id,
                brightness_pct=override.get("brightness_pct", default_brightness_pct),
                rgb_color=override.get("rgb_color", default_rgb_color),
                color_temp_kelvin=override.get(
                    "color_temp_kelvin",
                    override.get("color_temperature_kelvin", default_color_temp_kelvin),
                ),
                effect=override.get("effect", default_effect),
                state=override.get("state", default_state),  # NEW
                transition=override.get("transition", default_transition),  # NEW
            )
            targets.append(target)

        return targets
```

**Step 4: Update call site in ensure_state (around line 643)**

Find the `_build_targets` call and update it:

```python
        # Build targets
        pending_targets = self._build_targets(
            members,
            overrides,
            default_brightness_pct,
            default_rgb_color,
            default_color_temp_kelvin,
            default_effect,
            default_state=state_target,  # NEW: pass the global state target
            default_transition=transition if transition > 0 else None,  # NEW
        )
```

**Step 5: Run tests to verify they pass**

Run: `pytest tests/test_controller.py::TestLightControllerTargetBuilding -v`
Expected: All PASS

**Step 6: Run full test suite**

Run: `pytest tests/test_controller.py -v`
Expected: All tests PASS

**Step 7: Commit**

```bash
git add custom_components/ha_light_controller/controller.py tests/test_controller.py
git commit -m "feat: _build_targets reads state and transition from overrides

- Per-entity state override now populates LightTarget.state
- Per-entity transition override now populates LightTarget.transition
- Added default_state and default_transition parameters
- Updated ensure_state call site to pass defaults"
```

---

## Task 3: Implement per-entity state handling in command sending

**Files:**
- Modify: `custom_components/ha_light_controller/controller.py:514-526`
- Test: `tests/test_controller.py`

**Step 1: Write failing test for mixed state handling**

Add to `tests/test_controller.py`:

```python
class TestMixedStateHandling:
    """Tests for handling presets with mixed on/off states."""

    @pytest.mark.asyncio
    async def test_send_commands_splits_by_state(self, hass, mock_light_states):
        """Test that _send_commands handles mixed per-entity states."""
        controller = LightController(hass)

        # Create targets with mixed states
        targets = [
            LightTarget("light.on_1", brightness_pct=100, state="on"),
            LightTarget("light.on_2", brightness_pct=100, state="on"),
            LightTarget("light.off_1", brightness_pct=100, state="off"),
        ]

        # Track which entities get which commands
        turn_on_calls = []
        turn_off_calls = []

        async def mock_call(domain, service, data, **kwargs):
            if service == "turn_on":
                turn_on_calls.append(data.get("entity_id", []))
            elif service == "turn_off":
                turn_off_calls.append(data.get("entity_id", []))

        hass.services.async_call = AsyncMock(side_effect=mock_call)

        # Call the method that handles state splitting
        await controller._send_commands_per_target(targets)

        # Verify on commands went to on lights
        all_on_entities = [e for call in turn_on_calls for e in (call if isinstance(call, list) else [call])]
        assert "light.on_1" in all_on_entities
        assert "light.on_2" in all_on_entities
        assert "light.off_1" not in all_on_entities

        # Verify off command went to off light
        all_off_entities = [e for call in turn_off_calls for e in (call if isinstance(call, list) else [call])]
        assert "light.off_1" in all_off_entities
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_controller.py::TestMixedStateHandling -v`
Expected: FAIL - `_send_commands_per_target` doesn't exist

**Step 3: Implement _send_commands_per_target**

In `custom_components/ha_light_controller/controller.py`, add new method after `_send_commands` (around line 527):

```python
    async def _send_commands_per_target(
        self,
        targets: list[LightTarget],
        global_transition: float | None = None,
    ) -> None:
        """Send commands to targets, respecting per-entity state and transition.

        This method splits targets by state (on/off) and sends appropriate commands.
        Per-entity transition takes precedence over global_transition.
        """
        # Split targets by state
        on_targets = [t for t in targets if t.state == "on"]
        off_targets = [t for t in targets if t.state == "off"]

        # Send turn_off commands (no grouping needed, just entity list)
        if off_targets:
            off_entities = [t.entity_id for t in off_targets]
            await self._send_turn_off(off_entities)

        # Send turn_on commands (group by settings for efficiency)
        if on_targets:
            # Group targets with same settings (including transition)
            groups = self._group_by_settings_with_transition(on_targets, global_transition)
            tasks = []
            for group, transition in groups:
                tasks.append(self._send_turn_on(group, transition))
            await asyncio.gather(*tasks)

    def _group_by_settings_with_transition(
        self,
        targets: list[LightTarget],
        global_transition: float | None,
    ) -> list[tuple[LightGroup, float | None]]:
        """Group targets by settings, returning groups with their transition values."""
        groups: dict[tuple, tuple[LightGroup, float | None]] = {}

        for target in targets:
            # Use per-entity transition if set, else global
            transition = target.transition if target.transition is not None else global_transition

            rgb_key = tuple(target.rgb_color) if target.rgb_color else None
            key = (
                target.brightness_pct,
                rgb_key,
                target.color_temp_kelvin,
                target.effect,
                transition,  # Include transition in grouping key
            )

            if key not in groups:
                group = LightGroup(
                    entities=[target.entity_id],
                    brightness_pct=target.brightness_pct,
                    rgb_color=target.rgb_color,
                    color_temp_kelvin=target.color_temp_kelvin,
                    effect=target.effect,
                )
                groups[key] = (group, transition)
            else:
                groups[key][0].entities.append(target.entity_id)

        return list(groups.values())
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_controller.py::TestMixedStateHandling -v`
Expected: PASS

**Step 5: Commit**

```bash
git add custom_components/ha_light_controller/controller.py tests/test_controller.py
git commit -m "feat: add _send_commands_per_target for mixed state handling

- Splits targets by state (on/off) and sends appropriate commands
- Groups on-targets by settings for efficient batching
- Supports per-entity transition with fallback to global"
```

---

## Task 4: Wire up per-entity handling in ensure_state

**Files:**
- Modify: `custom_components/ha_light_controller/controller.py:652-700`
- Test: `tests/test_controller.py`

**Step 1: Write integration test for ensure_state with mixed states**

Add to `tests/test_controller.py`:

```python
class TestEnsureStateMixedTargets:
    """Tests for ensure_state with mixed per-entity states."""

    @pytest.mark.asyncio
    async def test_ensure_state_mixed_states(self, hass, mock_light_states):
        """Test ensure_state handles targets with mixed on/off states."""
        from tests.conftest import create_light_state

        # Set up state tracking
        entity_states = {
            "light.turn_on": "off",  # Currently off, target on
            "light.turn_off": "on",  # Currently on, target off
        }

        def get_state(entity_id):
            state_value = entity_states.get(entity_id, "unavailable")
            return create_light_state(entity_id, state_value, brightness=255)

        async def mock_call(domain, service, data, **kwargs):
            entities = data.get("entity_id", [])
            if not isinstance(entities, list):
                entities = [entities]
            for entity_id in entities:
                if service == "turn_on":
                    entity_states[entity_id] = "on"
                elif service == "turn_off":
                    entity_states[entity_id] = "off"

        hass.states.get = MagicMock(side_effect=get_state)
        hass.services.async_call = AsyncMock(side_effect=mock_call)

        controller = LightController(hass)

        result = await controller.ensure_state(
            entities=["light.turn_on", "light.turn_off"],
            state_target="on",  # Global default
            targets=[
                {"entity_id": "light.turn_on", "state": "on", "brightness_pct": 100},
                {"entity_id": "light.turn_off", "state": "off"},
            ],
        )

        assert result["success"] is True
        # Verify final states
        assert entity_states["light.turn_on"] == "on"
        assert entity_states["light.turn_off"] == "off"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_controller.py::TestEnsureStateMixedTargets -v`
Expected: FAIL - current code doesn't use per-entity state

**Step 3: Update ensure_state to use _send_commands_per_target**

In `custom_components/ha_light_controller/controller.py`, update the fire-and-forget section (around line 652):

Replace:
```python
        # Fire-and-forget mode
        if skip_verification:
            _LOGGER.info("Fire-and-forget mode")
            groups = self._group_by_settings(pending_targets)
            use_transition = transition if target_state == TargetState.ON else None
            await self._send_commands(groups, target_state, use_transition)
```

With:
```python
        # Fire-and-forget mode
        if skip_verification:
            _LOGGER.info("Fire-and-forget mode")
            # Use per-target command sending for mixed states
            await self._send_commands_per_target(
                pending_targets,
                global_transition=transition if transition > 0 else None,
            )
```

**Step 4: Update the main retry loop (around line 699)**

Replace:
```python
            groups = self._group_by_settings(pending_targets)
            await self._send_commands(groups, target_state, use_transition)
```

With:
```python
            # Use per-target command sending for mixed states
            await self._send_commands_per_target(
                pending_targets,
                global_transition=use_transition,
            )
```

**Step 5: Update verification to use per-target state**

In the verification section (around line 708), update:

Replace:
```python
            still_pending = [
                target
                for target in pending_targets
                if self._verify_light(target, target_state, tolerances)
                not in [VerificationResult.SUCCESS, VerificationResult.UNAVAILABLE]
            ]
```

With:
```python
            still_pending = [
                target
                for target in pending_targets
                if self._verify_light(
                    target,
                    TargetState.from_string(target.state),  # Use per-entity state
                    tolerances,
                )
                not in [VerificationResult.SUCCESS, VerificationResult.UNAVAILABLE]
            ]
```

**Step 6: Run tests to verify they pass**

Run: `pytest tests/test_controller.py::TestEnsureStateMixedTargets -v`
Expected: PASS

**Step 7: Run full test suite**

Run: `pytest tests/test_controller.py -v`
Expected: All tests PASS

**Step 8: Commit**

```bash
git add custom_components/ha_light_controller/controller.py tests/test_controller.py
git commit -m "feat: ensure_state uses per-entity state and transition

- Fire-and-forget mode uses _send_commands_per_target
- Retry loop uses _send_commands_per_target
- Verification uses per-entity target state
- Enables mixed on/off presets"
```

---

## Task 5: Fix preset-level state/transition in _create_preset_from_data

**Files:**
- Modify: `custom_components/ha_light_controller/config_flow.py:750-797`
- Test: `tests/test_config_flow.py`

**Step 1: Write failing test for preset creation with derived state**

Add to `tests/test_config_flow.py`:

```python
class TestPresetCreationStateDerivation:
    """Tests for preset state/transition derivation from per-entity configs."""

    @pytest.mark.asyncio
    async def test_preset_state_derived_from_targets_all_off(
        self, hass, config_entry_with_presets
    ):
        """Test preset state is 'off' when all targets are off."""
        from custom_components.ha_light_controller.config_flow import (
            LightControllerOptionsFlowHandler,
        )

        flow = LightControllerOptionsFlowHandler(config_entry_with_presets)
        flow.hass = hass

        # Set up preset data with all targets "off"
        flow._preset_data = {
            "name": "All Off Preset",
            "entities": ["light.test1", "light.test2"],
            "skip_verification": False,
            "targets": {
                "light.test1": {"entity_id": "light.test1", "state": "off"},
                "light.test2": {"entity_id": "light.test2", "state": "off"},
            },
        }

        # Mock preset_manager
        mock_preset_manager = MagicMock()
        mock_preset_manager.presets = {}
        mock_preset_manager.create_preset = AsyncMock()

        config_entry_with_presets.runtime_data = MagicMock()
        config_entry_with_presets.runtime_data.preset_manager = mock_preset_manager

        await flow._create_preset_from_data()

        # Verify create_preset was called with state="off"
        call_kwargs = mock_preset_manager.create_preset.call_args
        assert call_kwargs.kwargs.get("state") == "off" or call_kwargs[1].get("state") == "off"

    @pytest.mark.asyncio
    async def test_preset_state_derived_mixed_uses_on(
        self, hass, config_entry_with_presets
    ):
        """Test preset state is 'on' when targets are mixed (for backwards compat)."""
        from custom_components.ha_light_controller.config_flow import (
            LightControllerOptionsFlowHandler,
        )

        flow = LightControllerOptionsFlowHandler(config_entry_with_presets)
        flow.hass = hass

        # Set up preset data with mixed targets
        flow._preset_data = {
            "name": "Mixed Preset",
            "entities": ["light.test1", "light.test2"],
            "skip_verification": False,
            "targets": {
                "light.test1": {"entity_id": "light.test1", "state": "on"},
                "light.test2": {"entity_id": "light.test2", "state": "off"},
            },
        }

        mock_preset_manager = MagicMock()
        mock_preset_manager.presets = {}
        mock_preset_manager.create_preset = AsyncMock()

        config_entry_with_presets.runtime_data = MagicMock()
        config_entry_with_presets.runtime_data.preset_manager = mock_preset_manager

        await flow._create_preset_from_data()

        # Mixed state defaults to "on" for preset-level
        call_kwargs = mock_preset_manager.create_preset.call_args
        assert call_kwargs.kwargs.get("state") == "on" or call_kwargs[1].get("state") == "on"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_config_flow.py::TestPresetCreationStateDerivation -v`
Expected: FAIL - state is always "on"

**Step 3: Update _create_preset_from_data to derive state**

In `custom_components/ha_light_controller/config_flow.py`, update `_create_preset_from_data()`:

```python
    async def _create_preset_from_data(self) -> ConfigFlowResult:
        """Create or update the preset from collected data with per-entity targets."""
        data = self._preset_data
        name = data.get(PRESET_NAME, "").strip()
        entities = data.get(PRESET_ENTITIES, [])
        targets_dict = data.get("targets", {})

        # Convert targets dict to list format expected by preset_manager
        targets = list(targets_dict.values())

        # Derive preset-level state from per-entity targets
        # If all targets are "off", preset state is "off"; otherwise "on"
        target_states = [t.get("state", "on") for t in targets]
        preset_state = "off" if target_states and all(s == "off" for s in target_states) else "on"

        # Derive preset-level transition from per-entity targets
        # Use the maximum transition among targets (or 0.0 if none set)
        target_transitions = [t.get("transition", 0) for t in targets]
        preset_transition = max(target_transitions) if target_transitions else 0.0

        # Check if we're editing an existing preset
        editing_preset_id = getattr(self, "_editing_preset_id", None)

        # Get preset manager from runtime_data
        if hasattr(self.config_entry, 'runtime_data') and self.config_entry.runtime_data:
            preset_manager = self.config_entry.runtime_data.preset_manager
            if preset_manager:
                if editing_preset_id and editing_preset_id in preset_manager.presets:
                    # Delete old preset and create new one with same ID
                    await preset_manager.delete_preset(editing_preset_id)
                    await preset_manager.create_preset(
                        name=name,
                        entities=entities,
                        state=preset_state,  # FIXED: derived from targets
                        targets=targets,
                        transition=preset_transition,  # FIXED: derived from targets
                        skip_verification=data.get(PRESET_SKIP_VERIFICATION, False),
                    )
                    _LOGGER.info("Updated preset: %s with %d entity configs", name, len(targets))
                else:
                    # Create new preset
                    await preset_manager.create_preset(
                        name=name,
                        entities=entities,
                        state=preset_state,  # FIXED: derived from targets
                        targets=targets,
                        transition=preset_transition,  # FIXED: derived from targets
                        skip_verification=data.get(PRESET_SKIP_VERIFICATION, False),
                    )
                    _LOGGER.info("Created preset: %s with %d entity configs", name, len(targets))

        # Clear stored data
        self._preset_data = {}
        self._configuring_entity = None
        self._editing_preset_id = None

        # Return to menu
        return self.async_create_entry(title="", data=self.config_entry.options)
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_config_flow.py::TestPresetCreationStateDerivation -v`
Expected: PASS

**Step 5: Run full test suite**

Run: `pytest -v`
Expected: All tests PASS

**Step 6: Commit**

```bash
git add custom_components/ha_light_controller/config_flow.py tests/test_config_flow.py
git commit -m "fix: derive preset state/transition from per-entity configs

- Preset state is 'off' only when all targets are 'off'
- Preset transition is max of all per-entity transitions
- Removes hardcoded state='on' and transition=0.0"
```

---

## Task 6: Add test for preset activation with per-entity transition

**Files:**
- Test: `tests/test_controller.py`

**Step 1: Write test for per-entity transition**

Add to `tests/test_controller.py`:

```python
class TestPerEntityTransition:
    """Tests for per-entity transition handling."""

    @pytest.mark.asyncio
    async def test_ensure_state_per_entity_transition(self, hass, mock_light_states):
        """Test that per-entity transitions are respected."""
        from tests.conftest import create_light_state

        transitions_used = {}

        async def mock_call(domain, service, data, **kwargs):
            if service == "turn_on":
                entities = data.get("entity_id", [])
                transition = data.get("transition")
                if not isinstance(entities, list):
                    entities = [entities]
                for entity_id in entities:
                    transitions_used[entity_id] = transition

        hass.services.async_call = AsyncMock(side_effect=mock_call)

        # Set up states that will verify on first attempt
        def get_state(entity_id):
            return create_light_state(entity_id, "on", brightness=255)
        hass.states.get = MagicMock(side_effect=get_state)

        controller = LightController(hass)

        await controller.ensure_state(
            entities=["light.fast", "light.slow"],
            state_target="on",
            transition=1.0,  # Global fallback
            targets=[
                {"entity_id": "light.fast", "transition": 0.5},  # Per-entity
                {"entity_id": "light.slow", "transition": 3.0},  # Per-entity
            ],
            skip_verification=True,  # Skip verification for simplicity
        )

        # Verify per-entity transitions were used
        assert transitions_used.get("light.fast") == 0.5
        assert transitions_used.get("light.slow") == 3.0
```

**Step 2: Run test to verify it passes**

Run: `pytest tests/test_controller.py::TestPerEntityTransition -v`
Expected: PASS (should work after Task 3-4 implementation)

**Step 3: Commit**

```bash
git add tests/test_controller.py
git commit -m "test: add test for per-entity transition handling"
```

---

## Task 7: Run full test suite and verify coverage

**Step 1: Run all tests**

Run: `pytest -v`
Expected: All tests PASS

**Step 2: Check coverage**

Run: `pytest --cov=custom_components/ha_light_controller --cov-report=term-missing`
Expected: Coverage >90%

**Step 3: Verify no lingering issues**

Run: `grep -r "state=\"on\"" custom_components/ha_light_controller/config_flow.py`
Expected: No matches (hardcoded state removed)

Run: `grep -r "transition=0.0" custom_components/ha_light_controller/config_flow.py`
Expected: No matches (hardcoded transition removed)

**Step 4: Commit any fixes**

If any tests failed or coverage gaps exist, fix and commit.

---

## Task 8: Update documentation

**Files:**
- Modify: `USAGE.md`
- Modify: `README.md` (if needed)

**Step 1: Update USAGE.md with per-entity state/transition docs**

Add a section explaining per-entity configuration in presets:

```markdown
### Per-Entity Configuration in Presets

When creating a preset via the UI, you can configure each light individually:

- **State**: Set individual lights to "on" or "off" within the same preset
- **Transition**: Set different transition times for each light
- **Brightness/Color**: Already supported per-entity

This allows creating complex presets like "Movie Mode" where:
- Main ceiling light is off
- TV backlight is on at 20% with warm color
- Accent lights are on at 10%

All configured via a single button press.
```

**Step 2: Commit documentation**

```bash
git add USAGE.md README.md
git commit -m "docs: document per-entity state and transition in presets"
```

---

## Summary

After completing all tasks:
1. ✅ `LightTarget` has `state` and `transition` fields
2. ✅ `_build_targets()` reads per-entity state/transition from overrides
3. ✅ `_send_commands_per_target()` handles mixed on/off states
4. ✅ `ensure_state()` uses per-entity state for commands and verification
5. ✅ `_create_preset_from_data()` derives state/transition from targets
6. ✅ Full test coverage for new functionality
7. ✅ Documentation updated

The integration now fully supports per-entity state and transition configuration as the UI allows.
